"""Rome style ("style": "rome" in a brief).

Rome has no open register of construction dates, so this style mixes:
  * today's buildings from Overture Maps / OpenStreetMap, with dates ESTIMATED
    from their district (see rome_prepare.py);
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
PALATINE = (12.4875, 41.8895)


def inside(pt, poly):
    x, y = pt
    res = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            res = not res
    return res


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

    def is_land(self, x, y):
        j, i = self.ij(x, y)
        return bool(self.land[j, i])

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
            urban = -650 + d_forum * 0.25
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
        farm = -700 if Vector((x, y)).length < 6000 else -500
        if zn == "vatican":
            urban = 330
        return urban, abandon, reurban, farm


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
    town = H.mix_rgb(nt, tex(0.06), (0.52, 0.44, 0.32), (0.45, 0.38, 0.28))
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
    painted = N.painted_nyc("PaintedRome")
    tree_mat = N.painted_nyc("TreesRome", trees=True)
    facade, night = N.facade_material()
    tmat, now = terrain_material()
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
        if "san pietro" in low:
            start, grow = 1506, 110.0
        elif "giustizia" in low:
            start, grow = 1889, 22.0
        wall = rng.choice(WALL_COLS) if year < 1870 else rng.choice(WALL_COLS + [(0.86, 0.84, 0.78), (0.70, 0.66, 0.60)])
        key = ("bld", int(start // 2) * 2, int(grow))
        put(key, lambda part, pts=pts, zz=zz, h=h, wall=wall: N.extrude(part, pts, zz, h, wall, 0.55, (0.55, 0.22, 0.12)))
        zn = city.zone(cx, cy)
        if zn in ("abitato", "trastevere", "borgo") and year > 1350 and rng.random() < 0.7:
            m0 = rng.uniform(950, 1350)
            put(("med", int(m0 // 25) * 25, int(year // 25) * 25),
                lambda part, cx=cx, cy=cy, zz=zz: part.house({"x": cx, "y": cy, "ux": (1, 0), "uy": (0, 1),
                                                               "d": rng.uniform(8, 12), "w": rng.uniform(6, 9),
                                                               "h": rng.uniform(9, 13), "wall": rng.choice(H.WALLS),
                                                               "roof": TILE}, zz))

    # --- ancient fabric: Republic houses and Imperial insulae --------------
    x0, y0 = -2600.0, -2600.0
    step_ = 42.0
    yy = y0
    while yy < 2400:
        xx = x0
        while xx < 2800:
            px_, py_ = xx + rng.uniform(-10, 10), yy + rng.uniform(-10, 10)
            if city.is_land(px_, py_):
                zn = city.zone(px_, py_)
                if zn != "outside" and zn != "prati" and zn != "vatican":
                    u, ab, re_, _f = city.eras(px_, py_)
                    zz = z(px_, py_)
                    yaw = rng.uniform(-0.25, 0.25)
                    ux, uy = (math.cos(yaw), math.sin(yaw)), (-math.sin(yaw), math.cos(yaw))
                    end_rep = 64 if rng.random() < 0.6 else rng.uniform(-50, 120)
                    if u < 50:
                        a0 = u + rng.uniform(5, 80)
                        put(("rep", int(a0 // 25) * 25, int(end_rep // 25) * 25),
                            lambda part, px_=px_, py_=py_, zz=zz: part.house({"x": px_, "y": py_, "ux": ux, "uy": uy,
                                                                               "d": rng.uniform(12, 18), "w": rng.uniform(10, 15),
                                                                               "h": rng.uniform(6, 9),
                                                                               "wall": rng.choice(WALL_COLS), "roof": TILE}, zz))
                    i0 = max(end_rep, u) + rng.uniform(2, 40)
                    gone = (ab if ab < 9000 else rng.uniform(500, 900)) + rng.uniform(0, 250)
                    hgt = rng.uniform(11, 20)
                    put(("imp", int(i0 // 25) * 25, int(gone // 25) * 25),
                        lambda part, px_=px_, py_=py_, zz=zz, hgt=hgt: part.box(px_, py_, zz, ux, uy, rng.uniform(10, 15), rng.uniform(8, 12), hgt,
                                                                                (*rng.choice(WALL_COLS), 0.45), top=(*TILE, 0.0)))
            xx += step_
        yy += step_

    # medieval towers in the old town (c. 1150-1300), most later demolished
    for k in range(70):
        for _ in range(30):
            px_, py_ = rng.uniform(-1500, 300), rng.uniform(-800, 1500)
            if city.zone(px_, py_) in ("abitato", "trastevere") and city.is_land(px_, py_):
                break
        t0 = rng.uniform(1150, 1300)
        t1 = rng.uniform(1400, 1900) if rng.random() < 0.85 else 99999
        put(("tow", int(t0 // 25) * 25, int(t1 // 25) * 25),
            lambda part, px_=px_, py_=py_: part.box(px_, py_, z(px_, py_), (1, 0), (0, 1), 3.5, 3.5, rng.uniform(28, 45),
                                                    ((0.62, 0.42, 0.28, 0.2)), top=((0.5, 0.3, 0.2, 0.0))))

    # --- monuments ------------------------------------------------------------
    def mon(name, t0, t1, fn, grow=4.0, label=None, ruin=None):
        part = N.Partsc()
        fn(part)
        ob = part.to_object(name, painted, col)
        animated.append({"ob": ob, "year": t0, "grow": grow, "gone": t1, "fade": 3.0})
        if ruin:
            rpart = N.Partsc()
            ruin["fn"](rpart)
            rob = rpart.to_object(name + "_ruin", painted, col)
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

    # Circus Maximus
    cx_, cy_, cz_ = at((12.4851, 41.8861))
    def circus(p, h):
        yaw = math.radians(-58)
        ux, uy = (math.cos(yaw), math.sin(yaw)), (-math.sin(yaw), math.cos(yaw))
        for sd in (-1, 1):
            p.box(cx_ + uy[0] * sd * 62, cy_ + uy[1] * sd * 62, cz_, ux, uy, 300, 12, h, (*TRAVERTINE, 0.4))
        p.box(cx_, cy_, cz_, ux, uy, 250, 4, 2.5, (*MARBLE, 0.0))
        p.box(cx_ - ux[0] * 300, cy_ - ux[1] * 300, cz_, ux, uy, 8, 70, h, (*TRAVERTINE, 0.4))
    mon("CircusMaximus", -46, 550, lambda p: circus(p, 28), 6,
        ruin={"from": 550, "fn": lambda p: circus(p, 3), "to": 1600})
    marks["circus"] = (cx_, cy_, cz_ + 30)

    # Colosseum (72-80 AD); part of the outer ring falls in the 1349 earthquake
    ox, oy, oz = at((12.4922, 41.8902))
    def colosseum(p, broken):
        rot = math.radians(-20)
        n = 64
        for k in range(n):
            a0 = 2 * math.pi * k / n
            if broken and 0.5 < a0 < 2.6:
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
        ruin={"from": 1349, "fn": lambda p: colosseum(p, True)})
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

    # objects from bins
    for key, part in bins.items():
        ob = part.to_object("_".join(str(k) for k in key), facade if key[0] in ("bld", "imp") else painted, col)
        kind = key[0]
        if kind == "bld":
            animated.append({"ob": ob, "year": key[1], "grow": max(2.0, key[2]), "gone": None})
        elif kind in ("med", "rep", "imp", "tow"):
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
        smoke_col = (0.24, 0.22, 0.20) if e["kind"] == "fire" else (0.50, 0.47, 0.43)
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
    sun.data.color = (1.0, 0.93, 0.82)
    sun.rotation_euler = (math.radians(52), 0, math.radians(-40))
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
        return y + 754 if y < 0 else y + 753

    return {"proj": lambda lon, lat: proj(lon, lat), "year_text": year_text, "counter": auc,
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
