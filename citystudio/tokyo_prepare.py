"""Turns raw Tokyo downloads into data/tokyo/ for the renderer (based on rome_prepare).

Usage:  python3 citystudio/tokyo_prepare.py RAW_DIR OUT_DIR
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

LAT0, LON0 = 35.6852, 139.7528
KX = 111320.0 * math.cos(math.radians(LAT0))
KY = 111132.0
BOX = (-6500.0, -6500.0, 7500.0, 5500.0)          # x0, y0, x1, y1 in metres
RES = 18.0


def proj(lon, lat):
    return ((lon - LON0) * KX, (lat - LAT0) * KY)


def poly_m(lonlats):
    return Polygon([proj(lo, la) for lo, la in lonlats])


# Approximate historic zones (lon, lat). Illustrative outlines, not surveyed lines.
CASTLE = poly_m([(139.7440, 35.6800), (139.7440, 35.6920), (139.7600, 35.6920), (139.7620, 35.6800)])
SHITAMACHI = poly_m([(139.7620, 35.6680), (139.7650, 35.6980), (139.7850, 35.7200), (139.8050, 35.7150),
                     (139.8100, 35.6800), (139.7950, 35.6650), (139.7750, 35.6650)])
ASAKUSA = poly_m([(139.7860, 35.7050), (139.7860, 35.7200), (139.8010, 35.7200), (139.8010, 35.7050)])
YAMANOTE = poly_m([(139.7150, 35.6600), (139.7150, 35.7150), (139.7650, 35.7250), (139.7650, 35.6620)])
WEST = poly_m([(139.6900, 35.6450), (139.6900, 35.7350), (139.7150, 35.7350), (139.7150, 35.6450)])
# the shore around 1600: land south/east of this line was reclaimed from the sea later
SHORE_1600 = [(139.7300, 35.6150), (139.7420, 35.6300), (139.7520, 35.6480), (139.7580, 35.6600),
              (139.7600, 35.6700), (139.7580, 35.6800), (139.7660, 35.6790), (139.7730, 35.6760),
              (139.7850, 35.6760), (139.7950, 35.6740), (139.8150, 35.6720), (139.8400, 35.6700)]

LANDMARKS = {
    "東京駅": (1914, None), "国会議事堂": (1936, None), "東京都庁": (1991, None), "東京ドーム": (1988, None),
    "日本武道館": (1964, None), "国立西洋美術館": (1959, None), "歌舞伎座": (2013, None), "サンシャイン60": (1978, None),
    "六本木ヒルズ": (2003, None), "迎賓館": (1909, None), "明治神宮": (1920, None), "上野駅": (1932, None),
    "東京国立博物館": (1938, None), "日本銀行": (1896, None), "和光": (1932, None), "三越": (1914, None),
    "東京ミッドタウン": (2007, None), "麻布台ヒルズ": (2023, None), "虎ノ門ヒルズ": (2014, None), "東京国際フォーラム": (1996, None),
}
SKIP = ("東京タワー", "東京スカイツリー", "浅草寺", "五重塔", "雷門", "増上寺", "寛永寺", "皇居", "宮殿", "伏見櫓", "富士見櫓",
        "日本橋", "両国橋", "レインボーブリッジ", "tokyo tower", "skytree", "senso-ji")


_SEA = None
_SHORE = None


def reclaimed(x, y):
    """Distance (m) seaward of the 1600 shore, or 0 for land that already existed."""
    global _SEA, _SHORE
    if _SEA is None:
        from shapely.geometry import LineString
        pts = [proj(lo, la) for lo, la in SHORE_1600]
        _SHORE = LineString(pts)
        far = [(pts[-1][0] + 4000, pts[-1][1]), (pts[-1][0] + 4000, -20000), (pts[0][0], -20000)]
        _SEA = Polygon(pts + far)
    p = Point(x, y)
    return _SHORE.distance(p) if _SEA.contains(p) else 0.0


def fill_year(d):
    if d <= 0:
        return 0
    if d < 350:
        return int(1592 + d * 0.3)              # Edo-period fills (Hibiya inlet, Tsukiji, Fukagawa)
    if d < 1500:
        return int(1880 + (d - 350) * 0.03)     # Meiji: Tsukishima, Shibaura
    return int(min(1995, 1930 + (d - 1500) * 0.016))   # 20th century: Harumi, Toyosu, Odaiba


def estimate_year(cx, cy, rng):
    p = Point(cx, cy)
    f = fill_year(reclaimed(cx, cy))
    base = None
    if CASTLE.contains(p):
        base = int(rng.triangular(1890, 2020, 1960))
    elif SHITAMACHI.contains(p) or ASAKUSA.contains(p):
        base = int(rng.triangular(1924, 2022, 1975))       # rebuilt after 1923 and 1945
    elif YAMANOTE.contains(p):
        base = int(rng.triangular(1930, 2022, 1980))
    else:
        d = math.hypot(cx, cy)
        base = int(min(2018, rng.triangular(1930, 2022, 1975) + max(0.0, d - 5000) * 0.002))
    return max(base, f + 5)


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
    """Sea, rivers, canals and moats as polygons; river centre lines as a fallback."""
    polys, lines = [], []
    for r in json.load(open(os.path.join(raw, "water_all.json"))):
        sub, cls = r.get("subtype"), r.get("class")
        g = shapely.wkt.loads(r["wkt"])
        if g.geom_type in ("Polygon", "MultiPolygon"):
            if sub in ("ocean", "river", "canal") or cls in ("moat", "canal", "river", "ocean"):
                for p in ([g] if g.geom_type == "Polygon" else list(g.geoms)):
                    polys.append([proj(lo, la) for lo, la in p.exterior.coords])
                    for hole in p.interiors:
                        ISLANDS.append([proj(lo, la) for lo, la in hole.coords])
        elif sub == "river" and g.geom_type == "LineString":
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
    """Copernicus DSM tile N35 E139, buildings removed, smoothed."""
    a = np.array(Image.open(os.path.join(raw, "dem.tif")), dtype=np.float32)
    jj, ii = np.mgrid[0:ny, 0:nx]
    X = x0 + (ii + 0.5) * RES
    Y = y0 + ny * RES - (jj + 0.5) * RES
    lon = LON0 + X / KX
    lat = LAT0 + Y / KY
    row = np.clip(((36.0 - lat) * a.shape[0]).astype(int), 0, a.shape[0] - 1)
    col = np.clip(((lon - 139.0) * a.shape[1]).astype(int), 0, a.shape[1] - 1)
    sm = a[row, col].astype(np.float64)
    r = 8
    for axis in (0, 1):
        p = np.pad(sm, [(r, r) if q == axis else (0, 0) for q in (0, 1)], mode="edge")
        sm = np.min(np.stack([np.take(p, range(k, k + sm.shape[axis]), axis=axis) for k in range(2 * r + 1)]), axis=0)
    for _ in range(3):
        sm = box_blur(sm, 9)
    return np.clip(sm, 0, 60)


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


def poly_area(flat):
    xs, ys = flat[0::2], flat[1::2]
    return 0.5 * sum(xs[i] * ys[(i + 1) % len(xs)] - xs[(i + 1) % len(xs)] * ys[i] for i in range(len(xs)))


def main():
    raw, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    rng = random.Random(11)
    bld, walls = buildings(raw, rng)
    bld = [b for b in bld if -5800 < b[0] < 6800 and -5800 < b[1] < 4800]
    # Tokyo has many very small houses: keep all larger buildings and every third small one
    thin = random.Random(3)
    bld = [b for b in bld if b[4] > 14 or len(b[5]) > 10 or abs(poly_area(b[5])) > 160 or thin.random() < 0.33]
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
    # centre lines fill any stretch of river the outlines do not cover
    lmask = Image.new("L", (nx, ny), 0)
    ld = ImageDraw.Draw(lmask)
    for line in lines:
        ld.line([px(p) for p in line], fill=255, width=int(90 / RES))
    for isl in ISLANDS:
        d.polygon([px(p) for p in isl], fill=0)
    water = np.array(water) > 127
    near = water.copy()
    for _ in range(int(150 / RES)):                    # within 150 m of a drawn outline
        near = near | np.roll(near, 1, 0) | np.roll(near, -1, 0) | np.roll(near, 1, 1) | np.roll(near, -1, 1)
    water = water | ((np.array(lmask) > 127) & ~near)
    land = ~water
    elev = np.where(water, -2.0, np.maximum(elev, 0.6))
    shore = shore_distance(land, RES)
    np.savez_compressed(os.path.join(out, "terrain.npz"), land=land.astype(np.uint8), elev=elev.astype(np.float32),
                        shore=shore.astype(np.float32), box=np.array([x0, y0, RES, nx, ny], dtype=np.float64))
    zones = {k: [list(c) for c in list(z.exterior.coords)[:-1]] for k, z in
             (("castle", CASTLE), ("shitamachi", SHITAMACHI), ("asakusa", ASAKUSA), ("yamanote", YAMANOTE),
              ("west", WEST))}
    data = {"origin": [LAT0, LON0], "buildings": bld, "walls": walls, "roads": rd, "zones": zones,
            "sources": ["Overture Maps Foundation (incl. OpenStreetMap contributors, ODbL)",
                        "Copernicus GLO-30 DEM (ESA)"]}
    fill = np.zeros((ny, nx), dtype=np.int16)
    for j in range(ny):
        for i in range(nx):
            if land[j, i]:
                fill[j, i] = fill_year(reclaimed(x0 + (i + 0.5) * RES, y0 + ny * RES - (j + 0.5) * RES))
    np.savez_compressed(os.path.join(out, "terrain.npz"), land=land.astype(np.uint8), elev=elev.astype(np.float32),
                        shore=shore.astype(np.float32), fill=fill, box=np.array([x0, y0, RES, nx, ny], dtype=np.float64))
    with gzip.open(os.path.join(out, "tokyo.json.gz"), "wt") as f:
        json.dump(data, f, separators=(",", ":"))
    est = sum(1 for b in bld if b[3])
    print("[city-studio] Tokyo: %d buildings (%d with estimated dates), %d roads, %d river polygons, %d river lines"
          % (len(bld), est, len(rd), len(polys), len(lines)))


if __name__ == "__main__":
    main()
