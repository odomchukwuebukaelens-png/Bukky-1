"""Turns the raw New York downloads into one compact file the renderer uses.

Usage:  python3 citystudio/nyc_prepare.py RAW_DIR OUT_DIR
RAW_DIR must hold (all from NYC Open Data, data.cityofnewyork.us):
  manhattan_buildings.geojson  Building footprints (dataset 5zhs-2jue), Manhattan only
  boroughs.geojson             Borough Boundaries, clipped to shoreline (gthc-hcne)
  centerline.geojson           Street centerlines (inkn-q76z), Manhattan only
  parks.geojson                Parks Properties (enfh-gkve), Manhattan only
Writes OUT_DIR/nyc.json.gz and OUT_DIR/terrain.npz. Needs numpy and Pillow.

Everything is converted to metres around Times Square (x east, y north).
"""
import gzip
import json
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw

LAT0, LON0 = 40.758, -73.9855
KX = 111320.0 * math.cos(math.radians(LAT0))
KY = 111132.0
ROT = math.radians(29.0)          # Manhattan's street grid is turned 29 degrees from north
BATTERY = None                    # filled in below


def proj(lon, lat):
    return ((lon - LON0) * KX, (lat - LAT0) * KY)


def along(x, y):
    """Distance along the island (metres, measured parallel to the avenues)."""
    return x * math.sin(ROT) + y * math.cos(ROT)


def across(x, y):
    """Distance across the island (positive towards the East River)."""
    return x * math.cos(ROT) - y * math.sin(ROT)


BATTERY = proj(-74.0170, 40.7033)
U_BATTERY = along(*BATTERY)

# How far the built-up city reached along the island, by year (illustrative,
# based on commonly published histories of Manhattan's northward growth).
FRONTIER = [(1625, 0), (1660, 650), (1700, 1000), (1776, 2000), (1800, 2600), (1825, 3700), (1850, 5900),
            (1860, 7100), (1875, 8600), (1890, 11500), (1900, 13500), (1910, 16500), (1930, 20500)]


def interp(table, v):
    if v <= table[0][0]:
        return table[0][1]
    for (a, b), (c, d) in zip(table, table[1:]):
        if v <= c:
            return b + (d - b) * (v - a) / (c - a)
    return table[-1][1]


def frontier_year(u_from_battery):
    inv = [(b, a) for a, b in FRONTIER]
    return interp(inv, u_from_battery)


def simplify(pts, tol):
    """Douglas-Peucker on a closed ring."""
    if len(pts) < 5:
        return pts

    def rdp(seg):
        if len(seg) < 3:
            return seg
        (x1, y1), (x2, y2) = seg[0], seg[-1]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1e-9
        best, idx = -1, 0
        for i in range(1, len(seg) - 1):
            d = abs(dy * seg[i][0] - dx * seg[i][1] + x2 * y1 - y2 * x1) / L
            if d > best:
                best, idx = d, i
        if best > tol:
            return rdp(seg[:idx + 1])[:-1] + rdp(seg[idx:])
        return [seg[0], seg[-1]]
    half = len(pts) // 2
    out = rdp(pts[:half + 1])[:-1] + rdp(pts[half:] + [pts[0]])[:-1]
    return out if len(out) >= 3 else pts


def largest_ring(geom):
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    best, area = None, -1
    for poly in polys:
        ring = [proj(lon, lat) for lon, lat in poly[0]]
        a = abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]))) / 2
        if a > area:
            best, area = ring, a
    if best and best[0] == best[-1]:
        best = best[:-1]
    return best, area


