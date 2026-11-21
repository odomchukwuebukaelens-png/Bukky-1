"""New York style ("style": "nyc" in a brief).

Every building standing in Manhattan today rises in the year the city's
records give for it (NYC Open Data). Buildings that no longer exist - the
Dutch town, the 1800s rowhouses that came before today's towers, the Twin
Towers - are reconstructions and are kept apart in the code so they can be
labelled as such. The shoreline grows outwards in stages as land was filled.
"""
import bisect
import gzip
import json
import math
import os
import random

import bpy
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

import style_historic as H

ROT = math.radians(29.0)
KX = 111320.0 * math.cos(math.radians(40.758))
KY = 111132.0


def proj(lon, lat):
    return Vector(((lon + 73.9855) * KX, (lat - 40.758) * KY))


def along(x, y):
    return x * math.sin(ROT) + y * math.cos(ROT)


# Landmarks that are not in today's building data, or need detail added.
FORT_AMSTERDAM = proj(-74.0137, 40.7041)
WTC_SITE = proj(-74.0127, 40.7114)
TWIN_NORTH = proj(-74.01315, 40.71180)
TWIN_SOUTH = proj(-74.01250, 40.71105)
# bridge name in the street data: (towers start, opens, tower height m, deck height m)
BRIDGES = {"BROOKLYN BRG": (1870, 1883, 84, 41), "WILLIAMSBURG BRG": (1897, 1903, 102, 41),
           "MANHATTAN BRG": (1901, 1909, 98, 41), "ED KOCH QUEENSBORO BRG": (1903, 1909, 100, 40),
           "GEORGE WASHINGTON BRG": (1927, 1931, 184, 64)}
LIBERTY = proj(-74.0445, 40.6892)

# Recorded years that are known to differ from the completion year.
YEAR_FIX = {"Chrysler Building": 1930, "Tower 1 World Trade Ctr": 2014, "Tower 4 World Trade Ctr": 2013,
            "7 World Trade Center": 2006, "Castle Clinton": 1811}
SPIRES = {"Tower 1 World Trade Ctr": 541.0, "Empire State Building": 443.0, "Chrysler Building": 319.0}

ERA_COLOURS = [  # (from year, list of wall colours)
    (0, [(0.40, 0.16, 0.11), (0.46, 0.22, 0.15), (0.55, 0.47, 0.36), (0.36, 0.20, 0.14)]),
    (1850, [(0.36, 0.20, 0.14), (0.42, 0.18, 0.12), (0.30, 0.20, 0.16), (0.52, 0.40, 0.30)]),
    (1895, [(0.62, 0.56, 0.46), (0.55, 0.42, 0.30), (0.45, 0.24, 0.16), (0.68, 0.62, 0.52)]),
    (1945, [(0.58, 0.58, 0.56), (0.66, 0.65, 0.62), (0.30, 0.32, 0.34), (0.50, 0.48, 0.44)]),
    (1980, [(0.30, 0.38, 0.45), (0.42, 0.50, 0.56), (0.20, 0.24, 0.28), (0.60, 0.62, 0.62)]),
]
ROOF = (0.20, 0.20, 0.21)


class City:
    """The prepared data plus lookups for height, landfill year and when an
    area was farmed and built up."""
    def __init__(self, folder):
        with gzip.open(os.path.join(folder, "nyc.json.gz"), "rt") as f:
            self.data = json.load(f)
        t = np.load(os.path.join(folder, "terrain.npz"))
        self.grids = {}
        for key in ("tip", "wide"):
            x0, y0, res, nx, ny = t[key + "_box"]
            self.grids[key] = {"x0": x0, "y0": y0, "res": res, "nx": int(nx), "ny": int(ny),
                               "land": t[key + "_land"], "elev": t[key + "_elev"], "fill": t[key + "_fill"],
                               "mn": t[key + "_manhattan"]}
        self.u_battery = self.data["u_battery"]
        self.frontier = self.data["frontier"]
        self.battery = Vector(self.data["battery"])

    def grid_at(self, x, y):
        for key in ("tip", "wide"):
            g = self.grids[key]
            i = int((x - g["x0"]) / g["res"])
            j = int((g["y0"] + g["ny"] * g["res"] - y) / g["res"])
            if 0 <= i < g["nx"] and 0 <= j < g["ny"]:
                return g, j, i
        return None, 0, 0

    def elev(self, x, y):
        g, j, i = self.grid_at(x, y)
        return float(g["elev"][j, i]) if g else -7.0

    def fill(self, x, y):
        g, j, i = self.grid_at(x, y)
        return int(g["fill"][j, i]) if g else 0

    def manhattan(self, x, y):
        g, j, i = self.grid_at(x, y)
        return bool(g["mn"][j, i]) if g else False

    def built_up_year(self, x, y, in_manhattan=None):
        """Year by which this spot was part of the built-up city (illustrative)."""
        if in_manhattan is None:
            in_manhattan = self.manhattan(x, y)
        if in_manhattan:
            u = along(x, y) - self.u_battery
            inv = [(b, a) for a, b in self.frontier]
            return H.interp(inv, max(0.0, u))
        d = (Vector((x, y)) - self.battery).length
        return min(1935.0, max(1835.0, 1825 + d * 0.012))

    def farmed_year(self, x, y, in_manhattan=None):
        b = self.built_up_year(x, y, in_manhattan)
        return max(1630.0, b - (110 if b > 1700 else 15))


