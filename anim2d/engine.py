"""Minimal 2D animation engine (Skia): flat white line-art figures on black, drawn and animated in code.

Everything is a function of time, so micro-actions (blink, breathe, tremble, talk, steam, flicker)
are just maths on t. Frames are piped straight to ffmpeg.
"""
import math, os, random
import skia

W, H, FPS = 1920, 1080, 24
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "assets", "fonts")

# ---------------- palette ----------------
def C(hexs, a=1.0):
    h = hexs.lstrip("#"); return skia.Color4f(int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)
BG, INK, WHITE, GREY, DIM, DARK = "#0a0a0b", "#1c1c1f", "#f1f1ee", "#9b9b98", "#4a4a4c", "#262628"
AMBER, ACID, RED, TEAR, TV = "#e3a63a", "#b6ff3b", "#e5392b", "#7fc4ff", "#8fb4ff"
MOOD = {"normal": dict(white=WHITE, line=GREY), "frozen": dict(white="#e3f0d6", line="#7f8f6f"),
        "dark": dict(white="#bdbdb8", line="#6a6a68")}

# ---------------- easing / noise ----------------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def lerp(a, b, x): return a + (b - a) * x
def wobble(t, seed=0, amp=1.0, speed=1.0):
    """Smooth pseudo-random motion (sum of sines) for organic micro-movement."""
    return amp * (math.sin(t * 1.7 * speed + seed * 3.1) * 0.6 + math.sin(t * 3.3 * speed + seed * 1.3) * 0.3
                  + math.sin(t * 7.1 * speed + seed * 5.7) * 0.1)
def blinking(t, seed=0, every=3.2):
    """True during a natural blink (~0.13s), roughly every `every` seconds with jitter."""
    period = every + (seed % 7) * 0.23
    ph = (t + seed * 0.71) % period
    return ph < 0.13

# ---------------- pen ----------------
_tf = {}
def font(name, size):
    key = (name, size)
    if key not in _tf:
        _tf[key] = skia.Font(skia.Typeface.MakeFromFile(os.path.join(FONTS, name)), size)
    return _tf[key]

class Pen:
    def __init__(self, canvas, mood="normal"):
        self.c = canvas; self.mood = mood
    @property
    def white(self): return MOOD[self.mood]["white"]
    @property
    def line(self): return MOOD[self.mood]["line"]
    def paint(self, color, a=1.0, stroke=0, blur=0, cap=True):
        p = skia.Paint(AntiAlias=True, Color4f=C(color, a))
        if stroke:
            p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
            if cap: p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
        if blur: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
        return p
    # shapes: fill + optional outline
    def circle(self, x, y, r, fill=None, stroke=None, w=3, a=1.0, blur=0):
        if fill: self.c.drawCircle(x, y, r, self.paint(fill, a, blur=blur))
        if stroke: self.c.drawCircle(x, y, r, self.paint(stroke, a, w))
    def oval(self, x, y, rx, ry, fill=None, stroke=None, w=3, a=1.0):
        rc = skia.Rect.MakeLTRB(x - rx, y - ry, x + rx, y + ry)
        if fill: self.c.drawOval(rc, self.paint(fill, a))
        if stroke: self.c.drawOval(rc, self.paint(stroke, a, w))
    def rect(self, x, y, w_, h_, fill=None, stroke=None, w=3, a=1.0, r=0):
        rc = skia.Rect.MakeXYWH(x, y, w_, h_)
        if fill: self.c.drawRoundRect(rc, r, r, self.paint(fill, a))
        if stroke: self.c.drawRoundRect(rc, r, r, self.paint(stroke, a, w, cap=False))
    def ln(self, x0, y0, x1, y1, color, w=4, a=1.0, blur=0):
        self.c.drawLine(x0, y0, x1, y1, self.paint(color, a, w, blur=blur))
    def poly(self, pts, fill=None, stroke=None, w=3, a=1.0, blur=0, closed=True):
        p = skia.Path(); p.moveTo(*pts[0])
        for q in pts[1:]: p.lineTo(*q)
        if closed: p.close()
        if fill: self.c.drawPath(p, self.paint(fill, a, blur=blur))
        if stroke: self.c.drawPath(p, self.paint(stroke, a, w))
    def path(self, build, fill=None, stroke=None, w=3, a=1.0, blur=0):
        p = skia.Path(); build(p)
        if fill: self.c.drawPath(p, self.paint(fill, a, blur=blur))
        if stroke: self.c.drawPath(p, self.paint(stroke, a, w))
    def arc(self, x, y, rx, ry, start, sweep, color, w=3, a=1.0):
        self.c.drawArc(skia.Rect.MakeLTRB(x - rx, y - ry, x + rx, y + ry), start, sweep, False, self.paint(color, a, w))
    def text(self, s, x, y, size, color=WHITE, name="Anton-Regular.ttf", a=1.0, align="center"):
        f = font(name, size); wdt = f.measureText(s)
        dx = {"center": -wdt / 2, "left": 0, "right": -wdt}[align]
        self.c.drawString(s, x + dx, y, f, self.paint(color, a))
    def glow(self, x, y, r, color, a=0.5):
        sh = skia.GradientShader.MakeRadial((x, y), r, [C(color, a), C(color, 0)])
        p = skia.Paint(AntiAlias=True); p.setShader(sh); self.c.drawCircle(x, y, r, p)
    # transforms
    def push(self, tx=0, ty=0, s=1.0, rot=0, ox=0, oy=0):
        self.c.save(); self.c.translate(tx + ox, ty + oy); self.c.rotate(rot); self.c.scale(s, s); self.c.translate(-ox, -oy)
    def pop(self): self.c.restore()