def buildings(raw, rng, filename="manhattan_buildings.geojson", manhattan=True):
    path = os.path.join(raw, filename)
    if not os.path.exists(path):
        return []
    feats = json.load(open(path))["features"]
    out = []
    for f in feats:
        p, g = f["properties"], f["geometry"]
        if not g:
            continue
        ring, area = largest_ring(g)
        if not ring or area < 12:
            continue
        tol = 0.6
        pts = simplify(ring, tol)
        while len(pts) > 16:
            tol *= 1.6
            pts = simplify(ring, tol)
        cx = sum(x for x, _ in pts) / len(pts)
        cy = sum(y for _, y in pts) / len(pts)
        if manhattan:
            u = along(cx, cy) - U_BATTERY
        else:
            # other boroughs: built up later, roughly by distance from lower Manhattan
            d = math.hypot(cx - BATTERY[0], cy - BATTERY[1])
            u = max(0.0, d * 1.6 - 1500)
        year = int(float(p.get("construction_year") or 0))
        estimated = 0
        h_ft = float(p.get("height_roof") or 0)
        if year <= 0:
            # no recorded year: estimate from height (tall = modern), never before the area was built up
            if h_ft > 200:
                year = int(rng.uniform(1960, 2015))
            elif h_ft > 80:
                year = int(rng.uniform(1910, 1990))
            else:
                year = int(max(frontier_year(u) + 40, 1870) + rng.uniform(0, 50))
            estimated = 1
        elif year % 10 == 0 and year >= 1850:
            year -= rng.randint(0, 9)          # decade-rounded record: spread it across the decade
            estimated = 1
        h = max(3.0, float(p.get("height_roof") or 0) * 0.3048)
        if float(p.get("height_roof") or 0) <= 0:
            h = 12.0
        ground = float(p.get("ground_elevation") or 0) * 0.3048
        out.append([p.get("bin"), year, estimated, round(h * 10), round(ground * 10),
                    [int(round(v * 10)) for xy in pts for v in xy], p.get("name") or ""])
    return out


def streets(raw):
    feats = json.load(open(os.path.join(raw, "centerline.geojson")))["features"]
    out = []
    for f in feats:
        p, g = f["properties"], f["geometry"]
        if not g or p.get("rw_type") not in ("1", "2", "3", "4", "9", "14"):
            continue
        lines = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
        width = float(p.get("streetwidth") or 30) * 0.3048
        for line in lines:
            pts = [proj(lon, lat) for lon, lat in line]
            out.append([p.get("full_street_name") or "", round(width, 1),
                        [int(round(v * 10)) for xy in pts for v in xy]])
    return out


def parks(raw):
    feats = json.load(open(os.path.join(raw, "parks.geojson")))["features"]
    out = []
    for f in feats:
        p, g = f["properties"], f["geometry"]
        if not g:
            continue
        ring, area = largest_ring(g)
        if not ring or area < 400:
            continue
        date = (p.get("acquisitiondate") or "")[:4]
        year = int(date) if date.isdigit() else 1900
        out.append([p.get("name311") or "", year, [int(round(v * 10)) for xy in simplify(ring, 1.5) for v in xy]])
    return out


# Approximate New Jersey waterfront (west bank of the Hudson and Upper Bay).
# NYC Open Data stops at the state line; refine later with OpenStreetMap.
NJ_SHORE = [(-74.075, 40.640), (-74.070, 40.668), (-74.047, 40.690), (-74.040, 40.704), (-74.033, 40.716),
            (-74.027, 40.731), (-74.024, 40.745), (-74.018, 40.760), (-74.010, 40.775), (-73.996, 40.795),
            (-73.982, 40.815), (-73.966, 40.840), (-73.955, 40.862), (-73.940, 40.890), (-73.930, 40.920)]


