"""Turns raw London downloads into data/london/ for the renderer (based on rome_prepare).

Usage:  python3 citystudio/london_prepare.py RAW_DIR OUT_DIR
RAW_DIR holds Overture Maps extracts (buildings.json, roads.json, water_all.json,
landuse.json; each a list of rows with a "wkt" geometry) and the Copernicus
30 m elevation tiles dem_w.tif (N51 W001) and dem_e.tif (N51 E000). Needs numpy, Pillow and shapely.

Coordinates are metres around Bank junction (x east, y north).
London has no open register of construction years, so dates of today's buildings
are ESTIMATES from the district they stand in (see estimate_year).
"""
import gzip
import json
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import shapely.wkt
from shapely.geometry import Point, Polygon

LAT0, LON0 = 51.5133, -0.0890
KX = 111320.0 * math.cos(math.radians(LAT0))
KY = 111132.0
BOX = (-5600.0, -2600.0, 4800.0, 2400.0)          # x0, y0, x1, y1 in metres
RES = 12.0


def proj(lon, lat):
    return ((lon - LON0) * KX, (lat - LAT0) * KY)


def poly_m(lonlats):
    return Polygon([proj(lo, la) for lo, la in lonlats])


# Approximate historic zones (lon, lat). Illustrative outlines, not surveyed lines.
CITY = poly_m([(-0.0760, 51.5081), (-0.0770, 51.5135), (-0.0815, 51.5170), (-0.0880, 51.5185), (-0.0945, 51.5180),
               (-0.0975, 51.5165), (-0.1010, 51.5155), (-0.1030, 51.5140), (-0.1035, 51.5112), (-0.0900, 51.5085)])
FIRE1666 = poly_m([(-0.0790, 51.5086), (-0.0815, 51.5140), (-0.0885, 51.5172), (-0.0965, 51.5172), (-0.1060, 51.5155),
                   (-0.1115, 51.5135), (-0.1110, 51.5108), (-0.0880, 51.5084)])
SOUTHWARK = poly_m([(-0.1000, 51.5085), (-0.0800, 51.5065), (-0.0830, 51.4990), (-0.0960, 51.4985), (-0.1020, 51.5040)])
WESTMINSTER = poly_m([(-0.1320, 51.5030), (-0.1220, 51.5030), (-0.1220, 51.4960), (-0.1320, 51.4960)])
STRAND = poly_m([(-0.1250, 51.5090), (-0.1030, 51.5140), (-0.1020, 51.5110), (-0.1240, 51.5060)])
WESTEND = poly_m([(-0.1600, 51.5160), (-0.1250, 51.5170), (-0.1230, 51.5060), (-0.1450, 51.5020), (-0.1600, 51.5030)])

# Landmarks in today's data: name fragment -> (year shown, height in metres or None to keep)
LANDMARKS = {
    "the shard": (2012, None), "30 st mary axe": (2004, None), "leadenhall building": (2014, None),
    "elizabeth tower": (1859, None), "buckingham palace": (1703, None), "british museum": (1852, None),
    "bank of england": (1939, None), "royal exchange": (1844, None), "somerset house": (1796, None),
    "monument to the great fire": (1677, None), "southwark cathedral": (1220, 35.0), "westminster cathedral": (1903, None),
    "tower 42": (1980, None), "lloyd's building": (1986, None), "tate modern": (2000, None),
    "the globe": (1997, None), "guildhall": (1440, None), "national gallery": (1838, None),
    "st martin-in-the-fields": (1726, None), "royal courts of justice": (1882, None),
}
SKIP = ("white tower", "westminster abbey", "palace of westminster", "tower bridge")   # built separately


