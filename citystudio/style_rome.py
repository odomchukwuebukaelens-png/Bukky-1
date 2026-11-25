"""Rome style ("style": "rome" in a brief).

Rome has no open register of construction dates, so this style mixes:
  * today's buildings from Overture Maps / OpenStreetMap, with dates ESTIMATED
    from their district (see rome_prepare.py);
  * reconstructed ancient, medieval and Renaissance fabric (generated);
  * monuments rebuilt from their published dimensions, each with a life span
    (built, burnt, ruined, demolished), and the Tiber bridges;
  * a dense forest that is cleared only where buildings and streets appear.
Everything reconstructed is illustrative and labelled as such in the video.
"""
import gzip
import json
import math
import os
import random

import bpy
import numpy as np
from mathutils import Vector
from mathutils import noise as mnoise

import style_historic as H
import style_nyc as N
import people as P
from trees import tree_instancer

LAT0, LON0 = 41.8958, 12.4826
KX = 111320.0 * math.cos(math.radians(LAT0))
KY = 111132.0


def proj(lon, lat):
    return Vector(((lon - LON0) * KX, (lat - LAT0) * KY))


def P2(lonlat):
    return proj(lonlat[0], lonlat[1])


# Approximate Aurelian Wall circuit (lon, lat), 271-275 AD.
AURELIAN = [(12.4763, 41.9113), (12.4885, 41.9095), (12.4970, 41.9105), (12.5015, 41.9093), (12.5075, 41.9055),
            (12.5130, 41.8985), (12.5155, 41.8915), (12.5105, 41.8835), (12.5000, 41.8785), (12.4990, 41.8740),
            (12.4975, 41.8715), (12.4895, 41.8725), (12.4810, 41.8763), (12.4720, 41.8790), (12.4735, 41.8835),
            (12.4615, 41.8845), (12.4670, 41.8925), (12.4685, 41.8960), (12.4720, 41.9020), (12.4745, 41.9080)]
SERVIAN = [(12.4800, 41.8970), (12.4880, 41.9030), (12.4960, 41.9040), (12.5030, 41.9000), (12.5040, 41.8940),
           (12.4990, 41.8880), (12.4930, 41.8830), (12.4850, 41.8790), (12.4790, 41.8800), (12.4770, 41.8850),
           (12.4780, 41.8920)]

FORUM = (12.4853, 41.8925)
# open ground kept clear of houses: (lon, lat, radius m)
CLEAR = [(12.4853, 41.8925, 130), (12.4875, 41.8888, 170), (12.4922, 41.8902, 125), (12.4851, 41.8861, 150),
         (12.4815, 41.8840, 150), (12.4887, 41.8882, 150), (12.4817, 41.8929, 80), (12.4768, 41.8986, 60),
         (12.4848, 41.8955, 110), (12.4763, 41.9060, 65), (12.4925, 41.8791, 240), (12.4880, 41.8918, 70),
         (12.4799, 41.8918, 60), (12.4730, 41.8950, 90), (12.4977, 41.9031, 160), (12.4890, 41.8908, 80)]
PALATINE = (12.4875, 41.8895)
VITTORIANO = (12.4828, 41.8946)


def inside(pt, poly):
    x, y = pt
    res = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            res = not res
    return res


DATA_X, DATA_Y = (-4600.0, 4600.0), (-3600.0, 3800.0)
ROME_TREES = [("broad", 0.85), ("broad", 1.05), ("umbrella", 1.0), ("cypress", 0.9), ("broad", 1.2)]
TOWN_TREES = (1, 2, 2, 3, 3, 4)          # gardens: oaks, stone pines and cypresses