def raster(raw, x0, y0, res, nx, ny, bld):
    land = Image.new("L", (nx, ny), 0)
    mn = Image.new("L", (nx, ny), 0)
    draw = ImageDraw.Draw(land)
    draw_mn = ImageDraw.Draw(mn)

    def to_px(x, y):
        return ((x - x0) / res, (y0 + ny * res - y) / res)
    for f in json.load(open(os.path.join(raw, "boroughs.geojson")))["features"]:
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        is_manhattan = str(f["properties"].get("borocode")) == "1"
        for poly in polys:
            ring = [to_px(*proj(lon, lat)) for lon, lat in poly[0]]
            draw.polygon(ring, fill=255)
            if is_manhattan:
                draw_mn.polygon(ring, fill=255)
            for hole in poly[1:]:
                draw.polygon([to_px(*proj(lon, lat)) for lon, lat in hole], fill=0)
    nj = [proj(lon, lat) for lon, lat in NJ_SHORE]
    draw.polygon([to_px(*p) for p in nj] + [to_px(-40000, 40000), to_px(-40000, -40000)], fill=255)
    land = np.array(land) > 127

    # ground height from the buildings' recorded ground elevations
    acc = np.zeros((ny, nx))
    cnt = np.zeros((ny, nx))
    for b in bld:
        pts = b[5]
        cx = sum(pts[0::2]) / len(pts[0::2]) / 10
        cy = sum(pts[1::2]) / len(pts[1::2]) / 10
        i = int((cx - x0) / res)
        j = int((y0 + ny * res - cy) / res)
        if 0 <= i < nx and 0 <= j < ny:
            acc[j, i] += b[4] / 10
            cnt[j, i] += 1
    elev = np.where(cnt > 0, acc / np.maximum(cnt, 1), np.nan)
    known = ~np.isnan(elev)
    filled = np.where(known, elev, 4.0)
    for _ in range(60):                      # spread known heights into the gaps
        pad = np.pad(filled, 1, mode="edge")
        avg = (pad[:-2, 1:-1] + pad[2:, 1:-1] + pad[1:-1, :-2] + pad[1:-1, 2:]) / 4
        filled = np.where(known, filled, avg)
    elev = np.where(land, np.clip(filled, 0.8, 80), -7.0)
    return land, elev, np.array(mn) > 127


