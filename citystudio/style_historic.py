"""Realistic historical style ("style": "historic" in a brief).

Builds a coastal landscape (sea, forest, marsh, spreading farmland) and a town
that grows street by street, plus landmarks, a palisade, wharves and ships.
For every frame it also returns the information the overlay step draws on
top: year, era, ruler, population, captions and floating place labels.

The test brief uses an invented city. Real cities will feed real coastlines,
streets, footprints and dates into the same building blocks.
"""
import math
import random

import bpy
import bmesh  # noqa: E402 (must come after bpy)
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from mathutils import noise as mnoise

HAZE = (0.80, 0.76, 0.69)
FORT = Vector((0.0, -560.0))
TOWN_START = 1624.0
TOWN_SPAN = 166.0          # years for the town to reach its full 1790 extent
TOWN_REACH = 2000.0        # metres from the fort reached by then

WALLS = [(0.62, 0.58, 0.50), (0.42, 0.17, 0.11), (0.36, 0.22, 0.15), (0.58, 0.47, 0.30),
         (0.47, 0.44, 0.40), (0.50, 0.26, 0.16)]
ROOFS = [(0.42, 0.12, 0.07), (0.35, 0.11, 0.07), (0.22, 0.14, 0.10), (0.19, 0.19, 0.21),
         (0.30, 0.17, 0.10), (0.48, 0.18, 0.09)]
EARTH = (0.31, 0.27, 0.21)
STREET = (0.40, 0.36, 0.29)
STONE = (0.46, 0.43, 0.37)
WOOD = (0.14, 0.09, 0.06)
SAIL = (0.78, 0.75, 0.68)


# ----------------------------------------------------------------------------
# Landscape functions (plain maths, no Blender objects)
# ----------------------------------------------------------------------------
class Land:
    def __init__(self, seed):
        self.off = Vector((seed * 13.17, seed * 7.71, seed * 3.3))

    def n(self, x, y, s):
        return mnoise.noise(Vector((x / s, y / s, 0.0)) + self.off)

    def parts(self, x, y):
        """Positive = land, negative = water (roughly metres from the shore)."""
        xc = 70 * math.sin(y / 520.0)
        w = 300 + 0.10 * (y + 700)
        if y < -480:                                                # rounded southern tip
            w *= math.sqrt(max(0.0, 1 - ((-480 - y) / 260.0) ** 2))
        pen = w - abs(x - xc) if y > -740 else (y + 740) - abs(x - xc)    # the peninsula
        north = y - (2300 + 200 * math.sin(x / 700.0))              # mainland far north
        west = min((-1000 - 0.30 * y + 90 * math.sin(y / 380.0)) - x, y + 950 + 0.4 * (x + 1200))
        east = min(x - (850 + 0.20 * y + 120 * math.sin(y / 460.0)), y + 600)
        island = 170 - math.hypot(x + 430, y + 1230)
        wob = 130 * self.n(x, y, 520) + 50 * self.n(x, y, 170) + 14 * self.n(x, y, 45)
        return max(pen, north, west, east, island) + wob, pen + wob

    def value(self, x, y):
        return self.parts(x, y)[0]

    def height(self, x, y, v=None):
        if v is None:
            v = self.value(x, y)
        if v > 0:
            t = min(v / 140.0, 1.0)
            hills = max(0.0, self.n(x, y, 650)) * 30 * t
            return 0.6 + 2.4 * t + hills
        return -3.0 - 9.0 * min(-v / 160.0, 1.0)

    def settle(self, x, y, pen=None):
        """How far (in metres of 'settlement effort') a point is from the fort."""
        if pen is None:
            pen = self.parts(x, y)[1]
        d = (Vector((x, y)) - FORT).length * (1 + 0.18 * self.n(x, y, 300))
        return d + (0 if pen > 0 else 700)

    def forest(self, x, y):
        return 0.5 + 0.5 * self.n(x + 900, y - 400, 260)

    def shore_x(self, y, side):
        """x of the peninsula shore at height y, walking out from its spine."""
        x = 70 * math.sin(y / 520.0)
        for _ in range(400):
            x += 4 * side
            if self.parts(x, y)[1] < 0:
                return x
        return x


def town_front(year):
    if year < TOWN_START:
        return 0.0
    return 60 + TOWN_REACH * ((year - TOWN_START) / TOWN_SPAN) ** 1.25


def field_front(year):
    if year < TOWN_START:
        return 0.0
    return town_front(year) + 350 + 700 * min(1.0, (year - TOWN_START) / 40)


def year_for_distance(d):
    d = max(0.0, d - 60)
    return TOWN_START + 1 + TOWN_SPAN * (d / TOWN_REACH) ** 0.8