# ---------------- characters ----------------
# kinds: mom, dad, sis, you, kid (generic)
SIZES = {"dad": 380, "mom": 360, "you": 290, "sis": 240, "kid": 270, "old": 330, "tola": 270, "toddler": 170}

def face(pen, x, y, r, f, t, seed):
    """f: dict eyes=('dot'|'wide'|'closed'|'happy'|'side'|'angry'), look=(dx,dy) -1..1,
    mouth=('smile'|'flat'|'open'|'o'|'grin'|'frown'|'wobble'|'talk'), tears=0..1, tremble=0..1, red=0..1"""
    eyes = f.get("eyes", "dot"); ex = r * 0.36; ey = y - r * 0.08
    if f.get("blink", True) and eyes in ("dot", "side") and blinking(t, seed): eyes = "closed"
    lx, ly = f.get("look", (0, 0))
    tr = f.get("tremble", 0) * r * 0.03
    jx, jy = wobble(t, seed, tr, 9), wobble(t, seed + 5, tr, 11)
    for sx in (-1, 1):
        cx = x + sx * ex
        if eyes == "closed":
            pen.arc(cx, ey, r * 0.11, r * 0.06, 20, 140, INK, max(2, r * 0.045))
        elif eyes == "happy":
            pen.arc(cx, ey + r * 0.04, r * 0.11, r * 0.09, 200, 140, INK, max(2, r * 0.045))
        elif eyes == "angry":
            pen.circle(cx + lx * r * 0.04, ey, r * 0.07, fill=INK)
            pen.ln(cx - sx * r * 0.14, ey - r * 0.2, cx + sx * r * 0.08, ey - r * 0.12, INK, max(2, r * 0.05))
        elif eyes == "wide":
            er = r * 0.17
            pen.circle(cx, ey, er, fill="#fbfbf7", stroke=INK, w=max(2, r * 0.035))
            if f.get("red", 0) > 0:
                for k in range(3):
                    a = math.radians(200 + k * 50 + sx * 20)
                    pen.ln(cx + math.cos(a) * er * 0.95, ey + math.sin(a) * er * 0.95,
                           cx + math.cos(a) * er * 0.45, ey + math.sin(a) * er * 0.45, RED, max(1, r * 0.012), f["red"])
            pen.circle(cx + lx * er * 0.35 + jx, ey + ly * er * 0.35 + jy, er * 0.42, fill=INK)
            pen.circle(cx + lx * er * 0.35 + jx - er * 0.13, ey + ly * er * 0.35 + jy - er * 0.15, er * 0.12, fill="#ffffff")
        else:  # dot / side
            pen.circle(cx + lx * r * 0.06, ey + ly * r * 0.05, r * 0.075, fill=INK)
    if f.get("tears", 0) > 0:
        L = f["tears"]
        for sx in (-1, 1):
            cx = x + sx * ex + sx * r * 0.06
            pen.ln(cx, ey + r * 0.16, cx + sx * r * 0.02, ey + r * 0.16 + r * 0.55 * L, TEAR, max(2, r * 0.05), 0.9)
    my = y + r * 0.42; m = f.get("mouth", "smile"); mw = r * 0.22; lw = max(2, r * 0.045)
    if m == "talk": m = "open" if (int(t * 9 + seed) % 3) else "flat"
    if m == "smile": pen.arc(x, my - r * 0.08, mw, r * 0.1, 20, 140, INK, lw)
    elif m == "grin": pen.path(lambda p: (p.moveTo(x - mw * 1.2, my - r * 0.06), p.quadTo(x, my + r * 0.3, x + mw * 1.2, my - r * 0.06), p.close()), fill=INK)
    elif m == "frown": pen.arc(x, my + r * 0.06, mw * 0.9, r * 0.08, 200, 140, INK, lw)
    elif m == "flat": pen.ln(x - mw * 0.7, my, x + mw * 0.7, my, INK, lw)
    elif m == "open": pen.oval(x, my, mw * 0.6, r * 0.12, fill=INK)
    elif m == "o": pen.oval(x, my, r * 0.08, r * 0.1, fill=INK)
    elif m == "wobble":
        pen.path(lambda p: (p.moveTo(x - mw, my), p.cubicTo(x - mw / 2, my - r * 0.06, x, my + r * 0.06, x + mw / 2, my - r * 0.04), p.lineTo(x + mw, my)), stroke=INK, w=lw)

