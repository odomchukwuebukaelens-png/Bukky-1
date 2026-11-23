"""Paris style ("style": "paris" in a brief), built on the Rome/London machinery.

Paris has no open register of construction dates, so this style mixes:
  * today's buildings from Overture Maps / OpenStreetMap, with dates ESTIMATED
    from their district (see paris_prepare.py);
  * reconstructed ancient, medieval and Renaissance fabric (generated);
  * monuments rebuilt from their published dimensions, each with a life span
    (built, damaged, ruined, demolished).
Everything reconstructed is illustrative and labelled as such in the video.
"""
import gzip
import json
import math
import os
import random

import bpy
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from mathutils import noise as mnoise

import style_historic as H
import style_nyc as N
import people as P

LAT0, LON0 = 48.8530, 2.3499
KX = 111320.0 * math.cos(math.radians(LAT0))
KY = 111132.0


def proj(lon, lat):
    return Vector(((lon - LON0) * KX, (lat - LAT0) * KY))


def P2(lonlat):
    return proj(lonlat[0], lonlat[1])


NOTRE_DAME = (2.3499, 48.8530)
LOUVRE = (2.3376, 48.8604)
BASTILLE = (2.3691, 48.8532)
DATA_X, DATA_Y = (-6200.0, 6200.0), (-4600.0, 4600.0)
CLEAR = [(2.3499, 48.8530, 75), (2.3450, 48.8554, 25), (2.3376, 48.8604, 110), (2.3320, 48.8625, 90),
         (2.3691, 48.8532, 60), (2.3127, 48.8550, 130), (2.3462, 48.8462, 70), (2.2950, 48.8738, 60),
         (2.2945, 48.8584, 130), (2.3431, 48.8867, 70), (2.3527, 48.8452, 40), (2.3415, 48.8465, 50),
         (2.3655, 48.8556, 70), (2.3359, 48.8611, 30)]
WALL_PA = [(2.3365, 48.8615), (2.3455, 48.8650), (2.3560, 48.8615), (2.3625, 48.8555), (2.3560, 48.8480),
           (2.3470, 48.8455), (2.3380, 48.8480), (2.3350, 48.8545)]
WALL_C5 = [(2.3310, 48.8635), (2.3430, 48.8700), (2.3560, 48.8705), (2.3690, 48.8535)]


def inside(pt, poly):
    x, y = pt
    res = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            res = not res
    return res


class Paris:
    def __init__(self, folder):
        with gzip.open(os.path.join(folder, "paris.json.gz"), "rt") as f:
            self.data = json.load(f)
        t = np.load(os.path.join(folder, "terrain.npz"))
        self.land, self.elev, self.shore = t["land"], t["elev"], t["shore"]
        x0, y0, res, nx, ny = t["box"]
        self.x0, self.y0, self.res, self.nx, self.ny = x0, y0, res, int(nx), int(ny)
        self.zones = {k: [tuple(c) for c in v] for k, v in self.data["zones"].items()}

    def ij(self, x, y):
        i = int((x - self.x0) / self.res)
        j = int((self.y0 + self.ny * self.res - y) / self.res)
        return min(max(j, 0), self.ny - 1), min(max(i, 0), self.nx - 1)

    def z(self, x, y):
        j, i = self.ij(x, y)
        return float(self.elev[j, i])

    def is_land(self, x, y):
        j, i = self.ij(x, y)
        return bool(self.land[j, i])

    def zone(self, x, y):
        for k in ("cite", "left", "marais", "philippe", "charles", "haussmann"):
            if inside((x, y), self.zones[k]):
                return k
        return "outside"

    def in_fire(self, x, y):
        return False

    def eras(self, x, y, rng=None):
        """(urban_at, abandon_at, reurban_at, farm_at)."""
        zn = self.zone(x, y)
        d = Vector((x, y)).length
        never = 99999
        farm = -150 + d * 0.03
        if zn == "cite":
            return -250, never, never, farm
        if zn == "left":
            return 10 + d * 0.02, 280, 1150 + d * 0.05, farm
        if zn == "philippe":
            return 900 + d * 0.15, never, never, farm
        if zn == "marais":
            return 1250, never, never, farm
        if zn == "charles":
            return 1300 + d * 0.06, never, never, farm
        if zn == "haussmann":
            return min(1860.0, 1600 + d * 0.06), never, never, farm
        return min(1935.0, 1780 + d * 0.025), never, never, farm