# ----------------------------------------------------------------------------
# Materials
# ----------------------------------------------------------------------------
def facade_material():
    """Colour from the mesh; a grid of dark windows on walls, strength set by
    the colour's alpha (0 = no windows)."""
    mat = bpy.data.materials.new("Facade")
    nt = H.nodes(mat)
    bsdf = H.principled(nt)
    bsdf.inputs["Roughness"].default_value = 0.8
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "col"
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    pos = nt.nodes.new("ShaderNodeSeparateXYZ")
    nrm = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], pos.inputs[0])
    nt.links.new(geo.outputs["Normal"], nrm.inputs[0])
    m = H.math_node
    floors = m(nt, "GREATER_THAN", m(nt, "FRACT", m(nt, "DIVIDE", pos.outputs["Z"], 3.7)), 0.42)
    bays = m(nt, "GREATER_THAN",
             m(nt, "FRACT", m(nt, "DIVIDE", m(nt, "ADD", pos.outputs["X"], pos.outputs["Y"]), 3.1)), 0.38)
    walls = m(nt, "LESS_THAN", m(nt, "ABSOLUTE", nrm.outputs["Z"]), 0.5)
    mask = m(nt, "MULTIPLY", m(nt, "MULTIPLY", floors, bays), walls)
    mask = m(nt, "MULTIPLY", mask, attr.outputs["Alpha"])
    col = H.mix_rgb(nt, mask, attr.outputs["Color"], (0.045, 0.06, 0.08))
    nt.links.new(col, bsdf.inputs["Base Color"])
    night = nt.nodes.new("ShaderNodeValue")
    night.name = "night"
    night.outputs[0].default_value = 0.0
    lit = m(nt, "GREATER_THAN", m(nt, "FRACT", m(nt, "MULTIPLY", m(nt, "ADD", pos.outputs["X"],
                                                                     m(nt, "MULTIPLY", pos.outputs["Z"], 7.3)), 0.37)),
            0.45)
    glow = m(nt, "MULTIPLY", m(nt, "MULTIPLY", mask, lit), night.outputs[0])
    for name in ("Emission Color", "Emission"):
        if name in bsdf.inputs:
            bsdf.inputs[name].default_value = (1.0, 0.72, 0.38, 1)
            break
    nt.links.new(m(nt, "MULTIPLY", glow, 6.0), bsdf.inputs["Emission Strength"])
    H.add_haze(mat)
    return mat, night


def terrain_material():
    mat = bpy.data.materials.new("NYCTerrain")
    nt = H.nodes(mat)
    bsdf = H.principled(nt)
    bsdf.inputs["Roughness"].default_value = 0.95
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "era"
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(attr.outputs["Color"], sep.inputs[0])
    farm_at, urban_at, forest = sep.outputs[0], sep.outputs[1], sep.outputs[2]
    attr2 = nt.nodes.new("ShaderNodeAttribute")
    attr2.attribute_name = "inland"
    inland = attr2.outputs["Fac"]
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    pos = geo.outputs["Position"]

    def tex_noise(scale, detail=4):
        t = nt.nodes.new("ShaderNodeTexNoise")
        t.inputs["Scale"].default_value = scale
        t.inputs["Detail"].default_value = detail
        nt.links.new(pos, t.inputs["Vector"])
        return t.outputs["Fac"]

    canopy = nt.nodes.new("ShaderNodeTexVoronoi")
    canopy.inputs["Scale"].default_value = 0.09
    nt.links.new(pos, canopy.inputs["Vector"])
    clump = H.smooth(nt, canopy.outputs["Distance"], 0.15, 0.75)
    forest_col = H.mix_rgb(nt, clump, (0.050, 0.085, 0.034), (0.022, 0.040, 0.018))
    meadow = H.mix_rgb(nt, tex_noise(0.012), (0.20, 0.22, 0.07), (0.13, 0.17, 0.05))
    wild = H.mix_rgb(nt, H.smooth(nt, forest, 0.40, 0.52), meadow, forest_col)

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
    farm_col = ramp.outputs["Color"]

    now = nt.nodes.new("ShaderNodeValue")
    now.name = "now"
    now.outputs[0].default_value = 0.0
    farmed = H.smooth(nt, H.math_node(nt, "SUBTRACT", now.outputs[0], farm_at), 0.0, 0.004)
    farmed = H.math_node(nt, "MULTIPLY", farmed, H.smooth(nt, pick.outputs[1], 0.08, 0.12))
    urban = H.smooth(nt, H.math_node(nt, "SUBTRACT", now.outputs[0], urban_at), 0.0, 0.004)
    urban_col = H.mix_rgb(nt, tex_noise(0.05), (0.29, 0.28, 0.26), (0.24, 0.23, 0.22))
    land = H.mix_rgb(nt, urban, H.mix_rgb(nt, farmed, wild, farm_col), urban_col)
    beach = H.smooth(nt, inland, 0.55, 0.8)
    shore = H.mix_rgb(nt, beach, (0.33, 0.30, 0.22), land)
    under = H.smooth(nt, inland, 0.35, 0.5)
    final = H.mix_rgb(nt, under, (0.05, 0.07, 0.07), shore)
    nt.links.new(final, bsdf.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.35
    bump.inputs["Distance"].default_value = 2.0
    wild_amount = H.math_node(nt, "MULTIPLY", H.math_node(nt, "SUBTRACT", 1.0, urban),
                              H.math_node(nt, "SUBTRACT", 1.0, farmed))
    nt.links.new(H.math_node(nt, "MULTIPLY", H.math_node(nt, "MULTIPLY", clump, H.smooth(nt, forest, 0.40, 0.52)),
                             wild_amount), bump.inputs["Height"])
    nt.links.new(bump.outputs[0], bsdf.inputs["Normal"])
    H.add_haze(mat)
    return mat, now


def smooth_sphere():
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
    out = ([tuple(v.co) for v in bm.verts], [tuple(v.index for v in f.verts) for f in bm.faces])
    bm.free()
    return out


def year_norm(y):
    return (y - 1500.0) / 600.0


# ----------------------------------------------------------------------------
# Geometry helpers
# ----------------------------------------------------------------------------
def extrude(parts, pts, z0, h, wall, alpha, roof=ROOF):
    n = len(pts)
    verts = [(x, y, z0) for x, y in pts] + [(x, y, z0 + h) for x, y in pts]
    faces = [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)] + [tuple(range(n, 2 * n))]
    cols = [(*wall, alpha)] * n + [(*roof, 0.0)]
    parts.add(verts, faces, cols)


def oriented_box(pts):
    """Centre, direction and half sizes of a footprint's oriented bounding box."""
    best = None
    for i in range(len(pts)):
        a, b = Vector(pts[i]), Vector(pts[(i + 1) % len(pts)])
        if (b - a).length > (best[1] if best else 0):
            best = ((b - a).normalized(), (b - a).length)
    ux = best[0]
    uy = Vector((-ux.y, ux.x))
    xs = [Vector(p).dot(ux) for p in pts]
    ys = [Vector(p).dot(uy) for p in pts]
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    centre = ux * cx + uy * cy
    return centre, ux, uy, (max(xs) - min(xs)) / 2, (max(ys) - min(ys)) / 2


