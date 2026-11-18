"""Procedural toon dining-room set for Video 01 (Blender 4.2, Cycles-compatible).

build() creates the room, furniture, props, lights, and cameras.
Look: flat cartoon colours, soft single-bounce shading, thick dark outlines (inverted hull),
Standard view transform so colours stay exactly as picked.
"""
import bpy, math
from mathutils import Vector

PAL = {  # flat palette (linear-ish sRGB values picked by eye)
    "wall": (0.06, 0.12, 0.22), "wall_trim": (0.80, 0.62, 0.25), "floor": (0.32, 0.18, 0.09),
    "table": (0.40, 0.22, 0.10), "cloth": (0.92, 0.90, 0.84), "chair": (0.30, 0.16, 0.07),
    "cushion": (0.55, 0.12, 0.10), "plate": (0.95, 0.95, 0.95), "metal": (0.75, 0.76, 0.78),
    "rice": (0.85, 0.32, 0.08), "chicken": (0.70, 0.40, 0.15), "glass": (0.70, 0.85, 0.90),
    "window": (0.02, 0.05, 0.14), "door": (0.18, 0.28, 0.40), "lamp": (1.0, 0.85, 0.55),
    "candle": (0.95, 0.92, 0.80), "flame": (1.0, 0.7, 0.2), "frame": (0.55, 0.42, 0.20),
    "pot": (0.15, 0.15, 0.17), "accent": (0.71, 1.0, 0.23), "outline": (0.02, 0.02, 0.03),
}

def _mat(name, color, emit=0.0):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    if emit > 0:
        sh = nt.nodes.new("ShaderNodeEmission"); sh.inputs["Color"].default_value = (*color, 1); sh.inputs["Strength"].default_value = emit
    else:
        sh = nt.nodes.new("ShaderNodeBsdfDiffuse"); sh.inputs["Color"].default_value = (*color, 1)
    nt.links.new(sh.outputs[0], out.inputs["Surface"])
    return m

def _outline_mat():
    """Inverted-hull outline: black where we see back faces, transparent elsewhere (works in Cycles & Eevee)."""
    m = bpy.data.materials.get("OUTLINE")
    if m: return m
    m = bpy.data.materials.new("OUTLINE"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); geo = nt.nodes.new("ShaderNodeNewGeometry")
    mix = nt.nodes.new("ShaderNodeMixShader"); tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*PAL["outline"], 1)
    # shell normals are flipped: faces toward camera report Backfacing=1 -> must be invisible
    nt.links.new(geo.outputs["Backfacing"], mix.inputs[0]); nt.links.new(em.outputs[0], mix.inputs[1])
    nt.links.new(tr.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], out.inputs["Surface"])
    m.use_backface_culling = False
    return m

USE_HULL = False  # inverted-hull outlines misbehave in Cycles; Freestyle lines are used instead

def _outline(ob, thick=0.012):
    if not USE_HULL or ob.type != "MESH": return
    ob.data.materials.append(_outline_mat())
    mod = ob.modifiers.new("outline", "SOLIDIFY"); mod.thickness = thick; mod.offset = 1
    mod.use_flip_normals = True; mod.material_offset = len(ob.data.materials) - 1

def box(name, size, loc, mat, outline=True, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    ob = bpy.context.object; ob.name = name; ob.scale = size
    bpy.ops.object.transform_apply(scale=True)
    ob.data.materials.append(_mat(mat, PAL[mat]))
    bev = ob.modifiers.new("bevel", "BEVEL"); bev.width = min(0.01, min(size) * 0.2); bev.segments = 2
    if outline: _outline(ob)
    return ob

def cyl(name, r, h, loc, mat, outline=True, verts=32, emit=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc)
    ob = bpy.context.object; ob.name = name
    ob.data.materials.append(_mat(mat + ("_emit" if emit else ""), PAL[mat], emit))
    bpy.ops.object.shade_smooth()
    if outline: _outline(ob, 0.006)
    return ob

def chair(name, loc, facing):
    """Simple dining chair; facing = yaw in degrees (direction the sitter faces)."""
    g = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(g)
    g.location = loc; g.rotation_euler.z = math.radians(facing)
    parts = [box(f"{name}_seat", (0.45, 0.45, 0.05), (0, 0, 0.46), "chair"),
             box(f"{name}_cush", (0.40, 0.40, 0.05), (0, 0, 0.51), "cushion"),
             box(f"{name}_back", (0.45, 0.05, 0.55), (0, 0.22, 0.76), "chair")]
    for dx in (-0.2, 0.2):
        for dy in (-0.2, 0.2): parts.append(box(f"{name}_leg", (0.04, 0.04, 0.46), (dx, dy, 0.23), "chair"))
    for p in parts: p.parent = g
    return g

def place_setting(name, loc, yaw, food=True):
    g = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(g)
    g.location = loc; g.rotation_euler.z = math.radians(yaw)
    p = [cyl(f"{name}_plate", 0.13, 0.015, (0, 0, 0), "plate"),
         box(f"{name}_fork", (0.015, 0.17, 0.006), (-0.17, 0, 0.0), "metal", outline=False),
         box(f"{name}_knife", (0.015, 0.19, 0.006), (0.17, 0, 0.0), "metal", outline=False),
         cyl(f"{name}_glass", 0.035, 0.12, (0.17, -0.18, 0.06), "glass")]
    if food:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, location=(0.02, 0.01, 0.02)); r = bpy.context.object
        r.name = f"{name}_rice"; r.scale = (1, 1, 0.35); r.data.materials.append(_mat("rice", PAL["rice"])); _outline(r, 0.004)
        p.append(r)
    for o in p: o.parent = g
    return g