def head(pen, kind, x, y, r, f, t, seed, tilt=0):
    """Head centred at (x,y) with radius r, including hair/headwrap/hood and face."""
    wht, lin = pen.white, pen.line
    pen.push(rot=tilt, ox=x, oy=y + r)
    if kind == "you":  # hood behind the head
        pen.oval(x, y + r * 0.15, r * 1.32, r * 1.22, fill="#d9d9d4" if pen.mood == "normal" else "#cddbbf", stroke=lin, w=3)
    if kind == "sis":
        for sx in (-1, 1): pen.circle(x + sx * r * 0.95, y - r * 0.75, r * 0.5, fill=DARK, stroke=lin, w=2)
    pen.circle(x, y, r, fill=wht, stroke=lin, w=3)
    if kind == "mom":  # headwrap: tall rounded wrap with folds
        wc = AMBER if pen.mood == "normal" else "#a9b86a"
        pen.path(lambda p: (p.moveTo(x - r * 1.02, y - r * 0.2), p.cubicTo(x - r * 1.25, y - r * 2.1, x + r * 1.3, y - r * 2.2, x + r * 1.02, y - r * 0.2),
                            p.quadTo(x, y - r * 0.6, x - r * 1.02, y - r * 0.2), p.close()), fill=wc, stroke=lin, w=3)
        pen.circle(x + r * 0.35, y - r * 1.55, r * 0.38, fill=wc, stroke=lin, w=3)  # knot
        for k in range(2): pen.arc(x, y - r * (0.85 + 0.35 * k), r * (0.75 - 0.1 * k), r * 0.3, 195, 130, "#8a5d14", max(2, r * 0.04))
        for sx in (-1, 1): pen.circle(x + sx * r * 0.98, y + r * 0.25, r * 0.09, fill=AMBER)
    elif kind == "dad":
        pen.arc(x, y - r * 0.05, r * 0.98, r * 0.98, 200, 140, DARK, r * 0.22)
        pen.arc(x, y + r * 0.08, r * 0.86, r * 0.86, 25, 130, DIM, r * 0.16)  # beard
    elif kind in ("you", "kid", "toddler"):
        pen.arc(x, y - r * 0.08, r * 0.95, r * 0.95, 205, 130, DARK, r * (0.24 if kind != "toddler" else 0.12))
    elif kind == "tola":
        pen.circle(x, y - r * 1.05, r * 0.42, fill=DARK, stroke=lin, w=2)  # top bun
        pen.arc(x, y - r * 0.1, r * 0.93, r * 0.93, 210, 120, DARK, r * 0.14)
    elif kind == "sis":
        pen.arc(x, y - r * 0.1, r * 0.93, r * 0.93, 210, 120, DARK, r * 0.14)
    elif kind == "old":
        pen.arc(x, y - r * 0.1, r * 0.95, r * 0.95, 205, 130, "#bdbdbd", r * 0.2)
    face(pen, x, y, r, f, t, seed)
    pen.pop()