# ----------------------------------------------------------------------------
# Plan: decide every street, building and tree
# ----------------------------------------------------------------------------
class Grid:
    """Occupancy grid so buildings never overlap."""
    def __init__(self, cell=4.0):
        self.cell = cell
        self.used = set()

    def cells(self, cx, cy, ux, uy, hx, hy):
        out = []
        steps_x = max(1, int(hx * 2 / self.cell) + 1)
        steps_y = max(1, int(hy * 2 / self.cell) + 1)
        for i in range(steps_x + 1):
            for j in range(steps_y + 1):
                a = -hx + 2 * hx * i / steps_x
                b = -hy + 2 * hy * j / steps_y
                px = cx + ux[0] * a + uy[0] * b
                py = cy + ux[1] * a + uy[1] * b
                out.append((int(math.floor(px / self.cell)), int(math.floor(py / self.cell))))
        return out

    def free(self, cells):
        return not any(c in self.used for c in cells)

    def take(self, cells):
        self.used.update(cells)


def polyline(points, step):
    """Resample a polyline into segments of about `step` metres."""
    out = []
    for a, b in zip(points, points[1:]):
        a, b = Vector(a), Vector(b)
        n = max(1, int((b - a).length / step))
        for k in range(n):
            out.append((a.lerp(b, k / n), a.lerp(b, (k + 1) / n)))
    return out


def plan(brief):
    rng = random.Random(brief["seed"])
    land = Land(brief["seed"])
    grid = Grid()

    # --- streets -----------------------------------------------------------
    lines = []
    ys = [-470 + 68 * k for k in range(40) if -470 + 68 * k < 1900]
    # streets following the length of the peninsula
    for u in (-0.70, -0.35, 0.0, 0.35, 0.70):
        pts = []
        for y in range(-380, 1900, 40):
            xw, xe = land.shore_x(y, -1), land.shore_x(y, 1)
            half = (xe - xw) / 2 - 55
            if half < 40:
                continue
            pts.append(((xw + xe) / 2 + u * half, y))
        if len(pts) > 2:
            lines.append(pts)
    # cross streets
    for y in ys:
        if y < -380:
            continue
        xw, xe = land.shore_x(y, -1) + 50, land.shore_x(y, 1) - 50
        if xe - xw > 80:
            tilt = 0.08 * math.sin(y / 300.0)
            lines.append([(xw, y - tilt * (xw - 0)), (xe, y + tilt * xe)])
    # old crooked lanes near the fort
    for ang in (-62, -25, 12, 48, 80, 112):
        a = math.radians(ang)
        pts = []
        for r in range(70, 330, 30):
            bend = 0.25 * math.sin(r / 60.0 + ang)
            pts.append((FORT.x + r * math.cos(a + bend), FORT.y + r * math.sin(a + bend)))
        lines.append(pts)
    # shore streets near the tip
    for side in (-1, 1):
        pts = []
        for y in range(-520, -360, 20):
            pts.append((land.shore_x(y, side) - side * 40, y))
        lines.append(pts)

    market = Vector((land.shore_x(-120, 1) * 0.35, -120.0))
    church = Vector((land.shore_x(-20, -1) * 0.3, -20.0))
    for spot, r in ((market, 26), (church, 30), (FORT, 70)):
        for i in range(-r, r + 1, 4):
            for j in range(-r, r + 1, 4):
                grid.take([(int(math.floor((spot.x + i) / 4)), int(math.floor((spot.y + j) / 4)))])

    streets, houses = [], []
    for line in lines:
        for a, b in polyline(line, 34):
            mid = (a + b) / 2
            if land.value(mid.x, mid.y) < 25:
                continue
            d = (mid - FORT).length
            if d < 72:
                continue
            year = year_for_distance(d) + rng.uniform(-3, 3)
            streets.append({"a": a, "b": b, "year": year})
            along = (b - a).normalized()
            normal = Vector((-along.y, along.x))
            seg_len = (b - a).length
            for side in (-1, 1):
                for row in range(3):
                    t = rng.uniform(0, 4)
                    while t < seg_len - 4:
                        w = rng.uniform(7, 10.5)
                        dep = rng.uniform(9, 14)
                        off = 5.5 + dep / 2 + row * (dep + 2.5)
                        p = a + along * (t + w / 2) + normal * side * off
                        t += w + rng.uniform(0.3, 3.5)
                        if row and rng.random() < 0.35:
                            continue
                        v = land.value(p.x, p.y)
                        if v < 22:
                            continue
                        cells = grid.cells(p.x, p.y, normal * side, along, dep / 2, w / 2)
                        if not grid.free(cells):
                            continue
                        grid.take(cells)
                        houses.append({
                            "x": p.x, "y": p.y, "ux": tuple(normal * side), "uy": tuple(along),
                            "d": dep, "w": w, "h": rng.uniform(8.5, 13.5) + (1.5 if row == 0 else 0),
                            "year": year + rng.uniform(1, 9) + row * rng.uniform(6, 22),
                            "wall": rng.choice(WALLS), "roof": rng.choice(ROOFS)})

    # --- trees ---------------------------------------------------------------
    trees = []
    step = 15.0
    y = -1500.0
    while y < 2900:
        x = -1900.0
        while x < 1900:
            px, py = x + rng.uniform(-6, 6), y + rng.uniform(-6, 6)
            v, pen = land.parts(px, py)
            if v > 10:
                f = land.forest(px, py)
                dense = f > 0.45
                if dense or rng.random() < 0.06:
                    s = land.settle(px, py, pen)
                    near_fort = (Vector((px, py)) - FORT).length < 90
                    if not near_fort:
                        trees.append({"x": px, "y": py, "z": land.height(px, py, v), "settle": s,
                                      "r": rng.uniform(4.0, 7.5) * (1.0 if dense else 1.2),
                                      "g": rng.uniform(0.75, 1.2)})
            x += step
        y += step

    # --- wharves and landmarks -------------------------------------------------
    wharves = []
    for k, y in enumerate(range(-470, 260, 46)):
        xe = land.shore_x(y, 1)
        wharves.append({"x0": xe - 12, "y": y, "len": rng.uniform(45, 70),
                        "year": 1698 + k * 4 + rng.uniform(0, 3)})

    windmill = Vector((land.shore_x(-470, -1) + 45, -470.0))
    pal_y = -255.0
    palisade = (land.shore_x(pal_y, -1) + 20, land.shore_x(pal_y, 1) - 20, pal_y)
    return {"land": land, "streets": streets, "houses": houses, "trees": trees,
            "wharves": wharves, "market": market, "church": church, "windmill": windmill,
            "palisade": palisade}