def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.samples = 24; sc.cycles.use_denoising = True
    sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "None"
    sc.render.fps = 24; sc.render.resolution_x = 1920; sc.render.resolution_y = 1080
    sc.cycles.max_bounces = 3; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 0; sc.cycles.transparent_max_bounces = 8
    # cartoon outlines: Freestyle (works in Cycles on CPU and GPU)
    sc.render.use_freestyle = True; sc.render.line_thickness_mode = "RELATIVE"
    vl = sc.view_layers[0]; vl.use_freestyle = True
    ls = vl.freestyle_settings.linesets[0] if vl.freestyle_settings.linesets else vl.freestyle_settings.linesets.new("lines")
    ls.select_silhouette = ls.select_border = ls.select_crease = True
    if ls.linestyle is None: ls.linestyle = bpy.data.linestyles.new("ink")
    ls.linestyle.color = PAL["outline"]; ls.linestyle.thickness = 2.6
    vl.freestyle_settings.crease_angle = 2.4
    w = bpy.data.worlds.new("World"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.07, 0.12, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.6

    # room 6 x 5 x 2.8, table at origin, long axis = X
    box("floor", (6, 5, 0.1), (0, 0, -0.05), "floor", outline=False)
    box("wall_back", (6, 0.1, 2.8), (0, 2.5, 1.4), "wall", outline=False)
    box("wall_left", (0.1, 5, 2.8), (-3, 0, 1.4), "wall", outline=False)
    box("wall_right", (0.1, 5, 2.8), (3, 0, 1.4), "wall", outline=False)
    box("wall_front", (6, 0.1, 2.8), (0, -2.5, 1.4), "wall", outline=False)
    box("ceiling", (6, 5, 0.1), (0, 0, 2.85), "wall", outline=False)
    box("trim_back", (6, 0.12, 0.08), (0, 2.44, 0.9), "wall_trim", outline=False)
    box("trim_left", (0.12, 5, 0.08), (-2.94, 0, 0.9), "wall_trim", outline=False)
    box("window", (1.4, 0.05, 1.1), (0.9, 2.45, 1.6), "window")
    box("window_bar", (0.05, 0.06, 1.1), (0.9, 2.42, 1.6), "frame")
    box("door_hall", (0.05, 0.95, 2.1), (2.94, -1.2, 1.05), "door")
    box("frame_photo", (0.6, 0.04, 0.45), (-1.3, 2.44, 1.7), "frame")
    cyl("wall_clock", 0.22, 0.05, (-2.94, 0.8, 2.0), "plate").rotation_euler = (0, math.radians(90), 0)

    # table + cloth
    box("table_top", (2.4, 1.1, 0.06), (0, 0, 0.75), "table")
    for dx in (-1.1, 1.1):
        for dy in (-0.45, 0.45): box("table_leg", (0.07, 0.07, 0.72), (dx, dy, 0.37), "table")
    box("cloth", (2.5, 1.2, 0.012), (0, 0, 0.785), "cloth", outline=False)

    # seats: you (front, -Y facing +Y), sister (front right), dad (back left), mom (back right), EMPTY at the end (+X)
    seats = {"chair_you": ((-0.45, -0.85, 0), 0), "chair_sis": ((0.45, -0.85, 0), 0),
             "chair_dad": ((-0.45, 0.85, 0), 180), "chair_mom": ((0.45, 0.85, 0), 180),
             "chair_empty": ((1.62, 0, 0), 90)}
    for n, (loc, yaw) in seats.items(): chair(n, loc, yaw)
    settings = {"set_you": ((-0.45, -0.35, 0.80), 0), "set_sis": ((0.45, -0.35, 0.80), 0),
                "set_dad": ((-0.45, 0.35, 0.80), 180), "set_mom": ((0.45, 0.35, 0.80), 180),
                "set_empty": ((1.0, 0, 0.80), 90)}
    for n, (loc, yaw) in settings.items(): place_setting(n, loc, yaw, food=(n != "set_empty"))

    cyl("rice_pot", 0.16, 0.16, (0, 0, 0.87), "pot")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(0, 0, 0.95)); rp = bpy.context.object
    rp.name = "rice_pot_food"; rp.scale = (1, 1, 0.3); rp.data.materials.append(_mat("rice", PAL["rice"]))
    for i, x in enumerate((-0.75, 0.75)):
        cyl(f"candle_{i}", 0.025, 0.22, (x, 0, 0.90), "candle")
        cyl(f"flame_{i}", 0.012, 0.04, (x, 0, 1.03), "flame", outline=False, emit=6)
    # lights
    lamp = cyl("ceiling_lamp", 0.25, 0.12, (0, 0, 2.55), "lamp", emit=4)
    bpy.ops.object.light_add(type="AREA", location=(0, 0, 2.2)); key = bpy.context.object
    key.name = "L_key"; key.data.size = 1.6; key.data.energy = 380
    bpy.ops.object.light_add(type="POINT", location=(0, 0, 1.15)); cl = bpy.context.object
    cl.name = "L_candles"; cl.data.energy = 25; cl.data.shadow_soft_size = 0.3
    bpy.ops.object.light_add(type="AREA", location=(0.9, 2.2, 1.6), rotation=(math.radians(90), 0, 0)); win = bpy.context.object
    win.name = "L_window"; win.data.size = 1.2; win.data.energy = 30
    mood("warm")
    return sc

