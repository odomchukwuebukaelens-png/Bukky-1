"""City Studio prototype: brief (JSON) -> 3D city -> frames -> MP4.

Run inside Blender:   blender -b -P citystudio/make_video.py -- briefs/test_city.json
Options after the brief:  --stills   render only 3 preview frames (cheap check)
                          --check    only report GPU status, render nothing
"""
import json
import math
import os
import random
import shutil
import subprocess
import sys
import time

import bpy
import bmesh  # noqa: E402 (must come after bpy)
from mathutils import Vector

# ----------------------------------------------------------------------------
# Brief
# ----------------------------------------------------------------------------
DEFAULTS = {
    "name": "test_city",
    "title": "TEST CITY",
    "seed": 7,
    "duration_seconds": 10,
    "fps": 30,
    "resolution": [960, 540],
    "start_year": 1800,
    "end_year": 2025,
    "engine": "cycles",
    "samples": 24,
    "sound": True,
    "city": {"blocks_x": 9, "blocks_y": 13, "block_size": 60, "street_width": 14},
}


def load_brief(path):
    with open(path) as f:
        user = json.load(f)
    brief = dict(DEFAULTS)
    brief.update(user)
    city = dict(DEFAULTS["city"])
    city.update(user.get("city", {}))
    brief["city"] = city
    return brief


# ----------------------------------------------------------------------------
# GPU
# ----------------------------------------------------------------------------
def setup_gpu():
    """Turn on the NVIDIA card for Cycles. Returns a plain-language status."""
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
    except KeyError:
        return False, "Cycles add-on not available"
    for kind in ("OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = kind
        except TypeError:
            continue
        if hasattr(prefs, "refresh_devices"):
            prefs.refresh_devices()
        else:
            prefs.get_devices()
        gpus = [d for d in prefs.devices if d.type == kind]
        if gpus:
            for d in prefs.devices:
                d.use = d.type == kind
            return True, "%s on %s" % (kind, ", ".join(d.name for d in gpus))
    return False, "no NVIDIA GPU visible to Blender - using CPU (slow)"


# ----------------------------------------------------------------------------
# Meshes and materials
# ----------------------------------------------------------------------------
def mesh_box(name):
    """Unit box: 1 x 1 footprint centred on origin, z from 0 to 1."""
    v = [(-.5, -.5, 0), (.5, -.5, 0), (.5, .5, 0), (-.5, .5, 0),
         (-.5, -.5, 1), (.5, -.5, 1), (.5, .5, 1), (-.5, .5, 1)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    m = bpy.data.meshes.new(name)
    m.from_pydata(v, [], f)
    return m


def mesh_house(name):
    """Unit house: walls up to z=0.6, pitched roof up to z=1. Roof uses slot 1."""
    w = 0.6
    v = [(-.5, -.5, 0), (.5, -.5, 0), (.5, .5, 0), (-.5, .5, 0),
         (-.5, -.5, w), (.5, -.5, w), (.5, .5, w), (-.5, .5, w),
         (0, -.5, 1), (0, .5, 1)]
    f = [(0, 3, 2, 1), (0, 1, 5, 4), (2, 3, 7, 6), (1, 2, 6, 5), (3, 0, 4, 7),
         (4, 5, 8), (6, 7, 9),            # gable ends
         (5, 6, 9, 8), (7, 4, 8, 9)]      # roof slopes
    m = bpy.data.meshes.new(name)
    m.from_pydata(v, [], f)
    return m, (7, 8)


def mesh_tree(name):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.5)
    for vert in bm.verts:
        vert.co.z = vert.co.z * 1.2 + 0.75
    m = bpy.data.meshes.new(name)
    bm.to_mesh(m)
    bm.free()
    return m


def new_material(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    return mat, nt, bsdf


def flat_material(name, rgb, rough=0.8):
    mat, nt, bsdf = new_material(name)
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Roughness"].default_value = rough
    return mat


def object_colour_material(name, windows):
    """Colour comes from each object's own colour. If windows=True, the object
    colour's alpha channel switches on a simple dark window grid on the walls."""
    mat, nt, bsdf = new_material(name)
    bsdf.inputs["Roughness"].default_value = 0.75
    info = nt.nodes.new("ShaderNodeObjectInfo")
    if not windows:
        nt.links.new(info.outputs["Color"], bsdf.inputs["Base Color"])
        return mat

    def math(op, a, b=None):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = op
        for i, val in enumerate((a, b)):
            if val is None:
                continue
            if isinstance(val, (int, float)):
                n.inputs[i].default_value = val
            else:
                nt.links.new(val, n.inputs[i])
        return n.outputs[0]

    geo = nt.nodes.new("ShaderNodeNewGeometry")
    pos = nt.nodes.new("ShaderNodeSeparateXYZ")
    nrm = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], pos.inputs[0])
    nt.links.new(geo.outputs["Normal"], nrm.inputs[0])
    floors = math("GREATER_THAN", math("FRACT", math("DIVIDE", pos.outputs["Z"], 3.6)), 0.45)
    bays = math("GREATER_THAN",
                math("FRACT", math("DIVIDE", math("ADD", pos.outputs["X"], pos.outputs["Y"]), 3.0)), 0.4)
    walls = math("LESS_THAN", math("ABSOLUTE", nrm.outputs["Z"]), 0.5)
    mask = math("MULTIPLY", math("MULTIPLY", floors, bays), walls)
    mask = math("MULTIPLY", math("MULTIPLY", mask, info.outputs["Alpha"]), 0.8)
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    nt.links.new(mask, mix.inputs[0])
    nt.links.new(info.outputs["Color"], mix.inputs[6])
    mix.inputs[7].default_value = (0.05, 0.08, 0.13, 1)
    nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])
    return mat