class Partsc(H.Parts):
    """Parts with RGBA colours (alpha drives the window pattern)."""
    def to_object(self, name, mat, collection):
        me = bpy.data.meshes.new(name)
        me.from_pydata(self.verts, [], self.faces)
        attr = me.color_attributes.new("col", "FLOAT_COLOR", "CORNER")
        data = []
        for poly, c in zip(me.polygons, self.cols):
            rgba = (c[0], c[1], c[2], c[3] if len(c) > 3 else 0.0)
            data.extend(rgba * poly.loop_total)
        attr.data.foreach_set("color", data)
        me.materials.append(mat)
        ob = bpy.data.objects.new(name, me)
        collection.objects.link(ob)
        return ob


# ----------------------------------------------------------------------------
# Plan
# ----------------------------------------------------------------------------
def plan(brief):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    city = City(os.path.join(root, brief.get("data", "data/nyc")))
    rng = random.Random(brief["seed"])
    focus = Vector(brief.get("focus", [-2000, -5000]))
    radius = brief.get("detail_radius", 7000.0)

    real, older = [], []
    for b in city.data["buildings"]:
        bin_id, year, est, h, g, flat, name = b
        pts = [(flat[i] / 10.0, flat[i + 1] / 10.0) for i in range(0, len(flat), 2)]
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        if (Vector((cx, cy)) - focus).length > radius:
            continue
        year = YEAR_FIX.get(name, year)
        h = h / 10.0
        fill = city.fill(cx, cy)
        z0 = city.elev(cx, cy) - 0.5
        spire = SPIRES.get(name)
        church = any(k in name.upper() for k in ("CHURCH", "CHAPEL", "CATHEDRAL")) and h > 30
        real.append({"pts": pts, "year": year, "h": 20.0 if church else h, "z": z0, "name": name,
                     "spire": spire or (h if church else None), "c": (cx, cy)})
        # what stood here before today's building (reconstruction)
        start = max(city.built_up_year(cx, cy, True) + rng.uniform(0, 14), fill + 3)
        in_wtc = (Vector((cx, cy)) - WTC_SITE).length < 190
        end = year if not in_wtc else min(year, 1966)
        if end - start < 8:
            continue
        centre, ux, uy, hx, hy = oriented_box(pts)
        if start < 1840:
            stop = min(end, 1840 + rng.uniform(0, 30)) if end > 1860 else end
            older.append({"kind": "house", "c": centre, "ux": ux, "uy": uy, "hx": min(hx, 9), "hy": min(hy, 6),
                          "h": rng.uniform(9, 13), "start": start, "end": stop, "z": z0})
            start = stop
        if end - start >= 8:
            older.append({"kind": "row", "pts": [(centre + (Vector(p) - centre) * 0.96)[:] for p in pts],
                          "h": rng.uniform(12, 20), "start": start, "end": end, "z": z0})

    streets, bridges = [], {}
    for name, width, flat in city.data["streets"]:
        pts = [Vector((flat[i] / 10.0, flat[i + 1] / 10.0)) for i in range(0, len(flat), 2)]
        if name in BRIDGES:
            bridges.setdefault(name, []).append(pts)
            continue
        if "BRG" in name or "BRIDGE" in name:
            continue
        for a, b in zip(pts, pts[1:]):
            mid = (a + b) / 2
            if (mid - focus).length > radius:
                continue
            yr = max(city.built_up_year(mid.x, mid.y, True) - 4, city.fill(mid.x, mid.y) + 2)
            streets.append({"a": a, "b": b, "w": max(6.0, min(width, 30.0)), "year": yr,
                            "z": city.elev(mid.x, mid.y) + 0.25, "name": name})

    parks = []
    for name, year, flat in city.data["parks"]:
        pts = [(flat[i] / 10.0, flat[i + 1] / 10.0) for i in range(0, len(flat), 2)]
        c = Vector((sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)))
        if (c - focus).length > radius + 2000:
            continue
        parks.append({"pts": pts, "year": year, "name": name, "z": city.elev(c.x, c.y) + 0.35})

    # forest on all land near the focus, cleared when farming starts
    trees = []
    step = brief.get("tree_spacing", 22.0)
    sparse = (step / brief.get("tree_spacing_outside", step)) ** 2
    box = brief.get("tree_box", [focus.x - radius, focus.y - radius, focus.x + radius, focus.y + radius])
    y = box[1]
    while y < box[3]:
        x = box[0]
        while x < box[2]:
            px, py = x + rng.uniform(-8, 8), y + rng.uniform(-8, 8)
            g, j, i = city.grid_at(px, py)
            inside = "tree_box" in brief or (Vector((px, py)) - focus).length < radius
            if g is not None and g["land"][j, i] and inside:
                f = 0.5 + 0.5 * math.sin(px / 410.0 + 1.3) * math.cos(py / 530.0 - 0.4)
                mn = bool(g["mn"][j, i])
                if (f > 0.42 or rng.random() < 0.12) and (mn or rng.random() < sparse):
                    trees.append({"x": px, "y": py, "z": float(g["elev"][j, i]), "r": rng.uniform(4.5, 8),
                                  "gone": city.farmed_year(px, py, mn) + rng.uniform(-5, 10),
                                  "since": int(g["fill"][j, i]), "g": rng.uniform(0.75, 1.2)})
            x += step
        y += step

    park_trees = []
    for pk in parks:
        pts = pk["pts"]
        xs, ys = [q[0] for q in pts], [q[1] for q in pts]
        area = abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]))) / 2
        if area < 15000:
            continue
        yy = min(ys)
        while yy < max(ys):
            xx = min(xs)
            while xx < max(xs):
                px, py = xx + rng.uniform(-5, 5), yy + rng.uniform(-5, 5)
                inside = False
                for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
                    if (y1 > py) != (y2 > py) and px < x1 + (py - y1) * (x2 - x1) / (y2 - y1):
                        inside = not inside
                if inside and rng.random() < 0.75:
                    park_trees.append({"x": px, "y": py, "z": pk["z"], "r": rng.uniform(3.5, 6.5),
                                       "since": pk["year"] + rng.uniform(1, 14), "g": rng.uniform(0.85, 1.35)})
                xx += 16
            yy += 16

    real.sort(key=lambda r: r["year"])
    return {"city": city, "real": real, "older": older, "streets": streets, "parks": parks, "trees": trees,
            "park_trees": park_trees, "bridges": bridges,
            "standing_years": sorted(r["year"] for r in real) if brief.get("count_focus_only")
            else sorted(YEAR_FIX.get(b[6], b[1]) for b in city.data["buildings"])}