def estimate_year(cx, cy, rng):
    p = Point(cx, cy)
    if CITY.contains(p) or FIRE1666.contains(p):
        return int(rng.triangular(1850, 2020, 1965))       # the City was rebuilt again and again
    if WESTMINSTER.contains(p):
        return int(rng.uniform(1840, 1980))
    if STRAND.contains(p) or WESTEND.contains(p):
        return int(rng.triangular(1720, 1990, 1830))
    if SOUTHWARK.contains(p):
        return int(rng.triangular(1820, 2020, 1900))
    d = math.hypot(cx, cy)
    return int(min(2015, rng.uniform(1810, 1880) + d * 0.012))


def ring_coords(geom):
    if geom.geom_type == "MultiPolygon":
        geom = max(geom.geoms, key=lambda g: g.area)
    if geom.geom_type != "Polygon":
        return None
    return list(geom.exterior.coords)[:-1]


def buildings(raw, rng):
    out = []
    walls = []
    for r in json.load(open(os.path.join(raw, "buildings.json"))):
        name = ((r.get("names") or {}).get("primary") or "")
        low = name.lower()
        g = shapely.wkt.loads(r["wkt"])
        ring = ring_coords(g)
        if not ring:
            continue
        pts = [proj(lo, la) for lo, la in ring]
        poly = Polygon(pts)
        if not poly.is_valid or poly.area < 15:
            continue
        if any(k in low for k in SKIP):
            if "mura" in low:
                walls.append({"name": name, "pts": pts})
            continue
        simp = poly.simplify(0.8)
        if simp.geom_type != "Polygon":
            continue
        pts = list(simp.exterior.coords)[:-1]
        tol = 1.5
        while len(pts) > 18 and tol < 40:
            simp = poly.simplify(tol)
            if simp.geom_type != "Polygon":
                break
            pts = list(simp.exterior.coords)[:-1]
            tol *= 1.7
        c = poly.centroid
        h = r.get("height") or ((r.get("num_floors") or 0) * 3.4) or (rng.uniform(14, 22) if c.distance(Point(0, 0)) < 3000 else rng.uniform(15, 30))
        year, landmark = None, ""
        for k, (y, hh) in LANDMARKS.items():
            if k in low:
                year, landmark = y, name
                if hh:
                    h = hh
                break
        est = year is None
        if est:
            year = estimate_year(c.x, c.y, rng)
        out.append([round(c.x, 1), round(c.y, 1), year, 1 if est else 0, round(float(h), 1),
                    [round(v, 1) for xy in pts for v in xy], landmark])
    return out, walls


def thames(raw):
    """Polygons of the river (preferred) plus centre lines as a fallback."""
    polys, lines = [], []
    for r in json.load(open(os.path.join(raw, "water_all.json"))):
        name = ((r.get("names") or {}).get("primary") or "").lower()
        if r.get("subtype") != "river":
            continue
        g = shapely.wkt.loads(r["wkt"])
        if g.geom_type in ("Polygon", "MultiPolygon") and g.area > 1e-6:
            for p in ([g] if g.geom_type == "Polygon" else list(g.geoms)):
                polys.append([proj(lo, la) for lo, la in p.exterior.coords])
        elif "thames" in name and g.geom_type == "LineString":
            lines.append([proj(lo, la) for lo, la in g.coords])
    return polys, lines


def roads(raw):
    out = []
    for r in json.load(open(os.path.join(raw, "roads.json"))):
        cls = r.get("class") or ""
        if cls in ("footway", "steps", "cycleway", "path", "track", "service", "unknown"):
            continue
        g = shapely.wkt.loads(r["wkt"])
        if g.geom_type != "LineString":
            continue
        w = {"motorway": 22, "trunk": 18, "primary": 16, "secondary": 13, "tertiary": 11}.get(cls, 8)
        name = ((r.get("names") or {}).get("primary") or "")
        out.append([name, w, [round(v, 1) for lo, la in g.coords for v in proj(lo, la)]])
    return out


def box_blur(a, r):
    p = np.pad(a, r, mode="edge")
    c = np.cumsum(np.cumsum(p, 0), 1)
    c = np.pad(c, ((1, 0), (1, 0)))
    k = 2 * r + 1
    return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)