class Rome:
    def __init__(self, folder):
        with gzip.open(os.path.join(folder, "rome.json.gz"), "rt") as f:
            self.data = json.load(f)
        t = np.load(os.path.join(folder, "terrain.npz"))
        self.land, self.elev, self.shore = t["land"], t["elev"], t["shore"]
        x0, y0, res, nx, ny = t["box"]
        self.x0, self.y0, self.res, self.nx, self.ny = x0, y0, res, int(nx), int(ny)
        self.aur = [tuple(P2(p)) for p in AURELIAN]
        self.serv = [tuple(P2(p)) for p in SERVIAN]
        self.zones = {k: [tuple(c) for c in v] for k, v in self.data["zones"].items()}

    def ij(self, x, y):
        i = int((x - self.x0) / self.res)
        j = int((self.y0 + self.ny * self.res - y) / self.res)
        return min(max(j, 0), self.ny - 1), min(max(i, 0), self.nx - 1)

    def z(self, x, y):
        j, i = self.ij(x, y)
        return float(self.elev[j, i])

    def is_land(self, x, y, year=99999):
        j, i = self.ij(x, y)
        return bool(self.land[j, i])

    def fill(self, x, y):
        return 0

    def in_fire(self, x, y):
        return False

    def zone(self, x, y):
        for k in ("vatican", "borgo", "abitato", "trastevere", "prati"):
            if inside((x, y), self.zones[k]):
                return k
        if inside((x, y), self.serv):
            return "servian"
        if inside((x, y), self.aur):
            return "aurelian"
        return "outside"

    def eras(self, x, y, rng=None):
        """(urban_at, abandon_at, reurban_at, farm_at) for the ground at a point."""
        zn = self.zone(x, y)
        d_forum = (Vector((x, y)) - P2(FORUM)).length
        d_pal = (Vector((x, y)) - P2(PALATINE)).length
        if d_pal < 180:
            urban = -753
        elif zn == "servian":
            urban = -700 + d_forum * 0.12
        elif zn in ("abitato", "aurelian"):
            urban = -250 + d_forum * 0.12
        elif zn in ("trastevere", "borgo"):
            urban = -100 + d_forum * 0.05
        else:
            urban = 99999
        if zn in ("abitato", "trastevere", "borgo", "vatican"):
            abandon, reurban = 99999, 99999
        elif zn in ("servian", "aurelian"):
            abandon, reurban = 600 + d_forum * 0.03, 1873 + d_forum * 0.012
        elif zn == "prati":
            abandon, reurban, urban = 99999, 1885 + (x * 0.0), 1885
        else:
            dist = Vector((x, y)).length
            urban = min(1990, 1905 + max(0, dist - 2300) * 0.014)
            abandon, reurban = 99999, 99999
        if zn == "vatican":
            urban = 330
        return urban, abandon, reurban, urban - 60          # fields only shortly before a district is built


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
    town = H.mix_rgb(nt, tex(0.06), (0.17, 0.26, 0.08), (0.24, 0.30, 0.11))   # gardens and courtyards stay green
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
    v = m(nt, "FRACT", m(nt, "DIVIDE", pos.outputs["Z"], 12.0))
    u = m(nt, "FRACT", m(nt, "DIVIDE", m(nt, "ADD", pos.outputs["X"], pos.outputs["Y"]), 6.5))
    du = m(nt, "DIVIDE", m(nt, "SUBTRACT", u, 0.62), 0.26)                    # -1..1 across the opening
    dv = m(nt, "DIVIDE", m(nt, "SUBTRACT", v, 0.58), 0.20)
    in_bay = m(nt, "LESS_THAN", m(nt, "ABSOLUTE", du), 1.0)
    shaft = m(nt, "MULTIPLY", m(nt, "GREATER_THAN", v, 0.10), m(nt, "LESS_THAN", v, 0.58))
    head = m(nt, "LESS_THAN", m(nt, "ADD", m(nt, "MULTIPLY", du, du), m(nt, "MULTIPLY", dv, dv)), 1.0)
    head = m(nt, "MULTIPLY", head, m(nt, "GREATER_THAN", v, 0.57))
    opening = m(nt, "MULTIPLY", in_bay, m(nt, "MAXIMUM", shaft, head))
    walls = m(nt, "LESS_THAN", m(nt, "ABSOLUTE", nrm.outputs["Z"]), 0.5)
    mask = m(nt, "MULTIPLY", m(nt, "MULTIPLY", opening, walls), attr.outputs["Alpha"])
    cornice = m(nt, "MULTIPLY", m(nt, "GREATER_THAN", v, 0.88), m(nt, "LESS_THAN", v, 0.95))
    column = m(nt, "MULTIPLY", m(nt, "LESS_THAN", m(nt, "ABSOLUTE", m(nt, "SUBTRACT", u, 0.18)), 0.05),
               m(nt, "LESS_THAN", v, 0.88))
    trim = m(nt, "MULTIPLY", m(nt, "MAXIMUM", cornice, column), m(nt, "MULTIPLY", walls, attr.outputs["Alpha"]))
    stone = H.mix_rgb(nt, m(nt, "MULTIPLY", trim, 0.6), attr.outputs["Color"], (0.97, 0.92, 0.80))
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 0.35
    nt.links.new(geo.outputs["Position"], noise.inputs["Vector"])
    stone = H.mix_rgb(nt, m(nt, "MULTIPLY", H.smooth(nt, noise.outputs["Fac"], 0.45, 0.75), 0.35), stone, (0.55, 0.48, 0.38))
    c = H.mix_rgb(nt, mask, stone, (0.09, 0.07, 0.05))
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
WOOD = (0.42, 0.30, 0.20)
TIMBER = [WOOD]
THATCH = (0.55, 0.46, 0.25)
WALL_COLS = [(0.82, 0.62, 0.38), (0.86, 0.72, 0.50), (0.74, 0.48, 0.30), (0.90, 0.80, 0.62), (0.66, 0.38, 0.24)]


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
    city = Rome(os.path.join(root, brief.get("data", "data/rome")))
    rng = random.Random(brief["seed"])
    for k in N.MOOD:
        N.MOOD[k].clear()
    H.HAZE_NODES.clear()
    H.HAZE_DISTANCE = brief.get("haze_distance", 60000.0)
    H.HAZE_AMOUNT = brief.get("haze_amount", 0.18)
    if brief.get("haze_color"):
        H.HAZE = tuple(brief["haze_color"])
    H.HOUSE_DETAIL = True                       # windows, doors and overhanging tiled roofs
    painted = N.painted_nyc("PaintedRome")
    tree_mat = N.painted_nyc("TreesRome", trees=True)
    facade, night = N.facade_material()
    tmat, now = terrain_material()
    arch_mat = arcade_material()
    N.WATER_MAT.clear()
    N.WATER_MAT.append(N.shore_water_material(((0.20, 0.22, 0.12), (0.07, 0.10, 0.05), (0.035, 0.055, 0.03)), realistic=True))  # the olive-green Tiber
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
    me = bpy.data.meshes.new("RomeTerrain")
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
    H.principled(gnt).inputs["Base Color"].default_value = (0.08, 0.19, 0.05, 1)
    H.add_haze(gm)
    sea.materials.append(gm)
    g_ob = bpy.data.objects.new("FarGround", sea)
    g_ob.location.z = -1.0
    col.objects.link(g_ob)

    bins = {}

    def put(key, fn):
        part = bins.setdefault(key, N.Partsc())
        fn(part)

    OCC = 12.0
    occupied = {}
    plots = []

    def occupy(x, y, year, radius=8.0, house=True):
        if house:
            plots.append((x, y, year, radius))
        r = int(radius // OCC)
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                k = (int((x // OCC) + dx), int((y // OCC) + dy))
                if year < occupied.get(k, 1e9):
                    occupied[k] = year

    # --- footprints: nothing else may stand inside a monument, a bridge approach
    # or another building while it exists, and no tree grows inside them
    FC = 5.0
    FOOT = {}                      # 5 m cell -> [(from, to)] of monuments and approach roads
    BOCC = {}                      # 5 m cell -> [(from, to)] of buildings (people keep out of them)

    def hull(pts):
        pts = sorted(set((round(x_, 0), round(y_, 0)) for x_, y_ in pts))
        if len(pts) < 3:
            return pts

        def cross(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
        lo, hi = [], []
        for q in pts:
            while len(lo) >= 2 and cross(lo[-2], lo[-1], q) <= 0:
                lo.pop()
            lo.append(q)
        for q in reversed(pts):
            while len(hi) >= 2 and cross(hi[-2], hi[-1], q) <= 0:
                hi.pop()
            hi.append(q)
        return lo[:-1] + hi[:-1]

    def register(xy, t0, t1, pad=3.0, clear_trees=True):
        hp = hull(xy)
        if len(hp) < 3:
            return
        xs_, ys_ = [q[0] for q in hp], [q[1] for q in hp]
        for i in range(int((min(xs_) - pad) // FC), int((max(xs_) + pad) // FC) + 1):
            for j in range(int((min(ys_) - pad) // FC), int((max(ys_) + pad) // FC) + 1):
                cx_, cy_ = (i + 0.5) * FC, (j + 0.5) * FC
                if inside((cx_, cy_), hp) or any(math.hypot(cx_ - q[0], cy_ - q[1]) < pad for q in hp):
                    FOOT.setdefault((i, j), []).append((t0, t1))
                    if clear_trees:
                        occupy(cx_, cy_, t0, 1.0, house=False)

    def blocked(x, y, start, end, half):
        k = int(half // FC)
        ci, cj = int(x // FC), int(y // FC)
        for di in range(-k, k + 1):
            for dj in range(-k, k + 1):
                for a_, b_ in FOOT.get((ci + di, cj + dj), ()):
                    if a_ < end and b_ > start:
                        return True
        return False

    def mark_building(x, y, half, start, end):
        k = int(half // FC)
        ci, cj = int(x // FC), int(y // FC)
        for di in range(-k, k + 1):
            for dj in range(-k, k + 1):
                BOCC.setdefault((ci + di, cj + dj), []).append((start, end))

    def free_ground(x, y, year):
        """True where a person may stand: on land, not inside a building or monument."""
        if not city.is_land(x, y):
            return False
        c_ = (int(x // FC), int(y // FC))
        return not any(a_ <= year < b_ for a_, b_ in BOCC.get(c_, []) + FOOT.get(c_, []))

    # --- fire and bomb damage: buildings standing in a burnt or bombed area are
    # blackened and reduced to ruins, then (for some events) rebuilt later
    CHAR = (0.07, 0.06, 0.05, 0.0)
    burns = []
    for e in brief.get("fx", []):
        if e.get("destroy", 0) <= 0:
            continue
        burns.append({"e": e, "c": P2(e["ll"]), "r": e["radius"], "t": e["from"] + min(0.6 * (e["to"] - e["from"]), 0.06),
                      "p": e["destroy"], "ruin": e.get("ruin", 0.3), "rebuild": e.get("rebuild", 10.0),
                      "zone": e.get("zone")})
    dr = random.Random(brief["seed"] + 51)

    def damage(x, y, start, end):
        for bn in burns:
            if not (start < bn["t"] < end):
                continue
            hit = (Vector((x, y)) - bn["c"]).length < bn["r"]
            if not hit and bn["zone"] == "fire":
                hit = city.in_fire(x, y)
            if hit and dr.random() < bn["p"]:
                bn.setdefault("hits", []).append((x, y))
                return bn
        return None

    placed = {}

    def place(kind, start, end, x, y, zz, ux, uy, d, w, h, wall, roof, shape="house", bucket=25, extra=None):
        """A generated building that may burn or be bombed during its life."""
        if blocked(x, y, start, end, max(d, w) / 2):
            return                                     # never inside a monument or across a bridge approach
        placed[kind] = placed.get(kind, 0) + 1
        mark_building(x, y, max(d, w) / 2, start, end)
        def draw(part, hh, col_, rf, sh):
            if sh == "house":
                part.house(dict({"x": x, "y": y, "ux": ux, "uy": uy, "d": d, "w": w, "h": hh, "wall": col_, "roof": rf},
                                **(extra or {})), zz)
            else:
                part.box(x, y, zz, ux, uy, d / 2, w / 2, hh, (*col_, 0.6), top=(*rf, 0.0))
        bn = damage(x, y, start, end)
        if bn is None:
            put((kind, int(start // bucket) * bucket, int(end // bucket) * bucket), lambda part: draw(part, h, wall, roof, shape))
            return
        put((kind + "_b", int(start // bucket) * bucket, round(bn["t"], 3)), lambda part: draw(part, h, wall, roof, shape))
        put(("shell", round(bn["t"], 3), int(bn["t"] + bn["rebuild"])),
            lambda part: part.box(x, y, zz, ux, uy, d / 2, w / 2, h * bn["ruin"] * dr.uniform(0.6, 1.4), CHAR))

    # --- monuments ------------------------------------------------------------
    def mon(name, t0, t1, fn, grow=4.0, label=None, ruin=None, mat=None, foot=True):
        part = N.Partsc()
        fn(part)
        if foot:
            end_ = ruin.get("to", 99999) if ruin else t1
            register([(v[0], v[1]) for v in part.verts], t0 - grow, end_)
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

    # the Palatine huts of the earliest settlement
    hx, hy, hz = at(PALATINE)
    def huts(part):
        r2 = random.Random(5)
        for _ in range(24):
            a, d = r2.uniform(0, 6.28), r2.uniform(5, 90)
            x_, y_ = hx + math.cos(a) * d, hy + math.sin(a) * d
            part.house({"x": x_, "y": y_, "ux": (1, 0), "uy": (0, 1), "d": 6, "w": 4.5, "h": 4.2,
                        "wall": (0.45, 0.33, 0.20), "roof": (0.55, 0.46, 0.25)}, z(x_, y_))
    mon("PalatineHuts", -753, -500, huts, 3)
    marks["palatine"] = (hx, hy, hz + 20)

    jx, jy, jz = at((12.4817, 41.8929))
    mon("TempleJupiter", -509, 455, lambda p: temple(p, jx, jy, jz, 53, 62, 16, math.radians(90), cols=6),
        ruin={"from": 455, "fn": lambda p: temple(p, jx, jy, jz, 53, 62, 8, math.radians(90), ruin=True), "to": 1550})
    marks["jupiter"] = (jx, jy, jz + 35)

    for nm_, ll, w_, d_, yaw_, t0 in (("TempleSaturn", (12.4845, 41.8925), 22, 40, 2.6, -497),
                                      ("TempleCastor", (12.4859, 41.8919), 28, 40, -0.6, -484),
                                      ("TempleVenusRoma", (12.4890, 41.8908), 48, 100, 0.95, 135)):
        tx, ty, tz = at(ll)
        mon(nm_, t0, 600, lambda p, tx=tx, ty=ty, tz=tz, w_=w_, d_=d_, yaw_=yaw_: temple(p, tx, ty, tz, w_, d_, 13, yaw_, cols=6 if w_ < 40 else 10),
            ruin={"from": 600, "fn": lambda p, tx=tx, ty=ty, tz=tz, w_=w_, d_=d_, yaw_=yaw_: temple(p, tx, ty, tz, w_, d_, 13, yaw_, ruin=True)})
    marks["forum"] = (*at(FORUM)[:2], at(FORUM)[2] + 15)

    # imperial palaces on the Palatine (from 92 AD), ruined after the 6th century
    px0, py0, pz0 = at((12.4865, 41.8885))
    def palace(p, h, ruined):
        yaw = math.radians(-30)
        ux, uy = (math.cos(yaw), math.sin(yaw)), (-math.sin(yaw), math.cos(yaw))
        for dx, dy, w, d in ((0, 0, 70, 55), (85, -20, 60, 45), (-70, 30, 45, 40), (30, 70, 50, 30)):
            q = Vector((px0, py0)) + Vector(ux) * dx + Vector(uy) * dy
            p.box(q.x, q.y, pz0, ux, uy, w / 2, d / 2, h * (0.4 if ruined else 1.0), (*BRICK, 0.5 if not ruined else 0.0),
                  top=(*TILE, 0.0) if not ruined else None)
    mon("PalatinePalace", 92, 600, lambda p: palace(p, 24, False), 6,
        ruin={"from": 600, "fn": lambda p: palace(p, 24, True)})

    # Circus Maximus
    cx_, cy_, cz_ = at((12.4851, 41.8861))
    def circus(p, h):
        yaw = math.radians(-58)
        ux, uy = (math.cos(yaw), math.sin(yaw)), (-math.sin(yaw), math.cos(yaw))
        for sd in (-1, 1):
            p.box(cx_ + uy[0] * sd * 62, cy_ + uy[1] * sd * 62, cz_, ux, uy, 300, 12, h, (*TRAVERTINE, 1.0))
        p.box(cx_, cy_, cz_, ux, uy, 250, 4, 2.5, (*MARBLE, 0.0))
        p.box(cx_ - ux[0] * 300, cy_ - ux[1] * 300, cz_, ux, uy, 8, 70, h, (*TRAVERTINE, 1.0))
    mon("CircusMaximus", -46, 550, lambda p: circus(p, 28), 6,
        ruin={"from": 550, "fn": lambda p: circus(p, 3), "to": 1600}, mat=arch_mat)
    marks["circus"] = (cx_, cy_, cz_ + 30)

    # Colosseum (72-80 AD); part of the outer ring falls in the 1349 earthquake
    ox, oy, oz = at((12.4922, 41.8902))
    def colosseum(p, broken):
        rot = math.radians(-20)
        n = 64
        for k in range(n):
            a0 = 2 * math.pi * k / n
            if broken and 3.5 < a0 < 5.6:          # the south side fell in the 1349 earthquake
                levels = 2
            else:
                levels = 4
            for rx, ry, hh, thick in ((94, 78, 12 * levels, 6), (70, 54, 30, 18)):
                x_ = ox + rx * math.cos(a0) * math.cos(rot) - ry * math.sin(a0) * math.sin(rot)
                y_ = oy + rx * math.cos(a0) * math.sin(rot) + ry * math.sin(a0) * math.cos(rot)
                tang = Vector((-rx * math.sin(a0), ry * math.cos(a0)))
                ang = math.atan2(tang.y, tang.x) + rot
                ux, uy = (math.cos(ang), math.sin(ang)), (-math.sin(ang), math.cos(ang))
                p.box(x_, y_, oz, ux, uy, 2 * math.pi * rx / n / 2 + 0.6, thick / 2, hh, (*TRAVERTINE, 1.0))
        p.add([(ox + 50 * math.cos(a), oy + 30 * math.sin(a), oz + 0.6) for a in [2 * math.pi * k / 24 for k in range(24)]],
              [tuple(range(24))], [(0.72, 0.62, 0.42, 0.0)])
    mon("Colosseum", 72, 1349, lambda p: colosseum(p, False), 8,
        ruin={"from": 1349, "fn": lambda p: colosseum(p, True)}, mat=arch_mat)
    marks["colosseum"] = (ox, oy, oz + 55)

    # Mausoleum of Augustus (28 BC)
    mx, my, mz = at((12.4763, 41.9060))
    def mausoleum(p, h):
        pts = ring(mx, my, 44, 44, 32)
        N.extrude(p, pts, mz, h, TRAVERTINE, 0.0, roof=(0.25, 0.40, 0.15))
        N.extrude(p, ring(mx, my, 20, 20, 20), mz + h, h * 0.8, TRAVERTINE, 0.0, roof=(0.25, 0.40, 0.15))
    mon("MausoleumAugustus", -28, 1100, lambda p: mausoleum(p, 22), 4,
        ruin={"from": 1100, "fn": lambda p: mausoleum(p, 8)})
    marks["mausoleum"] = (mx, my, mz + 50)

    # Baths of Caracalla (216 AD), ruined after the aqueducts are cut (537)
    bx, by, bz = at((12.4925, 41.8791))
    def baths(p, h, ruined):
        yaw = math.radians(-30)
        ux, uy = (math.cos(yaw), math.sin(yaw)), (-math.sin(yaw), math.cos(yaw))
        p.box(bx, by, bz, ux, uy, 165, 160, 6, (*BRICK, 0.3))
        p.box(bx, by, bz, ux, uy, 110, 57, h, (*BRICK, 0.6 if not ruined else 0.0))
        if not ruined:
            N.extrude(p, ring(bx + ux[0] * 70, by + ux[1] * 70, 18, 18, 20), bz + h, 14, BRICK, 0.0, roof=(0.35, 0.35, 0.37))
    mon("BathsCaracalla", 216, 537, lambda p: baths(p, 38, False), 6,
        ruin={"from": 537, "fn": lambda p: baths(p, 24, True)})
    marks["caracalla"] = (bx, by, bz + 45)

    # Basilica of Maxentius (312), partly falls in the 847 earthquake
    vx, vy, vz = at((12.4880, 41.8918))
    mon("BasilicaMaxentius", 312, 847, lambda p: p.box(vx, vy, vz, (0.7, 0.71), (-0.71, 0.7), 50, 32, 35, (*BRICK, 0.5)), 6,
        ruin={"from": 847, "fn": lambda p: p.box(vx + 10, vy - 10, vz, (0.7, 0.71), (-0.71, 0.7), 40, 10, 24, (*BRICK, 0.5))})

    # Trajan's Column (113) still stands
    tx_, ty_, tz_ = at((12.4843, 41.8958))
    mon("TrajanColumn", 112, 99999, lambda p: (p.box(tx_, ty_, tz_, (1, 0), (0, 1), 3, 3, 6, (*MARBLE, 0.0)),
                                               p.box(tx_, ty_, tz_ + 6, (1, 0), (0, 1), 1.9, 1.9, 32, (*MARBLE, 0.0))), 2)
    marks["trajan"] = (tx_, ty_, tz_ + 45)

    # Old St Peter's (326), replaced by the new basilica 1506-1606
    sx, sy, sz = at((12.4540, 41.9022))
    mon("OldStPeters", 326, 1606, lambda p: (p.box(sx, sy, sz, (1, 0), (0, 1), 60, 32, 30, (*BRICK, 0.3), top=(*TILE, 0.0)),
                                             p.box(sx + 70, sy, sz, (1, 0), (0, 1), 25, 30, 10, (*STONE, 0.0))), 6)
    marks["stpeters"] = (sx, sy, sz + 140)

    # Bernini's colonnade (1656-1667)
    qx, qy, qz = at((12.4573, 41.9022))
    def colonnade(p):
        for sd in (-1, 1):
            for k in range(34):
                a = math.radians(-80 + 160 * k / 33)
                x_, y_ = qx + 100 * math.cos(a) * 0.0 + 70 * math.cos(a) - 10, qy + sd * (60 + 40 * math.sin(abs(a)) * 0) + sd * 55 * math.cos(a * 0.5)
                p.box(x_, y_, qz, (1, 0), (0, 1), 3.5, 3.5, 16, (*TRAVERTINE, 0.0))
    mon("Colonnade", 1656, 99999, colonnade, 11)

    def fit_span(a, b):
        """Stretch a bridge so it runs from bank to bank of the river as drawn."""
        m = (a + b) / 2
        u = (b - a).normalized()
        if city.is_land(m.x, m.y):
            best = None
            for k in range(-40, 41):                     # find the water nearest the given middle
                q = m + u * (k * 5.0)
                if not city.is_land(q.x, q.y) and (best is None or abs(k) < abs(best)):
                    best = k
            if best is None:
                return a, b
            m = m + u * (best * 5.0)
        ends = []
        for sgn in (-1, 1):
            t = 0.0
            while t < 600 and not city.is_land(m.x + u.x * sgn * t, m.y + u.y * sgn * t):
                t += 3.0
            ends.append(m + u * sgn * (t + 14.0))        # rest 14 m onto the bank
        return ends[0], ends[1]

    def bridge(p, a, b, z_deck, w, col_, houses=False, arches=True):
        a, b = fit_span(P2(a), P2(b))
        d = b - a
        u = d.normalized()
        v = Vector((-u.y, u.x))
        p.box((a.x + b.x) / 2, (a.y + b.y) / 2, z_deck, tuple(u), tuple(v), d.length / 2, w / 2, 2.5, col_)
        if arches:
            n = int(d.length / 18)
            for k in range(n + 1):
                q = a + d * (k / max(1, n))
                p.box(q.x, q.y, -3, tuple(u), tuple(v), 3.5, w / 2 + 1.5, z_deck + 3, col_)
        if houses:
            hr = random.Random(41)
            t = 14.0
            while t < d.length - 14:
                gap = hr.uniform(7.5, 10.5)
                if abs(t - d.length * 0.5) < 9:            # the chapel of St Thomas in the middle
                    q = a + u * t + v * (w / 2 - 6)
                    p.house({"x": q.x, "y": q.y, "ux": tuple(u), "uy": tuple(v), "d": 18, "w": 9, "h": 15,
                             "wall": (0.78, 0.74, 0.64), "roof": (0.30, 0.30, 0.33)}, z_deck + 2.5)
                    t += 20
                    continue
                if abs(t - d.length * 0.2) < 6:            # an open gap to the river
                    t += 12
                    continue
                for sd in (-1, 1):
                    q = a + u * (t + gap / 2) + v * sd * (w / 2 - 2.6)
                    p.house({"x": q.x, "y": q.y, "ux": tuple(v), "uy": tuple(u), "d": 6.2, "w": gap - 0.6,
                             "h": hr.uniform(11, 16), "wall": hr.choice(TIMBER + [(0.70, 0.52, 0.34)]),
                             "roof": hr.choice([(0.30, 0.28, 0.26), (0.52, 0.26, 0.15), (0.40, 0.36, 0.32)])},
                            z_deck + 2.5)
                t += gap
            for f in (0.08, 0.86):                          # gatehouses at both ends
                q = a + u * (d.length * f)
                p.box(q.x, q.y, z_deck + 2.5, tuple(u), tuple(v), 5, w / 2 + 1, 16, (*STONE, 0.0), top=((0.30, 0.30, 0.33, 0.0)))


    # --- the Tiber bridges. A bridge that still stands follows the street that
    # crosses the river there today; each end continues straight into the city
    # as a road, and nothing is built across those approach roads.
    river = [[Vector(q) for q in line] for line in city.data.get("tiber", [])]
    crossings = []
    for _n, w_, flat_ in city.data.get("roads", []):
        rp = [Vector((flat_[i], flat_[i + 1])) for i in range(0, len(flat_), 2)]
        for a_, b_ in zip(rp, rp[1:]):
            m_ = (a_ + b_) / 2
            if (b_ - a_).length > 4 and not city.is_land(m_.x, m_.y):
                crossings.append((m_, (b_ - a_).normalized(), w_))

    def across(ll, modern):
        q = P2(ll)
        if modern and crossings:
            m_, u_, w_ = min(crossings, key=lambda c_: (c_[0] - q).length)
            if (m_ - q).length < 160:
                return m_ - u_ * 40, m_ + u_ * 40
        best = None
        for line in river:
            for a_, b_ in zip(line, line[1:]):
                d = b_ - a_
                if d.length < 1:
                    continue
                t = max(0.0, min(1.0, (q - a_).dot(d) / d.length_squared))
                c = a_ + d * t
                if best is None or (c - q).length < best[0]:
                    best = ((c - q).length, c, d.normalized())
        if best is None:
            return q - Vector((40, 0)), q + Vector((40, 0))
        c, u = best[1], best[2]
        v = Vector((-u.y, u.x))
        return c - v * 40, c + v * 40

    inv = lambda p: (LON0 + p.x / KX, LAT0 + p.y / KY)  # noqa: E731
    APPROACH = []                                       # (start, end, width, from, to)
    approach_parts = {}

    BRIDGES = [  # name, (lon, lat), built, gone, deck height, width, colour
        ("PonsSublicius", (12.4778, 41.8878), -620, 450, 6.0, 7, WOOD),
        ("PonsAemilius", (12.4790, 41.8893), -142, 1598, 9.0, 9, TRAVERTINE),
        ("PonsFabricius", (12.4787, 41.8913), -62, 99999, 9.0, 6, (0.66, 0.42, 0.30)),
        ("PonsCestius", (12.4768, 41.8898), -46, 99999, 9.0, 6, TRAVERTINE),
        ("PonsAelius", (12.4668, 41.9014), 134, 99999, 9.0, 9, TRAVERTINE),
        ("PonteSisto", (12.4697, 41.8921), 1479, 99999, 9.0, 8, TRAVERTINE),
        ("PonteGaribaldi", (12.4732, 41.8907), 1888, 99999, 10.0, 18, (0.72, 0.70, 0.66)),
        ("PontePalatino", (12.4796, 41.8878), 1890, 99999, 10.0, 16, (0.72, 0.70, 0.66)),
        ("PonteMargherita", (12.4727, 41.9093), 1891, 99999, 10.0, 18, (0.80, 0.76, 0.68)),
        ("PonteUmberto", (12.4698, 41.9027), 1895, 99999, 10.0, 16, (0.80, 0.76, 0.68)),
        ("PonteCavour", (12.4731, 41.9047), 1901, 99999, 10.0, 18, (0.80, 0.76, 0.68)),
        ("PonteMazzini", (12.4668, 41.8957), 1908, 99999, 10.0, 15, (0.80, 0.76, 0.68)),
        ("PonteVittorio", (12.4650, 41.8994), 1911, 99999, 10.0, 20, (0.84, 0.80, 0.72)),
        ("PonteSublicio", (12.4752, 41.8803), 1918, 99999, 10.0, 18, (0.80, 0.76, 0.68)),
    ]
    for nm_, ll_, b0_, b1_, deck, wd, colr in BRIDGES:
        e0, e1 = fit_span(*across(ll_, b1_ >= 99999))
        u_ = (e1 - e0).normalized()
        for s0, s1 in ((e0 - u_ * 150, e0 + u_ * 6), (e1 - u_ * 6, e1 + u_ * 150)):
            seg = []                                     # the approach road runs on until it meets water or ends
            n_ = 30
            for k in range(n_ + 1):
                q = s0 + (s1 - s0) * (k / n_)
                if city.is_land(q.x, q.y) or (q - e0).length < 8 or (q - e1).length < 8:
                    seg.append(q)
            if len(seg) < 2:
                continue
            APPROACH.append((seg[0], seg[-1], wd, b0_, b1_))
            nrm = Vector((-u_.y, u_.x)) * (wd / 2 + 1.0)
            part = approach_parts.setdefault((b0_, b1_), N.Partsc())
            for qa, qb in zip(seg, seg[1:]):
                part.add([(*(qa - nrm), z(qa.x, qa.y) + 0.45), (*(qb - nrm), z(qb.x, qb.y) + 0.45),
                          (*(qb + nrm), z(qb.x, qb.y) + 0.45), (*(qa + nrm), z(qa.x, qa.y) + 0.45)], [(0, 1, 2, 3)],
                         [(0.56, 0.52, 0.46, 0.0) if b0_ < 1850 else (0.40, 0.40, 0.42, 0.0)])
            register([tuple(seg[0] - nrm), tuple(seg[0] + nrm), tuple(seg[-1] - nrm), tuple(seg[-1] + nrm)], b0_ - 1, b1_)
        a_, b_ = inv(e0), inv(e1)
        if nm_ == "PonsAemilius":                       # the Ponte Rotto: one broken arch left after 1598
            mon(nm_, b0_, b1_, lambda p, a_=a_, b_=b_, deck=deck, wd=wd, colr=colr: bridge(p, a_, b_, deck, wd, (*colr, 0.0)), 3,
                foot=False,
                ruin={"from": b1_, "fn": lambda p, a_=a_, b_=b_: p.box(*tuple((P2(a_) + P2(b_)) / 2), -3, (1, 0), (0, 1),
                                                                      6, 5, 12, (*TRAVERTINE, 0.0))})
            continue
        mon(nm_, b0_, b1_, lambda p, a_=a_, b_=b_, deck=deck, wd=wd, colr=colr: bridge(p, a_, b_, deck, wd, (*colr, 0.0),
                                                                                      arches=colr != WOOD), 3, foot=False)
        marks[nm_] = (*tuple((P2(a_) + P2(b_)) / 2), deck + 12)

    for (b0_, b1_), part in approach_parts.items():
        animated.append({"ob": part.to_object("bridge_roads_%d" % b0_, painted, col), "year": b0_, "grow": 0.0,
                         "gone": None if b1_ >= 99999 else b1_, "fade": 3.0})

    # the Pantheon (126): portico, drum and its great dome
    pnx, pny, pnz = at((12.4768, 41.8986))
    def pantheon(p):
        N.extrude(p, ring(pnx, pny, 22, 22, 28), pnz, 21, (0.80, 0.72, 0.58), 0.0, roof=(0.55, 0.55, 0.55))
        for k in range(6):
            a = math.pi * 0.5 * k / 5
            rr = 22 * math.cos(a)
            N.extrude(p, ring(pnx, pny, max(rr, 3), max(rr, 3), 28), pnz + 21 + 21 * math.sin(a) * 0.7, 3.2,
                      (0.62, 0.62, 0.62), 0.0, roof=(0.62, 0.62, 0.62))
        temple(p, pnx, pny - 30, pnz, 33, 16, 12, math.radians(90), col=(0.86, 0.80, 0.66), cols=8)
    mon("Pantheon", 126, 99999, pantheon, 5)
    marks["pantheon"] = (pnx, pny, pnz + 50)

    # the Vittoriano (1885-1911): white marble terraces, a curved colonnade and two bronze quadrigas, 81 m high
    vix, viy, viz = at(VITTORIANO)
    fwd = Vector((-0.28, 0.96)).normalized()                   # it faces Piazza Venezia and the Via del Corso
    side = Vector((fwd.y, -fwd.x))
    WHITE = (0.95, 0.94, 0.90)
    BRONZE = (0.20, 0.24, 0.20)
    def vittoriano(p):
        def bx(f_, s_, z0, hf, hs, h, col_):
            q = Vector((vix, viy)) + fwd * f_ + side * s_
            p.box(q.x, q.y, viz + z0, tuple(fwd), tuple(side), hf, hs, h, (*col_, 0.0))
        bx(-10, 0, -2, 62, 70, 10, WHITE)                       # lower terrace and stairs
        bx(-20, 0, 8, 48, 62, 10, WHITE)                        # the Altar of the Fatherland terrace
        bx(-6, 0, 8, 6, 14, 14, (0.90, 0.88, 0.82))             # the altar with the statue of Roma
        bx(-40, 0, 18, 26, 66, 22, WHITE)                       # main body
        for k in range(17):                                     # the curved portico of 16 columns
            a = math.radians(-46 + 92 * k / 16)
            off = Vector((math.cos(a) * 34 - 70, math.sin(a) * 58))
            q = Vector((vix, viy)) + fwd * (off.x + 24) + side * off.y
            p.box(q.x, q.y, viz + 40, tuple(fwd), tuple(side), 1.2, 1.2, 15, (*WHITE, 0.0))
        bx(-44, 0, 55, 18, 60, 4, WHITE)                        # entablature
        for sd in (-1, 1):                                      # the two propylaea and their quadrigas
            bx(-42, sd * 58, 40, 12, 10, 30, WHITE)
            bx(-42, sd * 58, 70, 6, 5, 6, BRONZE)
            bx(-42, sd * 58, 76, 2, 4, 5, BRONZE)
        bx(-8, 0, 22, 4, 4, 12, BRONZE)                         # the equestrian statue of Victor Emmanuel II
    mon("Vittoriano", 1885, 99999, vittoriano, 26)
    marks["vittoriano"] = (vix, viy, viz + 85)

    # the new St Peter's: nave and facade (1506-1626), Michelangelo's dome (1547-1590), 136 m to the cross
    spx, spy, spz = at((12.4534, 41.9022))
    def stpeters_body(p):
        p.box(spx + 20, spy, spz, (1, 0), (0, 1), 105, 75, 45, (*TRAVERTINE, 0.5), top=((0.55, 0.52, 0.48, 0.0)))
        p.box(spx + 120, spy, spz, (1, 0), (0, 1), 12, 58, 48, (*TRAVERTINE, 0.5), top=((0.55, 0.52, 0.48, 0.0)))
    def stpeters_dome(p):
        N.extrude(p, ring(spx - 10, spy, 30, 30, 32), spz + 45, 28, TRAVERTINE, 0.0, roof=TRAVERTINE)
        for k in range(9):
            a = math.pi * 0.5 * k / 8
            rr = 29 * math.cos(a)
            N.extrude(p, ring(spx - 10, spy, max(rr, 4), max(rr, 4), 32), spz + 73 + 40 * math.sin(a), 4.2,
                      (0.52, 0.56, 0.58), 0.0, roof=(0.52, 0.56, 0.58))
        N.extrude(p, ring(spx - 10, spy, 5, 5, 12), spz + 115, 14, TRAVERTINE, 0.0, roof=(0.85, 0.72, 0.35))
        p.box(spx - 10, spy, spz + 129, (1, 0), (0, 1), 0.6, 0.6, 7, (0.85, 0.72, 0.35, 0.0))
    mon("StPetersBody", 1506, 99999, stpeters_body, 100)
    mon("StPetersDome", 1547, 99999, stpeters_dome, 43)

    # walls
    serv = N.Partsc()
    wall_ring(serv, [tuple(P2(p)) for p in SERVIAN], z, 4.0, 9.0, (*STONE, 0.0))
    animated.append({"ob": serv.to_object("ServianWall", painted, col), "year": -378, "grow": 6, "gone": 300, "fade": 150})
    aur = N.Partsc()
    wall_ring(aur, [tuple(P2(p)) for p in AURELIAN], z, 4.0, 11.0, (*BRICK, 0.0), tower_every=30.0, tower=(4.0, 5.0))
    animated.append({"ob": aur.to_object("AurelianWall", painted, col), "year": 271, "grow": 4, "gone": None})
    marks["aurelian"] = (*tuple(P2((12.5015, 41.9093))), 25)

    # aqueduct arches (Aqua Claudia, 52 AD), broken in 537
    aq = N.Partsc()
    a0, a1 = P2((12.5300, 41.8780)), P2((12.5155, 41.8915))
    d = a1 - a0
    for k in range(int(d.length / 7)):
        p = a0 + d * (k / max(1, int(d.length / 7)))
        aq.box(p.x, p.y, z(p.x, p.y), tuple(d.normalized()), (-d.normalized().y, d.normalized().x), 1.4, 2.2, 26,
               (*TRAVERTINE, 0.0))
    aq.box((a0.x + a1.x) / 2, (a0.y + a1.y) / 2, z(a0.x, a0.y) + 26, tuple(d.normalized()),
           (-d.normalized().y, d.normalized().x), d.length / 2, 2.4, 3, (*TRAVERTINE, 0.0))
    animated.append({"ob": aq.to_object("AquaClaudia", painted, col), "year": 38, "grow": 14, "gone": None})

    # road mask: generated houses are never put on a street or walkway
    RC = 5.0
    roadcells = set()
    for _n, w_, flat_ in city.data.get("roads", []):
        rp = [(flat_[i], flat_[i + 1]) for i in range(0, len(flat_), 2)]
        rr_ = int((w_ / 2) // RC) + 1
        for (ax, ay), (bx, by) in zip(rp, rp[1:]):
            n_ = max(1, int(math.hypot(bx - ax, by - ay) / 2.5))
            for k in range(n_ + 1):
                qx, qy = ax + (bx - ax) * k / n_, ay + (by - ay) * k / n_
                ci, cj = int(qx // RC), int(qy // RC)
                for di in range(-rr_ + 1, rr_):
                    for dj in range(-rr_ + 1, rr_):
                        roadcells.add((ci + di, cj + dj))

    for s0, s1, wd_, _a, _b in APPROACH:
        n_ = max(1, int((s1 - s0).length / 2.5))
        for k in range(n_ + 1):
            q = s0 + (s1 - s0) * (k / n_)
            rr_ = int((wd_ / 2) // RC) + 1
            for di in range(-rr_ + 1, rr_):
                for dj in range(-rr_ + 1, rr_):
                    roadcells.add((int(q.x // RC) + di, int(q.y // RC) + dj))

    def off_road(x, y, half):
        k = int(half // RC)
        ci, cj = int(x // RC), int(y // RC)
        return not any((ci + di, cj + dj) in roadcells for di in range(-k, k + 1) for dj in range(-k, k + 1))

    def free_spot(x, y, half):
        for ox, oy in ((0, 0), (7, 0), (-7, 0), (0, 7), (0, -7), (7, 7), (-7, -7), (7, -7), (-7, 7)):
            if off_road(x + ox, y + oy, half):
                return x + ox, y + oy
        return None

    # --- today's buildings (estimated dates) and their medieval predecessors --------
    for b in city.data["buildings"]:
        cx, cy, year, est, h, flat, name = b
        pts = [(flat[i], flat[i + 1]) for i in range(0, len(flat), 2)]
        if not city.is_land(cx, cy):
            continue
        low = name.lower()
        if any((Vector((cx, cy)) - P2((lo, la))).length < r_ * 0.8 for lo, la, r_ in CLEAR) and not name:
            continue                                    # open ground of the Forum, Palatine, Circus and Colosseum
        if "basilica di san pietro" in low or "pantheon" in low:
            continue                                    # modelled separately with their domes
        if (Vector((cx, cy)) - P2(VITTORIANO)).length < 75:
            continue                                    # the Vittoriano is modelled separately
        if sum(0 if city.is_land(px, py) else 1 for px, py in pts) > 0.3 * len(pts):
            continue                                    # nothing stands in the river
        if not name and blocked(cx, cy, year, 99999, 2.0):
            continue                                    # nor inside a monument or across a bridge approach
        zz = z(cx, cy) - 0.5
        grow, start = 3.0, year
        if "giustizia" in low:
            start, grow = 1889, 22.0
        wall = rng.choice(WALL_COLS) if year < 1870 else rng.choice(WALL_COLS + [(0.86, 0.84, 0.78), (0.70, 0.66, 0.60)])
        if name:
            wall = MARBLE
        xs_, ys_ = [q[0] for q in pts], [q[1] for q in pts]
        half_ = max(6.0, 0.5 * max(max(xs_) - min(xs_), max(ys_) - min(ys_)))
        occupy(cx, cy, start, half_)
        mark_building(cx, cy, half_ * 0.8, start, 99999)
        roof = (0.55, 0.22, 0.12)
        bn = damage(cx, cy, start, 99999)
        if bn is None:
            put(("bld", int(start // 2) * 2, int(grow), 99999),
                lambda part, pts=pts, zz=zz, h=h, wall=wall: N.extrude(part, pts, zz, h, wall, 0.55, roof))
        else:
            t_, back = bn["t"], int(bn["t"] + bn["rebuild"] * dr.uniform(0.8, 1.6))
            put(("bld", int(start // 2) * 2, int(grow), round(t_, 3)),
                lambda part, pts=pts, zz=zz, h=h, wall=wall: N.extrude(part, pts, zz, h, wall, 0.55, roof))
            put(("shell", round(t_, 3), back),
                lambda part, pts=pts, zz=zz, h=h: N.extrude(part, pts, zz, max(3.0, h * bn["ruin"] * dr.uniform(0.5, 1.3)),
                                                            CHAR[:3], 0.0, roof=CHAR[:3]))
            put(("bld", back, 3, 99999),
                lambda part, pts=pts, zz=zz, h=h, wall=wall: N.extrude(part, pts, zz, h, wall, 0.55, roof))
        zn = city.zone(cx, cy)
        if zn in ("abitato", "trastevere", "borgo") and year > 1350 and rng.random() < 0.7:
            m0 = rng.uniform(950, 1350)
            occupy(cx, cy, m0, 6.0)
            yaw = rng.uniform(-0.3, 0.3)
            place("med", m0, year, cx, cy, zz + 0.5, (math.cos(yaw), math.sin(yaw)), (-math.sin(yaw), math.cos(yaw)),
                  rng.uniform(8, 12), rng.uniform(6, 9), rng.uniform(9, 13), rng.choice(WALL_COLS), TILE,
                  extra={"roof_h": 2.6})

    # the open ground of the Forum, Palatine, Circus, Colosseum valley etc. is paved, not wooded
    for lo, la, r_ in CLEAR:
        q = P2((lo, la))
        u0 = city.eras(q.x, q.y)[0]
        k = int(r_ // OCC)
        for di in range(-k, k + 1):
            for dj in range(-k, k + 1):
                if di * di + dj * dj <= k * k:
                    occupy(q.x + di * OCC, q.y + dj * OCC, max(u0, -600), 1.0, house=False)

    # --- generated fabric: Iron Age huts, Republic houses, Imperial insulae, farm villas ----
    fr = random.Random(brief["seed"] + 3)
    skipped = [0]
    VILLAGES = [P2(v) for v in brief.get("village_sites", [])]
    step_ = 34.0
    yy = city.y0
    while yy < city.y0 + ny * res:
        xx = city.x0
        while xx < city.x0 + nx * res:
            px_, py_ = xx + fr.uniform(-8, 8), yy + fr.uniform(-8, 8)
            xx += step_
            if not all(city.is_land(px_ + ox, py_ + oy) for ox, oy in ((0, 0), (16, 0), (-16, 0), (0, 16), (0, -16))):
                continue                                          # never in or at the edge of the river
            if any((Vector((px_, py_)) - P2((lo, la))).length < r_ for lo, la, r_ in CLEAR):
                continue
            spot = free_spot(px_, py_, 6.0)
            if spot is None:
                skipped[0] += 1
                continue
            px_, py_ = spot
            zn = city.zone(px_, py_)
            u, ab, re_, _f = city.eras(px_, py_)
            zz = z(px_, py_)
            yaw = fr.uniform(-0.3, 0.3)
            ux, uy = (math.cos(yaw), math.sin(yaw)), (-math.sin(yaw), math.cos(yaw))
            near_v = min([(Vector((px_, py_)) - v).length for v in VILLAGES] + [1e9])
            if near_v < 260 and fr.random() < 0.5:                 # Iron Age hut villages on the hills
                v0 = fr.uniform(-1000, -800) if near_v < 150 else fr.uniform(-800, -650)
                v1 = max(u, v0 + 80) + fr.uniform(0, 60)
                occupy(px_, py_, v0, 5.0)
                place("vil", v0, v1, px_, py_, zz, ux, uy, fr.uniform(6, 8), fr.uniform(4.5, 6), fr.uniform(4, 5),
                      (0.45, 0.33, 0.20), THATCH, extra={"detail": False, "hip": True})
            if zn in ("outside", "prati", "vatican"):
                if fr.random() < 0.035 and Vector((px_, py_)).length > 1800:     # villas and farmhouses in the countryside
                    f0 = fr.uniform(-250, 150)
                    f1 = fr.uniform(450, 700)
                    occupy(px_, py_, f0, 10.0)
                    place("rom", f0, f1, px_, py_, zz, ux, uy, fr.uniform(18, 26), fr.uniform(14, 20), fr.uniform(6.5, 8.5),
                          rng.choice(WALL_COLS), TILE, extra={"hip": True, "roof_h": 2.6, "eave": 0.7})
                    if fr.random() < 0.5:                                         # a medieval casale on the same spot
                        c0 = fr.uniform(1100, 1500)
                        place("med", c0, max(c0 + 40, u), px_, py_, zz, ux, uy, fr.uniform(12, 16), fr.uniform(9, 12),
                              fr.uniform(8, 12), rng.choice(WALL_COLS), TILE, extra={"roof_h": 2.6})
                continue
            if u < 50 and fr.random() < 0.75:                                    # Republic houses (domus)
                a0 = u + fr.uniform(5, 80)
                a1 = fr.uniform(-60, 64.2) if fr.random() < 0.4 else fr.uniform(64.2, 200)
                if a1 > a0 + 10:
                    occupy(px_, py_, a0, 8.0)
                    place("rep", a0, a1, px_, py_, zz, ux, uy, fr.uniform(12, 18), fr.uniform(10, 15), fr.uniform(6.5, 9),
                          rng.choice(WALL_COLS), TILE, extra={"hip": True, "roof_h": 2.4, "eave": 0.7})
            i0 = max(-50, u) + fr.uniform(2, 120)                                 # Imperial insulae
            i1 = (ab if ab < 9000 else fr.uniform(500, 900)) + fr.uniform(0, 250)
            if i1 > i0 + 20 and fr.random() < 0.8:
                occupy(px_, py_, i0, 8.0)
                place("imp", i0, i1, px_, py_, zz, ux, uy, fr.uniform(18, 26), fr.uniform(14, 20), fr.uniform(11, 20),
                      rng.choice(WALL_COLS), TILE, extra={"hip": True, "roof_h": 3.0, "eave": 0.6})
        yy += step_

    print("[city-studio] generated buildings:", placed, "skipped near streets:", skipped[0], flush=True)

    # medieval towers in the old town (c. 1150-1300), most later demolished
    for k in range(70):
        for _ in range(30):
            px_, py_ = rng.uniform(-1500, 300), rng.uniform(-800, 1500)
            if city.zone(px_, py_) in ("abitato", "trastevere") and off_road(px_, py_, 4.0) and \
                    all(city.is_land(px_ + ox, py_ + oy) for ox, oy in ((0, 0), (12, 0), (-12, 0), (0, 12), (0, -12))):
                break
        t0 = rng.uniform(1150, 1300)
        t1 = rng.uniform(1400, 1900) if rng.random() < 0.85 else 99999
        occupy(px_, py_, t0, 4.0)
        place("tow", t0, t1, px_, py_, z(px_, py_), (1, 0), (0, 1), 7, 7, rng.uniform(28, 45), (0.62, 0.42, 0.28),
              (0.5, 0.3, 0.2), shape="box")

    # objects from bins
    for key, part in bins.items():
        ob = part.to_object("_".join(str(k) for k in key), facade if key[0] in ("bld", "imp") else painted, col)
        kind = key[0]
        if kind == "bld":
            animated.append({"ob": ob, "year": key[1], "grow": max(2.0, key[2]),
                             "gone": None if key[3] >= 99999 else key[3], "fade": 0.004})
        elif kind.endswith("_b"):                       # burnt or bombed: vanish at the moment of the fire
            animated.append({"ob": ob, "year": key[1], "grow": 3.0, "gone": key[2], "fade": 0.004})
        elif kind == "shell":                           # blackened ruins until rebuilt
            animated.append({"ob": ob, "year": key[1], "grow": 0.0, "gone": key[2], "fade": 2.0})
        elif kind in ("med", "rep", "imp", "tow", "rom", "geo", "vil", "edo", "sam", "mei"):
            animated.append({"ob": ob, "year": key[1], "grow": 3.0, "gone": key[2] + 12.5, "fade": 15.0})

    # streets from the map data, appearing as each district is built up
    sb = {}
    for name, w, flat in city.data.get("roads", []):
        pts = [Vector((flat[i], flat[i + 1])) for i in range(0, len(flat), 2)]
        for a, b in zip(pts, pts[1:]):
            m = (a + b) / 2
            if not (DATA_X[0] < m.x < DATA_X[1] and DATA_Y[0] < m.y < DATA_Y[1]) or not city.is_land(m.x, m.y):
                continue
            d = b - a
            if d.length < 1.0:
                continue
            u_, ab_, re_, _f = city.eras(m.x, m.y)
            if u_ > 2030:
                continue
            yr = u_ + 5
            spans = [(yr, ab_)] if ab_ < 9000 else [(yr, 99999)]
            if ab_ < 9000 and re_ < 9000:
                spans.append((re_ + 3, 99999))
            nrm = Vector((-d.y, d.x)).normalized() * (w / 2)
            zz = z(m.x, m.y) + 0.35
            for s0, s1 in spans:
                sb.setdefault((int(s0 // 10) * 10, int(s1 // 25) * 25 if s1 < 9000 else 99999), N.Partsc()).add(
                    [(*(a - nrm), zz), (*(b - nrm), zz), (*(b + nrm), zz), (*(a + nrm), zz)], [(0, 1, 2, 3)],
                    [(0.56, 0.52, 0.46, 0.0) if s0 < 1850 else (0.40, 0.40, 0.42, 0.0)])
            steps = max(1, int(d.length / OCC))
            for k in range(steps + 1):
                q = a + d * (k / steps)
                occupy(q.x, q.y, yr, w / 2, house=False)
    for (yr, g_), part in sb.items():
        animated.append({"ob": part.to_object("streets_%d_%d" % (yr, g_), painted, col), "year": yr, "grow": 0.0,
                         "gone": None if g_ >= 99999 else g_, "fade": 30.0})

    # trees: a dense forest on every piece of open land. A tree stays until a
    # building or street is put under its crown; abandoned land grows back.
    tb = {}
    tr = random.Random(9)
    sp_in, sp_out = brief.get("tree_spacing", 15.0), brief.get("tree_spacing_outer", 21.0)

    def first_built(x_, y_, r):
        return min(occupied.get((int((x_ + ox) // OCC), int((y_ + oy) // OCC)), 99999)
                   for ox, oy in ((0, 0), (r * 0.7, 0), (-r * 0.7, 0), (0, r * 0.7), (0, -r * 0.7)))

    n_trees = 0
    gy_ = city.y0
    while gy_ < city.y0 + ny * res:
        inner_row = DATA_Y[0] < gy_ < DATA_Y[1]
        gx_ = city.x0
        while gx_ < city.x0 + nx * res:
            inner = inner_row and DATA_X[0] < gx_ < DATA_X[1]
            step = sp_in if inner else sp_out
            x_, y_ = gx_ + tr.uniform(-0.35, 0.35) * step, gy_ + tr.uniform(-0.35, 0.35) * step
            gx_ += step
            if not city.is_land(x_, y_):
                continue
            r = tr.uniform(6.0, 8.5) if inner else tr.uniform(8.5, 11.5)
            fy_ = city.fill(x_, y_)
            since = fy_ + 12 if fy_ else 0
            u, ab, re_, farm = city.eras(x_, y_)
            gone = first_built(x_, y_, r)
            if since >= gone:
                continue
            back = ab + tr.uniform(20, 200) if ab < 9000 else 99999      # trees return in the abandoned city
            back_gone = re_ if back < 9000 else 99999
            pt = (x_, y_, z(x_, y_), r, tr.uniform(0, 6.283), tr.randrange(5))
            town = u + 4 if (inner and u < 9000) else 99999         # the wild wood thins once a district is settled
            if town < gone and town > since:
                tb.setdefault(("t", int(since // 10) * 10 if since else -3000, int(town // 10) * 10), []).append(pt)
                if tr.random() < 0.45:
                    small = (x_, y_, pt[2], r * tr.uniform(0.40, 0.52), pt[4], tr.choice(TOWN_TREES))
                    tb.setdefault(("t", int(town // 10) * 10, int(gone // 10) * 10), []).append(small)
            else:
                tb.setdefault(("t", int(since // 10) * 10 if since else -3000, int(gone // 10) * 10), []).append(pt)
            n_trees += 1
            if back < 9000:
                tb.setdefault(("t", int(back // 50) * 50, int(back_gone // 50) * 50), []).append(pt)
        gy_ += sp_in if inner_row else sp_out
    print("[city-studio] forest trees:", n_trees, flush=True)

    # garden trees: planted around each house a few years after it is built
    import greenery
    gr = random.Random(brief["seed"] + 77)
    for gx, gy, gr_r, g0, g1 in greenery.garden_trees(plots, occupied, OCC, city.is_land, gr,
                                                      limit=brief.get("garden_trees", 110000)):
        if not off_road(gx, gy, 2.0):
            continue                                   # not on the street
        tb.setdefault(("t", int(g0 // 10) * 10, int(g1 // 25) * 25), []).append(
            (gx, gy, z(gx, gy), gr_r * 1.15, gr.uniform(0, 6.283), gr.choice(TOWN_TREES)))
    make_forest = tree_instancer(tree_mat, col, ROME_TREES)
    for key, pts_ in tb.items():
        ob = make_forest("trees_%d_%d" % key[1:], pts_)
        animated.append({"ob": ob, "year": key[1], "grow": 0.0, "gone": key[2], "fade": 20.0})

    # people, armies and vehicles from the brief
    # the street network from the map: marchers and traffic follow real streets
    import heapq
    nodes, adj = {}, {}

    def nid(x_, y_):
        key = (round(x_ * 0.5), round(y_ * 0.5))           # ends within 2 m are the same junction
        if key not in nodes:
            nodes[key] = (x_, y_)
        return key
    for _n, w_, flat_ in city.data.get("roads", []) + [("", a_[2], [a_[0].x, a_[0].y, a_[1].x, a_[1].y]) for a_ in APPROACH]:
        rp = [(flat_[i], flat_[i + 1]) for i in range(0, len(flat_), 2)]
        for (ax, ay), (bx, by) in zip(rp, rp[1:]):
            ka, kb = nid(ax, ay), nid(bx, by)
            d_ = math.hypot(bx - ax, by - ay)
            adj.setdefault(ka, []).append((kb, d_))
            adj.setdefault(kb, []).append((ka, d_))
    keys_ = list(adj)
    karr = np.array([nodes[k_] for k_ in keys_]) if keys_ else np.zeros((0, 2))

    def nearest(q):
        i_ = int(np.argmin(((karr - np.array(q)) ** 2).sum(1)))
        return keys_[i_]

    def route(a_, b_):
        if not keys_:
            return [a_, b_]
        s0, s1 = nearest(a_), nearest(b_)
        dist_, prev = {s0: 0.0}, {}
        heap = [(0.0, s0)]
        while heap:
            d_, k_ = heapq.heappop(heap)
            if k_ == s1:
                break
            if d_ > dist_.get(k_, 1e18) or d_ > 4000:
                continue
            for k2, w2 in adj.get(k_, ()):
                nd = d_ + w2
                if nd < dist_.get(k2, 1e18):
                    dist_[k2], prev[k2] = nd, k_
                    heapq.heappush(heap, (nd, k2))
        if s1 not in dist_:
            return [a_, b_]
        out_, k_ = [], s1
        while k_ != s0:
            out_.append(nodes[k_])
            k_ = prev[k_]
        out_.append(nodes[s0])
        out_.reverse()
        return [a_] + out_ + [b_] if (Vector(a_) - Vector(out_[0])).length > 3 else out_ + [b_]

    def plen(pp):
        return sum((Vector(b_) - Vector(a_)).length for a_, b_ in zip(pp, pp[1:]))

    WATERBORNE = ("boat", "barge", "longship", "riverboat", "blackship")
    groups = []
    for k, spec in enumerate(brief.get("groups", [])):
        sp = dict(spec)
        sp["path"] = [tuple(P2(p)) for p in spec["path"]]
        if len(sp["path"]) >= 2 and sp.get("speed", 0) > 0 and sp["kind"] not in WATERBORNE:
            routed = [sp["path"][0]]
            for a_, b_ in zip(sp["path"], sp["path"][1:]):
                routed += route(a_, b_)[1:]
            if not sp.get("loop") and plen(routed) > 320:     # keep the last 320 m before the goal
                keep, acc = [routed[-1]], 0.0
                for a_, b_ in zip(routed[::-1], routed[-2::-1]):
                    seg_ = (Vector(a_) - Vector(b_)).length
                    if acc + seg_ >= 320:
                        f_ = (320 - acc) / seg_
                        keep.append(tuple(Vector(a_) + (Vector(b_) - Vector(a_)) * f_))
                        break
                    keep.append(b_)
                    acc += seg_
                routed = keep[::-1]
            if sp.get("formation") == "block":            # a column as wide as the street it marches along
                sp["width"] = min(sp.get("width", 8), 7.2)
                L_ = plen(routed)
                sp["speed"] = round(L_ / max(1.0, (sp["to"] - sp["from"]) * 0.9), 2)
            elif not sp.get("loop"):
                sp["speed"] = round(plen(routed) / max(1.0, (sp["to"] - sp["from"]) * 0.95), 2)
            sp["path"] = routed
        yr_ = H.year_at(brief, (sp["from"] + sp["to"]) / 2)
        groups.append(P.make_group(sp, z, painted, col, brief["seed"] + 100 + k,
                                   free=lambda x_, y_, yr_=yr_: free_ground(x_, y_, yr_)))

    # the she-wolf (legend) at the Lupercal on the Palatine slope
    wx, wy, wz = at((12.4835, 41.8893))
    wolf = P.Mesh()
    grey = (0.45, 0.40, 0.34)
    for dx in (-0.55, 0.55):
        for dy in (-0.2, 0.2):
            wolf.box(wx + dx, wy + dy, wz, 0.07, 0.07, 0.55, grey)
    wolf.box(wx, wy, wz + 0.55, 0.8, 0.25, 0.4, grey)
    wolf.box(wx + 0.95, wy, wz + 0.85, 0.22, 0.15, 0.25, grey)
    wolf.box(wx + 1.2, wy, wz + 0.85, 0.12, 0.08, 0.12, grey)
    for dx in (-0.2, 0.15):
        wolf.box(wx + dx, wy + 0.45, wz, 0.15, 0.10, 0.18, (0.85, 0.66, 0.52))
    wob = P.finish(wolf, "SheWolf", painted, col)
    animated.append({"ob": wob, "year": -770, "grow": 0.0, "gone": -750, "fade": 0.5})
    marks["shewolf"] = (wx, wy, wz + 3)

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
        sz = e.get("size", 0.75)
        wind = Vector((0.55, 0.25))
        for _ in range(max(4, e.get("blobs", 45) // 4)):          # thin plumes rising and leaning downwind
            r = frng.uniform(0.1, 0.9) * e["radius"]
            a = frng.uniform(0, 2 * math.pi)
            q = Vector((math.cos(a), math.sin(a))) * r
            hgt = frng.uniform(60, 140) * sz
            for k in range(10):
                f_ = k / 9.0
                rr = (2.5 + 9.0 * f_) * sz * frng.uniform(0.8, 1.2)
                zz = z0 + 6 + hgt * f_
                d_ = q + wind * hgt * f_ * f_ * 0.8
                if e["kind"] == "fire":
                    sc = (0.05 + 0.12 * f_, 0.045 + 0.115 * f_, 0.04 + 0.11 * f_)
                else:
                    sc = (0.34 + 0.12 * f_, 0.32 + 0.12 * f_, 0.30 + 0.11 * f_)
                blobs.add([(d_.x + vx * rr, d_.y + vy * rr, zz + vz * rr * 0.8) for vx, vy, vz in fx_v], fx_f,
                          [sc] * len(fx_f))
        smoke = blobs.to_object("smoke", painted, col)
        smoke.location = (c.x, c.y, 0)
        smoke.data.polygons.foreach_set("use_smooth", [True] * len(smoke.data.polygons))
        flames = None
        if e["kind"] == "fire":
            fl = H.Parts()
            hits = next((bn.get("hits", []) for bn in burns if bn["e"] is e), [])
            frng.shuffle(hits)
            spots = [Vector(h_) for h_ in hits[:e.get("flames", 320)]]
            while len(spots) < min(60, e.get("flames", 320)):
                r = frng.uniform(0, 1.0) ** 0.7 * e["radius"]
                a = frng.uniform(0, 2 * math.pi)
                spots.append(c + Vector((math.cos(a), math.sin(a))) * r)
            for q in spots:                       # tongues of flame rising from each burning building
                for _ in range(3):
                    ox, oy = frng.uniform(-4, 4), frng.uniform(-4, 4)
                    rr = frng.uniform(1.2, 2.6)
                    hh = frng.uniform(5, 13)
                    zz = z(q.x + ox, q.y + oy) + frng.uniform(2, 7)
                    ang0 = frng.uniform(0, 6.28)
                    v = [(q.x + ox + math.cos(ang0 + k * 1.2566) * rr, q.y + oy + math.sin(ang0 + k * 1.2566) * rr, zz)
                         for k in range(5)] + [(q.x + ox + frng.uniform(-1, 1), q.y + oy + frng.uniform(-1, 1), zz + hh)]
                    fl.add(v, [(k, (k + 1) % 5, 5) for k in range(5)], [(1, 0.5, 0.1)] * 5)
            flames = fl.to_object("flames", emit, col)
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
        if y < -753:
            return "—"
        return y + 754 if y < 0 else y + 753

    def ground(x, y):
        return max(z(x, y), 0.3)

    # height map of tall buildings (with the year they appear) for camera clearance
    cell = 40.0
    tall = {}
    for b in city.data["buildings"]:
        cx, cy, year, est, h, flat, name = b
        if h < 30:
            continue
        for dx in (-2, -1, 0, 1, 2):
            for dy in (-2, -1, 0, 1, 2):
                k = (int(cx // cell) + dx, int(cy // cell) + dy)
                tall.setdefault(k, []).append((year, h))
    for extra in ((12.4524, 41.9022, 1547, 140), (12.4922, 41.8902, 72, 50), (12.4828, 41.8946, 1885, 82),
                  (12.4768, 41.8986, 126, 45), (12.4663, 41.9031, 139, 50), (12.4843, 41.8958, 112, 40)):
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