# ----------------------------------------------------------------------------
# Build
# ----------------------------------------------------------------------------
def terrain_objects(city, col, tmat):
    """Terrain meshes; land made by landfill is split off per fill year so it
    can appear when it was made."""
    out = []
    tip = city.grids["tip"]
    tip_box = (tip["x0"], tip["y0"], tip["x0"] + tip["nx"] * tip["res"], tip["y0"] + tip["ny"] * tip["res"])
    for key in ("wide", "tip"):
        g = city.grids[key]
        nx, ny, res = g["nx"], g["ny"], g["res"]
        xs = g["x0"] + (np.arange(nx) + 0.5) * res
        ys = g["y0"] + g["ny"] * res - (np.arange(ny) + 0.5) * res
        elev = g["elev"]
        groups = {}
        for j in range(ny - 1):
            for i in range(nx - 1):
                if key == "wide":
                    cx, cy = xs[i] + res / 2, ys[j] - res / 2
                    if tip_box[0] + res < cx < tip_box[2] - res and tip_box[1] + res < cy < tip_box[3] - res:
                        continue
                    yr = 0
                else:
                    yr = int(max(g["fill"][j, i], g["fill"][j, i + 1], g["fill"][j + 1, i], g["fill"][j + 1, i + 1]))
                    if not (g["land"][j, i] or g["land"][j + 1, i + 1] or g["land"][j, i + 1] or g["land"][j + 1, i]):
                        yr = 0
                groups.setdefault(yr, []).append((j, i))
        for yr, cells in groups.items():
            index = {}
            verts, faces, era, inland = [], [], [], []

            def vid(j, i):
                k = (j, i)
                if k not in index:
                    index[k] = len(verts)
                    x, y = float(xs[i]), float(ys[j])
                    e = float(elev[j, i])
                    land = e > -1
                    verts.append((x, y, e if (land or yr == 0) else -3.0))
                    mn = bool(g["mn"][j, i])
                    era.append((year_norm(city.farmed_year(x, y, mn)), year_norm(city.built_up_year(x, y, mn)),
                                0.5 + 0.5 * math.sin(x / 410.0 + 1.3) * math.cos(y / 530.0 - 0.4), 1.0))
                    inland.append(1.0 if land else 0.0)
                return index[k]
            for j, i in cells:
                faces.append((vid(j, i), vid(j, i + 1), vid(j + 1, i + 1), vid(j + 1, i)))
            me = bpy.data.meshes.new("terrain_%s_%d" % (key, yr))
            me.from_pydata(verts, [], faces)
            me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
            a = me.color_attributes.new("era", "FLOAT_COLOR", "POINT")
            a.data.foreach_set("color", [c for e4 in era for c in e4])
            b = me.attributes.new("inland", "FLOAT", "POINT")
            b.data.foreach_set("value", inland)
            me.materials.append(tmat)
            ob = bpy.data.objects.new(me.name, me)
            col.objects.link(ob)
            if yr:
                out.append({"ob": ob, "year": yr, "grow": 0.0, "fill": True})
    return out


def wall_line(city, parts, pts, z_extra, h, col_):
    for a, b in zip(pts, pts[1:]):
        d = b - a
        n = int(d.length / 5) + 1
        for k in range(n):
            p = a + d * ((k + 0.5) / n)
            parts.box(p.x, p.y, city.elev(p.x, p.y) + z_extra, tuple(d.normalized()),
                      (-d.normalized().y, d.normalized().x), d.length / n / 2 + 0.2, 0.7, h, col_)