def figure(pen, kind, x, y, s=1.0, pose=None, t=0.0, seed=0, seated=False):
    """Front-view figure standing on (x, y) (feet). pose keys:
    face (dict), tilt (deg), breathe (0..1), armL/armR (upper, lower) degrees from straight down
    (+ = outward), carry (bool: both hands forward), bob (px), lean (deg)."""
    pose = pose or {}; Hh = SIZES[kind] * s; wht, lin = pen.white, pen.line
    r = Hh * (0.15 if kind in ("you", "sis", "kid", "tola") else 0.19 if kind == "toddler" else 0.125)
    br = 1 + 0.012 * math.sin(t * 2.6 + seed) * pose.get("breathe", 1)
    bob = pose.get("bob", 0)
    pen.push(rot=pose.get("lean", 0), ox=x, oy=y)
    y = y - bob
    hip = y - Hh * 0.45; sh = y - Hh + 2 * r + Hh * 0.04
    if seated: hip = y + 40  # body continues down behind the table
    shw = Hh * (0.3 if kind != "sis" else 0.26); hpw = Hh * 0.27
    if not seated:
        lw = Hh * 0.05
        for sx in (-1, 1):
            pen.ln(x + sx * hpw * 0.3, hip, x + sx * hpw * 0.32, y - Hh * 0.03, wht, lw)
            pen.oval(x + sx * hpw * 0.4, y - Hh * 0.015, Hh * 0.05, Hh * 0.022, fill=DIM)
    # arms (behind torso edges)
    def arm(sx, up, lo):
        ax, ay = x + sx * shw * 0.5, sh + Hh * 0.03
        L = Hh * 0.2
        a1 = math.radians(up) * sx; ex_, ey_ = ax + math.sin(a1) * L, ay + math.cos(a1) * L
        a2 = math.radians(up + lo) * sx; hx, hy = ex_ + math.sin(a2) * L * 0.95, ey_ + math.cos(a2) * L * 0.95
        pen.ln(ax, ay, ex_, ey_, lin, Hh * 0.055 + 3); pen.ln(ex_, ey_, hx, hy, lin, Hh * 0.05 + 3)
        pen.ln(ax, ay, ex_, ey_, wht, Hh * 0.055); pen.ln(ex_, ey_, hx, hy, wht, Hh * 0.05)
        pen.circle(hx, hy, Hh * 0.03, fill=wht, stroke=lin, w=2)
        return hx, hy
    hands = {}
    for sx, key, dflt in ((-1, "armL", (8, 4)), (1, "armR", (8, 4))):
        up, lo = pose.get(key, dflt); hands[key] = arm(sx, up, lo)
    # torso / dress
    pen.push(s=1.0, ox=x, oy=hip);
    sy = br
    def torso(p):
        top = hip - (hip - sh) * sy
        p.moveTo(x - shw / 2, top); p.lineTo(x + shw / 2, top)
        if kind == "mom":
            p.lineTo(x + hpw * 0.55, hip); p.lineTo(x + Hh * 0.2, y - Hh * 0.2 if not seated else hip + 10); p.lineTo(x - Hh * 0.2, y - Hh * 0.2 if not seated else hip + 10); p.lineTo(x - hpw * 0.55, hip)
        else:
            p.lineTo(x + hpw / 2, hip + 4); p.lineTo(x - hpw / 2, hip + 4)
        p.close()
    pen.path(torso, fill=wht, stroke=lin, w=3)
    if kind == "you":  # hoodie strings + pocket
        for sx in (-1, 1): pen.ln(x + sx * Hh * 0.03, sh + Hh * 0.02, x + sx * Hh * 0.035, sh + Hh * 0.12, DIM, 3)
        pen.rect(x - Hh * 0.09, hip - Hh * 0.1, Hh * 0.18, Hh * 0.07, stroke=lin, w=2, r=6)
    if kind == "sis":
        pen.path(lambda p: (p.moveTo(x, sh + Hh * 0.08), p.lineTo(x + Hh * 0.025, sh + Hh * 0.13), p.lineTo(x - Hh * 0.025, sh + Hh * 0.13), p.close()), fill=AMBER)
    if kind == "dad":
        for k in range(3): pen.circle(x, sh + Hh * (0.06 + 0.07 * k), 2.5, fill=DIM)
    pen.pop()
    head(pen, kind, x, sh - r - Hh * 0.01, r, pose.get("face", {}), t, seed, tilt=pose.get("tilt", 0))
    pen.pop()
    return hands