def dem_grid(raw, x0, y0, nx, ny):
    """Copernicus DSM tiles W001 and E000 joined, smoothed so hills stay and roofs disappear."""
    w = np.array(Image.open(os.path.join(raw, "dem_w.tif")), dtype=np.float32)
    e = np.array(Image.open(os.path.join(raw, "dem_e.tif")), dtype=np.float32)
    jj, ii = np.mgrid[0:ny, 0:nx]
    X = x0 + (ii + 0.5) * RES
    Y = y0 + ny * RES - (jj + 0.5) * RES
    lon = LON0 + X / KX
    lat = LAT0 + Y / KY
    row = np.clip(((52.0 - lat) * 3600).astype(int), 0, 3599)
    out = np.where(lon < 0,
                   w[row, np.clip(((lon + 1.0) * w.shape[1]).astype(int), 0, w.shape[1] - 1)],
                   e[row, np.clip((lon * e.shape[1]).astype(int), 0, e.shape[1] - 1)])
    sm = out.astype(np.float64)
    # remove buildings and trees: take the lowest point within about 100 m first
    r = 8
    for axis in (0, 1):
        p = np.pad(sm, [(r, r) if a == axis else (0, 0) for a in (0, 1)], mode="edge")
        sm = np.min(np.stack([np.take(p, range(k, k + sm.shape[axis]), axis=axis) for k in range(2 * r + 1)]), axis=0)
    for _ in range(3):
        sm = box_blur(sm, 11)
    base = np.percentile(sm, 3)
    return np.clip(sm - base, 0, 60)


def shore_distance(land, res, cap=600.0):
    d = np.where(land, 0.0, 1e9)
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
    rng = random.Random(11)
    bld, walls = buildings(raw, rng)
    rd = roads(raw)
    polys, lines = thames(raw)
    x0, y0, x1, y1 = BOX
    nx, ny = int((x1 - x0) / RES), int((y1 - y0) / RES)
    elev = dem_grid(raw, x0, y0, nx, ny)
    water = Image.new("L", (nx, ny), 0)
    d = ImageDraw.Draw(water)

    def px(p):
        return ((p[0] - x0) / RES, (y0 + ny * RES - p[1]) / RES)
    for poly in polys:
        d.polygon([px(p) for p in poly], fill=255)
    for line in lines:
        d.line([px(p) for p in line], fill=255, width=int(200 / RES))
    water = np.array(water) > 127
    land = ~water
    elev = np.where(water, -2.0, np.maximum(elev, 0.6))
    shore = shore_distance(land, RES)
    np.savez_compressed(os.path.join(out, "terrain.npz"), land=land.astype(np.uint8), elev=elev.astype(np.float32),
                        shore=shore.astype(np.float32), box=np.array([x0, y0, RES, nx, ny], dtype=np.float64))
    zones = {k: [list(c) for c in list(z.exterior.coords)[:-1]] for k, z in
             (("city", CITY), ("fire", FIRE1666), ("southwark", SOUTHWARK), ("westminster", WESTMINSTER),
              ("strand", STRAND), ("westend", WESTEND))}
    data = {"origin": [LAT0, LON0], "buildings": bld, "walls": walls, "roads": rd, "zones": zones,
            "sources": ["Overture Maps Foundation (incl. OpenStreetMap contributors, ODbL)",
                        "Copernicus GLO-30 DEM (ESA)"]}
    with gzip.open(os.path.join(out, "london.json.gz"), "wt") as f:
        json.dump(data, f, separators=(",", ":"))
    est = sum(1 for b in bld if b[3])
    print("[city-studio] London: %d buildings (%d with estimated dates), %d roads, %d river polygons, %d river lines"
          % (len(bld), est, len(rd), len(polys), len(lines)))


if __name__ == "__main__":
    main()
