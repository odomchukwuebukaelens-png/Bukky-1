"""Turns raw Paris downloads into data/paris/ for the renderer (based on rome_prepare).

Usage:  python3 citystudio/paris_prepare.py RAW_DIR OUT_DIR
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

LAT0, LON0 = 48.8530, 2.3499
KX = 111320.0 * math.cos(math.radians(LAT0))
KY = 111132.0
BOX = (-7500.0, -5500.0, 7500.0, 5500.0)          # x0, y0, x1, y1 in metres
RES = 18.0


def proj(lon, lat):
    return ((lon - LON0) * KX, (lat - LAT0) * KY)


def poly_m(lonlats):
    return Polygon([proj(lo, la) for lo, la in lonlats])


# Approximate historic zones (lon, lat). Illustrative outlines, not surveyed lines.
CITE = poly_m([(2.3405, 48.8577), (2.3470, 48.8572), (2.3535, 48.8542), (2.3545, 48.8518), (2.3480, 48.8514),
               (2.3425, 48.8543)])
LEFT = poly_m([(2.3380, 48.8530), (2.3560, 48.8505), (2.3580, 48.8430), (2.3400, 48.8410), (2.3330, 48.8480)])
PHILIPPE = poly_m([(2.3365, 48.8615), (2.3455, 48.8650), (2.3560, 48.8615), (2.3625, 48.8555), (2.3560, 48.8480),
                   (2.3470, 48.8455), (2.3380, 48.8480), (2.3350, 48.8545)])
CHARLES = poly_m([(2.3310, 48.8635), (2.3430, 48.8700), (2.3560, 48.8705), (2.3690, 48.8535), (2.3610, 48.8500),
                  (2.3470, 48.8455), (2.3380, 48.8480), (2.3330, 48.8560)])
MARAIS = poly_m([(2.3520, 48.8620), (2.3660, 48.8615), (2.3690, 48.8540), (2.3560, 48.8545)])
HAUSSMANN = poly_m([(2.2950, 48.8800), (2.3700, 48.8830), (2.3900, 48.8600), (2.3700, 48.8380), (2.3200, 48.8350),
                    (2.2900, 48.8550)])

LANDMARKS = {
    "tour montparnasse": (1973, None), "centre pompidou": (1977, None), "centre georges pompidou": (1977, None),
    "opéra garnier": (1875, None), "palais garnier": (1875, None), "grand palais": (1900, None), "petit palais": (1900, None),
    "hôtel de ville": (1882, None), "gare du nord": (1865, None), "gare de l'est": (1850, None), "gare de lyon": (1900, None),
    "musée d'orsay": (1900, None), "église de la madeleine": (1842, None), "la madeleine": (1842, None),
    "saint-sulpice": (1745, None), "saint-eustache": (1632, None), "palais de justice": (1868, None),
    "palais du luxembourg": (1631, None), "palais-royal": (1639, None), "conciergerie": (1300, None),
    "saint-germain-des-prés": (1014, None), "institut de france": (1688, None), "bibliothèque nationale": (1868, None),
}
SKIP = ("notre-dame de paris", "cathédrale notre-dame", "sainte-chapelle", "tour eiffel", "arc de triomphe",
        "panthéon", "dôme des invalides", "basilique du sacré", "pyramide du louvre", "musée du louvre", "palais du louvre")


def estimate_year(cx, cy, rng):
    p = Point(cx, cy)
    if CITE.contains(p):
        return int(rng.triangular(1600, 1900, 1860))
    if MARAIS.contains(p):
        return int(rng.triangular(1600, 1900, 1680))
    if PHILIPPE.contains(p) or CHARLES.contains(p):
        return int(rng.triangular(1650, 1950, 1800))
    if HAUSSMANN.contains(p):
        return int(rng.triangular(1853, 1975, 1880))
    d = math.hypot(cx, cy)
    return int(min(2015, rng.uniform(1860, 1935) + max(0.0, d - 4000) * 0.006))


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


ISLANDS = []


def river(raw):
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
                for hole in p.interiors:                       # islands
                    ISLANDS.append([proj(lo, la) for lo, la in hole.coords])
        elif "seine" in name and g.geom_type == "LineString":
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
    """Copernicus DSM tile N48 E002, buildings removed, smoothed."""
    a = np.array(Image.open(os.path.join(raw, "dem.tif")), dtype=np.float32)
    jj, ii = np.mgrid[0:ny, 0:nx]
    X = x0 + (ii + 0.5) * RES
    Y = y0 + ny * RES - (jj + 0.5) * RES
    lon = LON0 + X / KX
    lat = LAT0 + Y / KY
    row = np.clip(((49.0 - lat) * a.shape[0]).astype(int), 0, a.shape[0] - 1)
    col = np.clip(((lon - 2.0) * a.shape[1]).astype(int), 0, a.shape[1] - 1)
    sm = a[row, col].astype(np.float64)
    r = 8
    for axis in (0, 1):
        p = np.pad(sm, [(r, r) if q == axis else (0, 0) for q in (0, 1)], mode="edge")
        sm = np.min(np.stack([np.take(p, range(k, k + sm.shape[axis]), axis=axis) for k in range(2 * r + 1)]), axis=0)
    for _ in range(3):
        sm = box_blur(sm, 9)
    base = np.percentile(sm, 3)
    return np.clip(sm - base, 0, 110)


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
    bld = [b for b in bld if abs(b[0]) < 6200 and abs(b[1]) < 4600]
    rd = roads(raw)
    polys, lines = river(raw)
    x0, y0, x1, y1 = BOX
    nx, ny = int((x1 - x0) / RES), int((y1 - y0) / RES)
    elev = dem_grid(raw, x0, y0, nx, ny)
    water = Image.new("L", (nx, ny), 0)
    d = ImageDraw.Draw(water)

    def px(p):
        return ((p[0] - x0) / RES, (y0 + ny * RES - p[1]) / RES)
    for poly in polys:
        d.polygon([px(p) for p in poly], fill=255)
    if not polys:
        for line in lines:
            d.line([px(p) for p in line], fill=255, width=int(130 / RES))
    for isl in ISLANDS:
        d.polygon([px(p) for p in isl], fill=0)
    water = np.array(water) > 127
    land = ~water
    elev = np.where(water, -2.0, np.maximum(elev, 0.6))
    shore = shore_distance(land, RES)
    np.savez_compressed(os.path.join(out, "terrain.npz"), land=land.astype(np.uint8), elev=elev.astype(np.float32),
                        shore=shore.astype(np.float32), box=np.array([x0, y0, RES, nx, ny], dtype=np.float64))
    zones = {k: [list(c) for c in list(z.exterior.coords)[:-1]] for k, z in
             (("cite", CITE), ("left", LEFT), ("philippe", PHILIPPE), ("charles", CHARLES), ("marais", MARAIS),
              ("haussmann", HAUSSMANN))}
    data = {"origin": [LAT0, LON0], "buildings": bld, "walls": walls, "roads": rd, "zones": zones,
            "sources": ["Overture Maps Foundation (incl. OpenStreetMap contributors, ODbL)",
                        "Copernicus GLO-30 DEM (ESA)"]}
    with gzip.open(os.path.join(out, "paris.json.gz"), "wt") as f:
        json.dump(data, f, separators=(",", ":"))
    est = sum(1 for b in bld if b[3])
    print("[city-studio] Paris: %d buildings (%d with estimated dates), %d roads, %d river polygons, %d river lines"
          % (len(bld), est, len(rd), len(polys), len(lines)))


if __name__ == "__main__":
    main()