def head_close(pen, kind, x, y, r, f, t, seed=0, tilt=0, shoulders=True):
    """Close-up: a big head with shoulders below, for CU / ECU shots."""
    if shoulders:
        pen.path(lambda p: (p.moveTo(x - r * 1.6, y + r * 2.6), p.cubicTo(x - r * 1.5, y + r * 1.15, x + r * 1.5, y + r * 1.15, x + r * 1.6, y + r * 2.6), p.close()),
                 fill=pen.white, stroke=pen.line, w=4)
    head(pen, kind, x, y, r, f, t, seed, tilt)

# ---------------- props ----------------
def floor(pen, y=880, a=1.0): pen.ln(0, y, W, y, pen.white, 4, a)

def window(pen, x, y, w=260, h=300, t=0.0, moon=True):
    pen.rect(x, y, w, h, fill="#10131c", stroke=GREY, w=4)
    pen.ln(x + w / 2, y, x + w / 2, y + h, GREY, 4); pen.ln(x, y + h / 2, x + w, y + h / 2, GREY, 4)
    rnd = random.Random(int(x))
    for k in range(7):
        sx, sy = x + rnd.random() * w, y + rnd.random() * h
        pen.circle(sx, sy, 2 + 1.2 * math.sin(t * 2 + k * 1.7), fill=WHITE, a=0.7)
    if moon:
        pen.glow(x + w * 0.68, y + h * 0.3, 70, "#fff2c0", 0.35); pen.circle(x + w * 0.68, y + h * 0.3, 30, fill="#f4ecd0")
    for sx in (0, 1):
        pen.rect(x - 22 + sx * (w + 4), y - 12, 40, h + 40, fill="#2b2c30", stroke="#3c3d42", w=2)

def wall_clock(pen, x, y, r, clock_s):
    pen.circle(x, y, r, stroke=pen.white, w=5)
    m = clock_s / 60.0; h_ = m / 60.0
    for ang, L, w in ((h_ * 30 - 90, r * 0.5, 6), (m * 6 - 90, r * 0.78, 4), (clock_s * 6 - 90, r * 0.85, 1.5)):
        a = math.radians(ang); pen.ln(x, y, x + math.cos(a) * L, y + math.sin(a) * L, pen.white if w > 2 else RED, w)

def frame_pic(pen, x, y, w=120, h=90):
    pen.rect(x, y, w, h, stroke=pen.white, w=4)
    pen.circle(x + w * 0.36, y + h / 2, 9, stroke=pen.white, w=3); pen.circle(x + w * 0.62, y + h / 2, 9, stroke=pen.white, w=3)

def door(pen, x, y, w=150, h=320, open_=0.0):
    pen.rect(x, y, w, h, stroke=pen.white, w=6)
    if open_ > 0: pen.rect(x + 3, y + 3, w * open_, h - 6, fill="#000000")
    pen.circle(x + w - 22, y + h * 0.55, 9, fill=pen.white)

def pendant_lamp(pen, x, y, t, on=1.0, flicker=0.0, cone_to=880, spread=360):
    k = on * (1 - flicker * (0.5 + 0.5 * math.sin(t * 37) * math.sin(t * 13)))
    pen.ln(x, 0, x, y - 40, GREY, 3)
    pen.poly([(x - 70, y), (x + 70, y), (x + 34, y - 44), (x - 34, y - 44)], fill="#c98f2c" if k > 0.2 else DIM, stroke=GREY, w=3)
    if k > 0.05:
        pen.poly([(x - 60, y), (x + 60, y), (x + spread, cone_to), (x - spread, cone_to)], fill=AMBER, a=0.22 * k, blur=18)
        pen.glow(x, y + 6, 90, AMBER, 0.55 * k)