def landfill(raw, x0, y0, res, nx, ny, land, manhattan_land):
    """Year from which each land cell exists. Land laid out by landfill in
    Lower Manhattan appears in stages, using historic street lines that mark
    old shorelines (approximate dates from published histories)."""
    feats = json.load(open(os.path.join(raw, "centerline.geojson")))["features"]
    lines = {}
    for f in feats:
        name = (f["properties"].get("full_street_name") or "").upper()
        g = f["geometry"]
        if not g:
            continue
        segs = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
        for s in segs:
            lines.setdefault(name, []).extend(proj(lon, lat) for lon, lat in s)

    def profile(name, u_max):
        pts = [(along(x, y) - U_BATTERY, across(x, y)) for x, y in lines.get(name, [])]
        pts = [p for p in pts if p[0] < u_max]
        bins = {}
        for u, v in pts:
            bins.setdefault(int(u // 25), []).append(v)
        return {k: float(np.median(v)) for k, v in bins.items()}

    # (street, side, fill year for land beyond it, how far up the island it counts)
    rules = [("PEARL ST", 1, 1690, 1350), ("WATER ST", 1, 1740, 1500), ("FRONT ST", 1, 1790, 1500),
             ("SOUTH ST", 1, 1815, 2200),
             ("GREENWICH ST", -1, 1790, 2400), ("WASHINGTON ST", -1, 1815, 2400), ("WEST ST", -1, 1850, 2400)]
    year = np.zeros((ny, nx), dtype=np.int16)
    jj, ii = np.mgrid[0:ny, 0:nx]
    X = x0 + (ii + 0.5) * res
    Y = y0 + ny * res - (jj + 0.5) * res
    U = X * math.sin(ROT) + Y * math.cos(ROT) - U_BATTERY
    V = X * math.cos(ROT) - Y * math.sin(ROT)
    manhattan = land & manhattan_land & (U > -400) & (U < 3000)
    for name, side, yr, u_max in rules:
        prof = profile(name, u_max)
        if not prof:
            print("[city-studio] street %s not found - skipped" % name)
            continue
        keys = sorted(prof)
        ub = np.clip((U // 25).astype(int), keys[0], keys[-1])
        vline = np.interp(ub, keys, [prof[k] for k in keys])
        inside = (U >= keys[0] * 25) & (U <= (keys[-1] + 1) * 25)
        beyond = (V - vline) * side > 6
        mask = manhattan & inside & beyond
        if name == "WEST ST":
            # beyond West Street: piers from the 1800s, except Battery Park City (1970s landfill)
            year = np.where(mask & (U < 1950) & (U > 150), 1976, np.where(mask, np.maximum(year, yr), year))
        else:
            year = np.where(mask, np.maximum(year, yr), year)
    # the southern tip (The Battery) was extended in the mid 1800s
    year = np.where(manhattan & (U < 120), np.maximum(year, 1855), year)
    return year


def shore_distance(land, res, cap=800.0):
    """Distance (m) from each water cell to the nearest land cell (0 on land)."""
    big = 1e9
    d = np.where(land, 0.0, big)
    diag = res * 1.41421
    for _ in range(int(cap / res) + 2):
        p = np.pad(d, 1, mode="edge")
        cand = np.minimum.reduce([p[1:-1, 1:-1], p[:-2, 1:-1] + res, p[2:, 1:-1] + res, p[1:-1, :-2] + res,
                                  p[1:-1, 2:] + res, p[:-2, :-2] + diag, p[:-2, 2:] + diag, p[2:, :-2] + diag,
                                  p[2:, 2:] + diag])
        if np.array_equal(cand, d):
            break
        d = cand
    return np.minimum(d, cap)


def main():
    raw, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    rng = random.Random(7)
    bld = buildings(raw, rng)
    outer = buildings(raw, rng, "bk_buildings.geojson", False) + buildings(raw, rng, "qn_buildings.geojson", False)
    st = streets(raw)
    pk = parks(raw)
    print("[city-studio] %d Manhattan buildings, %d Brooklyn/Queens buildings, %d street lines, %d parks" % (
        len(bld), len(outer), len(st), len(pk)))

    terrain = {}
    for key, (x0, y0, x1, y1, res) in {"wide": (-7000, -9500, 9000, 15500, 30.0),
                                        "tip": (-3600, -7000, -300, -3400, 8.0)}.items():
        nx, ny = int((x1 - x0) / res), int((y1 - y0) / res)
        land, elev, mn = raster(raw, x0, y0, res, nx, ny, bld + outer)
        fill = landfill(raw, x0, y0, res, nx, ny, land, mn)
        terrain[key + "_land"] = land.astype(np.uint8)
        terrain[key + "_elev"] = elev.astype(np.float32)
        terrain[key + "_fill"] = fill
        terrain[key + "_manhattan"] = mn.astype(np.uint8)
        terrain[key + "_shore"] = shore_distance(land, res).astype(np.float32)
        terrain[key + "_box"] = np.array([x0, y0, res, nx, ny], dtype=np.float64)
    np.savez_compressed(os.path.join(out, "terrain.npz"), **terrain)

    data = {"origin": [LAT0, LON0], "rotation_deg": 29.0, "battery": BATTERY, "u_battery": U_BATTERY,
            "frontier": FRONTIER, "buildings": bld, "outer_buildings": outer, "streets": st, "parks": pk,
            "sources": ["NYC Open Data: Building Footprints (5zhs-2jue)", "NYC Open Data: Borough Boundaries (gthc-hcne)",
                        "NYC Open Data: Centerline (inkn-q76z)", "NYC Open Data: Parks Properties (enfh-gkve)"]}
    with gzip.open(os.path.join(out, "nyc.json.gz"), "wt") as f:
        json.dump(data, f, separators=(",", ":"))
    print("[city-studio] wrote %s" % out)


if __name__ == "__main__":
    main()
