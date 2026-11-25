"""Tokyo style ("style": "tokyo" in a brief), built on the London machinery.

Tokyo has no open register of construction dates, so this style mixes:
  * today's buildings from Overture Maps / OpenStreetMap, with dates ESTIMATED
    from their district (see tokyo_prepare.py);
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

LAT0, LON0 = 35.6852, 139.7528
KX = 111320.0 * math.cos(math.radians(LAT0))
KY = 111132.0


def proj(lon, lat):
    return Vector(((lon - LON0) * KX, (lat - LAT0) * KY))


def P2(lonlat):
    return proj(lonlat[0], lonlat[1])


CASTLE_KEEP = (139.7530, 35.6880)
SENSOJI = (139.7967, 35.7148)
ZOJOJI = (139.7480, 35.6574)
KANEIJI = (139.7745, 35.7180)
TOKYO_TOWER = (139.7454, 35.6586)
SKYTREE = (139.8107, 35.7101)
DATA_X, DATA_Y = (-5800.0, 6800.0), (-5800.0, 4800.0)
CLEAR = [(139.7530, 35.6880, 120), (139.7967, 35.7148, 70), (139.7480, 35.6574, 70), (139.7745, 35.7180, 70),
         (139.7454, 35.6586, 70), (139.8107, 35.7101, 70), (139.7505, 35.6840, 90), (139.7745, 35.6838, 25),
         (139.7930, 35.6940, 30), (139.7671, 35.6812, 80), (139.7450, 35.6758, 70), (139.6993, 35.6764, 350)]


class Tokyo:
    def __init__(self, folder):
        with gzip.open(os.path.join(folder, "tokyo.json.gz"), "rt") as f:
            self.data = json.load(f)
        t = np.load(os.path.join(folder, "terrain.npz"))
        self.land, self.elev, self.shore, self.fillg = t["land"], t["elev"], t["shore"], t["fill"]
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

    def fill(self, x, y):
        j, i = self.ij(x, y)
        return int(self.fillg[j, i])

    def is_land(self, x, y, year=99999):
        j, i = self.ij(x, y)
        return bool(self.land[j, i]) and self.fillg[j, i] <= year

    def zone(self, x, y):
        for k in ("castle", "asakusa", "shitamachi", "yamanote", "west"):
            if inside((x, y), self.zones[k]):
                return k
        return "outside"

    def in_fire(self, x, y):
        return False

    def eras(self, x, y, rng=None):
        """(urban_at, abandon_at, reurban_at, farm_at)."""
        zn = self.zone(x, y)
        f = self.fill(x, y)
        d = (Vector((x, y)) - P2(CASTLE_KEEP)).length
        never = 99999
        farm = 0
        if zn == "asakusa":
            u = 1150
        elif zn == "castle":
            u = 1457
        elif zn == "shitamachi":
            u = 1600 + d * 0.02
        elif zn == "yamanote":
            u = 1620 + d * 0.025
        elif zn == "west":
            u = 1890 + d * 0.004
        elif d < 4600:
            u = 1640 + d * 0.02                          # the rest of Edo's townsmen and samurai quarters
        else:
            u = 1870 + max(0.0, d - 3000) * 0.012
        u = max(u, f + 3)
        return u, never, never, max(f + 2, u - 35)       # fields appear only shortly before a district is built


from trees import add_tree, tree_instancer, TREE_KINDS  # noqa: E402,F401


def inside(pt, poly):
    x, y = pt
    res = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            res = not res
    return res


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
KAWARA = (0.20, 0.22, 0.26)                       # dark grey clay roof tiles
THATCH = (0.52, 0.44, 0.26)
PLASTER = [(0.92, 0.90, 0.84), (0.86, 0.82, 0.74), (0.80, 0.74, 0.62)]
WOOD = [(0.42, 0.30, 0.20), (0.50, 0.38, 0.26), (0.34, 0.24, 0.16), (0.58, 0.46, 0.32)]
CONCRETE = [(0.78, 0.77, 0.74), (0.70, 0.70, 0.70), (0.84, 0.82, 0.78), (0.62, 0.64, 0.66)]
GLASS = [(0.30, 0.42, 0.55), (0.40, 0.52, 0.62), (0.22, 0.30, 0.40)]
VERMILION = (0.78, 0.20, 0.12)


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
    city = Tokyo(os.path.join(root, brief.get("data", "data/tokyo")))
    rng = random.Random(brief["seed"])
    for k in N.MOOD:
        N.MOOD[k].clear()
    H.HAZE_NODES.clear()
    H.HAZE_DISTANCE = brief.get("haze_distance", 60000.0)
    H.HAZE_AMOUNT = brief.get("haze_amount", 0.18)
    if brief.get("haze_color"):
        H.HAZE = tuple(brief["haze_color"])
    H.HOUSE_DETAIL = True                       # windows, doors and overhanging tiled roofs
    painted = N.painted_nyc("PaintedTokyo")
    tree_mat = N.painted_nyc("TreesTokyo", trees=True)
    facade, night = N.facade_material()
    tmat, now = terrain_material()
    arch_mat = arcade_material()
    N.WATER_MAT.clear()
    N.WATER_MAT.append(N.shore_water_material(((0.10, 0.24, 0.24), (0.03, 0.09, 0.11), (0.012, 0.035, 0.05)), realistic=True))
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
    fg = city.fillg.reshape(-1)
    fill_faces = {}
    old_faces = []
    for f in faces:
        fy_ = max(int(fg[k]) for k in f)
        if fy_ > 0:
            fill_faces.setdefault(int(fy_ // 10) * 10, []).append(f)
        else:
            old_faces.append(f)
    for fy_, ff in fill_faces.items():                  # reclaimed land rises out of the bay in its era
        used = sorted({k for f in ff for k in f})
        remap = {k: n for n, k in enumerate(used)}
        fm = bpy.data.meshes.new("fill_%d" % fy_)
        fm.from_pydata([verts[k] for k in used], [], [tuple(remap[k] for k in f) for f in ff])
        fm.polygons.foreach_set("use_smooth", [True] * len(fm.polygons))
        for name, data in (("era", era), ("era2", era2)):
            a_ = fm.color_attributes.new(name, "FLOAT_COLOR", "POINT")
            a_.data.foreach_set("color", [c for k in used for c in data[k]])
        fm.materials.append(tmat)
        fob = bpy.data.objects.new(fm.name, fm)
        col.objects.link(fob)
        animated.append({"ob": fob, "year": fy_, "grow": 0.0, "fill": True})
    faces_all = faces
    faces = old_faces
    me = bpy.data.meshes.new("TokyoTerrain")
    me.from_pydata(verts, [], faces)
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    for name, data in (("era", era), ("era2", era2)):
        a_ = me.color_attributes.new(name, "FLOAT_COLOR", "POINT")
        a_.data.foreach_set("color", [c for v in data for c in v])
    me.materials.append(tmat)
    col.objects.link(bpy.data.objects.new("RomeTerrain", me))
    wfaces = [f for f in faces_all if any((not city.land[k // nx, k % nx]) or fg[k] > 0 for k in f)]
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
    H.principled(gnt).inputs["Base Color"].default_value = (0.08, 0.20, 0.06, 1)
    H.add_haze(gm)
    sea.materials.append(gm)
    g_ob = bpy.data.objects.new("FarGround", sea)
    g_ob.location.z = -1.0
    col.objects.link(g_ob)
    bay = bpy.data.meshes.new("Bay")                     # Tokyo Bay beyond the detailed area
    bx0, by0 = city.x0, city.y0
    bx1 = city.x0 + nx * res
    bay.from_pydata([(-2000, by0 + 2, 0.3), (40000, by0 + 2, 0.3), (40000, -40000, 0.3), (-2000, -40000, 0.3),
                     (bx1 - 2, -2000, 0.3), (40000, -2000, 0.3)], [], [(0, 1, 2, 3), (4, 5, 1, 0)])
    bay.materials.append(N.WATER_MAT[0])
    col.objects.link(bpy.data.objects.new("Bay", bay))

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

    def tiered(p, cx, cy, cz, w0, d0, tiers, tier_h, wall, roof, shrink=0.78, yaw=0.0, base=0.0):
        """Japanese tiered building (castle keep, pagoda): stacked storeys with flared roofs."""
        ux, uy = (math.cos(yaw), math.sin(yaw)), (-math.sin(yaw), math.cos(yaw))
        if base > 0:
            p.box(cx, cy, cz, ux, uy, w0 / 2 + 6, d0 / 2 + 6, base, (*STONE, 0.0))
        zc = cz + base
        w, d = w0, d0
        for k in range(tiers):
            p.box(cx, cy, zc, ux, uy, w / 2, d / 2, tier_h, (*wall, 0.0))
            p.house({"x": cx, "y": cy, "ux": ux, "uy": uy, "d": w + 3.5, "w": d + 3.5, "h": tier_h * 0.75,
                     "wall": roof, "roof": roof, "hip": True}, zc + tier_h * 0.75)
            zc += tier_h
            w, d = w * shrink, d * shrink
        return zc

    def temple_hall(p, cx, cy, cz, w, d, h, yaw=0.0, wall=VERMILION, roof=KAWARA):
        ux, uy = (math.cos(yaw), math.sin(yaw)), (-math.sin(yaw), math.cos(yaw))
        p.box(cx, cy, cz, ux, uy, w / 2 + 3, d / 2 + 3, 1.5, (*STONE, 0.0))
        p.box(cx, cy, cz + 1.5, ux, uy, w / 2, d / 2, h * 0.45, (*wall, 0.0))
        p.house({"x": cx, "y": cy, "ux": ux, "uy": uy, "d": w + 8, "w": d + 8, "h": h * 0.55, "wall": roof,
                 "roof": roof, "hip": True}, cz + 1.5 + h * 0.45 - 1.0)

    def gate(p, cx, cy, cz, w, h, yaw=0.0, col_=VERMILION):
        ux, uy = (math.cos(yaw), math.sin(yaw)), (-math.sin(yaw), math.cos(yaw))
        for sd in (-1, 1):
            q = Vector((cx, cy)) + Vector(ux) * sd * w / 2
            p.box(q.x, q.y, cz, ux, uy, 0.8, 0.8, h, (*col_, 0.0))
        p.box(cx, cy, cz + h, ux, uy, w / 2 + 2.5, 1.4, 1.2, (*col_, 0.0))
        p.box(cx, cy, cz + h - 2.2, ux, uy, w / 2 + 0.5, 0.6, 0.8, (*col_, 0.0))

    def lattice_tower(p, cx, cy, cz, height, base_half, colours, deck=None):
        """Tokyo Tower style lattice tower, painted in bands."""
        def half(zz_):
            return base_half * math.exp(-zz_ / (height * 0.26)) + 1.2
        yaw_e = math.radians(-20)
        ue, ve = (math.cos(yaw_e), math.sin(yaw_e)), (-math.sin(yaw_e), math.cos(yaw_e))
        step = height / 48.0
        zz_ = 0.0
        k = 0
        while zz_ < height * 0.82:
            s0 = half(zz_)
            c_ = colours[(k // 4) % len(colours)]
            for sx in (-1, 1):
                for sy in (-1, 1):
                    q = Vector((cx, cy)) + Vector(ue) * sx * s0 + Vector(ve) * sy * s0
                    w_ = 3.4 if zz_ < height * 0.2 else (2.0 if zz_ < height * 0.45 else 1.3)
                    p.box(q.x, q.y, cz + zz_, ue, ve, w_, w_, step + 0.3, (*c_, 0.0))
            zz_ += step
            k += 1
        for zp in (deck or ()):
            sz = half(zp) + 4
            p.box(cx, cy, cz + zp, ue, ve, sz, sz, 6, (0.92, 0.90, 0.86, 0.0))
        p.box(cx, cy, cz + height * 0.82, ue, ve, 1.6, 1.6, height * 0.18, (*colours[0], 0.0))

    # Senso-ji (628, rebuilt many times; destroyed 1945, rebuilt 1958 and 1973)
    sx_, sy_, sz_ = at(SENSOJI)
    def sensoji(p):
        temple_hall(p, sx_, sy_ + 30, sz_, 34, 26, 30)
        pg = Vector((sx_ - 40, sy_ - 5))
        tiered(p, pg.x, pg.y, sz_, 9, 9, 5, 9.5, VERMILION, KAWARA, shrink=0.9, base=1.5)
        gate(p, sx_, sy_ - 90, sz_, 12, 11)                                   # Kaminarimon
        temple_hall(p, sx_, sy_ - 35, sz_, 22, 10, 18)                       # Hozomon
    mon("SensojiEarly", 645, 1945.19, lambda p: temple_hall(p, sx_, sy_ + 30, sz_, 24, 18, 22), 8)
    mon("Sensoji", 1649, 1945.19, sensoji, 3)
    mon("SensojiRebuilt", 1958, 99999, sensoji, 15)
    marks["sensoji"] = (sx_, sy_ + 30, sz_ + 40)
    marks["pagoda"] = (sx_ - 40, sy_ - 5, sz_ + 55)

    # Edo Castle: Ota Dokan's fort (1457), the Tokugawa keep (1607-1657), walls and the Imperial Palace (1888)
    cx_, cy_, cz_ = at(CASTLE_KEEP)
    def dokan(p):
        p.box(cx_, cy_, cz_, (1, 0), (0, 1), 45, 35, 3, (*STONE, 0.0))
        p.house({"x": cx_, "y": cy_, "ux": (1, 0), "uy": (0, 1), "d": 26, "w": 14, "h": 10, "wall": WOOD[0],
                 "roof": THATCH}, cz_ + 3)
        wall_ring(p, [(cx_ - 55, cy_ - 45), (cx_ + 55, cy_ - 45), (cx_ + 55, cy_ + 45), (cx_ - 55, cy_ + 45)], z, 1.2,
                  4.0, (*WOOD[1], 0.0))
    mon("DokanCastle", 1457, 1600, dokan, 4)
    def keep(p):
        tiered(p, cx_, cy_, cz_, 40, 34, 5, 11.0, (0.96, 0.95, 0.92), (0.32, 0.36, 0.38), shrink=0.84, base=12)
    mon("CastleKeep", 1607, 1657.1, keep, 30)
    def castle_walls(p):
        for rx, ry in ((180, 150), (320, 260)):
            wall_ring(p, [(cx_ - rx, cy_ - ry), (cx_ + rx, cy_ - ry), (cx_ + rx, cy_ + ry), (cx_ - rx, cy_ + ry)], z,
                      7.0, 9.0, (*STONE, 0.0), tower_every=120.0, tower=(6.0, 6.0))
        for qx, qy in ((cx_ + 180, cy_ - 150), (cx_ - 180, cy_ + 150), (cx_ + 180, cy_ + 150)):
            tiered(p, qx, qy, z(qx, qy) + 9, 14, 10, 3, 6.0, (0.96, 0.95, 0.92), (0.32, 0.36, 0.38), shrink=0.85)
    mon("CastleWalls", 1606, 99999, castle_walls, 30)
    def palace(p):
        for dx, dy, w_, d_ in ((0, -20, 90, 40), (-60, 40, 50, 30), (60, 40, 50, 30)):
            temple_hall(p, cx_ + dx, cy_ + dy, cz_, w_, d_, 16, wall=(0.86, 0.84, 0.78), roof=(0.32, 0.40, 0.38))
    mon("ImperialPalace", 1888, 99999, palace, 4)
    marks["castle"] = (cx_, cy_, cz_ + 75)
    marks["palace"] = (cx_, cy_, cz_ + 30)

    # Zojo-ji (1598) and Kan'ei-ji in Ueno (1625; burned in the 1868 battle)
    zx_, zy_, zz_ = at(ZOJOJI)
    mon("Zojoji", 1598, 99999, lambda p: (temple_hall(p, zx_, zy_, zz_, 36, 28, 28),
                                          gate(p, zx_, zy_ - 80, zz_, 16, 14)), 5)
    marks["zojoji"] = (zx_, zy_, zz_ + 36)
    kx_, ky_, kz_ = at(KANEIJI)
    mon("Kaneiji", 1625, 1868.51, lambda p: (temple_hall(p, kx_, ky_, kz_, 40, 30, 30),
                                             tiered(p, kx_ + 70, ky_ + 20, kz_, 9, 9, 5, 9, VERMILION, KAWARA, shrink=0.9)), 10)
    mon("UenoPagoda", 1639, 99999, lambda p: tiered(p, kx_ + 70, ky_ + 20, kz_, 9, 9, 5, 9, VERMILION, KAWARA, shrink=0.9), 1)
    marks["kaneiji"] = (kx_, ky_, kz_ + 40)

    # Bridges: Nihonbashi (1603), Ryogoku (1659), Kachidoki (1940), Rainbow Bridge (1993)
    mon("Nihonbashi", 1603, 1911, lambda p: bridge(p, (139.7745, 35.6845), (139.7745, 35.6830), 4, 8,
                                                    (*WOOD[0], 0.0), arches=False), 2, foot=False)
    mon("NihonbashiStone", 1911, 99999, lambda p: bridge(p, (139.7745, 35.6845), (139.7745, 35.6830), 4, 27,
                                                          (*STONE, 0.0)), 2, foot=False)
    marks["nihonbashi"] = (*tuple(P2((139.7745, 35.6838))), 10)
    approach((139.7745, 35.6845), (139.7745, 35.6830), 8, 1603, 99999)
    approach((139.7860, 35.6935), (139.7960, 35.6942), 10, 1659, 99999)
    for (b0_, b1_), part in approach_parts.items():
        animated.append({"ob": part.to_object("bridge_roads_%d" % b0_, painted, col), "year": b0_, "grow": 0.0,
                         "gone": None if b1_ >= 99999 else b1_, "fade": 3.0})
    mon("Ryogoku", 1659, 1932, lambda p: bridge(p, (139.7860, 35.6935), (139.7960, 35.6942), 5, 8,
                                                 (*WOOD[1], 0.0), arches=False), 2, foot=False)
    mon("RyogokuSteel", 1932, 99999, lambda p: bridge(p, (139.7860, 35.6935), (139.7960, 35.6942), 7, 24,
                                                       (0.35, 0.55, 0.45, 0.0)), 2, foot=False)
    marks["ryogoku"] = (*tuple(P2((139.7910, 35.6938))), 12)
    def rainbow(p):
        a, b = fit_span(P2((139.7600, 35.6430)), P2((139.7690, 35.6340)))
        d = b - a
        u = d.normalized()
        v = Vector((-u.y, u.x))
        p.box((a.x + b.x) / 2, (a.y + b.y) / 2, 52, tuple(u), tuple(v), d.length / 2, 15, 3, (0.92, 0.92, 0.90, 0.0))
        for f in (0.3, 0.7):
            q = a + d * f
            for sd in (-1, 1):
                qq = q + v * sd * 12
                p.box(qq.x, qq.y, -3, tuple(u), tuple(v), 3, 3, 126, (0.94, 0.94, 0.92, 0.0))
    mon("RainbowBridge", 1993, 99999, rainbow, 3, foot=False)
    marks["rainbow"] = (*tuple(P2((139.7645, 35.6385))), 130)

    # Tokyo Station (1914), the National Diet (1936), Tokyo Tower (1958), Tokyo Skytree (2012)
    tx_, ty_, tz_ = at((139.7671, 35.6812))
    def station(p):
        yaw = math.radians(-20)
        ux, uy = (math.cos(yaw), math.sin(yaw)), (-math.sin(yaw), math.cos(yaw))
        p.box(tx_, ty_, tz_, uy, ux, 160, 12, 18, (0.66, 0.30, 0.20, 0.6), top=(0.30, 0.32, 0.34, 0.0))
        for f in (-1, 0, 1):
            q = Vector((tx_, ty_)) + Vector(uy) * f * 120
            N.extrude(p, ring(q.x, q.y, 11, 11, 12), tz_ + 18, 8, (0.30, 0.32, 0.34), 0.0, roof=(0.30, 0.32, 0.34))
    mon("TokyoStation", 1914, 99999, station, 6)
    marks["station"] = (tx_, ty_, tz_ + 34)
    dx_, dy_, dz_ = at((139.7450, 35.6758))
    mon("Diet", 1920, 99999, lambda p: (p.box(dx_, dy_, dz_, (1, 0), (0, 1), 103, 45, 21, (0.88, 0.84, 0.76, 0.6)),
                                        tiered(p, dx_, dy_, dz_ + 21, 28, 28, 3, 14, (0.88, 0.84, 0.76), (0.80, 0.76, 0.68),
                                               shrink=0.75)), 16)
    marks["diet"] = (dx_, dy_, dz_ + 70)
    ox_, oy_, oz_ = at(TOKYO_TOWER)
    mon("TokyoTower", 1957.5, 99999, lambda p: lattice_tower(p, ox_, oy_, oz_, 333, 42,
                                                             [(0.92, 0.30, 0.12), (0.95, 0.95, 0.94)], deck=(150, 250)), 1.3)
    marks["tokyotower"] = (ox_, oy_, oz_ + 300)
    kx2, ky2, kz2 = at(SKYTREE)
    def skytree(p):
        steps = 60
        for k in range(steps):
            z0_ = 634 * k / steps
            r_ = 34 * (1 - k / steps) ** 1.3 + 6
            N.extrude(p, ring(kx2, ky2, r_, r_, 10), kz2 + z0_, 634 / steps + 0.3, (0.88, 0.90, 0.94), 0.0,
                      roof=(0.88, 0.90, 0.94))
        for zp, rr in ((350, 22), (450, 16)):
            N.extrude(p, ring(kx2, ky2, rr, rr, 20), kz2 + zp, 14, (0.40, 0.48, 0.56), 0.0, roof=(0.85, 0.87, 0.90))
    mon("Skytree", 2008.6, 99999, skytree, 3.5)
    marks["skytree"] = (kx2, ky2, kz2 + 560)

    # Meiji Shrine (1920) in its planted forest
    mx_, my_, mz_ = at((139.6993, 35.6764))
    mon("MeijiShrine", 1920, 99999, lambda p: (temple_hall(p, mx_, my_, mz_, 30, 22, 18, wall=(0.55, 0.42, 0.28),
                                                           roof=(0.30, 0.42, 0.36)),
                                               gate(p, mx_, my_ - 200, z(mx_, my_ - 200), 18, 12, col_=(0.50, 0.40, 0.30))), 4)
    marks["meiji"] = (mx_, my_, mz_ + 26)

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
        zz = z(cx, cy) - 0.5
        grow = 3.0
        start = year
        low = name.lower()
        if any((Vector((cx, cy)) - P2((lo, la))).length < r_ * 0.8 for lo, la, r_ in CLEAR):
            continue                                    # the castle, temples and towers are modelled separately
        if h > 60:
            wall = rng.choice(GLASS + CONCRETE[:2])
        elif year < 1945:
            wall = rng.choice(BRICKS[:2] + CONCRETE)
        else:
            wall = rng.choice(CONCRETE + PLASTER + GLASS[:1])
        win = 0.6
        if sum(0 if city.is_land(px, py) else 1 for px, py in pts) > 0.3 * len(pts):
            continue                                    # nothing stands in the river or the bay
        if not name and blocked(cx, cy, year, 99999, 2.0):
            continue                                    # nor inside a monument or across a bridge approach
        xs_, ys_ = [q[0] for q in pts], [q[1] for q in pts]
        half_ = max(6.0, 0.5 * max(max(xs_) - min(xs_), max(ys_) - min(ys_)))
        occupy(cx, cy, start, half_)
        mark_building(cx, cy, half_ * 0.8, start, 99999)
        bn = damage(cx, cy, start, 99999)
        if bn is None:
            put(("bld", int(start // 2) * 2, int(grow), 99999),
                lambda part, pts=pts, zz=zz, h=h, wall=wall, win=win: N.extrude(part, pts, zz, h, wall, win, (0.40, 0.42, 0.44)))
        else:
            t_, back = bn["t"], int(bn["t"] + bn["rebuild"] * dr.uniform(0.8, 1.6))
            put(("bld", int(start // 2) * 2, int(grow), round(t_, 3)),
                lambda part, pts=pts, zz=zz, h=h, wall=wall, win=win: N.extrude(part, pts, zz, h, wall, win, (0.40, 0.42, 0.44)))
            put(("shell", round(t_, 3), back),
                lambda part, pts=pts, zz=zz, h=h: N.extrude(part, pts, zz, max(3.0, h * bn["ruin"] * dr.uniform(0.5, 1.3)),
                                                            CHAR[:3], 0.0, roof=CHAR[:3]))
            put(("bld", back, 3, 99999),
                lambda part, pts=pts, zz=zz, h=h, wall=wall, win=win: N.extrude(part, pts, zz, h, wall, win, (0.40, 0.42, 0.44)))
        zn = city.zone(cx, cy)
        if False:
            m0 = 0
            put(("med", int(m0 // 25) * 25, int(year // 25) * 25),
                lambda part, cx=cx, cy=cy, zz=zz: part.house({"x": cx, "y": cy, "ux": (1, 0), "uy": (0, 1),
                                                               "d": rng.uniform(8, 12), "w": rng.uniform(6, 9),
                                                               "h": rng.uniform(9, 13), "wall": rng.choice(H.WALLS),
                                                               "roof": TILE}, zz))

    # --- historic fabric: farm villages, Edo townhouses and samurai estates, Meiji and Showa houses ----
    step_ = 28.0
    fr = random.Random(brief["seed"] + 3)
    VILLAGES = [P2(v) for v in brief.get("village_sites", [])]
    yy = city.y0
    while yy < city.y0 + ny * res:
        xx = city.x0
        while xx < city.x0 + nx * res:
            px_, py_ = xx + fr.uniform(-7, 7), yy + fr.uniform(-7, 7)
            xx += step_
            if not all(city.is_land(px_ + ox, py_ + oy) for ox, oy in ((0, 0), (10, 0), (-10, 0), (0, 10), (0, -10))):
                continue
            if any((Vector((px_, py_)) - P2((lo, la))).length < r_ for lo, la, r_ in CLEAR):
                continue
            spot = free_spot(px_, py_, 6.0)
            if spot is None:
                continue
            px_, py_ = spot
            zn = city.zone(px_, py_)
            beyond = not (DATA_X[0] < px_ < DATA_X[1] and DATA_Y[0] < py_ < DATA_Y[1])
            fy = city.fill(px_, py_)
            u, ab, re_, _f = city.eras(px_, py_)
            zz = z(px_, py_)
            yaw = fr.uniform(-0.35, 0.35)
            ux, uy = (math.cos(yaw), math.sin(yaw)), (-math.sin(yaw), math.cos(yaw))
            near_v = min([(Vector((px_, py_)) - v).length for v in VILLAGES] + [1e9])
            if near_v < 420 and fy == 0 and fr.random() < 0.45:        # thatched farm villages (minka)
                v0 = fr.uniform(600, 1100) if near_v < 250 else fr.uniform(1100, 1500)
                v1 = max(u + fr.uniform(0, 40), v0 + 60)
                occupy(px_, py_, v0, 7.0)
                place("vil", v0, v1, px_, py_, zz, ux, uy, fr.uniform(9, 13), fr.uniform(6, 9), fr.uniform(5, 7),
                      fr.choice(WOOD), THATCH, extra={"detail": False})
            if (zn in ("shitamachi", "asakusa", "castle") or (u < 1860 and zn != "yamanote")) and u < 1900:   # Edo townhouses
                m0 = max(u, fy + 3) + fr.uniform(0, 60)
                m1 = fr.uniform(1880, 1923.7) if fr.random() < 0.6 else fr.uniform(1923.7, 1945.3)
                if m1 > m0 + 5:
                    occupy(px_, py_, m0, 7.0)
                    place("edo", m0, m1, px_, py_, zz, ux, uy, fr.uniform(9, 13), fr.uniform(5, 7), fr.uniform(6.5, 9),
                          fr.choice(WOOD + PLASTER[:1]), KAWARA)
            if (zn == "yamanote" or (u < 1860 and fr.random() < 0.3)) and u < 1870 and fr.random() < 0.55 \
                    and off_road(px_, py_, 9.0):   # samurai estates
                m0 = u + fr.uniform(0, 80)
                m1 = fr.uniform(1870, 1920)
                occupy(px_, py_, m0, 9.0)
                place("sam", m0, m1, px_, py_, zz, ux, uy, fr.uniform(14, 20), fr.uniform(10, 14), fr.uniform(6, 8),
                      fr.choice(PLASTER), KAWARA)
            g0 = max(u, 1870, fy + 3) + fr.uniform(0, 50)
            if g0 < 1960 and (fr.random() < (0.5 if beyond else 0.7)):    # Meiji, Taisho and Showa houses
                g1 = 99999 if beyond else fr.uniform(max(g0 + 20, 1950), 2015)
                occupy(px_, py_, g0, 8.0)
                place("mei", g0, g1, px_, py_, zz, ux, uy, fr.uniform(10, 14), fr.uniform(7, 10), fr.uniform(6.5, 9.5),
                      fr.choice(WOOD + PLASTER), fr.choice([KAWARA, (0.32, 0.30, 0.30), (0.45, 0.20, 0.15)]))
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
                occupy(q.x, q.y, yr, w / 2, house=False)
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
    make_forest = tree_instancer(tree_mat, col)
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
        return "—" if y < 1457 else y - 1457

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
    for extra in ((139.7454, 35.6586, 1957, 350), (139.8107, 35.7101, 2008, 650), (139.7530, 35.6880, 1606, 90),
                  (139.7450, 35.6758, 1930, 75)):
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
