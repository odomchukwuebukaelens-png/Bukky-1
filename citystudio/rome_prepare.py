"""Turns raw Rome downloads into data/rome/ for the renderer.

Usage:  python3 citystudio/rome_prepare.py RAW_DIR OUT_DIR
RAW_DIR holds Overture Maps extracts (buildings.json, roads.json, water_all.json,
landuse.json; each a list of rows with a "wkt" geometry) and the Copernicus
30 m elevation tile dem.tif (N41 E012). Needs numpy, Pillow and shapely.

Coordinates are metres around Piazza Venezia (x east, y north).
Rome has no open register of construction years, so dates of today's buildings
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

LAT0, LON0 = 41.8958, 12.4826
KX = 111320.0 * math.cos(math.radians(LAT0))
KY = 111132.0
BOX = (-4600.0, -3600.0, 4600.0, 3800.0)          # x0, y0, x1, y1 in metres
RES = 12.0


def proj(lon, lat):
    return ((lon - LON0) * KX, (lat - LAT0) * KY)


def poly_m(lonlats):
    return Polygon([proj(lo, la) for lo, la in lonlats])


# Approximate historic zones (lon, lat). Illustrative outlines, not surveyed lines.
ABITATO = poly_m([(12.4762, 41.9110), (12.4818, 41.9080), (12.4845, 41.9010), (12.4842, 41.8960),
                  (12.4810, 41.8930), (12.4780, 41.8912), (12.4740, 41.8925), (12.4690, 41.8960),
                  (12.4672, 41.9010), (12.4698, 41.9065), (12.4735, 41.9100)])
TRASTEVERE = poly_m([(12.4745, 41.8930), (12.4775, 41.8885), (12.4755, 41.8840), (12.4680, 41.8835),
                     (12.4640, 41.8870), (12.4655, 41.8925), (12.4700, 41.8945)])
BORGO = poly_m([(12.4560, 41.9055), (12.4665, 41.9040), (12.4668, 41.9005), (12.4580, 41.9000),
                (12.4545, 41.9020)])
VATICAN = poly_m([(12.4460, 41.9080), (12.4560, 41.9070), (12.4580, 41.9010), (12.4530, 41.8995),
                  (12.4455, 41.9010)])
SERVIAN = poly_m([(12.4800, 41.8970), (12.4880, 41.9030), (12.4960, 41.9040), (12.5030, 41.9000),
                  (12.5040, 41.8940), (12.4990, 41.8880), (12.4930, 41.8830), (12.4850, 41.8790),
                  (12.4790, 41.8800), (12.4770, 41.8850), (12.4780, 41.8920)])
PRATI = poly_m([(12.4560, 41.9070), (12.4560, 41.9200), (12.4720, 41.9220), (12.4760, 41.9110),
                (12.4700, 41.9065)])

# Landmarks in today's data: name fragment -> (year shown, height in metres or None to keep)
LANDMARKS = {
    "pantheon": (126, None), "castel sant": (139, None), "basilica di san pietro": (1626, None),
    "santa maria maggiore": (432, None), "san giovanni in laterano": (1650, None),
    "palazzo del quirinale": (1583, None), "palazzo di giustizia": (1911, None),
    "vittoriano": (1911, None), "altare della patria": (1911, None), "monumento a vittorio emanuele": (1911, None),
    "palazzo venezia": (1467, None), "santa maria in trastevere": (1143, None),
    "teatro di marcello": (-13, None), "stazione termini": (1950, None), "roma termini": (1950, None),
    "sant'agnese in agone": (1657, None), "trinità dei monti": (1585, None), "palazzo farnese": (1589, None),
    "san paolo": (1854, None), "santa maria del popolo": (1477, None), "palazzo madama": (1505, None),
    "palazzo montecitorio": (1694, None), "palazzo senatorio": (1605, None),
}
SKIP = ("colosseo", "mura aureliane", "mura serviane", "mura leonine")   # built separately


def estimate_year(cx, cy, rng):
    p = Point(cx, cy)
    if VATICAN.contains(p):
        return int(rng.uniform(1450, 1700))
    if ABITATO.contains(p) or BORGO.contains(p):
        return int(rng.triangular(1430, 1850, 1620))
    if TRASTEVERE.contains(p):
        return int(rng.triangular(1450, 1900, 1650))
    if PRATI.contains(p):
        return int(rng.uniform(1885, 1935))
    d = math.hypot(cx, cy)
    if d < 2300:            # inside the Aurelian walls: mostly the post-1870 capital
        return int(rng.uniform(1873, 1930))
    return int(min(1990, rng.uniform(1910, 1940) + (d - 2300) * 0.012))


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


def tiber(raw):
    lines = []
    for r in json.load(open(os.path.join(raw, "water_all.json"))):
        name = ((r.get("names") or {}).get("primary") or "").lower()
        if "tevere" in name and r.get("subtype") == "river":
            g = shapely.wkt.loads(r["wkt"])
            parts = [g] if g.geom_type in ("LineString", "Polygon") else list(getattr(g, "geoms", []))
            for p in parts:
                coords = p.coords if p.geom_type == "LineString" else p.exterior.coords
                lines.append([proj(lo, la) for lo, la in coords])
    return lines


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
    """Copernicus DSM (includes roofs and trees), heavily smoothed so the seven
    hills remain while buildings disappear, then lowered to river level."""
    im = Image.open(os.path.join(raw, "dem.tif"))
    a = np.array(im, dtype=np.float32)            # 3600 x 3600, 1 arc-second, tile N41 E012
    out = np.zeros((ny, nx), dtype=np.float32)
    jj, ii = np.mgrid[0:ny, 0:nx]
    X = x0 + (ii + 0.5) * RES
    Y = y0 + ny * RES - (jj + 0.5) * RES
    lon = LON0 + X / KX
    lat = LAT0 + Y / KY
    col = np.clip(((lon - 12.0) * 3600).astype(int), 0, 3599)
    row = np.clip(((42.0 - lat) * 3600).astype(int), 0, 3599)
    out = a[row, col]
    sm = out.astype(np.float64)
    for _ in range(3):                         # three box blurs = a smooth Gaussian-like blur
        sm = box_blur(sm, 11)
    base = np.percentile(sm, 3)
    return np.clip(sm - base, 0, 80)


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
    riv = tiber(raw)
    x0, y0, x1, y1 = BOX
    nx, ny = int((x1 - x0) / RES), int((y1 - y0) / RES)
    elev = dem_grid(raw, x0, y0, nx, ny)
    water = Image.new("L", (nx, ny), 0)
    d = ImageDraw.Draw(water)

    def px(p):
        return ((p[0] - x0) / RES, (y0 + ny * RES - p[1]) / RES)
    for line in riv:
        d.line([px(p) for p in line], fill=255, width=int(95 / RES))
    water = np.array(water.filter(ImageFilter.MaxFilter(3))) > 127
    land = ~water
    elev = np.where(water, -2.0, np.maximum(elev, 0.6))
    shore = shore_distance(land, RES)
    np.savez_compressed(os.path.join(out, "terrain.npz"), land=land.astype(np.uint8), elev=elev.astype(np.float32),
                        shore=shore.astype(np.float32), box=np.array([x0, y0, RES, nx, ny], dtype=np.float64))
    zones = {k: [list(c) for c in list(z.exterior.coords)[:-1]] for k, z in
             (("abitato", ABITATO), ("trastevere", TRASTEVERE), ("borgo", BORGO), ("vatican", VATICAN),
              ("servian", SERVIAN), ("prati", PRATI))}
    data = {"origin": [LAT0, LON0], "buildings": bld, "walls": walls, "roads": rd, "tiber": riv, "zones": zones,
            "sources": ["Overture Maps Foundation (incl. OpenStreetMap contributors, ODbL)",
                        "Copernicus GLO-30 DEM (ESA)"]}
    with gzip.open(os.path.join(out, "rome.json.gz"), "wt") as f:
        json.dump(data, f, separators=(",", ":"))
    est = sum(1 for b in bld if b[3])
    print("[city-studio] Rome: %d buildings (%d with estimated dates), %d wall pieces, %d roads, %d river lines"
          % (len(bld), est, len(walls), len(rd), len(riv)))


if __name__ == "__main__":
    main()
