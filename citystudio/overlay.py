"""Draws the on-screen graphics on top of rendered frames.

Usage:  python3 overlay.py FRAMES_DIR N1 N2 ...
For every frame number N it reads frame_N.png and frame_N.json (written by
Blender) and saves comp_N.png with the year, era, ruler, population, compass,
captions, place labels and title card drawn on top.
Runs with the normal system Python (needs Pillow), not inside Blender.
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_DIRS = ["/usr/share/fonts/opentype/bebas-neue", "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF",
             "/usr/share/fonts/truetype/roboto/unhinted", "/usr/share/fonts/truetype/dejavu",
             os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts")]
FALLBACK = {"BebasNeue-Regular.otf": "DejaVuSansCondensed-Bold.ttf",
            "BebasNeue-Book.otf": "DejaVuSansCondensed.ttf",
            "Roboto-Medium.ttf": "DejaVuSans-Bold.ttf", "Roboto-Regular.ttf": "DejaVuSans.ttf",
            "Roboto-Bold.ttf": "DejaVuSans-Bold.ttf"}
_cache = {}
WARNED = set()


def font(name, size):
    key = (name, size)
    if key in _cache:
        return _cache[key]
    for candidate in (name, FALLBACK.get(name, name)):
        for d in FONT_DIRS:
            path = os.path.join(d, candidate)
            if os.path.exists(path):
                _cache[key] = ImageFont.truetype(path, size)
                return _cache[key]
        if candidate == name and name not in WARNED:
            WARNED.add(name)
            print("[city-studio] font %s not found - using a fallback (run ./studio setup)" % name)
    _cache[key] = ImageFont.load_default()
    return _cache[key]


class Layers:
    """Text goes on one layer, its soft shadow on another, then both are
    blended onto the frame in one go."""
    def __init__(self, size, s):
        self.s = s
        self.txt = Image.new("RGBA", size, (0, 0, 0, 0))
        self.shd = Image.new("RGBA", size, (0, 0, 0, 0))
        self.dt = ImageDraw.Draw(self.txt)
        self.ds = ImageDraw.Draw(self.shd)

    def text(self, xy, text, f, fill, alpha=1.0, anchor="la", spacing=0.0, shadow=0.75):
        if alpha <= 0.003 or not text:
            return
        a = int(255 * alpha)
        col = (*fill, a)
        sh = (0, 0, 0, int(255 * shadow * alpha))
        off = max(1, round(1.5 * self.s))
        if spacing <= 0:
            self.ds.text((xy[0] + off, xy[1] + off), text, font=f, fill=sh, anchor=anchor)
            self.dt.text(xy, text, font=f, fill=col, anchor=anchor)
            return
        widths = [self.dt.textlength(ch, font=f) for ch in text]
        total = sum(widths) + spacing * (len(text) - 1)
        x = xy[0] - (total / 2 if anchor[0] == "m" else total if anchor[0] == "r" else 0)
        va = "l" + anchor[1]
        for ch, w in zip(text, widths):
            self.ds.text((x + off, xy[1] + off), ch, font=f, fill=sh, anchor=va)
            self.dt.text((x, xy[1]), ch, font=f, fill=col, anchor=va)
            x += w + spacing

    def finish(self, frame):
        blur = self.shd.filter(ImageFilter.GaussianBlur(2.2 * self.s))
        frame.alpha_composite(blur)
        frame.alpha_composite(self.txt)
        return frame


_grad = {}


def gradients(w, h):
    if (w, h) not in _grad:
        g = Image.new("L", (1, h))
        for y in range(h):
            top = max(0.0, 1 - y / (0.20 * h)) * 0.35
            bot = max(0.0, (y - 0.66 * h) / (0.34 * h)) ** 1.4 * 0.62
            g.putpixel((0, y), int(255 * max(top, bot)))
        g = g.resize((w, h))
        black = Image.new("RGBA", (w, h), (0, 0, 0, 255))
        black.putalpha(g)
        _grad[(w, h)] = black
    return _grad[(w, h)]


def wrap(draw, text, f, width):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        test = (cur + " " + wd).strip()
        if draw.textlength(test, font=f) <= width or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def shield(draw, x, y, s, kind, alpha):
    if not kind:
        return
    w, h = 34 * s, 40 * s
    pts = [(x, y), (x + w, y), (x + w, y + h * 0.55)]
    for k in range(1, 12):
        t = k / 12
        pts.append((x + w - w / 2 * t, y + h * 0.55 + (h * 0.45) * math.sin(t * math.pi / 2)))
    for k in range(1, 12):
        t = k / 12
        pts.append((x + w / 2 - w / 2 * t, y + h - (h * 0.45) * (1 - math.cos(t * math.pi / 2))))
    pts.append((x, y + h * 0.55))
    a = int(255 * alpha)
    if kind == 1:
        draw.polygon(pts, fill=(36, 66, 128, a))
        right = [p for p in pts if p[0] >= x + w / 2 - 0.01] + [(x + w / 2, y + h), (x + w / 2, y)]
        draw.polygon(right, fill=(214, 120, 40, a))
        cx, cy, r = x + w / 2, y + h * 0.42, 7.5 * s
        star = []
        for k in range(10):
            ang = -math.pi / 2 + k * math.pi / 5
            rr = r if k % 2 == 0 else r * 0.42
            star.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
        draw.polygon(star, fill=(245, 242, 232, a))
    else:
        draw.polygon(pts, fill=(122, 24, 28, a))
        cx, cy = x + w / 2, y + h * 0.36
        draw.ellipse([cx - 5 * s, cy - 5 * s, cx + 5 * s, cy + 5 * s], outline=(232, 196, 92, a), width=max(1, int(2 * s)))
        draw.line([cx, cy + 5 * s, cx, cy + 17 * s], fill=(232, 196, 92, a), width=max(1, int(2.4 * s)))
        draw.line([cx, cy + 13 * s, cx + 5 * s, cy + 13 * s], fill=(232, 196, 92, a), width=max(1, int(2 * s)))
    draw.line(pts + [pts[0]], fill=(240, 238, 230, a), width=max(1, int(1.6 * s)))


def compose(frame_path, data, out_path):
    img = Image.open(frame_path).convert("RGBA")
    W, H = img.size
    s = H / 720.0
    X = lambda v: v * s  # noqa: E731  (720p layout, scaled to the render size)
    img.alpha_composite(gradients(W, H))
    L = Layers(img.size, s)
    gold, cream, white = (226, 200, 140), (240, 232, 214), (255, 255, 255)
    right = W - X(64)

    # title card
    tc = data.get("title_card")
    if tc:
        a = tc["alpha"]
        L.text((W / 2, X(226)), tc["kicker"].upper(), font("Roboto-Medium.ttf", int(X(15))), (232, 222, 200),
               a, "mm", spacing=X(4.5))
        L.text((W / 2, X(320)), tc["title"].upper(), font("BebasNeue-Book.otf", int(X(104))), (246, 240, 228),
               a, "mm", spacing=X(14), shadow=0.6)
        yf = font("BebasNeue-Regular.otf", int(X(30)))
        L.text((W / 2, X(416)), tc["years"], yf, gold, a, "mm", spacing=X(3))
        half = L.dt.textlength(tc["years"], font=yf) / 2 + X(26)
        for sgn in (-1, 1):
            x0, x1 = W / 2 + sgn * half, W / 2 + sgn * (half + X(95))
            L.dt.line([min(x0, x1), X(416), max(x0, x1), X(416)], fill=(*gold, int(200 * a)), width=max(1, int(X(1.2))))

    # top left: realm, shield and ruler
    has_shield = data.get("shield", 0)
    tx = X(66) + (X(48) if has_shield else 0)
    shield(L.dt, X(66), X(32), s, has_shield, 1.0)
    L.text((tx, X(31)), data.get("realm", "").upper(), font("BebasNeue-Regular.otf", int(X(31))), white)
    L.text((tx + X(1), X(66)), data.get("ruler", ""), font("Roboto-Regular.ttf", int(X(15))), (226, 226, 226))

    # top right: population and compass
    pf = font("Roboto-Medium.ttf", int(X(19)))
    value = data.get("population", "")
    L.text((right, X(34)), value, pf, white, anchor="ra")
    vw = L.dt.textlength(value, font=pf)
    L.text((right - vw - X(9), X(34)), "Population", pf, white, anchor="ra")
    L.text((right, X(59)), data.get("population_note", ""), font("Roboto-Regular.ttf", int(X(13))), (226, 226, 226),
           anchor="ra")
    cx, cy, r = right - X(28), X(112), X(15)
    L.dt.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255, 200), width=max(1, int(X(1.4))))
    L.ds.ellipse([cx - r + 1, cy - r + 1, cx + r + 1, cy + r + 1], outline=(0, 0, 0, 120), width=max(1, int(X(1.4))))
    ang = math.radians(-data.get("heading", 0.0))
    tip = (cx + math.sin(ang) * r * 0.8, cy - math.cos(ang) * r * 0.8)
    base = [(cx + math.sin(ang + sg * 2.6) * r * 0.45, cy - math.cos(ang + sg * 2.6) * r * 0.45) for sg in (-1, 1)]
    L.dt.polygon([tip, base[0], (cx, cy), base[1]], fill=(255, 255, 255, 235))
    L.text((cx, cy - r - X(8)), "N", font("Roboto-Bold.ttf", int(X(10))), white, anchor="mm")

    # bottom left: era, date and big year
    yr_font = font("BebasNeue-Regular.otf", int(X(108)))
    L.text((X(64), X(688)), str(data.get("year", "")), yr_font, white, anchor="ls", shadow=0.8)
    cap = data.get("caption") or {}
    date = cap.get("date")
    era_y = X(606)
    if date:
        L.text((X(66), X(606)), date.upper(), font("BebasNeue-Regular.otf", int(X(34))), cream, cap["alpha"], "ls")
        era_y = X(574)
    L.text((X(66), era_y), data.get("era", "").upper(), font("BebasNeue-Regular.otf", int(X(26))), gold, anchor="ls")

    # bottom centre: event caption
    if cap:
        a = cap["alpha"]
        L.text((W / 2, X(632)), cap["title"].upper(), font("BebasNeue-Regular.otf", int(X(33))), white, a, "ms",
               spacing=X(0.6))
        bf = font("Roboto-Regular.ttf", int(X(17)))
        for i, line in enumerate(wrap(L.dt, cap["body"], bf, X(620))[:3]):
            L.text((W / 2, X(657) + i * X(23)), line, bf, (236, 236, 236), a, "ms")

    # floating place labels
    lf = font("Roboto-Medium.ttf", int(X(12.5)))
    for lb in data.get("labels", []):
        a = lb["alpha"]
        if a <= 0.003:
            continue
        px, py = lb["x"] * W, lb["y"] * H
        L.dt.line([px, py - X(2), px, py - X(13)], fill=(255, 255, 255, int(220 * a)), width=max(1, int(X(1.2))))
        L.ds.line([px + 1, py - X(2) + 1, px + 1, py - X(13) + 1], fill=(0, 0, 0, int(150 * a)), width=max(1, int(X(1.2))))
        d = X(1.8)
        L.dt.ellipse([px - d, py - d, px + d, py + d], fill=(255, 255, 255, int(235 * a)))
        L.text((px, py - X(17)), lb["text"].upper(), lf, white, a, "ms", spacing=X(0.6), shadow=0.9)

    if data.get("fineprint"):
        L.text((right, H - X(14)), data["fineprint"], font("Roboto-Regular.ttf", int(X(10.5))), (230, 230, 230), 0.7,
               "rs")

    L.finish(img).convert("RGB").save(out_path, compress_level=1)


def main():
    folder = sys.argv[1]
    for n in sys.argv[2:]:
        n = int(n)
        src = os.path.join(folder, "frame_%06d.png" % n)
        info = os.path.join(folder, "frame_%06d.json" % n)
        out = os.path.join(folder, "comp_%06d.png" % n)
        if os.path.exists(out) and os.path.getsize(out) > 0:
            continue
        with open(info) as f:
            data = json.load(f)
        compose(src, data, out + ".tmp.png")
        os.replace(out + ".tmp.png", out)


if __name__ == "__main__":
    main()