def table_front(pen, cx, top, w, cloth=True):
    """Dining table seen from the front (from your seat): top edge + cloth drape to bottom of frame."""
    pen.rect(cx - w / 2, top, w, H - top + 20, fill="#cfccc3" if pen.mood == "normal" else "#9fb08c" if pen.mood == "frozen" else "#8f8d88", stroke=pen.line, w=4)
    pen.ln(cx - w / 2, top, cx + w / 2, top, pen.white, 8)

def plate(pen, x, y, s=1.0, food=True):
    pen.oval(x, y, 90 * s, 22 * s, fill="#fafaf5", stroke=GREY, w=3)
    pen.oval(x, y, 58 * s, 13 * s, stroke="#d0d0cb", w=2)
    if food: pen.oval(x - 8 * s, y - 6 * s, 34 * s, 10 * s, fill="#d9682a")

def fork(pen, x, y, ang=0, s=1.0):
    pen.push(rot=ang, ox=x, oy=y)
    pen.ln(x, y, x, y - 120 * s, GREY, 7 * s)
    for k in (-1, 0, 1): pen.ln(x + k * 8 * s, y - 120 * s, x + k * 8 * s, y - 160 * s, GREY, 4 * s)
    pen.pop()

def steam(pen, x, y, t, n=3, h=170, a=0.55, spread=28):
    for k in range(n):
        ph = (t * 0.6 + k / n) % 1.0
        def build(p, ph=ph, k=k):
            x0 = x + (k - (n - 1) / 2) * spread
            p.moveTo(x0, y)
            for j in range(1, 9):
                yy = y - h * ph * j / 8; xx = x0 + math.sin(j * 0.9 + t * 3 + k) * 14 * (j / 8)
                p.lineTo(xx, yy)
        pen.path(build, stroke=WHITE, w=4, a=a * (1 - ph))

def pot(pen, x, y, s=1.0, lid=0.0, t=0.0):
    pen.rect(x - 95 * s, y - 80 * s, 190 * s, 80 * s, fill="#2c2d31", stroke=GREY, w=4, r=10)
    pen.oval(x, y - 80 * s, 95 * s, 18 * s, fill="#d9682a", stroke=GREY, w=3)
    for sx in (-1, 1): pen.rect(x + sx * 110 * s - 15 * s, y - 70 * s, 30 * s, 12 * s, fill=GREY, r=5)
    if lid < 1:
        ly = y - 82 * s - lid * 140 * s
        pen.push(rot=-lid * 25, ox=x, oy=ly)
        pen.path(lambda p: (p.moveTo(x - 100 * s, ly), p.quadTo(x, ly - 50 * s, x + 100 * s, ly), p.close()), fill="#3a3b40", stroke=GREY, w=3)
        pen.circle(x, ly - 28 * s, 10 * s, fill=GREY)
        pen.pop()

def chair_back(pen, x, y, s=1.0, angle=0, color=None):
    """Front view of a chair seen from behind a seated person / at table end."""
    c = color or "#5b5d63"
    pen.push(rot=angle, ox=x, oy=y)
    pen.rect(x - 70 * s, y - 210 * s, 140 * s, 210 * s, stroke=c, w=8 * s, r=10 * s)
    pen.ln(x - 70 * s, y - 120 * s, x + 70 * s, y - 120 * s, c, 6 * s)
    pen.pop()

def chair_side(pen, x, y, s=1.0, facing=1, pulled=0.0, color=None):
    c = color or pen.white
    x = x + pulled * facing
    pen.ln(x, y, x, y - 110 * s, c, 7); pen.ln(x + facing * 90 * s, y, x + facing * 90 * s, y - 110 * s, c, 7)
    pen.ln(x - 4, y - 110 * s, x + facing * 94 * s, y - 110 * s, c, 9)
    pen.ln(x, y - 110 * s, x, y - 250 * s, c, 8)