def water_material():
    mat, nt, bsdf = new_material("Water")
    bsdf.inputs["Base Color"].default_value = (0.02, 0.22, 0.27, 1)
    bsdf.inputs["Roughness"].default_value = 0.12
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 0.05
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.15
    nt.links.new(noise.outputs[0], bump.inputs["Height"])
    nt.links.new(bump.outputs[0], bsdf.inputs["Normal"])
    return mat


def text_material():
    mat = bpy.data.materials.new("Overlay")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (1, 1, 1, 1)
    em.inputs["Strength"].default_value = 1.0
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs[0], out.inputs[0])
    return mat


# ----------------------------------------------------------------------------
# City plan (pure data - no Blender objects yet)
# ----------------------------------------------------------------------------
BRICK = [(0.45, 0.16, 0.11), (0.52, 0.22, 0.15), (0.38, 0.15, 0.12), (0.60, 0.42, 0.30)]
STONE = [(0.72, 0.66, 0.54), (0.62, 0.58, 0.50), (0.80, 0.75, 0.64), (0.50, 0.48, 0.46)]
GLASS = [(0.25, 0.42, 0.62), (0.35, 0.50, 0.66), (0.18, 0.30, 0.45), (0.55, 0.62, 0.70)]


def plan_city(brief):
    """Decide where every block, building and tree goes and in which year.
    Everything here is invented for the test (artistic, not factual)."""
    rng = random.Random(brief["seed"])
    c = brief["city"]
    nx, ny, bs, sw = c["blocks_x"], c["blocks_y"], c["block_size"], c["street_width"]
    pitch = bs + sw
    y0, y1 = brief["start_year"], brief["end_year"]
    span = y1 - y0
    half_w, half_h = nx * pitch / 2, ny * pitch / 2
    ph1, ph2 = rng.uniform(0, 6.28), rng.uniform(0, 6.28)

    def island_radius(theta):
        wob = 1 + 0.07 * math.sin(3 * theta + ph1) + 0.05 * math.sin(5 * theta + ph2)
        a, b = half_w * 1.12, half_h * 1.10
        return wob * a * b / math.hypot(b * math.cos(theta), a * math.sin(theta))

    def on_island(x, y, margin=0.0):
        return math.hypot(x, y) + margin < island_radius(math.atan2(y, x))

    old_town = Vector((0, -half_h * 0.8))          # the settlement starts at the south tip
    far = (Vector((half_w, half_h)) - old_town).length
    core = Vector((0, -half_h * 0.15))             # where towers cluster later

    blocks, buildings, trees = [], [], []
    for i in range(nx):
        for j in range(ny):
            cx = (i + 0.5) * pitch - half_w
            cy = (j + 0.5) * pitch - half_h
            h = pitch / 2
            if not all(on_island(cx + sx * h, cy + sy * h, 6) for sx in (-1, 1) for sy in (-1, 1)):
                continue
            d = (Vector((cx, cy)) - old_town).length / far
            year = y0 + span * 0.78 * d ** 0.85 + rng.uniform(-4, 4)
            year = max(y0 + 1, year)
            park = rng.random() < 0.07
            blocks.append({"x": cx, "y": cy, "year": year, "park": park})
            n_trees = 16 if park else rng.randint(4, 8)
            for _ in range(n_trees):
                trees.append({"x": cx + rng.uniform(-bs, bs) / 2, "y": cy + rng.uniform(-bs, bs) / 2,
                              "s": rng.uniform(7, 13), "gone": None if park else year,
                              "tint": rng.uniform(0.75, 1.15)})
            if park:
                continue

            core_d = (Vector((cx, cy)) - core).length / (half_h * 0.9)
            tower_block = core_d < 0.6 and rng.random() < 0.8
            early = year < y0 + span * 0.35
            n = 3 if early else 2
            lot = bs / n
            for a in range(n):
                for b in range(n):
                    lx = cx - bs / 2 + (a + 0.5) * lot
                    ly = cy - bs / 2 + (b + 0.5) * lot
                    built = year + rng.uniform(0, 14)
                    gone = None
                    if tower_block and rng.random() < 0.45:
                        # low building first, replaced later by a tower
                        gone = max(built + 20, y0 + span * rng.uniform(0.45, 0.97))
                        height = rng.uniform(35, 80) * (1.5 - core_d) + (gone - y0) / span * 70
                        modern = gone > y0 + span * 0.7
                        buildings.append({
                            "x": lx, "y": ly, "w": lot * rng.uniform(0.78, 0.92), "d": lot * rng.uniform(0.78, 0.92),
                            "h": height, "year": gone, "gone": None, "kind": "box", "windows": 1.0,
                            "rgb": rng.choice(GLASS if modern else STONE)})
                    if early:
                        buildings.append({
                            "x": lx, "y": ly, "w": lot * 0.78, "d": lot * 0.78, "h": rng.uniform(8, 13),
                            "year": built, "gone": gone, "kind": "house", "windows": 0.0,
                            "rgb": rng.choice(BRICK), "turn": rng.random() < 0.5})
                    else:
                        buildings.append({
                            "x": lx, "y": ly, "w": lot * 0.84, "d": lot * 0.84, "h": rng.uniform(14, 34),
                            "year": built, "gone": gone, "kind": "box", "windows": 0.6,
                            "rgb": rng.choice(BRICK + STONE)})

    # permanent woodland on the shore, outside the street grid
    limit = max(half_w, half_h) * 1.3
    tries = 0
    while len([t for t in trees if t["gone"] is None]) < 260 and tries < 20000:
        tries += 1
        x, y = rng.uniform(-limit, limit), rng.uniform(-limit, limit)
        if not on_island(x, y, 10):
            continue
        if any(abs(x - b["x"]) < pitch / 2 and abs(y - b["y"]) < pitch / 2 for b in blocks):
            continue
        trees.append({"x": x, "y": y, "s": rng.uniform(8, 15), "gone": None, "tint": rng.uniform(0.75, 1.15)})

    shore = [(island_radius(t) * math.cos(t), island_radius(t) * math.sin(t))
             for t in (k * 2 * math.pi / 120 for k in range(120))]
    return {"blocks": blocks, "buildings": buildings, "trees": trees, "shore": shore,
            "pitch": pitch, "block_size": bs, "extent": max(half_w, half_h)}