def build(brief, p):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    col = scene.collection
    city = p["city"]
    H.HAZE_DISTANCE = brief.get("haze_distance", 24000.0)
    H.HAZE_AMOUNT = brief.get("haze_amount", 0.7)
    painted = H.painted_material()
    facade, night = facade_material()
    tmat, now = terrain_material()
    animated = terrain_objects(city, col, tmat)

    sea = bpy.data.meshes.new("Sea")
    s = 60000
    sea.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
    sea.materials.append(H.water_material())
    col.objects.link(bpy.data.objects.new("Sea", sea))

    rng = random.Random(brief["seed"] + 1)

    def palette(year):
        cols = ERA_COLOURS[0][1]
        for y0, c in ERA_COLOURS:
            if year >= y0:
                cols = c
        return rng.choice(cols)

    # today's buildings, one object per year
    bins = {}
    for r in p["real"]:
        part = bins.setdefault(("real", int(r["year"])), Partsc())
        alpha = 1.0 if r["h"] > 25 else 0.55
        extrude(part, r["pts"], r["z"], r["h"] + 0.5, palette(r["year"]), alpha)
        if r.get("spire") and r["spire"] > r["h"]:
            c = Vector(r["c"])
            top = r["z"] + r["h"]
            k = 0.9 if r["spire"] - r["h"] > 40 else 2.5
            part.add([(c.x - k, c.y - k, top), (c.x + k, c.y - k, top), (c.x + k, c.y + k, top), (c.x - k, c.y + k, top),
                      (c.x, c.y, r["z"] + r["spire"])],
                     [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)], [(0.55, 0.56, 0.58, 0.0)] * 4)
    # earlier buildings (reconstructions), grouped by when they stand
    for o in p["older"]:
        key = ("older", int(o["start"] // 3), int(o["end"] // 3))
        part = bins.setdefault(key, Partsc())
        if o["kind"] == "house":
            part.house({"x": o["c"].x, "y": o["c"].y, "ux": tuple(o["ux"]), "uy": tuple(o["uy"]),
                        "d": o["hx"] * 2, "w": o["hy"] * 2, "h": o["h"],
                        "wall": rng.choice(H.WALLS), "roof": rng.choice(H.ROOFS)}, o["z"])
        else:
            extrude(part, o["pts"], o["z"], o["h"], palette(o["start"]), 0.45, roof=(0.24, 0.20, 0.18))
    for st in p["streets"]:
        part = bins.setdefault(("street", int(st["year"])), Partsc())
        a, b = st["a"], st["b"]
        d = (b - a)
        if d.length < 0.5:
            continue
        n = Vector((-d.y, d.x)).normalized() * st["w"] / 2
        part.add([(*(a - n), st["z"]), (*(b - n), st["z"]), (*(b + n), st["z"]), (*(a + n), st["z"])],
                 [(0, 1, 2, 3)], [(0.33, 0.32, 0.30, 0.0)])
    for pk in p["parks"]:
        part = bins.setdefault(("park", int(pk["year"])), Partsc())
        part.add([(x, y, pk["z"]) for x, y in pk["pts"]], [tuple(range(len(pk["pts"])))], [(0.12, 0.22, 0.06, 0.0)])

    for key, part in sorted(bins.items()):
        mat = facade if key[0] in ("real", "older") else painted
        ob = part.to_object("_".join(str(k) for k in key), mat, col)
        if key[0] == "older":
            animated.append({"ob": ob, "year": key[1] * 3, "grow": 2.0, "gone": key[2] * 3 + 1.5})
        else:
            animated.append({"ob": ob, "year": key[1], "grow": 2.5 if key[0] == "real" else 0.0})

    # forest, grouped by when it is cleared
    ico_v, ico_f = H.ico_template()
    tbins = {}
    for t in p["trees"]:
        k = (int(t["gone"] // 4), t["since"])
        g = t["g"]
        r = t["r"]
        vv = [(t["x"] + vx * r, t["y"] + vy * r, t["z"] + r * 0.9 + vz * r * 0.8) for vx, vy, vz in ico_v]
        tbins.setdefault(k, H.Parts()).add(vv, ico_f, [(0.045 * g, 0.075 * g, 0.030 * g)] * len(ico_f))
    for (gone, since), part in tbins.items():
        ob = part.to_object("trees_%d_%d" % (gone, since), painted, col)
        animated.append({"ob": ob, "year": since, "grow": 0.0, "gone": gone * 4 + 2, "fade": 0.5})

    pbins = {}
    for t in p["park_trees"]:
        k = int(t["since"] // 2)
        g = t["g"]
        r = t["r"]
        vv = [(t["x"] + vx * r, t["y"] + vy * r, t["z"] + r * 0.9 + vz * r * 0.8) for vx, vy, vz in ico_v]
        pbins.setdefault(k, H.Parts()).add(vv, ico_f, [(0.05 * g, 0.10 * g, 0.035 * g)] * len(ico_f))
    for k, part in pbins.items():
        animated.append({"ob": part.to_object("parktrees_%d" % k, painted, col), "year": k * 2, "grow": 3.0})

    # --- reconstructed landmarks -------------------------------------------
    marks = {}
    fort = Partsc()
    fz = city.elev(FORT_AMSTERDAM.x, FORT_AMSTERDAM.y)
    outer = []
    for k in range(4):
        a = math.radians(45 + 90 * k + 29)
        for da, rr in ((-20, 30), (0, 46), (20, 30)):
            outer.append((FORT_AMSTERDAM.x + rr * math.cos(a + math.radians(da)),
                          FORT_AMSTERDAM.y + rr * math.sin(a + math.radians(da))))
    inner = [(FORT_AMSTERDAM.x + (x - FORT_AMSTERDAM.x) * 0.78, FORT_AMSTERDAM.y + (y - FORT_AMSTERDAM.y) * 0.78)
             for x, y in outer]
    m = len(outer)
    v = [(x, y, fz) for x, y in outer] + [(x, y, fz + 6) for x, y in outer] + \
        [(x, y, fz + 6) for x, y in inner] + [(x, y, fz + 0.6) for x, y in inner]
    f, c = [], []
    for i in range(m):
        j = (i + 1) % m
        f += [(i, j, m + j, m + i), (m + i, m + j, 2 * m + j, 2 * m + i), (2 * m + i, 2 * m + j, 3 * m + j, 3 * m + i)]
        c += [(*H.STONE, 0.0), (0.30, 0.33, 0.17, 0.0), (*H.STONE, 0.0)]
    f.append(tuple(range(3 * m, 4 * m)))
    c.append((*H.EARTH, 0.0))
    fort.add(v, f, c)
    fort.house({"x": FORT_AMSTERDAM.x, "y": FORT_AMSTERDAM.y, "ux": (math.sin(ROT), math.cos(ROT)),
                "uy": (math.cos(ROT), -math.sin(ROT)), "d": 22, "w": 10, "h": 13,
                "wall": (0.55, 0.50, 0.42), "roof": (0.35, 0.11, 0.07)}, fz + 0.6)
    animated.append({"ob": fort.to_object("FortAmsterdam", painted, col), "year": 1625, "grow": 2.0, "gone": 1790})
    marks["fort"] = (FORT_AMSTERDAM.x, FORT_AMSTERDAM.y, fz + 16)

    wall_pts = []
    for st in p["streets"]:
        if st["name"].upper() == "WALL ST":
            wall_pts.append((along(st["a"].x, st["a"].y), st["a"]))
    if wall_pts:
        wall_pts.sort(key=lambda t: t[1].x)
        pal = Partsc()
        pts = [w[1] for w in wall_pts]
        wall_line(city, pal, pts, 0.0, 4.5, (*H.WOOD, 0.0))
        animated.append({"ob": pal.to_object("WallStreetPalisade", painted, col), "year": 1653, "grow": 2.0,
                         "gone": 1699})
        mid = pts[len(pts) // 2]
        marks["wall"] = (mid.x, mid.y, city.elev(mid.x, mid.y) + 8)

    # bridges, from the roadway lines in the street data
    for name, lines in p["bridges"].items():
        t_start, t_open, tower_h, deck_h = BRIDGES[name]
        allp = [q for line in lines for q in line]
        c = sum(allp, Vector((0, 0))) / len(allp)
        cov = [[0, 0], [0, 0]]
        for q in allp:
            d = q - c
            cov[0][0] += d.x * d.x
            cov[0][1] += d.x * d.y
            cov[1][1] += d.y * d.y
        ang = 0.5 * math.atan2(2 * cov[0][1], cov[0][0] - cov[1][1])
        axis = Vector((math.cos(ang), math.sin(ang)))
        side = Vector((-axis.y, axis.x))
        wet = [(q - c).dot(axis) for q in allp if city.elev(q.x, q.y) < 0]
        if not wet:
            continue
        s0, s1 = min(wet), max(wet)
        span = s1 - s0

        def deck_z(q):
            sv = (q - c).dot(axis)
            out = max(0.0, s0 - sv, sv - s1)
            return max(city.elev(q.x, q.y) + 0.5, deck_h - out * 0.09)
        deck = Partsc()
        grey = (0.36, 0.35, 0.33, 0.0)
        for line in lines:
            for qa, qb in zip(line, line[1:]):
                d = qb - qa
                if d.length < 0.5:
                    continue
                nrm = Vector((-d.y, d.x)).normalized() * 6
                za, zb = deck_z(qa), deck_z(qb)
                deck.add([(*(qa - nrm), za), (*(qb - nrm), zb), (*(qb + nrm), zb), (*(qa + nrm), za)],
                         [(0, 1, 2, 3)], [grey])
        towers = Partsc()
        stone = (0.60, 0.56, 0.48, 0.0) if name == "BROOKLYN BRG" else (0.42, 0.44, 0.46, 0.0)
        tpos = [c + axis * (s0 + span * 0.18), c + axis * (s1 - span * 0.18)]
        width = 14.0
        for tp in tpos:
            towers.box(tp.x, tp.y, -3, tuple(axis), tuple(side), 6, width, tower_h + 3, stone)
        cab = Partsc()
        a_end, b_end = c + axis * (s0 - span * 0.05), c + axis * (s1 + span * 0.05)
        for sd in (-1, 1):
            off = side * (width - 2) * sd
            for qa, qb, mid in ((a_end, tpos[0], False), (tpos[0], tpos[1], True), (tpos[1], b_end, False)):
                n = 14
                for k in range(n):
                    t0, t1 = k / n, (k + 1) / n

                    def zc(t, qa=qa, mid=mid):
                        if mid:
                            return tower_h - (tower_h - deck_h - 3) * 4 * t * (1 - t)
                        up = t if qa is a_end else 1 - t
                        return deck_h + (tower_h - deck_h) * up
                    p0, p1 = qa.lerp(qb, t0) + off, qa.lerp(qb, t1) + off
                    z0, z1 = zc(t0), zc(t1)
                    cab.add([(p0.x, p0.y, z0), (p1.x, p1.y, z1), (p1.x, p1.y, z1 + 1.2), (p0.x, p0.y, z0 + 1.2)],
                            [(0, 1, 2, 3)], [(0.28, 0.28, 0.28, 0.0)])
        animated.append({"ob": towers.to_object(name + "_towers", painted, col), "year": t_start,
                         "grow": max(2.0, (t_open - t_start) * 0.6)})
        animated.append({"ob": deck.to_object(name + "_deck", painted, col), "year": t_open - 1.5, "grow": 1.5})
        animated.append({"ob": cab.to_object(name + "_cables", painted, col), "year": t_open - 2.5, "grow": 1.0})
        key = name.split()[0].lower() if name != "ED KOCH QUEENSBORO BRG" else "queensboro"
        marks[key + "_bridge"] = (tpos[0].x, tpos[0].y, tower_h + 10)
    if "brooklyn_bridge" in marks:
        marks["bridge"] = marks["brooklyn_bridge"]

    # Statue of Liberty on its star-shaped base
    lib = Partsc()
    lz = city.elev(LIBERTY.x, LIBERTY.y)
    star = []
    for k in range(22):
        rr = 46 if k % 2 == 0 else 30
        a = math.radians(k * 360 / 22)
        star.append((LIBERTY.x + rr * math.cos(a), LIBERTY.y + rr * math.sin(a)))
    extrude(lib, star, lz, 9, (0.62, 0.58, 0.50), 0.0, roof=(0.40, 0.42, 0.30))
    lib.box(LIBERTY.x, LIBERTY.y, lz + 9, (1, 0), (0, 1), 9, 9, 27, (0.66, 0.62, 0.54, 0.0))
    animated.append({"ob": lib.to_object("LibertyBase", painted, col), "year": 1884, "grow": 2.0})
    statue = Partsc()
    green = (0.29, 0.50, 0.44, 0.0)
    statue.box(LIBERTY.x, LIBERTY.y, lz + 36, (1, 0), (0, 1), 4.5, 4.0, 34, green)
    statue.box(LIBERTY.x + 1.5, LIBERTY.y, lz + 70, (1, 0), (0, 1), 1.8, 1.8, 5, green)
    statue.box(LIBERTY.x + 4.5, LIBERTY.y + 0.5, lz + 62, (1, 0), (0, 1), 1.0, 1.0, 22, green)
    statue.box(LIBERTY.x + 4.5, LIBERTY.y + 0.5, lz + 84, (1, 0), (0, 1), 1.8, 1.8, 3, (0.80, 0.62, 0.25, 0.0))
    animated.append({"ob": statue.to_object("Liberty", painted, col), "year": 1886, "grow": 0.8})
    marks["liberty"] = (LIBERTY.x, LIBERTY.y, lz + 95)

    # Twin Towers (reconstruction): rise 1968-1973, gone in 2001
    tw = Partsc()
    for t, h in ((TWIN_NORTH, 417.0), (TWIN_SOUTH, 415.0)):
        z = city.elev(t.x, t.y)
        ux_ = (math.cos(ROT), -math.sin(ROT))
        uy_ = (math.sin(ROT), math.cos(ROT))
        tw.box(t.x, t.y, z, ux_, uy_, 31.7, 31.7, h, (0.62, 0.63, 0.64, 1.0), top=(0.25, 0.25, 0.26, 0.0))
    animated.append({"ob": tw.to_object("TwinTowers", facade, col), "year": 1969, "grow": 4.0, "gone": 2001.7,
                     "fade": brief.get("twin_fade", 0.25)})
    marks["twins"] = (TWIN_NORTH.x, TWIN_NORTH.y, 440)
    marks["onewtc"] = (WTC_SITE.x - 20, WTC_SITE.y + 30, 470)

    # fires, smoke and dust
    fx = []
    emit = bpy.data.materials.new("Flame")
    ent = H.nodes(emit)
    ent.nodes.clear()
    em = ent.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (1.0, 0.42, 0.08, 1)
    em.inputs["Strength"].default_value = 12.0
    outn = ent.nodes.new("ShaderNodeOutputMaterial")
    ent.links.new(em.outputs[0], outn.inputs[0])
    frng = random.Random(brief["seed"] + 9)
    for e in brief.get("fx", []):
        centre = proj(*e["ll"])
        z0 = city.elev(centre.x, centre.y)
        smoke_col = (0.20, 0.19, 0.18) if e["kind"] == "fire" else (0.50, 0.47, 0.43)
        blobs = H.Parts()
        fx_v, fx_f = smooth_sphere()
        for _ in range(e.get("blobs", 40)):
            r = frng.uniform(0.15, 1.0) * e["radius"]
            a = frng.uniform(0, 2 * math.pi)
            q = centre + Vector((math.cos(a), math.sin(a))) * r
            rr = frng.uniform(14, 40) * e.get("size", 1.0)
            zz = z0 + frng.uniform(0, 1.0) ** 2 * 70 * e.get("size", 1.0)
            blobs.add([(q.x + vx * rr, q.y + vy * rr, zz + vz * rr * 0.55) for vx, vy, vz in fx_v], fx_f,
                      [smoke_col] * len(fx_f))
        smoke = blobs.to_object("smoke", painted, col)
        smoke.location = (centre.x, centre.y, 0)
        me = smoke.data
        me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
        for v in me.vertices:
            v.co.x -= centre.x
            v.co.y -= centre.y
        flames = None
        if e["kind"] == "fire":
            fl = H.Parts()
            for _ in range(e.get("flames", 120)):
                r = frng.uniform(0, 1.0) * e["radius"]
                a = frng.uniform(0, 2 * math.pi)
                q = centre + Vector((math.cos(a), math.sin(a))) * r
                rr = frng.uniform(4, 9)
                fl.add([(q.x + vx * rr, q.y + vy * rr, z0 + 8 + vz * rr * 1.6) for vx, vy, vz in ico_v], ico_f,
                       [(1, 0.5, 0.1)] * len(ico_f))
            flames = fl.to_object("flames", emit, col)
        fx.append({"e": e, "smoke": smoke, "flames": flames})

    # light, sky and camera
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = brief.get("sun", 6.5)
    sun.data.angle = math.radians(2.5)
    sun.data.color = (1.0, 0.93, 0.82)
    sun.rotation_euler = (math.radians(52), 0, math.radians(-40))
    col.objects.link(sun)
    world = bpy.data.worlds.new("Sky")
    world.use_nodes = True
    bg = next(nd for nd in world.node_tree.nodes if nd.type == "BACKGROUND")
    bg.inputs[0].default_value = (*H.HAZE, 1)
    bg.inputs[1].default_value = brief.get("sky", 0.45)
    scene.world = world
    cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    cam.data.lens = brief.get("lens", 32)
    cam.data.clip_start = brief.get("clip_start", 20.0)
    cam.data.clip_end = brief.get("clip_end", 40000.0)
    col.objects.link(cam)
    scene.camera = cam

    named = {
        "governors": tuple(proj(-74.0167, 40.6895)) + (20,), "ellis": tuple(proj(-74.0396, 40.6995)) + (12,),
        "hudson": tuple(proj(-74.022, 40.725)) + (2,), "east_river": tuple(proj(-73.990, 40.702)) + (2,),
        "bpc": tuple(proj(-74.0168, 40.7130)) + (20,),
    }
    for r in p["real"]:
        if r["name"] == "Trinity Church":
            named["trinity"] = (r["c"][0], r["c"][1], r["z"] + (r["spire"] or r["h"]) + 6)
        if r["name"] == "Woolworth Building":
            named["woolworth"] = (r["c"][0], r["c"][1], r["z"] + r["h"] + 6)
    marks.update(named)
    labels = []
    for lb in brief.get("labels", []):
        if "ll" in lb:
            q = proj(lb["ll"][0], lb["ll"][1])
            labels.append(dict(lb, pos=Vector((q.x, q.y, city.elev(q.x, q.y) + lb["ll"][2]))))
        elif lb.get("at") in marks:
            labels.append(dict(lb, pos=Vector(marks[lb["at"]])))

    return {"scene": scene, "camera": cam, "animated": animated, "now": now, "labels": labels,
            "fx": fx, "sun": sun, "sky": bg, "night": night,
            "standing_years": p["standing_years"],
            "stats": "%d buildings from city records, %d reconstructed, %d trees" % (
                len(p["real"]), len(p["older"]), len(p["trees"]))}


# ----------------------------------------------------------------------------
# Per frame
# ----------------------------------------------------------------------------
def camera_at(brief, t, total_s):
    keys = brief["camera_keys"]
    if t <= keys[0]["t"]:
        k0 = k1 = keys[0]
        s = 0.0
    else:
        k0, k1, s = keys[-1], keys[-1], 0.0
        for a, b in zip(keys, keys[1:]):
            if a["t"] <= t <= b["t"]:
                k0, k1 = a, b
                s = H.ease((t - a["t"]) / max(1e-6, b["t"] - a["t"]))
                break
    if "target" in k0:
        def parts(k):
            q = proj(k["target"][0], k["target"][1])
            return Vector((q.x, q.y, k.get("look_z", 0.0))), k["dist"], k["height"], k["bearing"]
        t0_, d0, h0, b0 = parts(k0)
        t1_, d1, h1, b1 = parts(k1)
        db = (b1 - b0 + 180) % 360 - 180
        look = t0_.lerp(t1_, s)
        dist = d0 + (d1 - d0) * s
        height = h0 + (h1 - h0) * s
        bearing = math.radians(b0 + db * s)
        loc = Vector((look.x - math.sin(bearing) * dist, look.y - math.cos(bearing) * dist, height))
        return loc, look
    loc = Vector(k0["pos"]).lerp(Vector(k1["pos"]), s)
    look = Vector(k0["look"]).lerp(Vector(k1["look"]), s)
    return loc, look


def apply_frame(brief, rig, frame, total):
    fps = brief["fps"]
    t = frame / fps
    year = H.year_at(brief, t)
    for a in rig["animated"]:
        if a.get("fill"):
            k = H.ease((year - a["year"]) / 3.0)
            a["ob"].hide_render = k <= 0.001
            a["ob"].location.z = -6.0 * (1 - k)
            continue
        k = H.ease((year - a["year"]) / a["grow"]) if a["grow"] > 0 else (1.0 if year >= a["year"] else 0.0)
        if a.get("gone") is not None:
            k *= 1.0 - H.ease((year - a["gone"]) / a.get("fade", 1.5))
        a["ob"].hide_render = k <= 0.001
        a["ob"].scale.z = max(k, 0.001)
    rig["now"].outputs[0].default_value = year_norm(year)
    for f in rig["fx"]:
        e = f["e"]
        prog = (year - e["from"]) / max(1e-6, e["to"] - e["from"])
        on = 0.0 <= prog <= 1.0
        if f["flames"]:
            f["flames"].hide_render = not (0.0 <= prog <= 0.85)
            f["flames"].scale.z = 0.7 + 0.3 * math.sin(t * 23.0) * math.sin(t * 7.0)
        grow = H.ease(prog / 0.6) if prog > 0 else 0.0
        fade = 1.0 - H.ease((prog - 1.0) / 0.5) if prog > 1.0 else 1.0
        k = max(0.0, grow * fade)
        f["smoke"].hide_render = k <= 0.01 or not (prog > 0 and prog < 1.5)
        f["smoke"].scale = (0.4 + 0.8 * k, 0.4 + 0.8 * k, 0.4 + 1.2 * k)
        f["smoke"].location.z = 40 * k
        del on
    dusk = brief.get("dusk")
    d = H.ease((t - dusk["from"]) / (dusk["to"] - dusk["from"])) if dusk else 0.0
    rig["night"].outputs[0].default_value = d
    rig["sun"].data.energy = brief.get("sun", 6.5) * (1 - 0.8 * d)
    rig["sun"].data.color = (1.0, 0.93 - 0.35 * d, 0.82 - 0.5 * d)
    rig["sun"].rotation_euler = (math.radians(52 + 30 * d), 0, math.radians(-40 - 30 * d))
    rig["sky"].inputs[1].default_value = brief.get("sky", 0.45) * (1 - 0.65 * d)
    dusk_haze = (0.80 - 0.45 * d, 0.76 - 0.50 * d, 0.69 - 0.40 * d, 1)
    for em in H.HAZE_NODES:
        em.inputs["Color"].default_value = dusk_haze

    loc, look = camera_at(brief, t, total / fps)
    cam = rig["camera"]
    cam.location = loc
    cam.rotation_euler = (look - loc).to_track_quat("-Z", "Y").to_euler()
    heading = math.degrees(math.atan2(look.x - loc.x, look.y - loc.y))

    scene = rig["scene"]
    bpy.context.view_layer.update()
    labels = []
    for lb in rig["labels"]:
        if year < lb.get("from", -1e9) or year >= lb.get("until", 1e9):
            continue
        t0 = H.first_time(brief, lb.get("from", -1e9), total, fps)
        alpha = H.ease((t - t0) / 0.6) if lb.get("from") else 1.0
        if "until" in lb:
            alpha *= 1.0 - H.ease((year - lb["until"] + 2) / 2)
        pp = world_to_camera_view(scene, cam, lb["pos"])
        if pp.z <= 0 or not (0.03 < pp.x < 0.97 and 0.10 < pp.y < 0.84):
            continue
        if (lb["pos"] - cam.location).length > brief.get("label_max_distance", 7500):
            continue
        if any(abs(pp.x - q["x"]) < 0.10 and abs((1.0 - pp.y) - q["y"]) < 0.04 for q in labels):
            continue
        labels.append({"text": lb["text"], "x": pp.x, "y": 1.0 - pp.y, "alpha": round(alpha, 3),
                       "kind": lb.get("kind", "place")})

    caption = None
    events = brief.get("events", [])
    for i, ev in enumerate(events):
        t0 = max(ev.get("min_time", 0.0), H.first_time(brief, ev["year"], total, fps))
        t1 = (max(events[i + 1].get("min_time", 0.0), H.first_time(brief, events[i + 1]["year"], total, fps)) - 0.2
              if i + 1 < len(events) else total / fps + 1)
        t1 = min(t1, t0 + ev.get("hold", brief.get("caption_hold", 3.2)))
        if t0 <= t < t1:
            a = H.ease((t - t0) / 0.4) * (1 - H.ease((t - t1 + 0.4) / 0.4))
            caption = {"tag": ev.get("tag", str(ev["year"])), "title": ev["title"], "body": ev["body"],
                       "alpha": round(a, 3)}
    era = H.pick(brief["eras"], year)
    ruler = H.pick(brief["rulers"], year)
    standing = bisect.bisect_right(rig["standing_years"], year)
    title = None
    for tc in ([brief["title_card"]] if brief.get("title_card") else []) + brief.get("cards", []):
        if tc["start"] <= t <= tc["end"]:
            a = H.ease((t - tc["start"]) / 0.7) * (1 - H.ease((t - tc["end"] + 0.7) / 0.7))
            title = dict(tc, alpha=round(a, 3))
            if caption and tc.get("hide_caption", True):
                caption = None
            for q in labels:
                q["alpha"] = round(q["alpha"] * (1 - a), 3)
    pop = H.interp(brief["population"], year)
    return {
        "design": "atlas", "year": int(year), "era": era["text"] if era else "",
        "realm": ruler["realm"] if ruler else "", "ruler": ruler.get("name", "") if ruler else "",
        "badge": ruler.get("badge", "") if ruler else "",
        "population": H.fmt_pop(pop) or "", "population_label": brief.get("population_label", "Population"),
        "standing": "{:,}".format(standing), "standing_label": brief.get("standing_label", "Still standing"),
        "heading": heading, "caption": caption, "title_card": title, "labels": labels,
        "fineprint": brief.get("fineprint", ""),
    }