def sofa(pen, x, y, w=620):
    pen.rect(x, y - 160, w, 160, fill="#2b2c31", stroke=GREY, w=4, r=26)
    pen.rect(x + 30, y - 230, w - 60, 100, fill="#33343a", stroke=GREY, w=4, r=26)
    for sx in (0, 1): pen.rect(x - 20 + sx * (w - 40), y - 190, 60, 190, fill="#2f3036", stroke=GREY, w=4, r=22)

def tv(pen, x, y, w, h, t, on=True):
    pen.rect(x, y, w, h, fill="#12141a", stroke=pen.white, w=5, r=6)
    if on:
        k = 0.6 + 0.4 * abs(math.sin(t * 5.3)) * abs(math.sin(t * 2.1))
        pen.rect(x + 10, y + 10, w - 20, h - 20, fill=TV, a=0.55 * k)
        for j in range(4): pen.ln(x + 30, y + 40 + j * 30, x + w - 60 - 40 * (j % 2), y + 40 + j * 30, "#dfe9ff", 6, 0.6 * k)
        pen.glow(x + w / 2, y + h / 2, w * 0.9, TV, 0.18 * k)

def house(pen, x, y, t, lit=True):
    """Simple line-art house (front), y = ground."""
    pen.poly([(x - 330, y - 300), (x, y - 520), (x + 330, y - 300)], fill="#15161b", stroke=WHITE, w=5)
    pen.rect(x - 300, y - 300, 600, 300, fill="#121318", stroke=WHITE, w=5)
    k = 0.85 + 0.15 * math.sin(t * 9) * math.sin(t * 3.7) if lit else 0
    pen.rect(x - 230, y - 230, 170, 120, fill=AMBER if lit else "#1a1c22", stroke=WHITE, w=5, a=0.95 if lit else 1)
    if lit: pen.glow(x - 145, y - 170, 220, AMBER, 0.25 * k)
    pen.rect(x + 70, y - 230, 160, 120, fill="#1a1c22", stroke=WHITE, w=5)
    pen.rect(x - 40, y - 150, 90, 150, fill="#1a1c22", stroke=WHITE, w=5)
    pen.circle(x + 70, y - 165, 10, fill=AMBER, a=0.6 + 0.4 * math.sin(t * 6))

# ---------------- overlays ----------------
def music_note(pen, x, y, s, color, a=1.0):
    pen.oval(x, y, 22 * s, 16 * s, fill=color, a=a); pen.ln(x + 20 * s, y, x + 20 * s, y - 80 * s, color, 6 * s, a)
    pen.ln(x + 20 * s, y - 80 * s, x + 50 * s, y - 60 * s, color, 6 * s, a)

def pause_bars(pen, x, y, h=70, color=WHITE):
    pen.rect(x, y - h, h * 0.3, h, fill=color); pen.rect(x + h * 0.5, y - h, h * 0.3, h, fill=color)

def hud(pen, label, gt, rec=True):
    pen.rect(0, 0, W, 90, fill="#000000", a=0.35)
    pen.text(label, 52, 58, 26, "#cfcfcb", "JetBrainsMono-Regular.ttf", 0.85, "left")
    if rec:
        on = (gt % 1.0) < 0.6
        pen.circle(W - 290, 49, 8, fill=RED, a=1.0 if on else 0.25)
        f = int(round(gt * FPS)); s = f // FPS
        pen.text(f"{s // 3600:02d}:{s // 60 % 60:02d}:{s % 60:02d}:{f % FPS:02d}", W - 52, 58, 26, "#cfcfcb", "JetBrainsMono-Regular.ttf", 0.85, "right")

def vignette(pen, a=0.55):
    sh = skia.GradientShader.MakeRadial((W / 2, H / 2), W * 0.75, [C("#000000", 0), C("#000000", a)], [0.55, 1.0])
    p = skia.Paint(); p.setShader(sh); pen.c.drawRect(skia.Rect.MakeWH(W, H), p)

def kinetic(pen, text, t, color=ACID, size=230, shake=True):
    sc = 1.4 - 0.4 * ease_out(t / 0.18)
    dx = 14 * math.sin(t * 60) * clamp(1 - t / 0.45) if shake else 0
    pen.push(s=sc, ox=W / 2 + dx, oy=H / 2 + size * 0.35)
    pen.text(text, W / 2 + dx, H / 2 + size * 0.35, size, color)
    pen.pop()