# ----------------------------------------------------------------------------
# Terrain material: wild -> farmland -> town -> (abandoned fields) -> town
# ----------------------------------------------------------------------------
def terrain_material():
    mat = bpy.data.materials.new("RomeTerrain")
    nt = H.nodes(mat)
    bsdf = H.principled(nt)
    bsdf.inputs["Roughness"].default_value = 0.95
    a1 = nt.nodes.new("ShaderNodeAttribute")
    a1.attribute_name = "era"
    a2 = nt.nodes.new("ShaderNodeAttribute")
    a2.attribute_name = "era2"
    s1 = nt.nodes.new("ShaderNodeSeparateColor")
    s2 = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(a1.outputs["Color"], s1.inputs[0])
    nt.links.new(a2.outputs["Color"], s2.inputs[0])
    farm_at, urban_at, forest = s1.outputs[0], s1.outputs[1], s1.outputs[2]
    abandon_at, reurban_at = s2.outputs[0], s2.outputs[1]
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    pos = geo.outputs["Position"]

    def tex(scale, detail=4):
        t = nt.nodes.new("ShaderNodeTexNoise")
        t.inputs["Scale"].default_value = scale
        t.inputs["Detail"].default_value = detail
        nt.links.new(pos, t.inputs["Vector"])
        return t.outputs["Fac"]
    now = nt.nodes.new("ShaderNodeValue")
    now.name = "now"
    m = H.math_node
    step = lambda a: H.smooth(nt, m(nt, "SUBTRACT", now.outputs[0], a), 0.0, 0.004)  # noqa: E731
    canopy = nt.nodes.new("ShaderNodeTexVoronoi")
    canopy.inputs["Scale"].default_value = 0.09
    nt.links.new(pos, canopy.inputs["Vector"])
    clump = H.smooth(nt, canopy.outputs["Distance"], 0.15, 0.75)
    forest_col = H.mix_rgb(nt, clump, (0.05, 0.13, 0.03), (0.025, 0.07, 0.02))
    meadow = H.mix_rgb(nt, tex(0.012), (0.30, 0.30, 0.10), (0.20, 0.24, 0.07))
    wild = H.mix_rgb(nt, H.smooth(nt, forest, 0.45, 0.55), meadow, forest_col)
    cells = nt.nodes.new("ShaderNodeTexVoronoi")
    cells.distance = "CHEBYCHEV"
    cells.inputs["Scale"].default_value = 0.02
    nt.links.new(pos, cells.inputs["Vector"])
    pick = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(cells.outputs["Color"], pick.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    pal = [(0.0, (0.36, 0.33, 0.12)), (0.2, (0.24, 0.30, 0.08)), (0.4, (0.45, 0.38, 0.16)),
           (0.6, (0.20, 0.26, 0.07)), (0.8, (0.40, 0.30, 0.16))]
    els = ramp.color_ramp.elements
    els[0].position, els[0].color = pal[0][0], (*pal[0][1], 1)
    els[1].position, els[1].color = pal[1][0], (*pal[1][1], 1)
    for p_, c_ in pal[2:]:
        e = els.new(p_)
        e.color = (*c_, 1)
    nt.links.new(pick.outputs[0], ramp.inputs["Fac"])
    farmed = m(nt, "MULTIPLY", step(farm_at), H.smooth(nt, pick.outputs[1], 0.1, 0.14))
    urban = m(nt, "ADD", m(nt, "MULTIPLY", step(urban_at), m(nt, "SUBTRACT", 1.0, step(abandon_at))),
              step(reurban_at), clamp=True)
    town = H.mix_rgb(nt, tex(0.06), (0.38, 0.32, 0.24), (0.32, 0.27, 0.21))
    ruin_field = m(nt, "MULTIPLY", step(abandon_at), m(nt, "SUBTRACT", 1.0, step(reurban_at)))
    vineyard = H.mix_rgb(nt, tex(0.3, 2), (0.30, 0.32, 0.12), (0.38, 0.33, 0.18))
    land = H.mix_rgb(nt, farmed, wild, ramp.outputs["Color"])
    land = H.mix_rgb(nt, ruin_field, land, vineyard)
    land = H.mix_rgb(nt, urban, land, town)
    nt.links.new(land, bsdf.inputs["Base Color"])
    for name in ("Emission Color", "Emission"):
        if name in bsdf.inputs:
            bsdf.inputs[name].default_value = (1.0, 0.70, 0.38, 1)
            break
    glow = m(nt, "MULTIPLY", m(nt, "MULTIPLY", urban, N.mood_value(nt, "night")), H.smooth(nt, tex(0.6), 0.62, 0.72))
    nt.links.new(m(nt, "MULTIPLY", glow, 0.25), bsdf.inputs["Emission Strength"])
    H.add_haze(mat)
    return mat, now


def arcade_material():
    """Travertine with rows of tall arched openings (used for the Colosseum)."""
    mat = bpy.data.materials.new("Arcade")
    nt = H.nodes(mat)
    bsdf = H.principled(nt)
    bsdf.inputs["Roughness"].default_value = 0.85
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "col"
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    pos = nt.nodes.new("ShaderNodeSeparateXYZ")
    nrm = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], pos.inputs[0])
    nt.links.new(geo.outputs["Normal"], nrm.inputs[0])
    m = H.math_node
    storey = m(nt, "FRACT", m(nt, "DIVIDE", pos.outputs["Z"], 12.0))
    opening = m(nt, "MULTIPLY", m(nt, "GREATER_THAN", storey, 0.12), m(nt, "LESS_THAN", storey, 0.80))
    bays = m(nt, "GREATER_THAN", m(nt, "FRACT", m(nt, "DIVIDE", m(nt, "ADD", pos.outputs["X"], pos.outputs["Y"]), 6.5)), 0.42)
    walls = m(nt, "LESS_THAN", m(nt, "ABSOLUTE", nrm.outputs["Z"]), 0.5)
    mask = m(nt, "MULTIPLY", m(nt, "MULTIPLY", m(nt, "MULTIPLY", opening, bays), walls), attr.outputs["Alpha"])
    c = H.mix_rgb(nt, mask, attr.outputs["Color"], (0.10, 0.08, 0.06))
    nt.links.new(c, bsdf.inputs["Base Color"])
    return H.add_haze(mat)


def yn(y):
    return (y - 1500.0) / 600.0


# ----------------------------------------------------------------------------
# Geometry helpers
# ----------------------------------------------------------------------------
STONE = (0.80, 0.74, 0.62)
MARBLE = (0.93, 0.91, 0.86)
TRAVERTINE = (0.85, 0.78, 0.62)
BRICK = (0.62, 0.32, 0.20)
TILE = (0.62, 0.24, 0.12)
WALL_COLS = [(0.82, 0.62, 0.38), (0.86, 0.72, 0.50), (0.74, 0.48, 0.30), (0.90, 0.80, 0.62), (0.66, 0.38, 0.24)]
BRICKS = [(0.55, 0.30, 0.20), (0.62, 0.40, 0.28), (0.48, 0.26, 0.18), (0.70, 0.55, 0.40), (0.86, 0.84, 0.78)]
MODERN = [(0.30, 0.42, 0.52), (0.72, 0.74, 0.74), (0.20, 0.26, 0.32), (0.84, 0.82, 0.76)]
PORTLAND = (0.88, 0.86, 0.80)
LIMESTONE = [(0.74, 0.66, 0.52), (0.70, 0.62, 0.48), (0.78, 0.70, 0.56), (0.66, 0.58, 0.45), (0.80, 0.73, 0.60)]
ZINC = [(0.42, 0.45, 0.50), (0.38, 0.41, 0.46), (0.47, 0.50, 0.54)]
TIMBER = [(0.88, 0.84, 0.72), (0.80, 0.74, 0.60), (0.60, 0.44, 0.30), (0.92, 0.90, 0.82)]
SLATE = (0.30, 0.30, 0.33)