# ----------------------------------------------------------------------------
# Build the Blender scene from the plan
# ----------------------------------------------------------------------------
def build_scene(brief, plan):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    col = scene.collection

    def add(name, data):
        ob = bpy.data.objects.new(name, data)
        col.objects.link(ob)
        return ob

    box = mesh_box("Box")
    house, roof_faces = mesh_house("House")
    tree = mesh_tree("Tree")

    m_build = object_colour_material("Building", windows=True)
    m_plain = object_colour_material("Plain", windows=False)
    m_roof = flat_material("Roof", (0.55, 0.10, 0.07))
    box.materials.append(m_build)
    house.materials.append(m_build)
    house.materials.append(m_roof)
    for idx in roof_faces:
        house.polygons[idx].material_index = 1
    tree.materials.append(m_plain)

    # water and land
    water = add("Water", mesh_box("WaterMesh"))
    water.scale = (60000, 60000, 1)
    water.location.z = -3
    water.data.materials.append(water_material())

    n = len(plan["shore"])
    verts = [(x, y, 0) for x, y in plan["shore"]] + [(x * 1.03, y * 1.03, -3) for x, y in plan["shore"]]
    faces = [tuple(range(n))] + [(k, k + n, (k + 1) % n + n, (k + 1) % n) for k in range(n)]
    land_mesh = bpy.data.meshes.new("LandMesh")
    land_mesh.from_pydata(verts, [], faces)
    land_mesh.materials.append(flat_material("Grass", (0.20, 0.42, 0.10)))
    add("Land", land_mesh)

    pad_mesh = mesh_box("PadMesh")
    pad_mesh.materials.append(m_plain)

    animated = []   # (object, record, full_scale)
    bs, pitch = plan["block_size"], plan["pitch"]
    for b in plan["blocks"]:
        road = add("Road", pad_mesh)                    # pale street surface under the block
        road.location = (b["x"], b["y"], 0)
        road.color = (0.74, 0.71, 0.64, 0)
        animated.append((road, {"year": b["year"] - 3, "gone": None, "grow": 3}, (pitch + 0.5, pitch + 0.5, 0.25)))
        slab = add("Block", pad_mesh)                   # the block itself (pavement or park lawn)
        slab.location = (b["x"], b["y"], 0)
        slab.color = (0.25, 0.50, 0.13, 0) if b["park"] else (0.60, 0.57, 0.52, 0)
        animated.append((slab, {"year": b["year"] - 2, "gone": None, "grow": 3}, (bs, bs, 0.6)))

    for r in plan["buildings"]:
        ob = add("Bldg", house if r["kind"] == "house" else box)
        ob.location = (r["x"], r["y"], 0.6)
        if r.get("turn"):
            ob.rotation_euler.z = math.pi / 2
        ob.color = (*r["rgb"], r["windows"])
        rec = dict(r)
        rec["grow"] = 4 + r["h"] / 18            # taller buildings take more years to rise
        animated.append((ob, rec, (r["w"], r["d"], r["h"])))

    for t in plan["trees"]:
        ob = add("Tree", tree)
        ob.location = (t["x"], t["y"], 0)
        g = t["tint"]
        ob.color = (0.10 * g, 0.33 * g, 0.07 * g, 0)
        s = t["s"]
        animated.append((ob, {"year": -1e9, "gone": t["gone"], "grow": 1, "fade": 3}, (s, s, s)))

    # light and sky
    sun = add("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 3.2
    sun.data.angle = math.radians(3)
    sun.rotation_euler = (math.radians(52), 0, math.radians(-35))
    world = bpy.data.worlds.new("Sky")
    world.use_nodes = True
    bg = next(nd for nd in world.node_tree.nodes if nd.type == "BACKGROUND")
    bg.inputs[0].default_value = (0.70, 0.82, 0.95, 1)
    bg.inputs[1].default_value = 0.55
    scene.world = world

    # camera with the year counter attached to it
    cam = add("Camera", bpy.data.cameras.new("Camera"))
    cam.data.lens = 35
    cam.data.clip_end = 100000
    scene.camera = cam
    m_text = text_material()

    def overlay(name, body, size, y):
        cu = bpy.data.curves.new(name, "FONT")
        cu.body = body
        cu.size = size
        cu.align_x = "CENTER"
        cu.materials.append(m_text)
        ob = add(name, cu)
        ob.parent = cam
        ob.location = (0, y, -1)
        ob.visible_shadow = False
        return ob

    year_text = overlay("Year", str(brief["start_year"]), 0.06, 0.215)
    overlay("Title", "  ".join(brief["title"].upper()), 0.013, 0.192)

    return {"scene": scene, "animated": animated, "camera": cam, "year_text": year_text,
            "extent": plan["extent"]}


# ----------------------------------------------------------------------------
# Animation: everything is a function of the frame number
# ----------------------------------------------------------------------------
def ease(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def apply_frame(brief, rig, frame, total):
    fps = brief["fps"]
    t_cam = frame / max(1, total - 1)
    hold = min(fps, total // 5)                    # final year holds for the last second
    t_year = min(1.0, frame / max(1, total - 1 - hold))
    year = brief["start_year"] + (brief["end_year"] - brief["start_year"]) * t_year

    for ob, rec, full in rig["animated"]:
        k = ease((year - rec["year"]) / rec["grow"])
        if rec.get("gone") is not None:
            k *= 1 - ease((year - rec["gone"] + rec.get("fade", 2)) / rec.get("fade", 2))
        visible = k > 0.001
        ob.hide_render = not visible
        ob.hide_viewport = not visible
        if "fade" in rec:                           # trees shrink evenly
            ob.scale = (full[0] * k, full[1] * k, full[2] * k) if visible else (0, 0, 0)
        else:                                       # buildings rise from the ground
            ob.scale = (full[0], full[1], max(full[2] * k, 0.001))

    e = rig["extent"]
    s = t_cam * t_cam * (3 - 2 * t_cam)
    angle = math.radians(-125 + 75 * s)
    radius = e * (3.1 - 0.7 * s)
    height = e * (1.05 - 0.3 * s)
    cam = rig["camera"]
    cam.location = (radius * math.cos(angle), radius * math.sin(angle), height)
    target = Vector((0, 0, 20))
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    rig["year_text"].data.body = str(int(year))


# ----------------------------------------------------------------------------
# Render and assemble
# ----------------------------------------------------------------------------
def configure_render(brief, scene):
    r = scene.render
    r.resolution_x, r.resolution_y = brief["resolution"]
    r.resolution_percentage = 100
    r.fps = brief["fps"]
    r.image_settings.file_format = "PNG"
    r.use_persistent_data = True
    try:
        scene.view_settings.view_transform = "Standard"   # keeps colours bright and clean
    except TypeError:
        pass
    r.engine = "CYCLES"
    on_gpu, status = setup_gpu()
    scene.cycles.device = "GPU" if on_gpu else "CPU"
    scene.cycles.samples = brief["samples"]
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.max_bounces = 3
    try:
        scene.cycles.use_denoising = True
        scene.cycles.denoiser = "OPENIMAGEDENOISE"
    except TypeError:
        scene.cycles.use_denoising = False
    return status


def assemble(brief, frames_dir, out_path, total):
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("[city-studio] FFmpeg not found - frames are ready but no MP4 was made.")
        return False
    fps = brief["fps"]
    cmd = [ffmpeg, "-y", "-loglevel", "error", "-framerate", str(fps),
           "-i", os.path.join(frames_dir, "frame_%04d.png")]
    if brief.get("sound"):
        dur = total / fps
        cmd += ["-f", "lavfi", "-i",
                "anoisesrc=color=brown:duration=%.3f:amplitude=0.5,lowpass=f=500,"
                "afade=t=in:d=1.5,afade=t=out:st=%.3f:d=1.5,volume=0.5" % (dur, max(0, dur - 1.5)),
                "-c:a", "aac", "-b:a", "128k", "-shortest"]
    cmd += ["-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out_path]
    subprocess.run(cmd, check=True)
    return True


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    flags = {a for a in argv if a.startswith("--")}
    paths = [a for a in argv if not a.startswith("--")]

    if "--check" in flags:
        ok, status = setup_gpu()
        print("\n[city-studio] Blender %s" % bpy.app.version_string)
        print("[city-studio] GPU check: %s" % ("PASS - " + status if ok else "FAIL - " + status))
        return

    if not paths:
        sys.exit("Usage: ./studio run briefs/test_city.json")
    brief = load_brief(paths[0])
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(root, "output", brief["name"])
    frames_dir = os.path.join(out_dir, "stills" if "--stills" in flags else "frames")
    os.makedirs(frames_dir, exist_ok=True)

    random.seed(brief["seed"])
    plan = plan_city(brief)
    rig = build_scene(brief, plan)
    scene = rig["scene"]
    status = configure_render(brief, scene)
    total = int(round(brief["duration_seconds"] * brief["fps"]))
    print("\n[city-studio] %s: %d buildings, %d trees, %d frames at %dx%d" % (
        brief["name"], len(plan["buildings"]), len(plan["trees"]), total, *brief["resolution"]))
    print("[city-studio] Rendering with: %s" % status)

    frames = [0, total // 2, total - 1] if "--stills" in flags else list(range(total))
    done, started = 0, time.time()
    for f in frames:
        path = os.path.join(frames_dir, "frame_%04d.png" % (f + 1))
        if os.path.exists(path) and os.path.getsize(path) > 0:
            continue                                  # already rendered - resume from here
        apply_frame(brief, rig, f, total)
        scene.frame_set(f + 1)
        scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        done += 1
        if done == 1 or done % 10 == 0:
            per = (time.time() - started) / done
            left = sum(1 for g in frames if g > f)
            print("[city-studio] frame %d/%d  %.1fs per frame  about %.0f min left" % (
                f + 1, total, per, per * left / 60), flush=True)

    if "--stills" in flags:
        print("[city-studio] Preview stills saved in %s" % frames_dir)
        return
    apply_frame(brief, rig, total - 1, total)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out_dir, "scene.blend"))
    mp4 = os.path.join(out_dir, brief["name"] + ".mp4")
    if assemble(brief, frames_dir, mp4, total):
        print("[city-studio] DONE. Video saved: %s" % mp4)


if __name__ == "__main__":
    main()