MOODS = {  # key colour/energy, candle, window, world
    "warm":   dict(key=((1.0, 0.82, 0.6), 75), cand=((1.0, 0.6, 0.25), 8), win=((0.3, 0.45, 1.0), 12), world=0.45),
    "frozen": dict(key=((0.62, 0.85, 0.45), 55), cand=((0.7, 1.0, 0.3), 5), win=((0.3, 0.6, 0.6), 8), world=0.28),
    "dark":   dict(key=((0.5, 0.6, 0.55), 10), cand=((1.0, 0.55, 0.2), 12), win=((0.25, 0.35, 0.8), 6), world=0.10),
}
def mood(name, frame=None):
    m = MOODS[name]; o = bpy.data.objects
    for ob, (col, en) in (("L_key", m["key"]), ("L_candles", m["cand"]), ("L_window", m["win"])):
        o[ob].data.color = col; o[ob].data.energy = en
        if frame is not None:
            o[ob].data.keyframe_insert("color", frame=frame); o[ob].data.keyframe_insert("energy", frame=frame)
    bg = bpy.context.scene.world.node_tree.nodes["Background"].inputs[1]; bg.default_value = m["world"]
    if frame is not None: bg.keyframe_insert("default_value", frame=frame)

# Camera presets: (location, look-at point, focal length mm)
CAMS = {
    "WIDE_TABLE_POV":   ((-0.45, -1.75, 1.15), (0.3, 0.6, 0.95), 24),
    "WIDE_TABLE":       ((-2.6, -2.1, 1.9), (0.2, 0.2, 0.8), 22),
    "INT_DINING_WIDE":  ((2.7, -2.3, 1.7), (-0.3, 0.3, 0.8), 20),
    "INS_EMPTY_CHAIR":  ((0.55, -1.05, 1.15), (1.62, 0, 0.6), 30),
    "INS_FORK_HAND":    ((-0.55, -0.75, 1.05), (-0.6, -0.35, 0.8), 60),
    "INS_RICE_POT":     ((-0.35, -0.45, 1.15), (0, 0, 0.92), 55),
    "UNDER_TABLE":      ((0.0, -1.6, 0.25), (0.0, 0.0, 0.3), 18),
    "MCU_MOM_SPOON":    ((0.3, -0.6, 1.2), (0.45, 0.85, 1.1), 45),
    "ECU_SPOON":        ((0.35, 0.35, 1.05), (0.45, 0.55, 0.98), 100),
    "INS_GRAIN_LANDS":  ((0.4, 0.15, 0.9), (0.45, 0.4, 0.79), 100),
    "CU_DAD":           ((-0.4, -0.2, 1.25), (-0.45, 0.85, 1.15), 55),
    "WIDE_TABLE_DARK":  ((-2.4, 1.9, 1.7), (0.6, -0.1, 0.8), 24),
    "INS_CUSHION":      ((1.0, -0.6, 0.95), (1.62, 0, 0.5), 60),
    "TOP_TABLE":        ((0.0, -0.45, 2.15), (0.0, 0.0, 0.8), 22),
}
def add_cameras():
    cams = {}
    for n, (loc, tgt, f) in CAMS.items():
        cd = bpy.data.cameras.new(n); cd.lens = f; cd.clip_start = 0.02
        ob = bpy.data.objects.new(n, cd); bpy.context.collection.objects.link(ob); ob.location = loc
        d = Vector(tgt) - Vector(loc); ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        cams[n] = ob
    return cams

if __name__ == "__main__":
    build(); add_cameras()