def ring(cx, cy, rx, ry, n):
    return [(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]


def wall_ring(part, pts, z, thick, h, col, tower_every=0.0, tower=(0, 0)):
    for a, b in zip(pts, pts[1:] + pts[:1]):
        a, b = Vector(a), Vector(b)
        d = b - a
        n = max(1, int(d.length / 8))
        u = d.normalized()
        for k in range(n):
            p = a + d * ((k + 0.5) / n)
            part.box(p.x, p.y, z(p.x, p.y), tuple(u), (-u.y, u.x), d.length / n / 2 + 0.3, thick / 2, h, col)
        if tower_every:
            t = 0.0
            while t < d.length:
                p = a + u * t
                part.box(p.x, p.y, z(p.x, p.y), tuple(u), (-u.y, u.x), tower[0], tower[0], h + tower[1], col)
                t += tower_every


def temple(part, x, y, z, w, d, h, yaw, col=MARBLE, roof=TILE, cols=6, ruin=False):
    ux, uy = (math.cos(yaw), math.sin(yaw)), (-math.sin(yaw), math.cos(yaw))
    part.box(x, y, z, ux, uy, d / 2 + 2, w / 2 + 2, 3.0, col)                      # podium
    nc_side = max(4, int(d / (w / (cols - 1))))
    for i in range(cols):
        for j in (0,) if ruin else range(nc_side):
            off_w = -w / 2 + w * i / (cols - 1)
            off_d = d / 2 - d * j / max(1, nc_side - 1)
            if ruin and (i % 3 == 1):
                continue
            px = x + ux[0] * off_d + uy[0] * off_w
            py = y + ux[1] * off_d + uy[1] * off_w
            part.box(px, py, z + 3, ux, uy, 0.7, 0.7, h, col)
    if not ruin:
        part.box(x - ux[0] * d * 0.1, y - ux[1] * d * 0.1, z + 3, ux, uy, d * 0.35, w * 0.35, h, col)   # cella
        part.box(x, y, z + 3 + h, ux, uy, d / 2 + 0.5, w / 2 + 0.5, 1.6, col)                         # entablature
        ridge = z + 4.6 + h + w * 0.22
        v = []
        for sx in (-1, 1):
            v.append((x + ux[0] * sx * (d / 2 + 0.5) - uy[0] * (w / 2 + 0.5), y + ux[1] * sx * (d / 2 + 0.5) - uy[1] * (w / 2 + 0.5), z + 4.6 + h))
            v.append((x + ux[0] * sx * (d / 2 + 0.5) + uy[0] * (w / 2 + 0.5), y + ux[1] * sx * (d / 2 + 0.5) + uy[1] * (w / 2 + 0.5), z + 4.6 + h))
            v.append((x + ux[0] * sx * (d / 2 + 0.5), y + ux[1] * sx * (d / 2 + 0.5), ridge))
        part.add(v, [(0, 3, 5, 2), (1, 2, 5, 4), (0, 1, 2), (3, 5, 4)], [roof, roof, col, col])


# ----------------------------------------------------------------------------
# Plan and build
# ----------------------------------------------------------------------------
def build(brief, plan_unused=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    col = scene.collection
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    city = Paris(os.path.join(root, brief.get("data", "data/paris")))
    rng = random.Random(brief["seed"])
    for k in N.MOOD:
        N.MOOD[k].clear()
    H.HAZE_NODES.clear()
    H.HAZE_DISTANCE = brief.get("haze_distance", 60000.0)
    H.HAZE_AMOUNT = brief.get("haze_amount", 0.18)
    if brief.get("haze_color"):
        H.HAZE = tuple(brief["haze_color"])
    painted = N.painted_nyc("PaintedParis")
    tree_mat = N.painted_nyc("TreesParis", trees=True)
    facade, night = N.facade_material()
    tmat, now = terrain_material()
    arch_mat = arcade_material()
    N.WATER_MAT.clear()
    N.WATER_MAT.append(N.shore_water_material())
    animated = []
    z = city.z

    # --- terrain mesh and water --------------------------------------------
    nx, ny, res = city.nx, city.ny, city.res
    xs = city.x0 + (np.arange(nx) + 0.5) * res
    ys = city.y0 + ny * res - (np.arange(ny) + 0.5) * res
    verts, era, era2, wverts, wshore = [], [], [], [], []
    for j in range(ny):
        for i in range(nx):
            x, y = float(xs[i]), float(ys[j])
            e = float(city.elev[j, i])
            verts.append((x, y, e))
            u, a, r, f = city.eras(x, y)
            fo = 0.5 + 0.7 * mnoise.noise(Vector((x / 650.0 + 3.1, y / 650.0 - 1.7, 0.4)))
            era.append((yn(f), yn(u), max(0.0, min(1.0, fo)), 1.0))
            era2.append((yn(a), yn(r), 0.0, 1.0))
            wshore.append(min(1.0, float(city.shore[j, i]) / 300.0))
    faces = [(j * nx + i, j * nx + i + 1, (j + 1) * nx + i + 1, (j + 1) * nx + i)
             for j in range(ny - 1) for i in range(nx - 1)]
    me = bpy.data.meshes.new("LondonTerrain")
    me.from_pydata(verts, [], faces)
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    for name, data in (("era", era), ("era2", era2)):
        a_ = me.color_attributes.new(name, "FLOAT_COLOR", "POINT")
        a_.data.foreach_set("color", [c for v in data for c in v])
    me.materials.append(tmat)
    col.objects.link(bpy.data.objects.new("RomeTerrain", me))
    wfaces = [f for f in faces if any(not city.land[k // nx, k % nx] for k in f)]
    wme = bpy.data.meshes.new("RomeWater")
    wme.from_pydata([(v[0], v[1], 0.3) for v in verts], [], wfaces)
    wa = wme.color_attributes.new("shorec", "FLOAT_COLOR", "POINT")
    wa.data.foreach_set("color", [c for v in wshore for c in (v, v, v, 1.0)])
    wme.materials.append(N.WATER_MAT[0])
    col.objects.link(bpy.data.objects.new("RomeWater", wme))
    sea = bpy.data.meshes.new("Ground")
    s = 40000
    sea.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
    gm = bpy.data.materials.new("FarGround")
    gnt = H.nodes(gm)
    H.principled(gnt).inputs["Base Color"].default_value = (0.28, 0.30, 0.12, 1)
    H.add_haze(gm)
    sea.materials.append(gm)
    g_ob = bpy.data.objects.new("FarGround", sea)
    g_ob.location.z = -1.0
    col.objects.link(g_ob)

    bins = {}

    def put(key, fn):
        part = bins.setdefault(key, N.Partsc())
        fn(part)

    # --- today's buildings (estimated dates) and their predecessors --------
    for b in city.data["buildings"]:
        cx, cy, year, est, h, flat, name = b
        pts = [(flat[i], flat[i + 1]) for i in range(0, len(flat), 2)]
        zz = z(cx, cy) - 0.5
        grow = 3.0
        start = year
        low = name.lower()
        if any((Vector((cx, cy)) - P2((lo, la))).length < r_ * 0.8 for lo, la, r_ in CLEAR):
            continue                                    # monuments are modelled separately
        modern = year >= 1950
        wall = rng.choice(MODERN) if modern else rng.choice(LIMESTONE)
        roof = rng.choice(ZINC) if 1800 <= year < 1950 else rng.choice([SLATE, (0.62, 0.30, 0.18)])
        key = ("bld", int(start // 2) * 2, int(grow))
        if h < 32 and not modern:
            put(key, lambda part, pts=pts, zz=zz, h=h, wall=wall, roof=roof: N.extrude_roofed(part, pts, zz, h, wall, 0.6, roof))
        else:
            put(key, lambda part, pts=pts, zz=zz, h=h, wall=wall: N.extrude(part, pts, zz, h, wall, 0.6, (0.45, 0.45, 0.47)))
        zn = city.zone(cx, cy)
        if False:
            m0 = 0
            put(("med", int(m0 // 25) * 25, int(year // 25) * 25),
                lambda part, cx=cx, cy=cy, zz=zz: part.house({"x": cx, "y": cy, "ux": (1, 0), "uy": (0, 1),
                                                               "d": rng.uniform(8, 12), "w": rng.uniform(6, 9),
                                                               "h": rng.uniform(9, 13), "wall": rng.choice(H.WALLS),
                                                               "roof": TILE}, zz))

    # --- historic fabric: Gallic huts, Roman Lutetia, medieval timber, old-regime stone -----
    step_ = 26.0
    fr = random.Random(brief["seed"] + 3)
    yy = city.y0
    while yy < city.y0 + ny * res:
        xx = city.x0
        while xx < city.x0 + nx * res:
            px_, py_ = xx + fr.uniform(-8, 8), yy + fr.uniform(-8, 8)
            xx += step_
            if not city.is_land(px_, py_):
                continue
            if any((Vector((px_, py_)) - P2((lo, la))).length < r_ for lo, la, r_ in CLEAR):
                continue
            zn = city.zone(px_, py_)
            beyond = not (DATA_X[0] < px_ < DATA_X[1] and DATA_Y[0] < py_ < DATA_Y[1])
            if zn == "outside" and fr.random() < (0.6 if beyond else 0.8):
                continue
            u, ab, re_, _f = city.eras(px_, py_)
            zz = z(px_, py_)
            yaw = fr.uniform(-0.3, 0.3)
            ux, uy = (math.cos(yaw), math.sin(yaw)), (-math.sin(yaw), math.cos(yaw))
            if zn == "cite":                          # the Parisii's huts
                put(("gal", -250, 25), lambda part, px_=px_, py_=py_, zz=zz: part.house(
                    {"x": px_, "y": py_, "ux": ux, "uy": uy, "d": 7, "w": 6, "h": 4.5, "hip": True,
                     "wall": (0.48, 0.36, 0.24), "roof": (0.62, 0.52, 0.30)}, zz))
            if zn in ("cite", "left"):                # Roman Lutetia
                a0 = max(u, 0) + fr.uniform(10, 120)
                a1 = (ab if ab < 9000 else 500) + fr.uniform(-30, 20)
                put(("rom", int(a0 // 25) * 25, int(a1 // 25) * 25),
                    lambda part, px_=px_, py_=py_, zz=zz: part.house({"x": px_, "y": py_, "ux": ux, "uy": uy, "hip": True,
                                                                       "d": fr.uniform(10, 16), "w": fr.uniform(7, 11),
                                                                       "h": fr.uniform(5, 8), "wall": (0.88, 0.82, 0.68),
                                                                       "roof": TILE}, zz))
            if zn != "outside":                       # medieval and early-modern houses
                m0 = (re_ if re_ < 9000 else max(u, 500)) + fr.uniform(0, 150)
                if m0 < 1700:
                    m1 = fr.uniform(1853, 1880) if zn in ("haussmann", "charles", "philippe", "left") else fr.uniform(1750, 1900)
                    put(("med", int(m0 // 25) * 25, int(m1 // 5) * 5),
                        lambda part, px_=px_, py_=py_, zz=zz: part.house({"x": px_, "y": py_, "ux": ux, "uy": uy,
                                                                           "hip": fr.random() < 0.5,
                                                                           "d": fr.uniform(8, 12), "w": fr.uniform(5, 8),
                                                                           "h": fr.uniform(10, 16), "wall": fr.choice(TIMBER),
                                                                           "roof": fr.choice([SLATE, (0.62, 0.30, 0.18)])}, zz))
            g0 = max(u, 1640) + fr.uniform(0, 120)
            if g0 < 1880 and (zn in ("haussmann", "outside") or beyond):
                g1 = 99999 if beyond else fr.uniform(1855, 1900)
                put(("geo", int(g0 // 10) * 10, int(g1 // 25) * 25),
                    lambda part, px_=px_, py_=py_, zz=zz: part.house({"x": px_, "y": py_, "ux": ux, "uy": uy, "hip": True,
                                                                       "d": fr.uniform(12, 16), "w": fr.uniform(9, 12),
                                                                       "h": fr.uniform(14, 20), "wall": fr.choice(LIMESTONE),
                                                                       "roof": fr.choice(ZINC + [SLATE])}, zz))
        yy += step_

    # --- monuments ------------------------------------------------------------
    def mon(name, t0, t1, fn, grow=4.0, label=None, ruin=None, mat=None):
        part = N.Partsc()
        fn(part)
        ob = part.to_object(name, mat or painted, col)
        animated.append({"ob": ob, "year": t0, "grow": grow, "gone": t1, "fade": 3.0})
        if ruin:
            rpart = N.Partsc()
            ruin["fn"](rpart)
            rob = rpart.to_object(name + "_ruin", mat or painted, col)
            animated.append({"ob": rob, "year": ruin["from"], "grow": 0.5, "gone": ruin.get("to", 99999), "fade": 3.0})
        return ob

    marks = {}

    def at(lonlat):
        p = P2(lonlat)
        return p.x, p.y, z(p.x, p.y)

    def bridge(p, a, b, z_deck, w, col_, houses=False, arches=True):
        a, b = P2(a), P2(b)
        d = b - a
        u = d.normalized()
        v = Vector((-u.y, u.x))
        p.box((a.x + b.x) / 2, (a.y + b.y) / 2, z_deck, tuple(u), tuple(v), d.length / 2, w / 2, 2.5, col_)
        if arches:
            n = int(d.length / 16)
            for k in range(n + 1):
                q = a + d * (k / max(1, n))
                p.box(q.x, q.y, -3, tuple(u), tuple(v), 3.0, w / 2 + 1.0, z_deck + 3, col_)
        if houses:
            hr = random.Random(41)
            t = 8.0
            while t < d.length - 8:
                for sd in (-1, 1):
                    q = a + u * t + v * sd * (w / 2 - 3.0)
                    p.box(q.x, q.y, z_deck + 2.5, tuple(u), tuple(v), hr.uniform(2.5, 4), 3.0, hr.uniform(9, 13),
                          (*hr.choice(TIMBER), 0.0), top=((0.35, 0.36, 0.40, 0.0)))
                t += hr.uniform(7, 10)

    def rect_ring(p, cx, cy, hx, hy, h, thick, col_, yaw=0.0, roof=None):
        ux, uy = (math.cos(yaw), math.sin(yaw)), (-math.sin(yaw), math.cos(yaw))
        for sx, sy, lx, ly in ((0, 1, hx, thick), (0, -1, hx, thick), (1, 0, thick, hy), (-1, 0, thick, hy)):
            q = Vector((cx, cy)) + Vector(ux) * sx * (hx - thick) + Vector(uy) * sy * (hy - thick)
            p.box(q.x, q.y, z(cx, cy), ux, uy, lx, ly, h, (*col_, 0.6), top=(*(roof or SLATE), 0.0))

    # Roman Lutetia: forum, arena and baths on the left bank
    fx_, fy_, fz_ = at((2.3415, 48.8465))
    mon("Forum", 30, 280, lambda p: rect_ring(p, fx_, fy_, 85, 45, 10, 6, (0.86, 0.80, 0.66), roof=TILE), 4)
    marks["forum"] = (fx_, fy_, fz_ + 18)
    ax_, ay_, az_ = at((2.3527, 48.8452))
    def arena(p):
        for k in range(40):
            a = 2 * math.pi * k / 40
            x_, y_ = ax_ + 40 * math.cos(a), ay_ + 34 * math.sin(a)
            ang = math.atan2(34 * math.cos(a), -40 * math.sin(a))
            p.box(x_, y_, az_, (math.cos(ang), math.sin(ang)), (-math.sin(ang), math.cos(ang)), 3.4, 6, 10, (*STONE, 0.0))
    mon("Arena", 100, 280, arena, 4)
    marks["arena"] = (ax_, ay_, az_ + 16)
    bx_, by_, bz_ = at((2.3437, 48.8506))
    mon("Baths", 200, 99999, lambda p: p.box(bx_, by_, bz_, (1, 0), (0, 1), 50, 30, 15, (*BRICK, 0.4), top=(*TILE, 0.0)), 4)

    # Philippe Auguste's wall (1190-1213) and Charles V's wall (1356-1383)
    w1 = N.Partsc()
    pts = [tuple(P2(p)) for p in WALL_PA]
    wall_ring(w1, pts, z, 3.0, 9.0, (*STONE, 0.0), tower_every=60.0, tower=(3.5, 4.0))
    animated.append({"ob": w1.to_object("WallPhilippe", painted, col), "year": 1190, "grow": 23, "gone": 1700, "fade": 80})
    w2 = N.Partsc()
    pts2 = [tuple(P2(p)) for p in WALL_C5]
    for a, b in zip(pts2, pts2[1:]):
        wall_ring(w2, [a, b], z, 4.0, 10.0, (*STONE, 0.0), tower_every=80.0, tower=(4.0, 5.0))
    animated.append({"ob": w2.to_object("WallCharles", painted, col), "year": 1356, "grow": 27, "gone": 1670, "fade": 40})
    marks["wall"] = (*tuple(P2((2.3455, 48.8650))), 14)

    # Notre-Dame (1163-1260), spire 1250-1786 and 1859-2019, restored 2024
    nx_, ny_, nz_ = at(NOTRE_DAME)
    yaw = math.radians(-22)
    ux, uy = (math.cos(yaw), math.sin(yaw)), (-math.sin(yaw), math.cos(yaw))
    def notre_dame(p):
        p.box(nx_, ny_, nz_, ux, uy, 58, 20, 33, (*LIMESTONE[0], 0.6), top=(0.40, 0.42, 0.46, 0.0))
        p.box(nx_ + ux[0] * 8, ny_ + ux[1] * 8, nz_, ux, uy, 7, 25, 33, (*LIMESTONE[0], 0.6), top=(0.40, 0.42, 0.46, 0.0))
        N.extrude(p, ring(nx_ + ux[0] * 58, ny_ + ux[1] * 58, 20, 20, 16), nz_, 30, LIMESTONE[0], 0.6, roof=(0.40, 0.42, 0.46))
        for sd in (-1, 1):
            q = Vector((nx_, ny_)) - Vector(ux) * 52 + Vector(uy) * sd * 12
            p.box(q.x, q.y, nz_, ux, uy, 7, 7, 69, (*LIMESTONE[0], 0.7))
        q = Vector((nx_, ny_)) - Vector(ux) * 52
        p.box(q.x, q.y, nz_, ux, uy, 7, 5, 45, (*LIMESTONE[0], 0.7))
    mon("NotreDame", 1163, 99999, notre_dame, 97)
    def spire_part(p):
        q = Vector((nx_, ny_)) + Vector(ux) * 8
        p.add([(q.x - 4, q.y - 4, nz_ + 33), (q.x + 4, q.y - 4, nz_ + 33), (q.x + 4, q.y + 4, nz_ + 33),
               (q.x - 4, q.y + 4, nz_ + 33), (q.x, q.y, nz_ + 96)], [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)],
              [(0.30, 0.32, 0.36, 0.0)] * 4)
    for k, (t0, t1) in enumerate(((1250, 1786), (1859, 2019.29), (2024.6, 99999))):
        part = N.Partsc()
        spire_part(part)
        animated.append({"ob": part.to_object("NDSpire%d" % k, painted, col), "year": t0, "grow": 3, "gone": t1, "fade": 0.02})
    marks["notredame"] = (nx_, ny_, nz_ + 80)

    # Sainte-Chapelle (1248)
    cx2, cy2, cz2 = at((2.3450, 48.8554))
    mon("SainteChapelle", 1243, 99999, lambda p: (p.box(cx2, cy2, cz2, ux, uy, 18, 8, 42, (*LIMESTONE[1], 0.8), top=(0.40, 0.42, 0.46, 0.0)),
                                                  p.add([(cx2 - 2, cy2 - 2, cz2 + 42), (cx2 + 2, cy2 - 2, cz2 + 42), (cx2 + 2, cy2 + 2, cz2 + 42),
                                                         (cx2 - 2, cy2 + 2, cz2 + 42), (cx2, cy2, cz2 + 75)], [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)],
                                                        [(0.80, 0.65, 0.25, 0.0)] * 4)), 5)
    marks["saintechapelle"] = (cx2, cy2, cz2 + 80)

    # The Louvre: fortress (1190-1528), palace (from 1546), Grande Galerie, Tuileries (1564-1871), pyramid (1989)
    lx, ly, lz = at(LOUVRE)
    def fortress(p):
        rect_ring(p, lx, ly, 36, 39, 14, 3, STONE)
        N.extrude(p, ring(lx, ly, 8, 8, 16), lz, 32, STONE, 0.0, roof=SLATE)
        for sx in (-1, 1):
            for sy in (-1, 1):
                N.extrude(p, ring(lx + sx * 36, ly + sy * 39, 5, 5, 12), lz, 20, STONE, 0.0, roof=SLATE)
    mon("LouvreFortress", 1190, 1528, fortress, 12)
    mon("LouvrePalace", 1546, 99999, lambda p: rect_ring(p, lx, ly, 80, 80, 26, 12, LIMESTONE[2], roof=ZINC[0]), 120)
    def galerie(p):
        a, b = P2((2.3363, 48.8596)), P2((2.3298, 48.8613))
        d = b - a
        u = d.normalized()
        v = Vector((-u.y, u.x))
        p.box((a.x + b.x) / 2, (a.y + b.y) / 2, z(a.x, a.y), tuple(u), tuple(v), d.length / 2, 13, 22, (*LIMESTONE[2], 0.6), top=(*ZINC[0], 0.0))
    mon("GrandeGalerie", 1595, 99999, galerie, 15)
    def north_wing(p):
        a, b = P2((2.3365, 48.8622)), P2((2.3308, 48.8638))
        d = b - a
        u = d.normalized()
        v = Vector((-u.y, u.x))
        p.box((a.x + b.x) / 2, (a.y + b.y) / 2, z(a.x, a.y), tuple(u), tuple(v), d.length / 2, 16, 24, (*LIMESTONE[2], 0.6), top=(*ZINC[0], 0.0))
    mon("RichelieuWing", 1852, 99999, north_wing, 6)
    tx2, ty2, tz2 = at((2.3301, 48.8626))
    mon("Tuileries", 1564, 1871.39, lambda p: p.box(tx2, ty2, tz2, (math.cos(math.radians(70)), math.sin(math.radians(70))),
                                                    (-math.sin(math.radians(70)), math.cos(math.radians(70))), 160, 14, 26,
                                                    (*LIMESTONE[2], 0.6), top=(*ZINC[0], 0.0)), 15)
    px2, py2, pz2 = at((2.3359, 48.8611))
    pyr = lambda p: p.add([(px2 - 17.5, py2 - 17.5, pz2), (px2 + 17.5, py2 - 17.5, pz2), (px2 + 17.5, py2 + 17.5, pz2),  # noqa: E731
                           (px2 - 17.5, py2 + 17.5, pz2), (px2, py2, pz2 + 21.6)], [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)],
                          [(0.55, 0.70, 0.80, 0.0)] * 4)
    mon("Pyramid", 1989, 99999, pyr, 1)
    marks["louvre"] = (lx, ly, lz + 40)
    marks["tuileries"] = (tx2, ty2, tz2 + 35)
    marks["pyramid"] = (px2, py2, pz2 + 30)

    # Medieval bridges with houses, Pont Neuf (1607)
    mon("PontNotreDame", 1413, 1786, lambda p: bridge(p, (2.3494, 48.8562), (2.3504, 48.8545), 6, 18, (*STONE, 0.0), houses=True), 3)
    mon("PetitPont", 1185, 1718, lambda p: bridge(p, (2.3473, 48.8526), (2.3466, 48.8511), 6, 18, (*STONE, 0.0), houses=True), 3)
    mon("PontNeuf", 1578, 99999, lambda p: (bridge(p, (2.3398, 48.8590), (2.3413, 48.8569), 8, 22, (0.84, 0.80, 0.70, 0.0)),
                                           bridge(p, (2.3413, 48.8569), (2.3423, 48.8550), 8, 22, (0.84, 0.80, 0.70, 0.0))), 29)
    marks["pontneuf"] = (*tuple(P2((2.3413, 48.8569))), 16)

    # The Bastille (1370-1789) and the July Column (1840)
    sx3, sy3, sz3 = at(BASTILLE)
    def bastille(p):
        p.box(sx3, sy3, sz3, (0.34, 0.94), (-0.94, 0.34), 33, 15, 22, (*STONE, 0.0))
        for k in range(8):
            q = Vector((sx3, sy3)) + Vector((0.34, 0.94)) * (-33 + 22 * (k % 4)) + Vector((-0.94, 0.34)) * (15 if k < 4 else -15)
            N.extrude(p, ring(q.x, q.y, 6, 6, 12), sz3, 24, STONE, 0.0, roof=SLATE)
    mon("Bastille", 1370, 1789.6, bastille, 13)
    mon("JulyColumn", 1835, 99999, lambda p: (p.box(sx3, sy3, sz3, (1, 0), (0, 1), 6, 6, 8, (*STONE, 0.0)),
                                              p.box(sx3, sy3, sz3 + 8, (1, 0), (0, 1), 2, 2, 42, (0.35, 0.40, 0.35, 0.0)),
                                              p.box(sx3, sy3, sz3 + 50, (1, 0), (0, 1), 1.2, 1.2, 4, (0.85, 0.70, 0.25, 0.0))), 5)
    marks["bastille"] = (sx3, sy3, sz3 + 35)

    # Place des Vosges (1612)
    vx2, vy2, vz2 = at((2.3655, 48.8556))
    mon("PlaceDesVosges", 1605, 99999, lambda p: rect_ring(p, vx2, vy2, 70, 70, 16, 9, (0.70, 0.38, 0.28), roof=SLATE), 7)

    # Les Invalides (1706), the Panthéon (1790), the Arc de Triomphe (1836)
    def dome(p, cx, cy, cz, base_r, drum_h, dome_r, z0, col_, cap):
        N.extrude(p, ring(cx, cy, base_r, base_r, 28), cz + z0, drum_h, col_, 0.6, roof=col_)
        prof = [(1.0, 0.0), (0.96, 0.28), (0.85, 0.52), (0.66, 0.74), (0.42, 0.9), (0.15, 1.0)]
        top = cz + z0 + drum_h
        for (r0, h0), (r1, h1) in zip(prof, prof[1:]):
            N.extrude(p, ring(cx, cy, dome_r * (r0 + r1) / 2, dome_r * (r0 + r1) / 2, 28), top + dome_r * h0,
                      dome_r * (h1 - h0) + 0.3, cap, 0.0, roof=cap)
        N.extrude(p, ring(cx, cy, 2.5, 2.5, 10), top + dome_r, 12, cap, 0.0, roof=cap)
    ix, iy, iz = at((2.3127, 48.8550))
    mon("Invalides", 1671, 99999, lambda p: (rect_ring(p, ix, iy + 90, 100, 60, 18, 14, LIMESTONE[0], roof=ZINC[0]),
                                             p.box(ix, iy, iz, (1, 0), (0, 1), 30, 30, 30, (*LIMESTONE[0], 0.5)),
                                             dome(p, ix, iy, iz, 15, 20, 14, 30, LIMESTONE[0], (0.86, 0.68, 0.22))), 35)
    marks["invalides"] = (ix, iy, iz + 110)
    pn_x, pn_y, pn_z = at((2.3462, 48.8462))
    mon("Pantheon", 1758, 99999, lambda p: (p.box(pn_x, pn_y, pn_z, (1, 0), (0, 1), 55, 20, 30, (*LIMESTONE[2], 0.4)),
                                            p.box(pn_x, pn_y, pn_z, (1, 0), (0, 1), 20, 42, 30, (*LIMESTONE[2], 0.4)),
                                            dome(p, pn_x, pn_y, pn_z, 14, 18, 13, 30, LIMESTONE[2], (0.55, 0.58, 0.60))), 32)
    marks["pantheon"] = (pn_x, pn_y, pn_z + 90)
    ar_x, ar_y, ar_z = at((2.2950, 48.8738))
    def arc(p):
        for sd in (-1, 1):
            p.box(ar_x + sd * 15, ar_y, ar_z, (1, 0), (0, 1), 7.5, 11, 50, (*LIMESTONE[2], 0.0))
        p.box(ar_x, ar_y, ar_z + 30, (1, 0), (0, 1), 22.5, 11, 20, (*LIMESTONE[2], 0.0))
    mon("ArcDeTriomphe", 1806, 99999, arc, 30)
    marks["arc"] = (ar_x, ar_y, ar_z + 60)

    # The Eiffel Tower (1887-1889)
    ex, ey, ez = at((2.2945, 48.8584))
    def eiffel(p):
        bronze = (0.45, 0.33, 0.24, 0.0)
        def half(zz_):
            return 62 * math.exp(-zz_ / 72.0) + 1.5
        yaw_e = math.radians(-46)
        ue, ve = (math.cos(yaw_e), math.sin(yaw_e)), (-math.sin(yaw_e), math.cos(yaw_e))
        step = 6.0
        zz_ = 0.0
        while zz_ < 276:
            s0 = half(zz_)
            for sx in (-1, 1):
                for sy in (-1, 1):
                    k = 1.0 if zz_ > 57 else 1.0
                    q = Vector((ex, ey)) + Vector(ue) * sx * s0 * k + Vector(ve) * sy * s0 * k
                    w_ = 7.0 if zz_ < 57 else (3.5 if zz_ < 115 else 2.0)
                    p.box(q.x, q.y, ez + zz_, ue, ve, w_, w_, step + 0.3, bronze)
            zz_ += step
        for zp, sz in ((57, half(57) + 6), (115, half(115) + 4), (276, 6)):
            p.box(ex, ey, ez + zp, ue, ve, sz, sz, 4, bronze)
        p.box(ex, ey, ez + 276, ue, ve, 1.0, 1.0, 24, bronze)
    mon("EiffelTower", 1887.1, 99999, eiffel, 2.2)
    marks["eiffel"] = (ex, ey, ez + 310)

    # Sacré-Cœur (1875-1914) on Montmartre
    sc_x, sc_y, sc_z = at((2.3431, 48.8867))
    white = (0.95, 0.94, 0.90)
    mon("SacreCoeur", 1875, 99999, lambda p: (p.box(sc_x, sc_y, sc_z, (1, 0), (0, 1), 40, 25, 22, (*white, 0.3)),
                                              dome(p, sc_x, sc_y, sc_z, 9, 14, 11, 22, white, white),
                                              N.extrude(p, ring(sc_x, sc_y + 32, 4, 4, 12), sc_z, 60, white, 0.0, roof=white)), 39)
    marks["sacrecoeur"] = (sc_x, sc_y, sc_z + 90)

    # objects from bins
    for key, part in bins.items():
        ob = part.to_object("_".join(str(k) for k in key), facade if key[0] in ("bld", "imp") else painted, col)
        kind = key[0]
        if kind == "bld":
            animated.append({"ob": ob, "year": key[1], "grow": max(2.0, key[2]), "gone": None})
        elif kind in ("med", "rep", "imp", "tow", "rom", "geo", "gal"):
            animated.append({"ob": ob, "year": key[1], "grow": 3.0, "gone": key[2] + 12.5, "fade": 15.0})

    # trees: forest on hills and riverbanks, cleared by farms/town
    ico_v, ico_f = H.ico_template()
    tb = {}
    tr = random.Random(9)
    for _ in range(26000):
        x_, y_ = tr.uniform(city.x0, city.x0 + nx * res), tr.uniform(city.y0, city.y0 + ny * res)
        if not city.is_land(x_, y_):
            continue
        fo = 0.5 + 0.7 * mnoise.noise(Vector((x_ / 650.0 + 3.1, y_ / 650.0 - 1.7, 0.4)))
        if fo < 0.5:
            continue
        u, ab, re_, farm = city.eras(x_, y_)
        gone = min(u, farm + tr.uniform(0, 600))
        back = ab + tr.uniform(20, 200) if ab < 9000 else 99999      # trees return in the abandoned city
        back_gone = re_ if back < 9000 else 99999
        r = tr.uniform(4, 7)
        g = tr.uniform(0.8, 1.2)
        vv = [(x_ + vx * r, y_ + vy * r, z(x_, y_) + r * 0.9 + vz * r * 0.8) for vx, vy, vz in ico_v]
        col_ = (0.055 * g, 0.20 * g, 0.035 * g)
        tb.setdefault(("t", -3000, int(gone // 50) * 50), H.Parts()).add(vv, ico_f, [col_] * len(ico_f))
        if back < 9000:
            tb.setdefault(("t", int(back // 50) * 50, int(back_gone // 50) * 50), H.Parts()).add(vv, ico_f, [col_] * len(ico_f))
    for key, part in tb.items():
        ob = part.to_object("trees_%d_%d" % key[1:], tree_mat, col)
        animated.append({"ob": ob, "year": key[1], "grow": 0.0, "gone": key[2], "fade": 20.0})

    # people, armies and vehicles from the brief
    groups = []
    for k, spec in enumerate(brief.get("groups", [])):
        sp = dict(spec)
        sp["path"] = [tuple(P2(p)) for p in spec["path"]]
        groups.append(P.make_group(sp, z, painted, col, brief["seed"] + 100 + k))

    # fires / smoke / dust reuse the New York effects
    fx = []
    emit = bpy.data.materials.new("Flame")
    ent = H.nodes(emit)
    ent.nodes.clear()
    em = ent.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (1.0, 0.22, 0.02, 1)
    em.inputs["Strength"].default_value = 1.6
    outn = ent.nodes.new("ShaderNodeOutputMaterial")
    ent.links.new(em.outputs[0], outn.inputs[0])
    frng = random.Random(brief["seed"] + 9)
    fx_v, fx_f = N.smooth_sphere()
    for e in brief.get("fx", []):
        c = P2(e["ll"])
        z0 = z(c.x, c.y)
        blobs = H.Parts()
        smoke_col = (0.20, 0.19, 0.18) if e["kind"] == "fire" else (0.40, 0.38, 0.35)
        for _ in range(e.get("blobs", 45)):
            r = frng.uniform(0.15, 1.0) * e["radius"]
            a = frng.uniform(0, 2 * math.pi)
            q = Vector((math.cos(a), math.sin(a))) * r
            rr = frng.uniform(14, 40) * e.get("size", 0.75)
            zz = z0 + frng.uniform(0, 1.0) ** 2 * 70 * e.get("size", 0.75)
            blobs.add([(q.x + vx * rr, q.y + vy * rr, zz + vz * rr * 0.55) for vx, vy, vz in fx_v], fx_f,
                      [smoke_col] * len(fx_f))
        smoke = blobs.to_object("smoke", painted, col)
        smoke.location = (c.x, c.y, 0)
        smoke.data.polygons.foreach_set("use_smooth", [True] * len(smoke.data.polygons))
        flames = None
        if e["kind"] == "fire":
            fl = H.Parts()
            for _ in range(e.get("flames", 320)):
                r = frng.uniform(0, 1.0) ** 0.7 * e["radius"]
                a = frng.uniform(0, 2 * math.pi)
                q = c + Vector((math.cos(a), math.sin(a))) * r
                rr = frng.uniform(2.0, 5.0)
                zz = z0 + frng.uniform(4, 12)
                fl.add([(q.x + vx * rr, q.y + vy * rr, zz + vz * rr * 2.2) for vx, vy, vz in fx_v], fx_f,
                       [(1, 0.5, 0.1)] * len(fx_f))
            flames = fl.to_object("flames", emit, col)
            flames.data.polygons.foreach_set("use_smooth", [True] * len(flames.data.polygons))
        fx.append({"e": e, "smoke": smoke, "flames": flames})

    # sun, sky, camera
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = brief.get("sun", 5.0)
    sun.data.angle = math.radians(1.0)
    sun.data.color = tuple(brief.get("sun_color", [1.0, 0.93, 0.82]))
    sun.rotation_euler = (math.radians(brief.get("sun_tilt", 52)), 0, math.radians(brief.get("sun_heading", -40)))
    col.objects.link(sun)
    world = bpy.data.worlds.new("Sky")
    world.use_nodes = True
    bg = next(nd for nd in world.node_tree.nodes if nd.type == "BACKGROUND")
    bg.inputs[0].default_value = (*H.HAZE, 1)
    bg.inputs[1].default_value = brief.get("sky", 0.9)
    scene.world = world
    wnt = world.node_tree
    tc = wnt.nodes.new("ShaderNodeTexCoord")
    sz_ = wnt.nodes.new("ShaderNodeSeparateXYZ")
    wnt.links.new(tc.outputs["Generated"], sz_.inputs[0])
    mr = wnt.nodes.new("ShaderNodeMapRange")
    wnt.links.new(sz_.outputs["Z"], mr.inputs["Value"])
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = 0.35
    zen = wnt.nodes.new("ShaderNodeMix")
    zen.data_type = "RGBA"
    wnt.links.new(mr.outputs[0], zen.inputs[0])
    zen.inputs[7].default_value = (*brief.get("zenith", [0.22, 0.42, 0.78]), 1)
    wnt.links.new(zen.outputs[2], bg.inputs[0])
    H.SKY_MIX = zen
    cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    cam.data.lens = brief.get("lens", 32)
    cam.data.clip_start = brief.get("clip_start", 1.0)
    cam.data.clip_end = brief.get("clip_end", 30000.0)
    col.objects.link(cam)
    scene.camera = cam

    labels = []
    for lb in brief.get("labels", []):
        if "ll" in lb:
            q = P2(lb["ll"])
            labels.append(dict(lb, pos=Vector((q.x, q.y, z(q.x, q.y) + lb["ll"][2]))))
        elif lb.get("at") in marks:
            labels.append(dict(lb, pos=Vector(marks[lb["at"]])))

    def before(t, year):
        for g in groups:
            P.place_group(g, t)

    def auc(year):
        y = int(round(year))
        return "—" if y < -52 else (y + 52 if y < 0 else y + 51)

    def ground(x, y):
        return max(z(x, y), 0.3)

    # height map of tall buildings (with the year they appear) for camera clearance
    cell = 40.0
    tall = {}
    for b in city.data["buildings"]:
        cx, cy, year, est, h, flat, name = b
        if h < 35:
            continue
        for dx in (-2, -1, 0, 1, 2):
            for dy in (-2, -1, 0, 1, 2):
                k = (int(cx // cell) + dx, int(cy // cell) + dy)
                tall.setdefault(k, []).append((year, h))
    for extra in ((2.2945, 48.8584, 1887, 330), (2.3499, 48.8530, 1200, 96), (2.3127, 48.8550, 1700, 107),
                  (2.3462, 48.8462, 1780, 83), (2.3431, 48.8867, 1900, 85)):
        q = P2(extra[:2])
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                tall.setdefault((int(q.x // cell) + dx, int(q.y // cell) + dy), []).append((extra[2], extra[3]))

    def clearance(x, y, year):
        hs = [h for yr, h in tall.get((int(x // cell), int(y // cell)), ()) if yr <= year + 3]
        return ground(x, y) + (max(hs) + 30.0 if hs else 0.0)

    return {"proj": lambda lon, lat: proj(lon, lat), "year_text": year_text, "counter": auc, "ground": ground, "clearance": clearance,
            "before_frame": before,
            "scene": scene, "camera": cam, "animated": animated, "now": now, "labels": labels, "fx": fx,
            "sun": sun, "sky": bg, "night": night, "ships": [], "city": None, "beams": [], "groups": groups,
            "stats": "%d of today's buildings (estimated dates), %d groups of people" % (
                len(city.data["buildings"]), len(groups))}


def plan(brief):
    return None


def year_text(y):
    y = int(round(y))
    return "%d BC" % (-y) if y < 0 else ("AD %d" % y if y < 1000 else str(y))


def apply_frame(brief, rig, frame, total):
    return N.apply_frame(brief, rig, frame, total)