# ----------------------------------------------------------------------------
# Small mesh helpers
# ----------------------------------------------------------------------------
class Parts:
    """Collects many small shapes into one mesh with a colour per face."""
    def __init__(self):
        self.verts, self.faces, self.cols = [], [], []

    def add(self, verts, faces, cols):
        base = len(self.verts)
        self.verts.extend(verts)
        for f, c in zip(faces, cols):
            self.faces.append(tuple(base + i for i in f))
            self.cols.append(c)

    def box(self, cx, cy, z0, ux, uy, hx, hy, h, col, top=None):
        p = []
        for zz in (z0, z0 + h):
            for a, b in ((-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)):
                p.append((cx + ux[0] * a + uy[0] * b, cy + ux[1] * a + uy[1] * b, zz))
        f = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7)]
        self.add(p, f, [col] * 4 + [top or col])

    def quad(self, pts, z, col):
        self.add([(x, y, z) for x, y in pts], [(0, 1, 2, 3)], [col])

    def house(self, hs, z0):
        ux, uy = hs["ux"], hs["uy"]
        hx, hy, h = hs["d"] / 2, hs["w"] / 2, hs["h"]
        wz = z0 + h * 0.6
        rz = z0 + h
        x, y = hs["x"], hs["y"]

        def P(a, b, zz):
            return (x + ux[0] * a + uy[0] * b, y + ux[1] * a + uy[1] * b, zz)
        v = [P(-hx, -hy, z0), P(hx, -hy, z0), P(hx, hy, z0), P(-hx, hy, z0),
             P(-hx, -hy, wz), P(hx, -hy, wz), P(hx, hy, wz), P(-hx, hy, wz),
             P(-hx, 0, rz), P(hx, 0, rz)]
        f = [(0, 1, 5, 4), (2, 3, 7, 6), (1, 2, 6, 5), (3, 0, 4, 7),
             (5, 6, 9), (7, 4, 8), (4, 5, 9, 8), (6, 7, 8, 9)]
        w, r = hs["wall"], hs["roof"]
        self.add(v, f, [w, w, w, w, w, w, r, r])
        # yard / lot surface
        k = 1.35
        self.quad([P(-hx * k, -hy * 1.1, 0)[:2], P(hx * k, -hy * 1.1, 0)[:2],
                   P(hx * k, hy * 1.1, 0)[:2], P(-hx * k, hy * 1.1, 0)[:2]], z0 + 0.12, EARTH)

    def to_object(self, name, mat, collection):
        me = bpy.data.meshes.new(name)
        me.from_pydata(self.verts, [], self.faces)
        attr = me.color_attributes.new("col", "FLOAT_COLOR", "CORNER")
        data = []
        for poly, c in zip(me.polygons, self.cols):
            data.extend([c[0], c[1], c[2], 1.0] * poly.loop_total)
        attr.data.foreach_set("color", data)
        me.materials.append(mat)
        ob = bpy.data.objects.new(name, me)
        collection.objects.link(ob)
        return ob


ICO = None


def ico_template():
    global ICO
    if ICO is None:
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
        ICO = ([tuple(v.co) for v in bm.verts], [tuple(v.index for v in f.verts) for f in bm.faces])
        bm.free()
    return ICO


# ----------------------------------------------------------------------------
# Materials
# ----------------------------------------------------------------------------
def nodes(mat):
    mat.use_nodes = True
    return mat.node_tree


