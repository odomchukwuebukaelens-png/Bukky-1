"""City Studio prototype: brief (JSON) -> 3D city -> frames -> MP4.

Run inside Blender:   blender -b -P citystudio/make_video.py -- briefs/test_city.json
Normally started through the ./studio launcher, which runs several copies of
this script side by side (workers) and then joins their output.
Options:  --check          report GPU status, render nothing
          --probe-eevee    test whether the fast EEVEE renderer works here
          --stills         render only 3 preview frames
          --engine=X       eevee or cycles
          --worker=I/N     render every Nth chunk, starting at chunk I
          --assemble       join finished chunks into the final MP4
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
    "engine": "auto",
    "samples": 24,
    "chunk_frames": 300,
    "sound": True,
    "city": {"blocks_x": 9, "blocks_y": 13, "block_size": 60, "street_width": 14},
}


HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO_PYTHON = os.environ.get("STUDIO_PYTHON", "python3")


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
def eevee_id():
    ids = {e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}
    return "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in ids else "BLENDER_EEVEE"


def configure_render(brief, scene, engine):
    r = scene.render
    realistic = brief.get("style") in ("historic", "nyc")
    r.resolution_x, r.resolution_y = brief["resolution"]
    r.resolution_percentage = 100
    r.fps = brief["fps"]
    r.image_settings.file_format = "PNG"
    r.image_settings.compression = 15
    r.use_persistent_data = True
    r.filter_size = float(brief.get("filter_size", 1.5))   # smaller = crisper pixels
    try:
        # AgX gives soft, film-like highlights for the realistic style;
        # Standard keeps the toy style bright and clean
        scene.view_settings.view_transform = ("Standard" if brief.get("view") == "standard" or not realistic
                                              else "AgX")
    except TypeError:
        scene.view_settings.view_transform = "Filmic" if realistic else "Standard"
    if realistic:
        looks = ("Medium High Contrast", "Standard - Medium High Contrast", "None") \
            if brief.get("view") == "standard" else ("AgX - Punchy", "Punchy", "AgX - Medium High Contrast", "None")
        for look in looks:
            try:
                scene.view_settings.look = look
                break
            except TypeError:
                continue
    if engine == "eevee":
        r.engine = eevee_id()
        try:
            scene.eevee.taa_render_samples = int(brief.get("eevee_samples", 16))
            if brief.get("ao", True) and realistic:
                ev = scene.eevee
                for attr, val in (("use_gtao", True), ("gtao_distance", 25.0), ("gtao_factor", 1.3),
                                  ("use_shadows", True), ("use_soft_shadows", True)):
                    if hasattr(ev, attr):
                        setattr(ev, attr, val)
        except AttributeError:
            pass
        return "EEVEE (fast mode)"
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
    return "Cycles, " + status


def probe_eevee():
    """Render one tiny EEVEE frame. If this machine cannot do it, Blender
    either raises an error or crashes; the launcher reads the exit code."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    scene.collection.objects.link(cam)
    scene.camera = cam
    scene.render.engine = eevee_id()
    scene.render.resolution_x, scene.render.resolution_y = 64, 36
    path = os.path.join(bpy.app.tempdir, "probe.png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    if not os.path.exists(path):
        sys.exit(1)
    print("[city-studio] EEVEE probe OK")


def ffmpeg_path():
    exe = shutil.which("ffmpeg")
    if not exe:
        sys.exit("[city-studio] FFmpeg not found. Run ./studio setup first.")
    return exe


def run_overlay(frames_dir, numbers):
    """Draw the on-screen graphics onto frames (comp_N.png) with system Python."""
    for i in range(0, len(numbers), 60):
        subprocess.run([STUDIO_PYTHON, os.path.join(HERE, "overlay.py"), frames_dir] +
                       [str(n) for n in numbers[i:i + 60]], check=True)


def encode_chunk(brief, frames_dir, first, count, out_path):
    """Frames of one chunk -> a small video file, then the frames are deleted
    so the disk never fills up."""
    numbers = list(range(first + 1, first + count + 1))
    overlay = os.path.exists(os.path.join(frames_dir, "frame_%06d.json" % numbers[0]))
    if overlay:
        run_overlay(frames_dir, numbers)
    tmp = out_path + ".part.mp4"
    subprocess.run([ffmpeg_path(), "-y", "-loglevel", "error", "-framerate", str(brief["fps"]),
                    "-start_number", str(first + 1),
                    "-i", os.path.join(frames_dir, ("comp_%06d.png" if overlay else "frame_%06d.png")),
                    "-frames:v", str(count)] + (["-vf", "unsharp=5:5:%.2f:5:5:0" % brief["sharpen"]]
                                                if brief.get("sharpen") else []) +
                   ["-c:v", "libx264", "-crf", str(brief.get("crf", 19)),
                    "-preset", "slow", "-pix_fmt", "yuv420p", tmp],
                   check=True)
    os.replace(tmp, out_path)
    for n in numbers:
        for pattern in ("frame_%06d.png", "frame_%06d.json", "comp_%06d.png"):
            path = os.path.join(frames_dir, pattern % n)
            if os.path.exists(path):
                os.remove(path)


def chunk_list(brief, total):
    size = max(1, int(brief["chunk_frames"]))
    return [(i, start, min(size, total - start)) for i, start in enumerate(range(0, total, size))]


def build_music_bed(tracks, out, dur):
    """Chain the given songs with crossfades and repeat them to fill the video."""
    cmd = [ffmpeg_path(), "-y", "-loglevel", "error"]
    for t in tracks:
        cmd += ["-i", t]
    if len(tracks) == 1:
        chain = "[0:a]aformat=sample_rates=44100:channel_layouts=stereo[a0]"
        last = "[a0]"
    else:
        parts = ["[%d:a]aformat=sample_rates=44100:channel_layouts=stereo[s%d]" % (i, i) for i in range(len(tracks))]
        last = "[s0]"
        for i in range(1, len(tracks)):
            parts.append("%s[s%d]acrossfade=d=4:c1=tri:c2=tri[x%d]" % (last, i, i))
            last = "[x%d]" % i
        chain = ";".join(parts)
    one = out + ".once.wav"
    subprocess.run(cmd + ["-filter_complex", chain, "-map", last, one], check=True)
    subprocess.run([ffmpeg_path(), "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", one, "-t", "%.3f" % dur,
                    "-af", "afade=t=in:d=1.5", out], check=True)
    os.remove(one)


def assemble(brief, out_dir, total):
    chunks_dir = os.path.join(out_dir, "chunks")
    names = []
    for i, _, _ in chunk_list(brief, total):
        path = os.path.join(chunks_dir, "chunk_%04d.mp4" % i)
        if not os.path.exists(path):
            sys.exit("[city-studio] Chunk %d is missing - run the same command again to finish it." % i)
        names.append(path)
    listing = os.path.join(chunks_dir, "list.txt")
    with open(listing, "w") as f:
        f.writelines("file '%s'\n" % n for n in names)
    mp4 = os.path.join(out_dir, brief["name"] + ".mp4")
    cmd = [ffmpeg_path(), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", listing]
    music = brief.get("music")
    root = os.path.dirname(HERE)
    tracks = [os.path.join(root, t) for t in brief.get("music_tracks", [])]
    found = [t for t in tracks if os.path.exists(t)]
    for t in tracks:
        if t not in found:
            print("[city-studio] Music file not found: %s" % t)
    dur = total / brief["fps"]
    if found:
        music = os.path.join(out_dir, "music_bed.wav")
        build_music_bed(found, music, dur)
    elif tracks:
        print("[city-studio] Using generated music instead.")
    sfx_events = brief.get("_sfx_timeline", brief.get("sfx", []))
    if music and sfx_events:
        bed = music
        if bed == "generate":
            bed = os.path.join(out_dir, "music.wav")
            subprocess.run([STUDIO_PYTHON, os.path.join(HERE, "music.py"), bed, "%.3f" % dur,
                            str(brief["seed"]), str(brief.get("music_build_at", 4.0)),
                            ",".join(str(v) for v in brief.get("music_accents", []))], check=True)
        ev_path = os.path.join(out_dir, "sfx_events.json")
        with open(ev_path, "w") as f:
            json.dump(sfx_events, f)
        fx = os.path.join(out_dir, "sfx.wav")
        subprocess.run([STUDIO_PYTHON, os.path.join(HERE, "sfx.py"), fx, "%.3f" % dur, ev_path], check=True)
        mixed = os.path.join(out_dir, "soundtrack.wav")
        subprocess.run([ffmpeg_path(), "-y", "-loglevel", "error", "-i", bed, "-i", fx, "-filter_complex",
                        "[0:a]volume=%.2f[m];[1:a]volume=%.2f[f];[m][f]amix=inputs=2:duration=first:normalize=0"
                        % (brief.get("music_volume", 0.8), brief.get("sfx_volume", 1.0)), mixed], check=True)
        music = mixed
    if music:
        dur = total / brief["fps"]
        if music == "generate":
            music = os.path.join(out_dir, "music.wav")
            subprocess.run([STUDIO_PYTHON, os.path.join(HERE, "music.py"), music, "%.3f" % dur,
                            str(brief["seed"]), str(brief.get("music_build_at", 4.0)),
                            ",".join(str(v) for v in brief.get("music_accents", []))], check=True)
        cmd += ["-i", music, "-map", "0:v", "-map", "1:a",
                "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st=%.3f:d=1.5" % max(0, dur - 1.5),
                "-c:a", "aac", "-b:a", "192k", "-shortest"]
    elif brief.get("sound"):
        dur = total / brief["fps"]
        cmd += ["-f", "lavfi", "-i",
                "anoisesrc=color=brown:duration=%.3f:amplitude=0.5,lowpass=f=500,"
                "afade=t=in:d=1.5,afade=t=out:st=%.3f:d=1.5,volume=0.5" % (dur, max(0, dur - 1.5)),
                "-c:a", "aac", "-b:a", "128k", "-shortest"]
    cmd += ["-c:v", "copy", "-movflags", "+faststart", mp4]
    subprocess.run(cmd, check=True)
    print("[city-studio] DONE. Video saved: %s" % mp4)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    opts = {}
    paths = []
    for a in argv:
        if a.startswith("--"):
            key, _, val = a[2:].partition("=")
            opts[key] = val or True
        else:
            paths.append(a)

    if "check" in opts:
        ok, status = setup_gpu()
        print("\n[city-studio] Blender %s" % bpy.app.version_string)
        print("[city-studio] GPU check: %s" % ("PASS - " + status if ok else "FAIL - " + status))
        return
    if "probe-eevee" in opts:
        probe_eevee()
        return
    if not paths:
        sys.exit("Usage: ./studio run briefs/test_city.json")

    brief = load_brief(paths[0])
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    total = int(round(brief["duration_seconds"] * brief["fps"]))
    timeline_total, mapping = total, None
    if "sample" in opts:
        # a short video cut from several moments of the full timeline
        segs = brief.get("sample_segments", [[3, 2.5], [62, 2.5], [123, 2.5], [268, 2.5], [345, 2.5], [442, 2.5]])
        mapping = [int(round(a * brief["fps"])) + k for a, length in segs
                   for k in range(int(round(length * brief["fps"])))]
        mapping = [min(m, total - 1) for m in mapping]
        brief["name"] = brief["name"] + "_sample"
        brief["music_build_at"] = 0.5
        brief["music_accents"] = [round(i * 2.5, 2) for i in range(1, len(segs))]
        total = len(mapping)
        # move sound effects onto the sample's shorter timeline
        timeline, offset = [], 0.0
        for a, length in segs:
            for ev in brief.get("sfx", []):
                s0, s1 = max(ev["at"], a), min(ev["at"] + ev["dur"], a + length)
                if s1 - s0 > 0.2:
                    timeline.append(dict(ev, at=round(offset + s0 - a, 3), dur=round(s1 - s0, 3)))
            offset += length
        brief["_sfx_timeline"] = timeline
    out_dir = os.path.join(root, "output", brief["name"])
    if "assemble" in opts:
        assemble(brief, out_dir, total)
        return

    engine = opts.get("engine") or brief["engine"]
    if engine not in ("eevee", "cycles"):
        engine = "cycles"
    index, count = (int(x) for x in str(opts.get("worker", "0/1")).split("/"))
    tag = "[city-studio] worker %d:" % (index + 1)

    random.seed(brief["seed"])
    built = time.time()
    if brief.get("style") in ("historic", "nyc"):
        sys.path.insert(0, HERE)
        if brief["style"] == "nyc":
            import style_nyc as style
        else:
            import style_historic as style
        plan = style.plan(brief)
        rig = style.build(brief, plan)
        update = style.apply_frame
        stats = rig["stats"]
    else:
        plan = plan_city(brief)
        rig = build_scene(brief, plan)
        update = apply_frame
        stats = "%d buildings, %d trees" % (len(plan["buildings"]), len(plan["trees"]))
    scene = rig["scene"]
    status = configure_render(brief, scene, engine)
    if index == 0:
        print("\n[city-studio] %s: %s, %d frames at %dx%d (scene built in %.0fs)" % (
            brief["name"], stats, total, *brief["resolution"], time.time() - built))
        print("[city-studio] Rendering with: %s, %d worker(s)" % (status, count), flush=True)

    def render(f, path):
        info = update(brief, rig, mapping[f] if mapping else f, timeline_total)
        scene.frame_set(f + 1)
        scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        if info is not None:
            with open(path[:-4] + ".json", "w") as fh:
                json.dump(info, fh)

    if "stills" in opts:
        stills_dir = os.path.join(out_dir, "stills")
        os.makedirs(stills_dir, exist_ok=True)
        picks = opts.get("frames")
        frames = [int(x) - 1 for x in str(picks).split(",")] if picks else [0, total // 2, total - 1]
        for f in frames:
            render(f, os.path.join(stills_dir, "frame_%06d.png" % (f + 1)))
        if os.path.exists(os.path.join(stills_dir, "frame_%06d.json" % (frames[0] + 1))):
            for f in frames:
                comp = os.path.join(stills_dir, "comp_%06d.png" % (f + 1))
                if os.path.exists(comp):
                    os.remove(comp)
            run_overlay(stills_dir, [f + 1 for f in frames])
        print("[city-studio] Preview stills saved in %s" % stills_dir)
        return

    frames_dir = os.path.join(out_dir, "frames")
    chunks_dir = os.path.join(out_dir, "chunks")
    os.makedirs(frames_dir, exist_ok=True)
    os.makedirs(chunks_dir, exist_ok=True)
    mine = [c for c in chunk_list(brief, total) if c[0] % count == index]
    todo = [c for c in mine if not os.path.exists(os.path.join(chunks_dir, "chunk_%04d.mp4" % c[0]))]
    left = sum(c[2] for c in todo)
    done, started = 0, time.time()
    for i, start, n in todo:
        for f in range(start, start + n):
            path = os.path.join(frames_dir, "frame_%06d.png" % (f + 1))
            if not (os.path.exists(path) and os.path.getsize(path) > 0):   # resume inside a chunk
                render(f, path)
            done += 1
            if done == 5 or done % 100 == 0:
                per = (time.time() - started) / done
                print("%s %d of %d frames, %.2fs per frame, about %.0f min left" % (
                    tag, done, left, per, per * (left - done) / 60), flush=True)
        encode_chunk(brief, frames_dir, start, n, os.path.join(chunks_dir, "chunk_%04d.mp4" % i))
    if done:
        print("%s finished %d frames in %.1f min (%.2fs per frame)" % (
            tag, done, (time.time() - started) / 60, (time.time() - started) / done), flush=True)
    if index == 0:
        update(brief, rig, total - 1, total)
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out_dir, "scene.blend"))


if __name__ == "__main__":
    main()
