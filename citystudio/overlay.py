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
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_DIRS = ["/usr/share/fonts/opentype/bebas-neue", "/usr/share/fonts/opentype/league-spartan",
             "/usr/share/fonts/truetype/lato", "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF",
             "/usr/share/fonts/truetype/roboto/unhinted", "/usr/share/fonts/truetype/dejavu",
             os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts")]
FALLBACK = {"BebasNeue-Regular.otf": "DejaVuSansCondensed-Bold.ttf",
            "BebasNeue-Book.otf": "DejaVuSansCondensed.ttf",
            "Roboto-Medium.ttf": "DejaVuSans-Bold.ttf", "Roboto-Regular.ttf": "DejaVuSans.ttf",
            "Roboto-Bold.ttf": "DejaVuSans-Bold.ttf",
            "LeagueSpartan-Bold.otf": "DejaVuSans-Bold.ttf", "LeagueSpartan-Medium.otf": "DejaVuSans-Bold.ttf",
            "LeagueSpartan-Black.otf": "DejaVuSans-Bold.ttf", "Lato-Bold.ttf": "DejaVuSans-Bold.ttf",
            "Lato-Regular.ttf": "DejaVuSans.ttf", "Lato-Semibold.ttf": "DejaVuSans-Bold.ttf",
            "Lato-Black.ttf": "DejaVuSans-Bold.ttf"}
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


def badge(layer, draw, cx, cy, r, kind, alpha):
    """Small round flag badge: nl = Dutch tricolour, gb = cross on white, us = stripes and canton."""
    if not kind:
        return
    a = int(255 * alpha)
    box = [cx - r, cy - r, cx + r, cy + r]
    size = int(r * 2) + 2
    flag = Image.new("RGBA", (size * 4, size * 4), (0, 0, 0, 0))
    fd = ImageDraw.Draw(flag)
    S = size * 4
    if kind == "nl":
        for i, c in enumerate([(222, 120, 40), (245, 245, 240), (36, 70, 140)]):
            fd.rectangle([0, i * S / 3, S, (i + 1) * S / 3], fill=(*c, 255))
    elif kind == "gb":
        fd.rectangle([0, 0, S, S], fill=(245, 245, 240, 255))
        fd.rectangle([S * 0.42, 0, S * 0.58, S], fill=(196, 30, 40, 255))
        fd.rectangle([0, S * 0.42, S, S * 0.58], fill=(196, 30, 40, 255))
    elif kind == "us":
        for i in range(7):
            fd.rectangle([0, i * S / 7, S, (i + 0.5) * S / 7], fill=(190, 30, 45, 255))
            fd.rectangle([0, (i + 0.5) * S / 7, S, (i + 1) * S / 7], fill=(245, 245, 240, 255))
        fd.rectangle([0, 0, S * 0.5, S * 0.5], fill=(30, 50, 110, 255))
    elif kind == "spqr":
        fd.rectangle([0, 0, S, S], fill=(130, 18, 30, 255))
        fd.rectangle([S * 0.18, S * 0.42, S * 0.82, S * 0.58], fill=(226, 184, 70, 255))
        fd.polygon([(S * 0.5, S * 0.12), (S * 0.62, S * 0.36), (S * 0.38, S * 0.36)], fill=(226, 184, 70, 255))
    elif kind == "kingdom":
        fd.rectangle([0, 0, S, S], fill=(110, 70, 40, 255))
        fd.ellipse([S * 0.3, S * 0.3, S * 0.7, S * 0.7], fill=(220, 190, 120, 255))
    elif kind == "goth":
        fd.rectangle([0, 0, S, S], fill=(60, 70, 95, 255))
        fd.rectangle([S * 0.44, S * 0.12, S * 0.56, S * 0.88], fill=(220, 200, 140, 255))
    elif kind == "byz":
        fd.rectangle([0, 0, S, S], fill=(95, 30, 110, 255))
        fd.rectangle([S * 0.44, S * 0.15, S * 0.56, S * 0.85], fill=(235, 195, 70, 255))
        fd.rectangle([S * 0.2, S * 0.38, S * 0.8, S * 0.5], fill=(235, 195, 70, 255))
    elif kind == "papal":
        fd.rectangle([0, 0, S / 2, S], fill=(250, 215, 40, 255))
        fd.rectangle([S / 2, 0, S, S], fill=(245, 245, 240, 255))
    elif kind in ("italy", "italy_k", "repub1849", "france"):
        cols = [(20, 140, 70), (245, 245, 240), (205, 33, 42)] if kind != "france" else [(30, 60, 150), (245, 245, 240), (205, 33, 42)]
        for i, c in enumerate(cols):
            fd.rectangle([i * S / 3, 0, (i + 1) * S / 3, S], fill=(*c, 255))
        if kind == "italy_k":
            fd.rectangle([S * 0.42, S * 0.36, S * 0.58, S * 0.62], fill=(205, 33, 42, 255))
            fd.rectangle([S * 0.48, S * 0.38, S * 0.52, S * 0.6], fill=(245, 245, 240, 255))
    elif kind == "occupied":
        fd.rectangle([0, 0, S, S], fill=(110, 110, 110, 255))
    elif kind == "gaul":
        fd.rectangle([0, 0, S, S], fill=(40, 90, 60, 255))
        fd.ellipse([S * 0.28, S * 0.28, S * 0.72, S * 0.72], outline=(230, 200, 110, 255), width=max(1, S // 10))
    elif kind == "frank":
        fd.rectangle([0, 0, S, S], fill=(150, 40, 40, 255))
        fd.polygon([(S * 0.5, S * 0.2), (S * 0.62, S * 0.5), (S * 0.5, S * 0.8), (S * 0.38, S * 0.5)], fill=(235, 195, 70, 255))
    elif kind == "fleur":
        fd.rectangle([0, 0, S, S], fill=(25, 50, 140, 255))
        for cx_, cy_ in ((0.3, 0.32), (0.7, 0.32), (0.5, 0.68)):
            fd.ellipse([S * (cx_ - 0.09), S * (cy_ - 0.09), S * (cx_ + 0.09), S * (cy_ + 0.09)], fill=(235, 200, 70, 255))
    elif kind == "commune":
        fd.rectangle([0, 0, S, S], fill=(190, 20, 25, 255))
    elif kind == "england":
        fd.rectangle([0, 0, S, S], fill=(245, 245, 240, 255))
        fd.rectangle([S * 0.42, 0, S * 0.58, S], fill=(200, 16, 46, 255))
        fd.rectangle([0, S * 0.42, S, S * 0.58], fill=(200, 16, 46, 255))
    elif kind == "uk":
        fd.rectangle([0, 0, S, S], fill=(1, 33, 105, 255))
        for w_, c_ in ((S * 0.2, (245, 245, 240)), (S * 0.08, (200, 16, 46))):
            fd.line([0, 0, S, S], fill=(*c_, 255), width=int(w_))
            fd.line([0, S, S, 0], fill=(*c_, 255), width=int(w_))
        fd.rectangle([S * 0.38, 0, S * 0.62, S], fill=(245, 245, 240, 255))
        fd.rectangle([0, S * 0.38, S, S * 0.62], fill=(245, 245, 240, 255))
        fd.rectangle([S * 0.44, 0, S * 0.56, S], fill=(200, 16, 46, 255))
        fd.rectangle([0, S * 0.44, S, S * 0.56], fill=(200, 16, 46, 255))
    elif kind == "saxon":
        fd.rectangle([0, 0, S, S], fill=(160, 30, 30, 255))
        fd.ellipse([S * 0.3, S * 0.3, S * 0.7, S * 0.7], fill=(230, 190, 60, 255))
    elif kind == "dane":
        fd.rectangle([0, 0, S, S], fill=(40, 40, 50, 255))
        fd.polygon([(S * 0.25, S * 0.7), (S * 0.5, S * 0.25), (S * 0.75, S * 0.7)], fill=(220, 200, 160, 255))
    elif kind == "lenape":
        fd.rectangle([0, 0, S, S], fill=(70, 110, 70, 255))
        fd.ellipse([S * 0.3, S * 0.3, S * 0.7, S * 0.7], outline=(240, 230, 200, 255), width=max(1, S // 14))
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, S - 1, S - 1], fill=a)
    flag.putalpha(mask)
    flag = flag.resize((size, size), Image.LANCZOS)
    layer.alpha_composite(flag, (int(cx - size / 2), int(cy - size / 2)))
    draw.ellipse(box, outline=(255, 255, 255, int(220 * alpha)), width=max(1, int(r / 7)))


_agrad = {}


def atlas_gradients(w, h):
    if (w, h) not in _agrad:
        g = Image.new("L", (w, h))
        px = g.load()
        for y in range(h):
            for x in range(0, w, 4):
                tl = max(0.0, 1 - math.hypot(x / (0.42 * w), y / (0.34 * h))) * 0.55
                tr = max(0.0, 1 - math.hypot((w - x) / (0.30 * w), y / (0.26 * h))) * 0.45
                bot = max(0.0, (y - 0.70 * h) / (0.30 * h)) ** 1.3 * 0.6
                v = int(255 * min(0.75, max(tl, tr, bot)))
                for k in range(4):
                    if x + k < w:
                        px[x + k, y] = v
        black = Image.new("RGBA", (w, h), (8, 10, 14, 255))
        black.putalpha(g)
        _agrad[(w, h)] = black
    return _agrad[(w, h)]


def weather(img, data):
    """Falling snow and rain, drawn over the rendered picture."""
    w = data.get("weather") or {}
    snow, rain, t = w.get("snow", 0), w.get("rain", 0), w.get("t", 0)
    if snow < 0.02 and rain < 0.02:
        return
    W, H = img.size
    s = H / 720.0
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rnd = random.Random(42)
    for i in range(int(420 * snow)):
        x0, y0 = rnd.uniform(0, W), rnd.uniform(0, H)
        speed, size = rnd.uniform(40, 110) * s, rnd.uniform(1.0, 3.2) * s
        y = (y0 + t * speed) % H
        x = (x0 + 14 * s * math.sin(t * 0.9 + i)) % W
        d.ellipse([x - size, y - size, x + size, y + size], fill=(255, 255, 255, int(210 * snow)))
    for i in range(int(520 * rain)):
        x0, y0 = rnd.uniform(0, W), rnd.uniform(0, H)
        speed, length = rnd.uniform(700, 1100) * s, rnd.uniform(14, 30) * s
        y = (y0 + t * speed) % H
        x = (x0 - t * speed * 0.18) % W
        d.line([x, y, x - length * 0.18, y + length], fill=(205, 215, 230, int(95 * rain)), width=max(1, int(s)))
    if rain > 0.02:
        img.alpha_composite(Image.new("RGBA", img.size, (60, 70, 85, int(40 * rain))))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(0.6 * s)))


def grade(img, data):
    g = data.get("grade")
    if not g:
        return img
    from PIL import ImageEnhance
    rgb = img.convert("RGB")
    rgb = ImageEnhance.Color(rgb).enhance(g.get("saturation", 1.0))
    rgb = ImageEnhance.Contrast(rgb).enhance(g.get("contrast", 1.0))
    rgb = ImageEnhance.Brightness(rgb).enhance(g.get("brightness", 1.0))
    return rgb.convert("RGBA")


FW_COLOURS = [(255, 90, 80), (255, 210, 90), (120, 200, 255), (140, 255, 150), (255, 130, 230)]


def fireworks(img, data):
    fws = data.get("fireworks") or []
    if not fws:
        return
    W, H = img.size
    s = H / 720.0
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for fw in fws:
        age = fw["age"]
        if age > 1.3:
            continue
        r = (20 + 70 * min(1.0, age / 0.5)) * s * fw["scale"]
        a = int(255 * max(0.0, 1.0 - max(0.0, age - 0.4) / 0.9))
        cx, cy = fw["x"] * W, fw["y"] * H - 40 * s * fw["scale"]
        col = FW_COLOURS[fw["hue"] % len(FW_COLOURS)]
        for k in range(28):
            ang = k * 2 * math.pi / 28
            x1, y1 = cx + math.cos(ang) * r, cy + math.sin(ang) * r + age * 18 * s
            x0, y0 = cx + math.cos(ang) * r * 0.75, cy + math.sin(ang) * r * 0.75 + age * 12 * s
            d.line([x0, y0, x1, y1], fill=(*col, a), width=max(1, int(2 * s)))
            d.ellipse([x1 - 1.6 * s, y1 - 1.6 * s, x1 + 1.6 * s, y1 + 1.6 * s], fill=(255, 250, 230, a))
    glow = layer.filter(ImageFilter.GaussianBlur(4 * s))
    img.alpha_composite(glow)
    img.alpha_composite(layer)


def compose_atlas(img, data):
    W, H = img.size
    s = H / 720.0
    X = lambda v: v * s  # noqa: E731
    img = grade(img, data)
    weather(img, data)
    fireworks(img, data)
    img.alpha_composite(atlas_gradients(W, H))
    L = Layers(img.size, s)
    amber, white, soft = (240, 178, 74), (255, 255, 255), (222, 226, 230)
    left, right = X(56), W - X(56)

    tc = data.get("title_card")
    if tc:
        a = tc["alpha"]
        L.text((W / 2, X(262)), tc.get("kicker", "").upper(), font("Lato-Bold.ttf", int(X(17))), amber, a, "mm",
               spacing=X(6))
        L.text((W / 2, X(342)), tc.get("title", "").upper(), font("LeagueSpartan-Bold.otf", int(X(118))), white,
               a, "mm", spacing=X(4), shadow=0.7)
        L.dt.rectangle([W / 2 - X(60), X(404), W / 2 + X(60), X(408)], fill=(*amber, int(255 * a)))
        L.text((W / 2, X(438)), tc.get("years", ""), font("Lato-Semibold.ttf", int(X(22))), soft, a, "mm",
               spacing=X(3))
        if tc.get("note"):
            L.text((W / 2, X(470)), tc["note"], font("Lato-Regular.ttf", int(X(15))), soft, a, "mm")

    # top left: era, year, ruler badge
    L.text((left + X(2), X(42)), data.get("era", "").upper(), font("Lato-Bold.ttf", int(X(14))), amber, spacing=X(3.5))
    yt = data.get("year_text") or str(data.get("year", ""))
    L.text((left - X(2), X(128)), yt, font("LeagueSpartan-Bold.otf", int(X(92 if len(yt) <= 6 else 74))), white,
           anchor="ls", shadow=0.85)
    by = X(156)
    tx = left
    if data.get("badge"):
        badge(L.txt, L.dt, left + X(11), by, X(11), data["badge"], 1.0)
        tx = left + X(30)
    rf = font("Lato-Bold.ttf", int(X(15)))
    realm = data.get("realm", "")
    L.text((tx, by), realm, rf, white, anchor="lm")
    if data.get("ruler"):
        rx = tx + L.dt.textlength(realm, font=rf) + X(8)
        L.text((rx, by), "·  " + data["ruler"], font("Lato-Regular.ttf", int(X(15))), soft, anchor="lm")

    # top right: two counters
    lab = font("Lato-Bold.ttf", int(X(11)))
    val = font("LeagueSpartan-Bold.otf", int(X(30)))
    L.text((right, X(40)), data.get("population_label", "").upper(), lab, amber, anchor="ra", spacing=X(2.5))
    L.text((right, X(84)), data.get("population", "") or "—", val, white, anchor="rs")
    L.text((right, X(110)), data.get("standing_label", "").upper(), lab, amber, anchor="ra", spacing=X(2.5))
    L.text((right, X(154)), data.get("standing", ""), val, white, anchor="rs")

    # bottom left: caption with a date tag
    cap = data.get("caption")
    if cap:
        a = cap["alpha"]
        tf = font("LeagueSpartan-Bold.otf", int(X(17)))
        tag = cap.get("tag", "")
        tw = L.dt.textlength(tag, font=tf)
        y0 = X(592)
        L.dt.rounded_rectangle([left, y0 - X(13), left + tw + X(20), y0 + X(13)], radius=X(4),
                               fill=(*amber, int(235 * a)))
        L.dt.text((left + X(10), y0 + X(1)), tag, font=tf, fill=(24, 20, 14, int(255 * a)), anchor="lm")
        L.text((left + tw + X(32), y0 + X(2)), cap["title"], font("LeagueSpartan-Bold.otf", int(X(28))), white, a,
               "lm")
        bf = font("Lato-Regular.ttf", int(X(17)))
        for i, line in enumerate(wrap(L.dt, cap["body"], bf, X(760))[:2]):
            L.text((left, X(634) + i * X(24)), line, bf, soft, a, "ls")

    # place labels: amber ring and text to the right
    lf = font("LeagueSpartan-Bold.otf", int(X(17)))
    label_col = tuple(data.get("label_color") or (255, 255, 255))   # bold white with a dark outline
    for lb in data.get("labels", []):
        a = lb["alpha"]
        if a <= 0.003:
            continue
        px, py = lb["x"] * W, lb["y"] * H
        r = X(4.2)
        L.ds.ellipse([px - r + 1, py - r + 1, px + r + 1, py + r + 1], outline=(0, 0, 0, int(160 * a)),
                     width=max(1, int(X(2))))
        L.dt.ellipse([px - r, py - r, px + r, py + r], outline=(*amber, int(255 * a)), width=max(1, int(X(2))))
        L.dt.ellipse([px - X(1.6), py - X(1.6), px + X(1.6), py + X(1.6)], fill=(255, 255, 255, int(255 * a)))
        L.ds.text((px + X(10.5), py + X(1.5)), lb["text"].upper(), font=lf, fill=(0, 0, 0, int(200 * a)), anchor="lm",
                  stroke_width=max(1, int(X(2.5))), stroke_fill=(0, 0, 0, int(200 * a)))
        L.dt.text((px + X(9), py), lb["text"].upper(), font=lf, fill=(*label_col, int(255 * a)), anchor="lm",
                  stroke_width=max(1, int(X(1.6))), stroke_fill=(10, 10, 12, int(235 * a)))

    # bottom right: compass arrow and fine print
    cx, cy = right - X(10), H - X(62)
    ang = math.radians(-data.get("heading", 0.0))
    tip = (cx + math.sin(ang) * X(13), cy - math.cos(ang) * X(13))
    tail = (cx - math.sin(ang) * X(9), cy + math.cos(ang) * X(9))
    side = [(cx + math.sin(ang + sg * 1.9) * X(6), cy - math.cos(ang + sg * 1.9) * X(6)) for sg in (-1, 1)]
    L.dt.polygon([tip, side[0], tail, side[1]], fill=(255, 255, 255, 230))
    L.dt.polygon([tip, side[0], (cx, cy), side[1]], fill=(*amber, 255))
    L.text((cx, cy - X(24)), "N", font("Lato-Bold.ttf", int(X(11))), white, anchor="mm")
    if data.get("fineprint"):
        L.text((right, H - X(18)), data["fineprint"], font("Lato-Regular.ttf", int(X(11))), soft, 0.75, "rs")
    return L.finish(img)


def compose(frame_path, data, out_path):
    img = Image.open(frame_path).convert("RGBA")
    if data.get("design") == "atlas":
        compose_atlas(img, data).convert("RGB").save(out_path, compress_level=1)
        return
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