def add_haze(mat, distance=11000.0, amount=0.8):
    """Fade a material towards the haze colour with distance from the camera
    (aerial perspective). Cheap, and works in both Cycles and EEVEE."""
    nt = mat.node_tree
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    src = out.inputs["Surface"].links[0].from_socket
    cam = nt.nodes.new("ShaderNodeCameraData")
    div = nt.nodes.new("ShaderNodeMath")
    div.operation = "DIVIDE"
    nt.links.new(cam.outputs["View Distance"], div.inputs[0])
    div.inputs[1].default_value = -distance
    ex = nt.nodes.new("ShaderNodeMath")
    ex.operation = "EXPONENT"
    nt.links.new(div.outputs[0], ex.inputs[0])
    fac = nt.nodes.new("ShaderNodeMapRange")
    nt.links.new(ex.outputs[0], fac.inputs["Value"])
    fac.inputs["From Min"].default_value = 0.0
    fac.inputs["From Max"].default_value = 1.0
    fac.inputs["To Min"].default_value = amount
    fac.inputs["To Max"].default_value = 0.0
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*HAZE, 1)
    em.inputs["Strength"].default_value = 1.0
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(fac.outputs[0], mix.inputs[0])
    nt.links.new(src, mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return mat


def principled(nt):
    return next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")


def mix_rgb(nt, fac, a, b):
    m = nt.nodes.new("ShaderNodeMix")
    m.data_type = "RGBA"
    for sock, val in ((m.inputs[0], fac), (m.inputs[6], a), (m.inputs[7], b)):
        if isinstance(val, (tuple, list)):
            sock.default_value = (*val[:3], 1) if len(val) == 3 else val
        elif isinstance(val, (int, float)):
            sock.default_value = val
        else:
            nt.links.new(val, sock)
    return m.outputs[2]


def math_node(nt, op, a, b=None, clamp=False):
    m = nt.nodes.new("ShaderNodeMath")
    m.operation = op
    m.use_clamp = clamp
    for i, val in enumerate((a, b)):
        if val is None:
            continue
        if isinstance(val, (int, float)):
            m.inputs[i].default_value = val
        else:
            nt.links.new(val, m.inputs[i])
    return m.outputs[0]


def smooth(nt, val, lo, hi):
    m = nt.nodes.new("ShaderNodeMapRange")
    m.interpolation_type = "SMOOTHSTEP"
    nt.links.new(val, m.inputs["Value"])
    m.inputs["From Min"].default_value = lo
    m.inputs["From Max"].default_value = hi
    return m.outputs[0]


def painted_material():
    mat = bpy.data.materials.new("Painted")
    nt = nodes(mat)
    bsdf = principled(nt)
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "col"
    nt.links.new(attr.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.85
    return add_haze(mat)


def water_material():
    mat = bpy.data.materials.new("Water")
    nt = nodes(mat)
    bsdf = principled(nt)
    bsdf.inputs["Base Color"].default_value = (0.028, 0.058, 0.078, 1)
    bsdf.inputs["Roughness"].default_value = 0.10
    for name in ("Specular IOR Level", "Specular"):
        if name in bsdf.inputs:
            bsdf.inputs[name].default_value = 0.35
            break
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    scale = nt.nodes.new("ShaderNodeVectorMath")
    scale.operation = "MULTIPLY"
    nt.links.new(geo.outputs["Position"], scale.inputs[0])
    scale.inputs[1].default_value = (0.03, 0.06, 0.03)
    tex = nt.nodes.new("ShaderNodeTexNoise")
    tex.inputs["Detail"].default_value = 6
    nt.links.new(scale.outputs[0], tex.inputs["Vector"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.18
    nt.links.new(tex.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs[0], bsdf.inputs["Normal"])
    return add_haze(mat, distance=12000, amount=0.75)


def terrain_material():
    """Colour comes from three numbers stored on the terrain: how far inland
    a point is, how late it gets settled, and whether it is forest. A single
    'frontier' value, changed every frame, turns wild land into farmland."""
    mat = bpy.data.materials.new("Terrain")
    nt = nodes(mat)
    bsdf = principled(nt)
    bsdf.inputs["Roughness"].default_value = 0.95
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "mask"
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(attr.outputs["Color"], sep.inputs[0])
    inland, settle, forest = sep.outputs[0], sep.outputs[1], sep.outputs[2]

    geo = nt.nodes.new("ShaderNodeNewGeometry")
    pos = geo.outputs["Position"]

    def tex_noise(scale, detail=4):
        t = nt.nodes.new("ShaderNodeTexNoise")
        t.inputs["Scale"].default_value = scale
        t.inputs["Detail"].default_value = detail
        nt.links.new(pos, t.inputs["Vector"])
        return t.outputs["Fac"]

    # wild land: meadow, marsh and forest canopy
    canopy = nt.nodes.new("ShaderNodeTexVoronoi")
    canopy.inputs["Scale"].default_value = 0.09
    nt.links.new(pos, canopy.inputs["Vector"])
    clump = smooth(nt, canopy.outputs["Distance"], 0.15, 0.75)
    forest_col = mix_rgb(nt, clump, (0.050, 0.085, 0.034), (0.022, 0.040, 0.018))
    meadow = mix_rgb(nt, tex_noise(0.012), (0.20, 0.22, 0.07), (0.13, 0.17, 0.05))
    wild = mix_rgb(nt, smooth(nt, forest, 0.40, 0.52), meadow, forest_col)

    # farmland: rectangular field cells in a small palette
    stretch = nt.nodes.new("ShaderNodeVectorMath")
    stretch.operation = "MULTIPLY"
    nt.links.new(pos, stretch.inputs[0])
    stretch.inputs[1].default_value = (1.0, 0.45, 1.0)
    cells = nt.nodes.new("ShaderNodeTexVoronoi")
    cells.distance = "CHEBYCHEV"
    cells.inputs["Scale"].default_value = 0.022
    nt.links.new(stretch.outputs[0], cells.inputs["Vector"])
    pick = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(cells.outputs["Color"], pick.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    palette = [(0.0, (0.20, 0.26, 0.07)), (0.18, (0.36, 0.31, 0.12)), (0.36, (0.13, 0.20, 0.05)),
               (0.52, (0.30, 0.20, 0.10)), (0.70, (0.42, 0.35, 0.14)), (0.86, (0.17, 0.24, 0.06))]
    els = ramp.color_ramp.elements
    els[0].position, els[0].color = palette[0][0], (*palette[0][1], 1)
    els[1].position, els[1].color = palette[1][0], (*palette[1][1], 1)
    for p, c in palette[2:]:
        e = els.new(p)
        e.color = (*c, 1)
    nt.links.new(pick.outputs[0], ramp.inputs["Fac"])
    furrow = mix_rgb(nt, math_node(nt, "MULTIPLY", tex_noise(0.6, 2), 0.25),
                     ramp.outputs["Color"], (0.20, 0.18, 0.11))

    frontier = nt.nodes.new("ShaderNodeValue")
    frontier.name = "frontier"
    frontier.outputs[0].default_value = 0.0
    edge = math_node(nt, "SUBTRACT", frontier.outputs[0], settle)
    farmed = smooth(nt, edge, 0.0, 0.015)
    in_use = smooth(nt, pick.outputs[1], 0.08, 0.12)        # leave a few cells wild
    farmed = math_node(nt, "MULTIPLY", farmed, in_use)
    land_col = mix_rgb(nt, farmed, wild, furrow)

    # shore, beach and sea floor
    beach = smooth(nt, inland, 0.505, 0.53)
    shore = mix_rgb(nt, beach, (0.33, 0.30, 0.22), land_col)
    under = smooth(nt, inland, 0.49, 0.50)
    final = mix_rgb(nt, under, (0.05, 0.07, 0.07), shore)
    nt.links.new(final, bsdf.inputs["Base Color"])

    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.35
    bump.inputs["Distance"].default_value = 2.0
    nt.links.new(math_node(nt, "MULTIPLY", clump, smooth(nt, forest, 0.40, 0.52)), bump.inputs["Height"])
    nt.links.new(bump.outputs[0], bsdf.inputs["Normal"])
    add_haze(mat)
    return mat, frontier


# ----------------------------------------------------------------------------
# Build the Blender scene
# ----------------------------------------------------------------------------
def build(brief, p):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    col = scene.collection
    land = p["land"]
    painted = painted_material()

    # terrain grid
    n, size, cy0 = 230, 7600.0, 800.0
    verts, mask = [], []
    for j in range(n + 1):
        for i in range(n + 1):
            x = -size / 2 + size * i / n
            y = cy0 - size / 2 + size * j / n
            v, pen = land.parts(x, y)
            verts.append((x, y, land.height(x, y, v)))
            mask.append((max(0.0, min(1.0, 0.5 + v / 300.0)),
                         land.settle(x, y, pen) / 6000.0, land.forest(x, y), 1.0))
    faces = [(j * (n + 1) + i, j * (n + 1) + i + 1, (j + 1) * (n + 1) + i + 1, (j + 1) * (n + 1) + i)
             for j in range(n) for i in range(n)]
    me = bpy.data.meshes.new("Terrain")
    me.from_pydata(verts, [], faces)
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    attr = me.color_attributes.new("mask", "FLOAT_COLOR", "POINT")
    attr.data.foreach_set("color", [c for m in mask for c in m])
    tmat, frontier = terrain_material()
    me.materials.append(tmat)
    col.objects.link(bpy.data.objects.new("Terrain", me))

    sea = bpy.data.meshes.new("Sea")
    s = 30000
    sea.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
    sea.materials.append(water_material())
    col.objects.link(bpy.data.objects.new("Sea", sea))

    def ground(x, y):
        return land.height(x, y)

    # streets and houses, grouped into one object per year so thousands of
    # buildings stay fast to render
    bins = {}
    for st in p["streets"]:
        a, b = st["a"], st["b"]
        along = (b - a).normalized()
        nrm = Vector((-along.y, along.x)) * 4.5
        z = max(ground(a.x, a.y), ground(b.x, b.y), 0.8) + 0.2
        key = ("street", int(st["year"]))
        bins.setdefault(key, Parts()).quad(
            [tuple(a - nrm), tuple(b - nrm + along * 1.5), tuple(b + nrm + along * 1.5), tuple(a + nrm)],
            z, STREET)
    for hs in p["houses"]:
        key = ("house", int(hs["year"]))
        bins.setdefault(key, Parts()).house(hs, ground(hs["x"], hs["y"]))

    animated = []
    for (kind, year), parts in sorted(bins.items()):
        ob = parts.to_object("%s_%d" % (kind, year), painted, col)
        animated.append({"ob": ob, "year": year, "grow": 4.0 if kind == "house" else 0.0})

    # trees, grouped by when the settlers reach them
    ico_v, ico_f = ico_template()
    tree_bins = {}
    for t in p["trees"]:
        key = int(t["settle"] / 30.0)
        g = t["g"]
        colr = (0.045 * g, 0.075 * g, 0.030 * g)
        r = t["r"]
        vv = [(t["x"] + vx * r, t["y"] + vy * r, t["z"] + r * 0.9 + vz * r * 0.8) for vx, vy, vz in ico_v]
        tree_bins.setdefault(key, Parts()).add(vv, ico_f, [colr] * len(ico_f))
    trees = []
    for key, parts in tree_bins.items():
        ob = parts.to_object("trees_%d" % key, painted, col)
        trees.append({"ob": ob, "settle": key * 30.0 + 30.0})

    # fort
    fort = Parts()
    fz = ground(FORT.x, FORT.y)
    outer = []
    for k in range(4):
        a = math.radians(45 + 90 * k)
        for da, rr in ((-20, 44), (0, 66), (20, 44)):
            outer.append((FORT.x + rr * math.cos(a + math.radians(da)), FORT.y + rr * math.sin(a + math.radians(da))))
    inner = [(FORT.x + (x - FORT.x) * 0.8, FORT.y + (y - FORT.y) * 0.8) for x, y in outer]
    m = len(outer)
    v = [(x, y, fz) for x, y in outer] + [(x, y, fz + 6) for x, y in outer] + \
        [(x, y, fz + 6) for x, y in inner] + [(x, y, fz + 0.5) for x, y in inner]
    f, c = [], []
    for i in range(m):
        j = (i + 1) % m
        f += [(i, j, m + j, m + i), (m + i, m + j, 2 * m + j, 2 * m + i), (2 * m + i, 2 * m + j, 3 * m + j, 3 * m + i)]
        c += [STONE, (0.30, 0.33, 0.17), STONE]
    f.append(tuple(range(3 * m, 4 * m)))
    c.append(EARTH)
    fort.add(v, f, c)
    for dx, dy, w, d in ((-14, 10, 20, 9), (14, 10, 20, 9), (0, -16, 26, 10)):
        fort.house({"x": FORT.x + dx, "y": FORT.y + dy, "ux": (0, 1), "uy": (1, 0), "d": d, "w": w, "h": 10,
                    "wall": (0.55, 0.50, 0.42), "roof": (0.35, 0.11, 0.07)}, fz + 0.5)
    fort.box(FORT.x, FORT.y + 2, fz, (1, 0), (0, 1), 0.4, 0.4, 26, WOOD)
    fort.box(FORT.x + 3.5, FORT.y + 2, fz + 21, (1, 0), (0, 1), 3.2, 0.2, 4, (0.85, 0.42, 0.12))
    fort_ob = fort.to_object("Fort", painted, col)
    animated.append({"ob": fort_ob, "year": 1625, "grow": 2.0})

    # windmill with turning sails
    wm = p["windmill"]
    wz = ground(wm.x, wm.y)
    mill = Parts()
    mill.box(wm.x, wm.y, wz, (1, 0), (0, 1), 5, 5, 14, (0.50, 0.45, 0.38), (0.30, 0.14, 0.08))
    mill_ob = mill.to_object("Windmill", painted, col)
    animated.append({"ob": mill_ob, "year": 1627, "grow": 2.0})
    blades = Parts()
    for k in range(4):
        a = math.radians(90 * k)
        ca, sa = math.cos(a), math.sin(a)
        corners = []
        for r, w in ((1.0, -1.4), (15.0, -1.4), (15.0, 1.4), (1.0, 1.4)):
            corners.append((0.0, r * ca - w * sa, r * sa + w * ca))
        blades.add(corners, [(0, 1, 2, 3)], [SAIL])
    blade_ob = blades.to_object("MillSails", painted, col)
    blade_ob.location = (wm.x - 5.6, wm.y, wz + 12)
    animated.append({"ob": blade_ob, "year": 1627, "grow": 0.0})

    # church with a spire
    ch = p["church"]
    cz = ground(ch.x, ch.y)
    church = Parts()
    church.house({"x": ch.x, "y": ch.y, "ux": (0, 1), "uy": (1, 0), "d": 34, "w": 15, "h": 17,
                  "wall": (0.60, 0.56, 0.48), "roof": (0.20, 0.20, 0.22)}, cz)
    church.box(ch.x, ch.y - 20, cz, (1, 0), (0, 1), 4.5, 4.5, 26, (0.60, 0.56, 0.48))
    church.add([(ch.x - 4.5, ch.y - 24.5, cz + 26), (ch.x + 4.5, ch.y - 24.5, cz + 26),
                (ch.x + 4.5, ch.y - 15.5, cz + 26), (ch.x - 4.5, ch.y - 15.5, cz + 26),
                (ch.x, ch.y - 20, cz + 48)],
               [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)], [(0.18, 0.20, 0.20)] * 4)
    animated.append({"ob": church.to_object("Church", painted, col), "year": 1690, "grow": 4.0})

    # market square paving
    mk = p["market"]
    sq = Parts()
    mzz = ground(mk.x, mk.y) + 0.25
    sq.quad([(mk.x - 24, mk.y - 24), (mk.x + 24, mk.y - 24), (mk.x + 24, mk.y + 24), (mk.x - 24, mk.y + 24)],
            mzz, (0.47, 0.43, 0.35))
    animated.append({"ob": sq.to_object("Market", painted, col), "year": 1700, "grow": 0.0})

    # palisade wall across the peninsula
    x0, x1, py = p["palisade"]
    pal = Parts()
    steps = int((x1 - x0) / 6)
    for k in range(steps):
        xa = x0 + (x1 - x0) * k / steps
        pal.box(xa + 3, py, ground(xa, py), (1, 0), (0, 1), 3.1, 0.8, 5, WOOD)
    pal_ob = pal.to_object("Palisade", painted, col)
    animated.append({"ob": pal_ob, "year": 1660, "grow": 3.0, "gone": 1706})

    # wharves
    for wf in p["wharves"]:
        part = Parts()
        part.box(wf["x0"] + wf["len"] / 2, wf["y"], -2.0, (1, 0), (0, 1), wf["len"] / 2, 5.5, 3.3,
                 (0.22, 0.16, 0.11), (0.33, 0.26, 0.18))
        animated.append({"ob": part.to_object("Wharf", painted, col), "year": wf["year"], "grow": 2.0})

    # ships
    rng = random.Random(brief["seed"] + 5)
    ships = []
    for k in range(7):
        sp = Parts()
        L, B = 30.0, 7.5
        hull = [(-L / 2, -B / 2, 0.0), (L / 2 - 6, -B / 2, 0.0), (L / 2, 0.0, 0.0), (L / 2 - 6, B / 2, 0.0),
                (-L / 2, B / 2, 0.0),
                (-L / 2, -B / 2, 4.0), (L / 2 - 6, -B / 2, 4.0), (L / 2, 0.0, 4.5), (L / 2 - 6, B / 2, 4.0),
                (-L / 2, B / 2, 4.0)]
        sp.add(hull, [(0, 1, 6, 5), (1, 2, 7, 6), (2, 3, 8, 7), (3, 4, 9, 8), (4, 0, 5, 9), (5, 6, 7, 8, 9)],
               [WOOD] * 5 + [(0.25, 0.18, 0.12)])
        for mx in (-8.0, 1.0, 9.0):
            sp.box(mx, 0, 4, (1, 0), (0, 1), 0.35, 0.35, 24, WOOD)
            for sz in (9.0, 17.0):
                sp.box(mx, 0, sz, (1, 0), (0, 1), 0.35, 5.0, 6.5, SAIL)
        ob = sp.to_object("Ship%d" % k, painted, col)
        if k < 3:
            start = Vector((rng.uniform(-900, 600), rng.uniform(-1500, -900)))
            vel = Vector((rng.choice((-1, 1)) * rng.uniform(3, 6), rng.uniform(1, 3)))
            appear = (1622, 1650, 1680)[k]
        else:
            wf = p["wharves"][min(len(p["wharves"]) - 1, 2 + (k - 3) * 3)]
            start = Vector((wf["x0"] + wf["len"] + 9, wf["y"] + 12))
            vel = Vector((0.0, 0.0))
            appear = wf["year"] + 6
        ob.rotation_euler.z = math.atan2(vel.y, vel.x) if vel.length else math.radians(rng.uniform(-10, 10))
        ships.append({"ob": ob, "start": start, "vel": vel, "year": appear})

    # light, sky, camera
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 5.0
    sun.data.angle = math.radians(2.5)
    sun.data.color = (1.0, 0.93, 0.82)
    sun.rotation_euler = (math.radians(55), 0, math.radians(-50))
    col.objects.link(sun)
    world = bpy.data.worlds.new("Sky")
    world.use_nodes = True
    bg = next(nd for nd in world.node_tree.nodes if nd.type == "BACKGROUND")
    bg.inputs[0].default_value = (*HAZE, 1)
    bg.inputs[1].default_value = 0.75
    scene.world = world

    cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    cam.data.lens = 30
    cam.data.clip_end = 30000
    col.objects.link(cam)
    scene.camera = cam

    labels = []
    for lb in brief.get("labels", []):
        anchor = {
            "fort": (FORT.x, FORT.y, fz + 22), "windmill": (wm.x, wm.y, wz + 26),
            "church": (ch.x, ch.y - 20, cz + 50), "market": (mk.x, mk.y, mzz + 4),
            "palisade": ((x0 + x1) / 2, py, ground((x0 + x1) / 2, py) + 8),
            "wharf": (p["wharves"][len(p["wharves"]) // 2]["x0"] + 30, p["wharves"][len(p["wharves"]) // 2]["y"], 6),
            "island": (-430, -1230, 12), "west_river": (-1050, 150, 1), "east_river": (1000, -150, 1),
        }.get(lb["at"])
        if anchor:
            labels.append(dict(lb, pos=Vector(anchor)))

    return {"scene": scene, "camera": cam, "animated": animated, "trees": trees, "ships": ships,
            "frontier": frontier, "blades": blade_ob, "labels": labels,
            "stats": "%d buildings, %d trees" % (len(p["houses"]), len(p["trees"]))}


# ----------------------------------------------------------------------------
# Story timing
# ----------------------------------------------------------------------------
def interp(keys, x):
    if x <= keys[0][0]:
        return keys[0][1]
    for (x0, y0), (x1, y1) in zip(keys, keys[1:]):
        if x <= x1:
            t = (x - x0) / (x1 - x0) if x1 > x0 else 1.0
            return y0 + (y1 - y0) * t
    return keys[-1][1]


def year_at(brief, t):
    return interp(brief["year_keys"], t)


def first_time(brief, year, total, fps):
    for f in range(total):
        if year_at(brief, f / fps) >= year:
            return f / fps
    return total / fps


def pick(entries, year):
    cur = None
    for e in entries:
        if year >= e["from"]:
            cur = e
    return cur


def fmt_pop(v):
    if v <= 0:
        return None
    step = 10 if v < 1000 else 100 if v < 20000 else 1000
    return "c. {:,}".format(int(round(v / step) * step))


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


# ----------------------------------------------------------------------------
# Per-frame update
# ----------------------------------------------------------------------------
def apply_frame(brief, rig, frame, total):
    fps = brief["fps"]
    t = frame / fps
    year = year_at(brief, t)

    for a in rig["animated"]:
        if a["grow"] > 0:
            k = ease((year - a["year"]) / a["grow"])
        else:
            k = 1.0 if year >= a["year"] else 0.0
        if a.get("gone") is not None:
            k *= 1.0 - ease((year - a["gone"]) / 3.0)
        a["ob"].hide_render = k <= 0.001
        a["ob"].scale.z = max(k, 0.001)
    front = field_front(year)
    for tr in rig["trees"]:
        tr["ob"].hide_render = tr["settle"] < front
    rig["frontier"].outputs[0].default_value = front / 6000.0
    for sh in rig["ships"]:
        sh["ob"].hide_render = year < sh["year"]
        pos = sh["start"] + sh["vel"] * (t * 4)
        sh["ob"].location = (pos.x, pos.y, 0.0)
    rig["blades"].rotation_euler.x = t * 1.3

    # camera: slow drift and gentle push in, always looking over the town
    cp = brief["camera"]
    s = ease(t / (total / fps))
    loc = Vector(cp["from"]).lerp(Vector(cp["to"]), s)
    look = Vector(cp["look_from"]).lerp(Vector(cp["look_to"]), s)
    cam = rig["camera"]
    cam.location = loc
    cam.rotation_euler = (look - loc).to_track_quat("-Z", "Y").to_euler()
    heading = math.degrees(math.atan2(look.x - loc.x, look.y - loc.y))

    # overlay information
    scene = rig["scene"]
    bpy.context.view_layer.update()
    labels = []
    for lb in rig["labels"]:
        if year < lb.get("from", -1e9) or year >= lb.get("until", 1e9):
            continue
        t0 = first_time(brief, lb.get("from", -1e9), total, fps)
        alpha = ease((t - t0) / 0.6) if lb.get("from") else 1.0
        if "until" in lb:
            alpha *= 1.0 - ease((year - lb["until"] + 4) / 4)
        p = world_to_camera_view(scene, cam, lb["pos"])
        if p.z <= 0 or not (0.04 < p.x < 0.96 and 0.12 < p.y < 0.92):
            continue
        labels.append({"text": lb["text"], "x": p.x, "y": 1.0 - p.y, "alpha": round(alpha, 3)})

    caption = None
    events = brief.get("events", [])
    for i, ev in enumerate(events):
        t0 = max(ev.get("min_time", 0.0), first_time(brief, ev["year"], total, fps))
        t1 = first_time(brief, events[i + 1]["year"], total, fps) - 0.25 if i + 1 < len(events) else total / fps + 1
        if t0 <= t < t1:
            a = ease((t - t0) / 0.5) * (1 - ease((t - t1 + 0.5) / 0.5))
            caption = {"title": ev["title"], "body": ev["body"], "alpha": round(a, 3),
                       "date": ev.get("date") if year < ev["year"] + 2 else None}
    era = pick(brief["eras"], year)
    ruler = pick(brief["rulers"], year)
    pop = fmt_pop(interp(brief["population"], year))
    tc = brief.get("title_card")
    title = None
    if tc and tc["start"] <= t <= tc["end"]:
        a = ease((t - tc["start"]) / 0.8) * (1 - ease((t - tc["end"] + 0.8) / 0.8))
        title = {"kicker": tc["kicker"], "title": tc["title"], "years": tc["years"], "alpha": round(a, 3)}
    return {
        "year": int(year), "era": era["text"] if era else "",
        "realm": ruler["realm"] if ruler else "", "ruler": ruler["name"] if ruler else "",
        "shield": ruler.get("shield", 0) if ruler else 0,
        "population": pop or "—", "population_note": brief.get("population_note", ""),
        "heading": heading, "caption": caption, "title_card": title, "labels": labels,
        "fineprint": brief.get("fineprint", ""),
    }
