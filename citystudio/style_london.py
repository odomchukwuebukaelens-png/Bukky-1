"""London style ("style": "london" in a brief), built on the Rome machinery.

London has no open register of construction dates, so this style mixes:
  * today's buildings from Overture Maps / OpenStreetMap, with dates ESTIMATED
    from their district (see london_prepare.py);
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
from trees import tree_instancer

LAT0, LON0 = 51.5133, -0.0890
KX = 111320.0 * math.cos(math.radians(LAT0))
KY = 111132.0


def proj(lon, lat):
    return Vector(((lon - LON0) * KX, (lat - LAT0) * KY))


def P2(lonlat):
    return proj(lonlat[0], lonlat[1])


LONDON_TREES = [("broad", 0.85), ("broad", 1.0), ("broad", 1.15), ("broad", 0.95), ("con", 0.9)]   # oak, ash, elm, beech, yew
LONDON_BRIDGE = ((-0.0877, 51.5081), (-0.0868, 51.5049))
TOWER = (-0.0760, 51.5081)
STPAULS = (-0.0984, 51.5138)
# area covered by real building data (metres); beyond it the suburbs are generated
DATA_X, DATA_Y = (-5950.0, 5100.0), (-3680.0, 2400.0)
CLEAR = [(-0.0984, 51.5138, 90), (-0.0760, 51.5081, 140), (-0.1275, 51.4994, 80), (-0.1246, 51.4995, 110),
         (-0.0855, 51.5132, 70), (-0.0920, 51.5156, 45), (-0.0865, 51.5045, 45), (-0.0803, 51.5145, 30),
         (-0.0972, 51.5081, 25)]


def inside(pt, poly):
    x, y = pt
    res = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            res = not res
    return res


class London:
    def __init__(self, folder):
        with gzip.open(os.path.join(folder, "london.json.gz"), "rt") as f:
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

    def is_land(self, x, y, year=99999):
        j, i = self.ij(x, y)
        return bool(self.land[j, i])

    def fill(self, x, y):
        return 0

    def zone(self, x, y):
        for k in ("city", "southwark", "westminster", "strand", "westend"):
            if inside((x, y), self.zones[k]):
                return k
        return "outside"

    def in_fire(self, x, y):
        return inside((x, y), self.zones["fire"])

    def eras(self, x, y, rng=None):
        """(urban_at, abandon_at, reurban_at, farm_at)."""
        zn = self.zone(x, y)
        d = Vector((x, y)).length
        never = 99999
        if zn == "city":
            return 50 + d * 0.01, 420, 886 + d * 0.05, 70 + d * 0.02
        if zn == "southwark":
            return 70, 420, 1000 + d * 0.03, 70 + d * 0.02
        if zn == "strand":
            return 650, 890, 1550 + d * 0.02, 70 + d * 0.02
        if zn == "westminster":
            return 1050, never, never, 70 + d * 0.02
        if zn == "westend":
            return 1660 + max(0.0, -x - 2500) * 0.04, never, never, 70 + d * 0.02
        return min(1930.0, 1760 + d * 0.025), never, never, 70 + d * 0.02


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
    city = London(os.path.join(root, brief.get("data", "data/london")))
    rng = random.Random(brief["seed"])
    for k in N.MOOD:
        N.MOOD[k].clear()
    H.HAZE_NODES.clear()
    H.HAZE_DISTANCE = brief.get("haze_distance", 60000.0)
    H.HAZE_AMOUNT = brief.get("haze_amount", 0.18)
    if brief.get("haze_color"):
        H.HAZE = tuple(brief["haze_color"])
    H.HOUSE_DETAIL = True                       # windows, doors, chimneys and overhanging roofs
    painted = N.painted_nyc("PaintedLondon")
    tree_mat = N.painted_nyc("TreesLondon", trees=True)
    facade, night = N.facade_material()
    tmat, now = terrain_material()
    arch_mat = arcade_material()
    N.WATER_MAT.clear()
    N.WATER_MAT.append(N.shore_water_material(((0.17, 0.19, 0.13), (0.06, 0.08, 0.05), (0.03, 0.045, 0.03)), realistic=True))  # the brown-green Thames
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

    OCC = 12.0
    occupied = {}
    plots = []

    def occupy(x, y, year, radius=8.0, house=True):
        if house:
            plots.append((x, y, year, radius))
        r = int(radius // OCC) + 1
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
        burns.append({"e": e, "c": P2(e["ll"]), "r": e["radius"], "t": e["from"] + 0.6 * (e["to"] - e["from"]),
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

    def place(kind, start, end, x, y, zz, ux, uy, d, w, h, wall, roof, shape="house", bucket=25, extra=None):
        """A generated building that may burn or be bombed during its life."""
        if blocked(x, y, start, end, max(d, w) / 2):
            return                                     # never inside a monument or across a bridge approach
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

    # Roman Londinium: wooden bridge, forum, amphitheatre, the wall
    mon("RomanBridge", 52, 420, lambda p: bridge(p, LONDON_BRIDGE[0], LONDON_BRIDGE[1], 5, 7, (0.40, 0.30, 0.20, 0.0)), 2, foot=False)
    fx_, fy_, fz_ = at((-0.0855, 51.5132))
    mon("Forum", 80, 300, lambda p: (p.box(fx_, fy_, fz_, (1, 0), (0, 1), 85, 25, 24, (*STONE, 0.3), top=(*TILE, 0.0)),
                                     p.box(fx_, fy_ - 60, fz_, (1, 0), (0, 1), 85, 4, 9, (*STONE, 0.0)),
                                     p.box(fx_ - 85, fy_ - 30, fz_, (1, 0), (0, 1), 4, 30, 9, (*STONE, 0.0)),
                                     p.box(fx_ + 85, fy_ - 30, fz_, (1, 0), (0, 1), 4, 30, 9, (*STONE, 0.0))), 5)
    marks["forum"] = (fx_, fy_, fz_ + 32)
    ax_, ay_, az_ = at((-0.0920, 51.5156))
    def amph(p):
        n = 40
        for k in range(n):
            a = 2 * math.pi * k / n
            x_, y_ = ax_ + 33 * math.cos(a), ay_ + 27 * math.sin(a)
            ang = math.atan2(27 * math.cos(a), -33 * math.sin(a))
            p.box(x_, y_, az_, (math.cos(ang), math.sin(ang)), (-math.sin(ang), math.cos(ang)), 2.8, 5, 9, (*STONE, 0.0))
    mon("Amphitheatre", 70, 350, amph, 4)
    marks["amphitheatre"] = (ax_, ay_, az_ + 15)
    wall_r = N.Partsc()
    wall_ring(wall_r, city.zones["city"], z, 3.0, 8.0, (*STONE, 0.0), tower_every=60.0, tower=(3.5, 4.0))
    animated.append({"ob": wall_r.to_object("LondonWall", painted, col), "year": 200, "grow": 6, "gone": 1790, "fade": 60})
    marks["wall"] = (*tuple(P2((-0.0880, 51.5185))), 14)

    # Old London Bridge with houses (1209-1831), then a plain stone bridge
    mon("OldLondonBridge", 1209, 1831, lambda p: bridge(p, LONDON_BRIDGE[0], LONDON_BRIDGE[1], 6, 16, (*STONE, 0.0), houses=True), 6, foot=False)
    mon("LondonBridge1831", 1831, 99999, lambda p: bridge(p, (-0.0880, 51.5082), (-0.0871, 51.5049), 9, 20, (0.72, 0.70, 0.64, 0.0)), 3, foot=False)
    # every bridge end continues straight into the city as a road; nothing is built across it
    APPROACH = []                                       # (start, end, width, from, to)
    approach_parts = {}

    def approach(a_ll, b_ll, wd, b0_, b1_):
        e0, e1 = fit_span(P2(a_ll), P2(b_ll))
        u_ = (e1 - e0).normalized()
        for s0, s1 in ((e0 - u_ * 150, e0 + u_ * 6), (e1 - u_ * 6, e1 + u_ * 150)):
            seg = []
            for k in range(31):
                q = s0 + (s1 - s0) * (k / 30)
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
                         [(0.44, 0.41, 0.35, 0.0) if b0_ < 1850 else (0.31, 0.31, 0.33, 0.0)])
            register([tuple(seg[0] - nrm), tuple(seg[0] + nrm), tuple(seg[-1] - nrm), tuple(seg[-1] + nrm)], b0_ - 1, b1_)

    crossings = []                                      # streets that cross the river today
    for _n, w_, flat_ in city.data.get("roads", []):
        rp = [Vector((flat_[i], flat_[i + 1])) for i in range(0, len(flat_), 2)]
        for a_, b_ in zip(rp, rp[1:]):
            m_ = (a_ + b_) / 2
            if (b_ - a_).length > 4 and not city.is_land(m_.x, m_.y):
                crossings.append((m_, (b_ - a_).normalized()))
    inv = lambda p: (LON0 + p.x / KX, LAT0 + p.y / KY)  # noqa: E731

    def across(ll):
        """Two points either side of the river: along today's crossing street if there is one,
        otherwise along the shortest way over the water."""
        q = P2(ll)
        if crossings:
            m_, u_ = min(crossings, key=lambda c_: (c_[0] - q).length)
            if (m_ - q).length < 160:
                return inv(m_ - u_ * 40), inv(m_ + u_ * 40)
        best = None
        for k in range(18):
            a = math.pi * k / 18
            u_ = Vector((math.cos(a), math.sin(a)))
            span = 0.0
            for sg in (-1, 1):
                t = 0.0
                while t < 500 and not city.is_land(q.x + u_.x * sg * t, q.y + u_.y * sg * t):
                    t += 4.0
                span += t
            if best is None or span < best[0]:
                best = (span, u_)
        u_ = best[1]
        return inv(q - u_ * 40), inv(q + u_ * 40)

    THAMES_BRIDGES = [  # name, (lon, lat), built, gone, deck, width, colour, arches
        ("WestminsterOld", (-0.1218, 51.5008), 1750, 1862, 9, 13, STONE, True),
        ("Westminster", (-0.1218, 51.5008), 1862, 99999, 9, 26, (0.30, 0.45, 0.35), True),
        ("BlackfriarsOld", (-0.1043, 51.5096), 1769, 1869, 9, 13, STONE, True),
        ("Blackfriars", (-0.1043, 51.5096), 1869, 99999, 9, 32, (0.55, 0.20, 0.18), True),
        ("WaterlooOld", (-0.1166, 51.5085), 1817, 1937, 9, 13, (0.70, 0.68, 0.62), True),
        ("Waterloo", (-0.1166, 51.5085), 1945, 99999, 9, 24, (0.80, 0.78, 0.72), True),
        ("SouthwarkOld", (-0.0943, 51.5082), 1819, 1919, 9, 12, (0.32, 0.30, 0.30), True),
        ("Southwark", (-0.0943, 51.5082), 1921, 99999, 9, 17, (0.45, 0.55, 0.45), True),
        ("Lambeth", (-0.1222, 51.4945), 1862, 99999, 9, 18, (0.60, 0.20, 0.18), True),
        ("Millennium", (-0.0985, 51.5095), 2000, 99999, 8, 4, (0.85, 0.86, 0.88), False),
    ]
    for nm_, ll_, b0_, b1_, deck, wd, colr, arch in THAMES_BRIDGES:
        a_, b_ = across(ll_)
        mon(nm_, b0_, b1_, lambda p, a_=a_, b_=b_, deck=deck, wd=wd, colr=colr, arch=arch:
            bridge(p, a_, b_, deck, wd, (*colr, 0.0), arches=arch), 3, foot=False)
        approach(a_, b_, max(8, wd * 0.6), b0_, b1_)
    approach(LONDON_BRIDGE[0], LONDON_BRIDGE[1], 10, 52, 99999)
    for (b0_, b1_), part in approach_parts.items():
        animated.append({"ob": part.to_object("bridge_roads_%d" % b0_, painted, col), "year": b0_, "grow": 0.0,
                         "gone": None if b1_ >= 99999 else b1_, "fade": 3.0})

    marks["bridge"] = (*tuple(P2((-0.0873, 51.5065))), 25)

    # The Tower of London: the White Tower (1078) and its curtain walls
    tx_, ty_, tz_ = at(TOWER)
    def white_tower(p):
        p.box(tx_, ty_, tz_, (1, 0), (0, 1), 18, 16, 27, (*PORTLAND, 0.3))
        for sx in (-1, 1):
            for sy in (-1, 1):
                p.box(tx_ + sx * 17, ty_ + sy * 15, tz_, (1, 0), (0, 1), 3, 3, 33, (*PORTLAND, 0.0),
                      top=((0.30, 0.32, 0.30, 0.0)))
    mon("WhiteTower", 1078, 99999, white_tower, 20)
    def curtain(p):
        for rx, ry, h in ((70, 62, 11), (100, 92, 9)):
            pts = [(tx_ - rx, ty_ - ry), (tx_ + rx, ty_ - ry), (tx_ + rx, ty_ + ry), (tx_ - rx, ty_ + ry)]
            wall_ring(p, pts, z, 3.0, h, (*STONE, 0.0), tower_every=35.0, tower=(5.0, 5.0))
    mon("TowerWalls", 1240, 99999, curtain, 40)
    marks["tower"] = (tx_, ty_, tz_ + 42)

    # Old St Paul's (1087-1666) with its spire (lost to lightning in 1561)
    sx_, sy_, sz_ = at(STPAULS)
    def old_pauls(p):
        p.box(sx_ - 20, sy_, sz_, (1, 0), (0, 1), 90, 15, 30, (*STONE, 0.3), top=(*SLATE, 0.0))
        p.box(sx_, sy_, sz_, (1, 0), (0, 1), 14, 45, 28, (*STONE, 0.3), top=(*SLATE, 0.0))
        p.box(sx_, sy_, sz_, (1, 0), (0, 1), 13, 13, 70, (*STONE, 0.0))
    mon("OldStPauls", 1087, 1666.73, old_pauls, 200)
    spire = N.Partsc()
    spire.add([(sx_ - 12, sy_ - 12, sz_ + 70), (sx_ + 12, sy_ - 12, sz_ + 70), (sx_ + 12, sy_ + 12, sz_ + 70),
               (sx_ - 12, sy_ + 12, sz_ + 70), (sx_, sy_, sz_ + 149)], [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)],
              [(0.25, 0.25, 0.28, 0.0)] * 4)
    animated.append({"ob": spire.to_object("OldPaulsSpire", painted, col), "year": 1221, "grow": 10, "gone": 1561.4, "fade": 0.3})
    # Wren's St Paul's (1675-1710)
    def new_pauls(p):
        p.box(sx_ - 15, sy_, sz_, (1, 0), (0, 1), 75, 17, 30, (*PORTLAND, 0.5), top=(*SLATE, 0.0))
        p.box(sx_, sy_, sz_, (1, 0), (0, 1), 17, 38, 30, (*PORTLAND, 0.5), top=(*SLATE, 0.0))
        for sd in (-1, 1):
            p.box(sx_ - 85, sy_ + sd * 13, sz_, (1, 0), (0, 1), 6, 6, 64, (*PORTLAND, 0.3))
        N.extrude(p, ring(sx_, sy_, 22, 22, 32), sz_ + 30, 26, PORTLAND, 0.5, roof=PORTLAND)
        prof = [(1.0, 0.0), (0.97, 0.25), (0.88, 0.5), (0.72, 0.72), (0.5, 0.88), (0.25, 0.97), (0.08, 1.0)]
        for (r0, h0), (r1, h1) in zip(prof, prof[1:]):
            N.extrude(p, ring(sx_, sy_, 20 * r0, 20 * r0, 32), sz_ + 56 + 26 * h0, 26 * (h1 - h0) + 0.4,
                      (0.42, 0.44, 0.44), 0.0, roof=(0.42, 0.44, 0.44))
        N.extrude(p, ring(sx_, sy_, 3, 3, 12), sz_ + 82, 16, PORTLAND, 0.0, roof=(0.85, 0.70, 0.25))
        p.box(sx_, sy_, sz_ + 98, (1, 0), (0, 1), 0.9, 0.9, 7, (0.85, 0.70, 0.25, 0.0))
    mon("StPauls", 1675, 99999, new_pauls, 35)
    marks["stpauls"] = (sx_, sy_, sz_ + 112)

    # Westminster Abbey (1245-1269, west towers 1745) and the Palace of Westminster
    wx_, wy_, wz_ = at((-0.1275, 51.4994))
    mon("WestminsterAbbey", 1060, 99999, lambda p: (p.box(wx_, wy_, wz_, (1, 0), (0, 1), 50, 11, 31, (*STONE, 0.3), top=(*SLATE, 0.0)),
                                                    p.box(wx_ + 15, wy_, wz_, (1, 0), (0, 1), 11, 30, 31, (*STONE, 0.3), top=(*SLATE, 0.0))), 25)
    mon("AbbeyTowers", 1745, 99999, lambda p: [p.box(wx_ - 52, wy_ + sd * 8, wz_, (1, 0), (0, 1), 5, 5, 69, (*STONE, 0.0)) for sd in (-1, 1)], 10)
    marks["abbey"] = (wx_, wy_, wz_ + 75)
    px_, py_, pz_ = at((-0.1246, 51.4995))
    mon("OldPalace", 1097, 1834.79, lambda p: (p.box(px_ - 30, py_ + 30, pz_, (1, 0), (0, 1), 40, 12, 28, (*STONE, 0.0), top=(*SLATE, 0.0)),
                                               p.box(px_ + 10, py_ - 10, pz_, (1, 0), (0, 1), 20, 60, 16, (*STONE, 0.3), top=(*SLATE, 0.0))), 10)
    def new_palace(p):
        yaw = math.radians(-15)
        ux, uy = (math.cos(yaw), math.sin(yaw)), (-math.sin(yaw), math.cos(yaw))
        q = Vector((px_, py_)) + Vector(uy) * 40
        p.box(q.x + 10, q.y, pz_, uy, ux, 135, 30, 22, (0.82, 0.74, 0.55, 0.8), top=(*SLATE, 0.0))
        vt = Vector((px_, py_)) - Vector(uy) * 85
        p.box(vt.x + 10, vt.y, pz_, (1, 0), (0, 1), 12, 12, 98, (0.82, 0.74, 0.55, 0.6))
    mon("NewPalace", 1840, 99999, new_palace, 30)
    marks["parliament"] = (px_, py_, pz_ + 105)

    # The Globe Theatre (1599-1644, rebuilt 1997)
    gx_, gy_, gz_ = at((-0.0972, 51.5081))
    globe = lambda p: N.extrude(p, ring(gx_, gy_, 15, 15, 20), gz_, 10, (0.92, 0.88, 0.76), 0.0, roof=(0.65, 0.58, 0.32))  # noqa: E731
    mon("Globe", 1599, 1644, globe, 1)
    mon("GlobeRebuilt", 1997, 99999, globe, 2)
    marks["globe"] = (gx_, gy_, gz_ + 16)

    # Tower Bridge (1886-1894)
    def tower_bridge(p):
        a, b = fit_span(P2((-0.0756, 51.5064)), P2((-0.0749, 51.5045)))
        d = b - a
        u = d.normalized()
        v = Vector((-u.y, u.x))
        for f in (0.36, 0.64):
            q = a + d * f
            p.box(q.x, q.y, -3, tuple(u), tuple(v), 9, 11, 8, (0.62, 0.60, 0.55, 0.0))           # pier
            for sd in (-1, 1):
                leg = q + v * sd * 7
                p.box(leg.x, leg.y, 5, tuple(u), tuple(v), 5, 3.5, 52, (0.80, 0.76, 0.66, 0.7))
                p.add([(leg.x - 5, leg.y - 3.5, 57), (leg.x + 5, leg.y - 3.5, 57), (leg.x + 5, leg.y + 3.5, 57),
                       (leg.x - 5, leg.y + 3.5, 57), (leg.x, leg.y, 66)], [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)],
                      [(0.28, 0.32, 0.36, 0.0)] * 4)
            p.box(q.x, q.y, 34, tuple(u), tuple(v), 5, 7, 14, (0.80, 0.76, 0.66, 0.7))
        q0, q1 = a + d * 0.36, a + d * 0.64
        for sd in (-1, 1):
            m = (q0 + q1) / 2 + v * sd * 4
            p.box(m.x, m.y, 44, tuple(u), tuple(v), (q1 - q0).length / 2, 2.2, 4, (0.25, 0.45, 0.65, 0.0))
        p.box((a.x + b.x) / 2, (a.y + b.y) / 2, 9, tuple(u), tuple(v), d.length / 2, 8, 2.0, (0.30, 0.34, 0.38, 0.0))
    mon("TowerBridge", 1886, 99999, tower_bridge, 8, foot=False)
    marks["towerbridge"] = (*tuple(P2((-0.0753, 51.5055))), 80)

    # The Shard (2012) and 30 St Mary Axe (2004)
    hx_, hy_, hz_ = at((-0.0865, 51.5045))
    def shard(p):
        base = [(hx_ - 32, hy_ - 22), (hx_ + 30, hy_ - 26), (hx_ + 26, hy_ + 26), (hx_ - 30, hy_ + 22)]
        layers = 24
        for k in range(layers):
            f0, f1 = 1 - k / layers, 1 - (k + 1) / layers
            pts = [(hx_ + (x - hx_) * f0, hy_ + (y - hy_) * f0) for x, y in base]
            N.extrude(p, pts, hz_ + 300 * k / layers, 300 / layers + 0.2, (0.62, 0.70, 0.78), 0.0, roof=(0.62, 0.70, 0.78))
    mon("TheShard", 2009, 99999, shard, 3)
    marks["shard"] = (hx_, hy_, hz_ + 315)
    gx2, gy2, gz2 = at((-0.0803, 51.5145))
    def gherkin(p):
        prof = [(0.0, 0.62), (0.15, 0.85), (0.35, 1.0), (0.55, 0.97), (0.72, 0.82), (0.86, 0.6), (0.95, 0.35), (1.0, 0.1)]
        for (h0, r0), (h1, r1) in zip(prof, prof[1:]):
            N.extrude(p, ring(gx2, gy2, 28 * (r0 + r1) / 2, 28 * (r0 + r1) / 2, 28), gz2 + 180 * h0, 180 * (h1 - h0) + 0.3,
                      (0.25, 0.38, 0.45), 0.9, roof=(0.25, 0.38, 0.45))
    mon("Gherkin", 2001, 99999, gherkin, 3)
    marks["gherkin"] = (gx2, gy2, gz2 + 195)

    # road mask: generated houses are never put on a street or walkway
    RC = 5.0
    roadcells = set()
    for _n, w_, flat_ in city.data.get("roads", []):
        rp = [(flat_[i], flat_[i + 1]) for i in range(0, len(flat_), 2)]
        rr_ = int((w_ / 2 + 1.5) // RC) + 1
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
        k = int(half // RC) + 1
        ci, cj = int(x // RC), int(y // RC)
        return not any((ci + di, cj + dj) in roadcells for di in range(-k, k + 1) for dj in range(-k, k + 1))

    def free_spot(x, y, half):
        for ox, oy in ((0, 0), (7, 0), (-7, 0), (0, 7), (0, -7), (7, 7), (-7, -7), (7, -7), (-7, 7)):
            if off_road(x + ox, y + oy, half):
                return x + ox, y + oy
        return None

    # --- today's buildings (estimated dates) and their predecessors --------
    for b in city.data["buildings"]:
        cx, cy, year, est, h, flat, name = b
        pts = [(flat[i], flat[i + 1]) for i in range(0, len(flat), 2)]
        if not city.is_land(cx, cy):
            continue
        if sum(0 if city.is_land(px, py) else 1 for px, py in pts) > 0.3 * len(pts):
            continue                                    # nothing stands in the Thames
        if not name and blocked(cx, cy, year, 99999, 2.0):
            continue                                    # nor inside a monument or across a bridge approach
        zz = z(cx, cy) - 0.5
        grow = 3.0
        start = year
        low = name.lower()
        if any(k in low for k in ("the shard", "30 st mary axe")):
            continue                                    # modelled separately with their real shapes
        if any((Vector((cx, cy)) - P2((lo, la))).length < r_ * 0.8 for lo, la, r_ in CLEAR[:4]):
            continue                                    # St Paul's, the Tower, the Abbey and Palace are modelled
        wall = rng.choice(BRICKS) if year < 1900 else rng.choice(BRICKS + MODERN)
        if name and year < 1950:
            wall = PORTLAND
        win = 0.0 if (name and year < 1800) else 0.55       # old stone landmarks: no office-style window grid
        xs_, ys_ = [q[0] for q in pts], [q[1] for q in pts]
        half_ = max(6.0, 0.5 * max(max(xs_) - min(xs_), max(ys_) - min(ys_)))
        occupy(cx, cy, start, half_)
        mark_building(cx, cy, half_ * 0.8, start, 99999)
        bn = damage(cx, cy, start, 99999)
        if bn is None:
            put(("bld", int(start // 2) * 2, int(grow), 99999),
                lambda part, pts=pts, zz=zz, h=h, wall=wall, win=win: N.extrude(part, pts, zz, h, wall, win, (0.55, 0.22, 0.12)))
        else:
            t_, back = bn["t"], int(bn["t"] + bn["rebuild"] * dr.uniform(0.8, 1.6))
            put(("bld", int(start // 2) * 2, int(grow), round(t_, 3)),
                lambda part, pts=pts, zz=zz, h=h, wall=wall, win=win: N.extrude(part, pts, zz, h, wall, win, (0.55, 0.22, 0.12)))
            put(("shell", round(t_, 3), back),
                lambda part, pts=pts, zz=zz, h=h: N.extrude(part, pts, zz, max(3.0, h * bn["ruin"] * dr.uniform(0.5, 1.3)),
                                                            CHAR[:3], 0.0, roof=CHAR[:3]))
            put(("bld", back, 3, 99999),
                lambda part, pts=pts, zz=zz, h=h, wall=wall, win=win: N.extrude(part, pts, zz, h, wall, win, (0.55, 0.22, 0.12)))
        zn = city.zone(cx, cy)
        if False:
            m0 = 0
            put(("med", int(m0 // 25) * 25, int(year // 25) * 25),
                lambda part, cx=cx, cy=cy, zz=zz: part.house({"x": cx, "y": cy, "ux": (1, 0), "uy": (0, 1),
                                                               "d": rng.uniform(8, 12), "w": rng.uniform(6, 9),
                                                               "h": rng.uniform(9, 13), "wall": rng.choice(H.WALLS),
                                                               "roof": TILE}, zz))

    # --- historic fabric: Roman, medieval timber, post-Fire brick, Georgian ----
    step_ = 40.0
    fr = random.Random(brief["seed"] + 3)
    yy = city.y0
    while yy < city.y0 + ny * res:
        xx = city.x0
        while xx < city.x0 + nx * res:
            px_, py_ = xx + fr.uniform(-8, 8), yy + fr.uniform(-8, 8)
            xx += step_
            if not all(city.is_land(px_ + ox, py_ + oy) for ox, oy in ((0, 0), (12, 0), (-12, 0), (0, 12), (0, -12))):
                continue
            if any((Vector((px_, py_)) - P2((lo, la))).length < r_ for lo, la, r_ in CLEAR):
                continue
            spot = free_spot(px_, py_, 6.0)
            if spot is None:
                continue                                  # houses never stand on a street
            px_, py_ = spot
            zn = city.zone(px_, py_)
            beyond = not (DATA_X[0] < px_ < DATA_X[1] and DATA_Y[0] < py_ < DATA_Y[1])
            if zn == "outside" and fr.random() < (0.35 if beyond else 0.6):
                continue
            u, ab, re_, _f = city.eras(px_, py_)
            zz = z(px_, py_)
            yaw = fr.uniform(-0.3, 0.3)
            ux, uy = (math.cos(yaw), math.sin(yaw)), (-math.sin(yaw), math.cos(yaw))
            if zn in ("city", "southwark"):          # Roman Londinium
                a0, a1 = u + fr.uniform(0, 120), ab + fr.uniform(-30, 20)
                occupy(px_, py_, a0, 9.0)
                place("rom", a0, a1, px_, py_, zz, ux, uy, fr.uniform(10, 16), fr.uniform(7, 11), fr.uniform(5, 8),
                      (0.86, 0.80, 0.66), TILE)
            if zn != "outside":                       # medieval / Tudor timber houses
                m0 = (re_ if re_ < 9000 else u) + fr.uniform(0, 200)
                if m0 < 1680:
                    m1 = 1666.8 if city.in_fire(px_, py_) else fr.uniform(1700, 1880)
                    if m1 > m0 + 5:
                        occupy(px_, py_, m0, 8.0)
                        place("med", m0, m1, px_, py_, zz, ux, uy, fr.uniform(8, 12), fr.uniform(5, 8), fr.uniform(9, 14),
                              fr.choice(TIMBER), fr.choice([(0.32, 0.28, 0.25), (0.50, 0.25, 0.15)]),
                              extra={"chimney": True, "roof_h": 3.4, "frame_col": (0.22, 0.15, 0.10)})
            g0 = 1667.5 + fr.uniform(0, 20) if city.in_fire(px_, py_) else max(u, 1700) + fr.uniform(0, 80)
            if g0 < 1900:                             # brick and stucco terraces
                g1 = 99999 if beyond else fr.uniform(max(g0 + 40, 1860), 2010)
                stucco = zn == "westend" and fr.random() < 0.5
                occupy(px_, py_, g0, 9.0)
                place("geo", g0, g1, px_, py_, zz, ux, uy, fr.uniform(18, 28), fr.uniform(12, 18), fr.uniform(12, 18),
                      (0.92, 0.90, 0.84) if stucco else fr.choice(BRICKS[:3]), SLATE, shape="box", bucket=10)
        yy += step_

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
        elif kind in ("med", "rep", "imp", "tow", "rom", "geo"):
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
            yr = max((re_ if (ab_ < 9000 and re_ < 9000) else u_) + 5, 900 + m.length * 0.04)
            if yr > 2030:
                continue
            nrm = Vector((-d.y, d.x)).normalized() * (w / 2)
            zz = z(m.x, m.y) + 0.35
            sb.setdefault(int(yr // 10) * 10, N.Partsc()).add(
                [(*(a - nrm), zz), (*(b - nrm), zz), (*(b + nrm), zz), (*(a + nrm), zz)], [(0, 1, 2, 3)],
                [(0.44, 0.41, 0.35, 0.0) if yr < 1850 else (0.31, 0.31, 0.33, 0.0)])
            steps = max(1, int(d.length / OCC))
            for k in range(steps + 1):
                q = a + d * (k / steps)
                occupy(q.x, q.y, yr, w / 2 + 2, house=False)
    for yr, part in sb.items():
        animated.append({"ob": part.to_object("streets_%d" % yr, painted, col), "year": yr, "grow": 0.0, "gone": None})

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
                    small = (x_, y_, pt[2], r * tr.uniform(0.40, 0.52), pt[4], tr.choice((1, 2, 2, 3, 4)))
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
            (gx, gy, z(gx, gy), gr_r * 1.15, gr.uniform(0, 6.283), gr.choice((1, 2, 2, 4))))
    make_forest = tree_instancer(tree_mat, col, LONDON_TREES)
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
        return "—" if y < 47 else y - 47

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
    for extra in ((-0.0865, 51.5045, 2010, 310), (-0.0803, 51.5145, 2002, 180), (-0.0984, 51.5138, 1675, 112)):
        q = P2(extra[:2])
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                tall.setdefault((int(q.x // cell) + dx, int(q.y // cell) + dy), []).append((extra[2], extra[3]))

    def clearance(x, y, year):
        hs = [h for yr, h in tall.get((int(x // cell), int(y // cell)), ()) if yr <= year + 3]
        return ground(x, y) + (max(hs) + 30.0 if hs else 24.0)      # always above the tree tops

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
