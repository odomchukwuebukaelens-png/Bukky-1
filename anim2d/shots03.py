"""Video 03: 'If The Ice Cream Truck Ever Comes After Midnight... DON'T BUY ANYTHING'.
Every builder has several distinct compositions (comp = v % N). Shot names: 'BUILDER#v:opts'."""
import math, random
from engine import *
from scenes import sky, moon, clouds, treeline, grass, fireflies
from shots01 import camera

PINK, BLUE, CREAM = "#ff6fb5", "#6fb8ff", "#fff3d6"
CLK = 0 * 3600 + 14 * 60  # 12:14 AM

def has(o, *k): return any(x in o.split(",") for x in k)

# ---------------- props ----------------
def notes(pen, x, y, t, n=4, color=PINK, missing=False, spread=70):
    for k in range(n):
        if missing and k % 2: continue
        ph = (t * 0.6 + k / n) % 1
        music_note(pen, x + k * spread + 30 * math.sin(t * 2 + k), y - ph * 160, 0.9, color, 1 - ph)

def truck(pen, x, y, s, t, menu=1.0, window=0.0, arm=0.0, cone=True, bell=False, lights=True, song=True, driver_dark=True):
    """Side-view ice cream truck, front facing left. (x, y) = ground under the middle."""
    S = s
    pen.push(s=S, ox=x, oy=y)
    bx, by = x - 300, y - 340
    pen.rect(bx, by, 520, 290, fill="#e9e6df", stroke=GREY, w=5, r=14)              # box
    pen.rect(bx - 190, by + 110, 200, 180, fill="#e9e6df", stroke=GREY, w=5, r=20)  # cab
    pen.rect(bx - 170, by + 125, 110, 80, fill="#0b0d14" if driver_dark else "#334", stroke=GREY, w=4, r=8)  # driver window
    pen.rect(bx - 196, by + 240, 30, 22, fill="#555555", r=6)                          # dead headlight
    for wx in (bx - 90, bx + 400):
        pen.circle(wx, y - 50, 54, fill="#1b1b1e", stroke=GREY, w=5); pen.circle(wx, y - 50, 22, fill=GREY)
    for k in range(9): pen.rect(bx + k * 58, by + 250, 40, 40, fill=PINK if k % 2 else BLUE, a=0.9)  # stripes
    # menu board
    pen.rect(bx + 300, by + 30, 190, 160, fill="#1a0f1f", stroke=PINK, w=6, r=8)
    if menu > 0:
        pen.glow(bx + 395, by + 110, 260, PINK, 0.30 * menu); pen.glow(bx + 395, by + 110, 160, BLUE, 0.22 * menu)
        for k in range(5): pen.rect(bx + 320, by + 50 + k * 26, 120 - (k * 17) % 50, 12, fill=CREAM if k % 2 else BLUE, a=0.8 * menu)
    # serving window
    pen.rect(bx + 40, by + 60, 220, 150, fill="#0b0d14", stroke=GREY, w=5)
    if window < 1:
        pen.rect(bx + 40, by + 60, 220, 150 * (1 - window), fill="#cfccc3", stroke=GREY, w=4)
        for k in range(4): pen.ln(bx + 40, by + 60 + k * 36 * (1 - window), bx + 260, by + 60 + k * 36 * (1 - window), GREY, 2)
    if arm > 0:  # long thin arm out of the window holding a cone
        ax0, ay0 = bx + 150, by + 170; ax1 = ax0 - 420 * arm; ay1 = ay0 + 60 * arm
        pen.path(lambda p: (p.moveTo(ax0, ay0), p.cubicTo(ax0 - 120, ay0 - 40, ax1 + 120, ay1 + 40, ax1, ay1)), stroke=WHITE, w=22)
        for k in range(4): pen.ln(ax1, ay1, ax1 - 40, ay1 - 30 + k * 18, WHITE, 7)
        if cone:
            pen.poly([(ax1 - 50, ay1 - 30), (ax1 - 10, ay1 - 30), (ax1 - 30, ay1 + 40)], fill="#d9a35a", stroke="#8a6a3a", w=3)
            pen.circle(ax1 - 30, ay1 - 48, 30, fill="#f6c9e0")
    # roof speaker + string lights + bell
    pen.poly([(bx + 160, by), (bx + 180, by - 50), (bx + 240, by - 70), (bx + 240, by - 10)], fill=GREY)
    if lights:
        for k in range(12): pen.circle(bx + k * 46, by - 6, 7, fill=[PINK, BLUE, CREAM][k % 3], a=0.6 + 0.4 * math.sin(t * 4 + k))
    pen.circle(bx + 280, by + 40, 16, fill=AMBER)
    if bell: pen.text("DING", bx + 280, by - 20, 50, AMBER)
    if song: notes(pen, bx + 240, by - 90, t)
    pen.pop()

def house_row(pen, t, y, lit=(), dark_all=False, n=5, x0=120, gap=380, s=1.0):
    for i in range(n):
        x = x0 + i * gap; w_, h_ = 300 * s, 240 * s
        pen.rect(x - w_ / 2, y - h_, w_, h_, fill="#14161c", stroke=GREY, w=3)
        pen.poly([(x - w_ / 2 - 20, y - h_), (x, y - h_ - 120 * s), (x + w_ / 2 + 20, y - h_)], fill="#101218", stroke=GREY, w=3)
        on = (i in lit) and not dark_all
        pen.rect(x - 80 * s, y - h_ + 60 * s, 60 * s, 60 * s, fill="#ffcf73" if on else "#1d2233", stroke=GREY, w=2)
        pen.rect(x + 20 * s, y - h_ + 60 * s, 60 * s, 60 * s, fill="#1d2233", stroke=GREY, w=2)
        pen.rect(x - 25 * s, y - 100 * s, 50 * s, 100 * s, fill="#2a2d38")

def streetlamp(pen, x, y, h=380, on=True):
    pen.ln(x, y, x, y - h, GREY, 8); pen.ln(x, y - h, x + 60, y - h, GREY, 8)
    if on: pen.glow(x + 60, y - h + 10, 220, "#ffe7a0", 0.35); pen.circle(x + 60, y - h + 10, 14, fill="#ffe7a0")

def night_street_bg(pen, t, horizon=640):
    sky(pen, t); moon(pen, 1600, 180, t, 50); clouds(pen, t)
    treeline(pen, t, horizon, "#0a0f14", 81, 120)

def kid(pen, x, y, s, t, seed, cone=False, jersey=False, back=False, eyes="dot"):
    figure(pen, "kid", x, y, s, {"face": {"mouth": "flat", "eyes": eyes, "blink": False}, "armR": (60, 50) if cone else (8, 4)}, t, seed=seed)
    Hh = 270 * s
    for k in range(3): pen.ln(x - Hh * 0.13, y - Hh * (0.5 + 0.06 * k), x + Hh * 0.13, y - Hh * (0.5 + 0.06 * k), BLUE, 3, 0.7)  # pajama stripes
    if jersey:
        pen.rect(x - Hh * 0.12, y - Hh * 0.68, Hh * 0.24, Hh * 0.18, fill="#2a6a3a"); pen.text("23", x, y - Hh * 0.53, Hh * 0.12, WHITE, "JetBrainsMono-Regular.ttf")
    if cone:
        cx, cy = x + Hh * 0.33, y - Hh * 0.62
        pen.poly([(cx - 12 * s, cy), (cx + 12 * s, cy), (cx, cy + 40 * s)], fill="#d9a35a"); pen.circle(cx, cy - 8 * s, 14 * s, fill="#bff0d8")
    if back: pen.rect(x - Hh * 0.2, y - Hh * 1.0, Hh * 0.4, Hh * 0.3, fill=DARK, a=0.8)

def bedroom_bg(pen, t, lamp=False, curtain=True, clock_txt="12:14"):
    pen.rect(0, 0, W, H, fill="#121521")
    for x in range(0, W, 90): pen.ln(x, 0, x, 900, "#161a28", 3)  # wallpaper stripes
    pen.rect(1250, 180, 420, 380, fill="#0b1020", stroke="#c9c2b0", w=8); pen.ln(1460, 180, 1460, 560, "#c9c2b0", 6)  # window
    moon(pen, 1560, 260, t, 30)
    if curtain:
        sw = 30 * math.sin(t * 1.6)
        pen.path(lambda p: (p.moveTo(1230, 170), p.quadTo(1300 + sw, 380, 1260 + sw * 1.5, 580), p.lineTo(1215, 580), p.close()), fill="#6a4aa0", a=0.9)
    pen.rect(200, 220, 160, 220, fill="#22344a", stroke="#3a4a6a", w=4)  # poster
    pen.circle(280, 300, 40, stroke=AMBER, w=5); pen.ln(230, 400, 330, 400, AMBER, 5)
    pen.rect(0, 900, W, 180, fill="#1b1e2a")
    # nightstand + lamp + clock
    pen.rect(140, 700, 220, 200, fill="#3a2f26", stroke="#5a4630", w=4)
    pen.ln(250, 700, 250, 600, GREY, 6); pen.poly([(190, 600), (310, 600), (280, 530), (220, 530)], fill="#c98f2c" if lamp else "#4a3f30")
    if lamp: pen.glow(250, 600, 320, AMBER, 0.45)
    pen.rect(170, 640, 70, 50, fill="#0a0a0a", r=6); pen.text(clock_txt, 205, 675, 22, RED, "JetBrainsMono-Regular.ttf")
    # bed
    pen.rect(420, 640, 760, 260, fill="#2b3550", stroke="#3a4a6a", w=5, r=20)
    pen.rect(420, 560, 40, 340, fill="#3a2f26"); pen.rect(1140, 600, 40, 300, fill="#3a2f26")
    pen.oval(560, 640, 110, 40, fill="#d8d8d2")

# ---------------- builders ----------------
def STREET(pen, t, d, gt, s, v, o):
    """Night street. comps: 0 from your window (high), 1 street-level low, 2 down-the-street perspective,
    3 across the street at your house, 4 wide with the truck small."""
    comp = v % 5
    camera(pen, t, d, 1.0, 1.06, W / 2, 560, s)
    tx_far, tx_stop = 2300, 960
    pos = {"approach": lerp(2400, 1500, smooth(t / d)), "roll": lerp(1900, 1100, smooth(t / d)), "stop": tx_stop, "leave": lerp(960, -600, smooth(t / d))}
    tx = next((pos[k] for k in pos if has(o, k)), None)
    lit = (1, 3) if has(o, "lights") else ()
    dark = has(o, "dark")
    if comp in (0, 4):
        night_street_bg(pen, t, 470)
        house_row(pen, t, 560, lit, dark, 5, 140, 410, 0.8)
        pen.rect(0, 560, W, 520, fill="#1b1d22"); pen.ln(0, 700, W, 700, "#e8e1cc", 4, 0.4)
        for x in (60, 880, 1700): streetlamp(pen, x, 600, 330)
        if tx is not None: truck(pen, tx, 900, 0.55 if comp == 0 else 0.35, t, song=not has(o, "silent"), bell=has(o, "bell"))
        if comp == 0:  # your window sill in foreground
            pen.rect(0, 960, W, 140, fill="#2a2d38"); pen.rect(0, 0, 120, H, fill="#121521"); pen.rect(W - 120, 0, 120, H, fill="#121521")
    elif comp == 1:
        night_street_bg(pen, t, 600)
        pen.rect(0, 700, W, 380, fill="#1b1d22")
        for k in range(10): pen.rect(k * 220 - 40, 880, 120, 10, fill="#e8e1cc", a=0.4)
        streetlamp(pen, 300, 760, 520)
        if tx is not None: truck(pen, tx, 900, 0.9, t, song=not has(o, "silent"), bell=has(o, "bell"))
        grass(pen, 1000, t, "#122014", 40)
    elif comp == 2:
        sky(pen, t); moon(pen, 960, 200, t, 40)
        pen.poly([(0, H), (840, 520), (1080, 520), (W, H)], fill="#1b1d22")
        for k in range(6):
            z = 0.25 + k * 0.15
            for sx in (-1, 1):
                x = 960 + sx * (180 + k * 170); y = 520 + k * 90
                pen.rect(x - 90 * z, y - 140 * z, 180 * z, 140 * z, fill="#14161c", stroke=GREY, w=2)
                pen.rect(x - 30 * z, y - 100 * z, 40 * z, 40 * z, fill="#ffcf73" if (k in lit) else "#1d2233")
        if tx is not None:
            z = clamp(1 - (tx - 960) / 1500, 0.2, 1.0)
            truck(pen, 960, 520 + 420 * z, 0.25 + 0.4 * z, t, song=not has(o, "silent"))
    else:  # across the street, looking at YOUR house (your window lit or dark)
        night_street_bg(pen, t, 420)
        pen.rect(560, 300, 800, 520, fill="#14161c", stroke=GREY, w=4); pen.poly([(520, 300), (960, 120), (1400, 300)], fill="#101218", stroke=GREY, w=4)
        pen.rect(1020, 380, 160, 140, fill="#ffcf73" if has(o, "lamp") else "#1d2233", stroke=GREY, w=4)  # your window
        if has(o, "lamp"): pen.glow(1100, 450, 260, AMBER, 0.3)
        pen.rect(700, 380, 160, 140, fill="#1d2233", stroke=GREY, w=4)
        pen.rect(900, 640, 120, 180, fill="#2a2d38", stroke=GREY, w=4)
        pen.rect(0, 820, W, 260, fill="#1b1d22")
        if tx is not None: truck(pen, tx, 1060, 0.5, t, song=not has(o, "silent"))
    if has(o, "notes"): notes(pen, 1300, 300, t, 5, PINK, missing=has(o, "missing"))
    pen.pop()

def TRUCK(pen, t, d, gt, s, v, o):
    """Truck details. comps: 0 full side, 1 menu-board side close, 2 serving window close, 3 cab + dark driver window,
    4 roof speaker + lights, 5 low angle wheels + exhaust."""
    comp = v % 6
    pen.rect(0, 0, W, H, fill="#06080e"); sky(pen, t)
    pen.rect(0, 900, W, 180, fill="#1b1d22")
    win = ease_out(t / 0.7) if has(o, "open") else (1.0 if has(o, "opened") else 0.0)
    arm = ease_out(t / d) if has(o, "arm") else (1.0 if has(o, "armout") else 0.0)
    kw = dict(menu=1.0, window=win, arm=arm, bell=has(o, "bell") and (t % 0.6) < 0.35, song=not has(o, "silent"))
    # each close-up places a specific truck part (local offset from the truck origin) at frame centre
    def frame(sc, lx, ly, cx=960, cy=540):
        camera(pen, t, d, 1.0, 1.05, cx, cy, s); truck(pen, cx - lx * sc, cy - ly * sc, sc, t, **kw)
    if comp == 0: camera(pen, t, d, 1.0, 1.05, 960, 560, s); truck(pen, 1060, 960, 1.6, t, **kw)
    elif comp == 1: frame(2.8, 95, -230)            # menu board
    elif comp == 2: frame(3.0, -150, -205)          # serving window
    elif comp == 3: frame(3.2, -415, -175)          # cab + dark driver window
    elif comp == 4: frame(3.0, -90, -360, 960, 300)  # roof speaker + string lights
    else:
        camera(pen, t, d, 1.0, 1.05, 960, 700, s); truck(pen, 1200, 1250, 2.4, t, **kw)
        for k in range(4):
            ph = (t * 0.8 + k / 4) % 1; pen.circle(200 - ph * 160, 980 - ph * 120, 30 + ph * 60, fill=GREY, a=0.25 * (1 - ph))
    pen.pop()

def MENU(pen, t, d, gt, s, v, o):
    """Menu board close: prices in dollars (saturday) or in years (midnight)."""
    comp = v % 4
    z = [1.0, 1.3, 1.6, 1.15][comp]; fy = [540, 420, 700, 560][comp]
    camera(pen, t, d, z, z * 1.04, 960, fy, s)
    pen.rect(0, 0, W, H, fill="#0b0710")
    pen.glow(960, 540, 900, PINK, 0.25); pen.glow(960, 540, 600, BLUE, 0.18)
    pen.rect(460, 80, 1000, 920, fill="#1a0f1f", stroke=PINK, w=12, r=20)
    pen.text("MENU", 960, 200, 100, CREAM)
    items = [("ROCKET POP", "$2" if has(o, "dollars") else "1 YEAR"), ("CHOCOLATE CONE", "$3" if has(o, "dollars") else "3 YEARS"),
             ("MOON MINT", "$3" if has(o, "dollars") else "1 WEEK"), ("BIRTHDAY SWIRL", "$4" if has(o, "dollars") else "5 YEARS")]
    hi = {"rocket": 0, "choc": 1, "mint": 2}.get(next((k for k in ("rocket", "choc", "mint") if has(o, k)), ""), -1)
    if has(o, "month", "year"):
        lab = "1 MONTH" if has(o, "month") else "1 YEAR"
        pen.text("~ your name ~", 960, 520, 90, WHITE, "Montserrat-VF.ttf"); pen.text(lab, 960, 700, 120, PINK)
        if t > 0.4: pen.text("PAID", 1300, 820, 110, RED, a=ease_out((t - 0.4) / 0.3))
        pen.pop(); return
    if has(o, "due"):
        pen.text("~ your name ~", 960, 520, 90, WHITE, "Montserrat-VF.ttf"); pen.text("DUE", 960, 760, 200, RED, a=0.6 + 0.4 * math.sin(t * 8))
        pen.pop(); return
    if has(o, "prices"):
        for i, pr in enumerate(("1 YEAR", "3 YEARS", "1 WEEK", "5 YEARS")): pen.text(pr, 960, 360 + i * 140, 110, PINK)
        pen.pop(); return
    for i, (name, price) in enumerate(items):
        y = 330 + i * 120
        if i == hi: pen.rect(500, y - 70, 920, 96, fill=PINK, a=0.25 + 0.15 * math.sin(t * 8), r=10)
        pen.text(name, 540, y, 56, BLUE if i % 2 else CREAM, "JetBrainsMono-Regular.ttf", align="left")
        pen.text(price, 1400, y, 56, PINK, "JetBrainsMono-Regular.ttf", align="right")
    if not has(o, "dollars"):
        y = 860; pen.ln(520, y - 70, 1400, y - 70, PINK, 3)
        if has(o, "name", "everything", "paid"):
            pen.text("~ your name ~", 540, y, 64, WHITE, "Montserrat-VF.ttf", align="left")
            label = "PAID" if has(o, "paid") else "EVERYTHING"
            k = ease_out(t / 0.4) if has(o, "paid", "everything") else 1
            pen.text(label, 1400, y, 64, RED if label == "PAID" else PINK, align="right", a=k)
    pen.pop()

def BEDROOM(pen, t, d, gt, s, v, o):
    """Your bedroom. comps: 0 wide, 1 bed close (you lying awake), 2 nightstand + clock, 3 window + curtain from bed, 4 lamp close."""
    comp = v % 5
    lamp = has(o, "lamp")
    z, fx, fy = [(1.0, 960, 540), (1.7, 760, 680), (2.6, 220, 650), (1.9, 1440, 380), (2.8, 250, 600)][comp]
    camera(pen, t, d, z, z * 1.04, fx, fy, s)
    clock = "12:15" if has(o, "1215") else "12:14"
    bedroom_bg(pen, t, lamp=lamp and not (has(o, "off") and t > d * 0.5), clock_txt=clock)
    eyes = "closed" if has(o, "shut") else ("wide" if has(o, "scared", "freeze") else "dot")
    if not has(o, "empty"):
        head_close(pen, "you", 560, 600, 70, {"eyes": eyes, "mouth": "o" if has(o, "hum") else "flat", "blink": not has(o, "freeze"),
                                              "look": (1, -0.5) if has(o, "look") else (0, 0)}, t, seed=3, shoulders=False)
        pen.rect(470, 650, 700, 120, fill="#3a4a7a", stroke="#4a5a8a", w=4, r=30)  # blanket
        if has(o, "ears"):
            for sx in (-1, 1): pen.oval(560 + sx * 70, 600, 22, 34, fill=pen.white, stroke=pen.line, w=3)
    if has(o, "notes"): notes(pen, 1330, 300, t, 4, PINK, missing=has(o, "missing"))
    if has(o, "hum"): notes(pen, 640, 480, t, 3, AMBER)
    if has(o, "sweat"): pen.oval(610, 560, 6, 10, fill=TEAR)
    pen.pop()

def WINDOW_DOWN(pen, t, d, gt, s, v, o):
    """Looking down from your window at the truck outside your house (frame in foreground)."""
    comp = v % 3
    camera(pen, t, d, 1.0, 1.05, W / 2, 560, s)
    night_street_bg(pen, t, 380)
    pen.rect(0, 420, W, 660, fill="#1b1d22"); pen.rect(0, 420, W, 30, fill="#2a2d38")
    tx = [980, 1100, 860][comp]
    truck(pen, tx, 900, 0.75, t, window=1.0 if has(o, "opened", "dad") else 0.0, arm=1.0 if has(o, "dad") else 0.0, cone=False, song=not has(o, "silent"))
    if has(o, "kids"):
        for i in range(6): kid(pen, 420 + i * 70, 930, 0.42, t, 30 + i, back=(i == 5))
    if has(o, "dad"):
        figure(pen, "dad", tx - 380, 950, 0.62, {"face": {"mouth": "flat", "eyes": "dot"}, "armR": (100, 10)}, t, seed=1)
        for k in range(6):
            a = t * 3 + k; pen.glow(tx - 300 + math.cos(a) * 20, 700 + math.sin(a) * 15 - k * 8, 26, "#d8ff8a", 0.6); pen.circle(tx - 300 + math.cos(a) * 20, 700 + math.sin(a) * 15 - k * 8, 4, fill="#efffc0")
    if has(o, "closed"):
        k = smooth(t / d); pen.rect(110, 70, (W - 220) * k, H, fill="#6a4aa0")
        pen.circle(110 + (W - 220) * k, 540, 50, fill=pen.white, stroke=pen.line, w=4)
    pen.rect(0, 0, W, 90, fill="#121521"); pen.rect(0, 0, 110, H, fill="#121521"); pen.rect(W - 110, 0, 110, H, fill="#121521")
    pen.rect(90, 70, W - 180, H - 60, stroke="#c9c2b0", w=16); pen.ln(W / 2, 70, W / 2, H, "#c9c2b0", 10)
    pen.pop()

def KIDS(pen, t, d, gt, s, v, o):
    """The line of kids on the sidewalk. comps: 0 wide line, 1 feet (bare), 2 one with cone, 3 jersey kid, 4 back of line facing your house."""
    comp = 4 if has(o, "c4") else v % 5
    camera(pen, t, d, 1.0, 1.05, W / 2, 600, s)
    pen.rect(0, 0, W, H, fill="#0b0a12"); pen.glow(1700, 400, 900, PINK, 0.25); pen.glow(1700, 400, 600, BLUE, 0.2)
    pen.rect(0, 880, W, 200, fill="#2a2a30")
    if has(o, "stripes"):
        pen.rect(0, 0, W, H, fill="#d8dcea")
        for k in range(14): pen.rect(0, k * 80, W, 36, fill=BLUE, a=0.7)
        pen.rect(860, 0, 200, H, fill="#d8dcea", a=0.0); [pen.circle(960, 200 + j * 220, 20, fill="#ffffff", stroke=GREY, w=3) for j in range(4)]
        pen.pop(); return
    if has(o, "faces"):
        for i in range(4):
            head_close(pen, "kid", 260 + i * 470, 560, 170, {"eyes": "dot", "mouth": "flat", "blink": False, "look": (1, 0)}, t, seed=90 + i)
        pen.text("?", 1820, 300, 160, GREY); pen.pop(); return
    if has(o, "conecu"):
        pen.oval(960, 900, 180, 70, fill=pen.white, stroke=pen.line, w=5)
        pen.poly([(880, 600), (1040, 600), (960, 900)], fill="#d9a35a", stroke="#8a6a3a", w=6); pen.circle(960, 560, 110, fill="#bff0d8")
        pen.text("NO DRIPS", 1450, 300, 70, ACID, "JetBrainsMono-Regular.ttf"); pen.pop(); return
    if has(o, "number"):
        pen.rect(0, 0, W, H, fill="#2a6a3a"); pen.text("23", 960, 760, 560, WHITE); pen.pop(); return
    if has(o, "faded"):
        pen.rect(0, 0, W, H, fill="#5a7a5a"); pen.text("FIREBIRDS", 960, 500, 180, "#c9d9c0", a=0.6)
        pen.text("EST. 1998 – CLOSED 2004", 960, 680, 60, "#c9d9c0", "JetBrainsMono-Regular.ttf", a=0.8); pen.pop(); return
    if has(o, "arrow"):
        for i in range(7): kid(pen, 220 + i * 230, 900, 0.85, t, 30 + i, back=(i == 6))
        k = ease_out(t / 0.5); pen.ln(1300, 300, 1300 + 350 * k, 300, ACID, 14); pen.poly([(1650 * 1, 260), (1700, 300), (1650, 340)], fill=ACID, a=k)
        pen.text("NEW", 1700, 240, 60, ACID); pen.pop(); return
    if has(o, "backkid"):
        kid(pen, 960, 1180, 3.0, t, 46, back=True); pen.pop(); return
    if has(o, "tohouse"):
        pen.rect(0, 0, W, 880, fill="#0b0d14"); pen.rect(560, 160, 800, 520, fill="#14161c", stroke=GREY, w=4)
        pen.poly([(520, 160), (960, 20), (1400, 160)], fill="#101218", stroke=GREY, w=4); pen.rect(1020, 240, 160, 140, fill="#1d2233", stroke=GREY, w=4)
        pen.text("YOUR WINDOW", 1100, 440, 40, ACID, "JetBrainsMono-Regular.ttf")
        for i in range(5): kid(pen, 300 + i * 330, 1120, 1.4, t, 60 + i, back=True)
        pen.pop(); return
    n = 6 + (int(t * 2) if has(o, "grow") else 0)
    if comp == 0:
        for i in range(n): kid(pen, 200 + i * 190, 900, 0.9, t, 30 + i, cone=(i == 2), jersey=(i == 4))
        if has(o, "count"):
            for i in range(min(n, int(t / max(d, 0.1) * n) + 1)): pen.text(str(i + 1), 200 + i * 190, 520, 70, ACID)
    elif comp == 1:
        for i in range(5):
            x = 260 + i * 330
            for sx in (-1, 1): pen.oval(x + sx * 40, 900, 46, 20, fill=pen.white, stroke=pen.line, w=3)
            pen.ln(x - 40, 880, x - 40, 600, pen.white, 30); pen.ln(x + 40, 880, x + 40, 600, pen.white, 30)
            for k in range(4): pen.ln(x - 80, 640 + k * 40, x + 80, 640 + k * 40, BLUE, 4, 0.6)
    elif comp == 2:
        kid(pen, 960, 1100, 2.6, t, 32, cone=True)
        pen.text("NEVER MELTS", 1500, 300, 60, ACID, "JetBrainsMono-Regular.ttf")
    elif comp == 3:
        kid(pen, 960, 1120, 2.6, t, 34, jersey=True)
        pen.text("FRESNO FIREBIRDS · 2004", 960, 200, 50, ACID, "JetBrainsMono-Regular.ttf")
    else:
        for i in range(6): kid(pen, 300 + i * 220, 900, 0.95, t, 40 + i, back=(i == 5), eyes="wide" if i == 5 else "dot")
        pen.circle(300 + 5 * 220, 520, 90, stroke=RED, w=6, a=0.6 + 0.4 * math.sin(t * 6))
    pen.pop()

def ARM(pen, t, d, gt, s, v, o):
    """Close on the long arm and the cone: reaching, smell trails, never melting, sill puddle with a coin."""
    comp = v % 4
    camera(pen, t, d, 1.0, 1.06, W / 2, 540, s)
    pen.rect(0, 0, W, H, fill="#08070c"); pen.glow(1600, 300, 800, PINK, 0.2)
    if has(o, "sill"):
        pen.rect(0, 640, W, 440, fill="#2a2d38"); pen.rect(0, 620, W, 30, fill="#c9c2b0")
        k = smooth(t / d) if has(o, "melt") else 1.0
        if has(o, "coincu"):
            pen.rect(0, 0, W, H, fill="#14110c"); pen.circle(960, 540, 360, fill=AMBER, stroke="#8a5d14", w=20)
            pen.text("1952", 960, 600, 180, "#8a5d14", "JetBrainsMono-Regular.ttf"); pen.glow(800, 380, 200, WHITE, 0.3 + 0.2 * math.sin(t * 4))
            pen.pop(); return
        if has(o, "puddle"):
            pen.glow(200, 300, 700, "#fff3d6", 0.25); pen.oval(960, 760, 420 * (0.6 + 0.4 * k), 80, fill="#f6c9e0", a=0.6); pen.pop(); return
        if has(o, "coin"):
            pen.oval(960, 760, 360, 70, fill="#f6c9e0", a=0.55); pen.circle(960, 750, 46, fill=AMBER, stroke="#8a5d14", w=6)
            pen.text("1952", 960, 765, 30, "#8a5d14", "JetBrainsMono-Regular.ttf")
        else:
            pen.poly([(920, 580), (1000, 580), (960, 720)], fill="#d9a35a"); pen.circle(960, 560, 60, fill="#f6c9e0")
            pen.text("STEP BACK", 960, 260, 80, ACID)
        pen.pop(); return
    if has(o, "coins"):
        for k in range(6):
            y = (t * 500 + k * 160) % 1000; pen.circle(400 + k * 220, y, 40, fill=AMBER, stroke="#8a5d14", w=5)
        red_x(pen, t - 0.2, 960, 540, 300); pen.pop(); return
    x1 = [1100, 900, 1200, 1000][comp] - 300 * ease_out(t / d)
    pen.path(lambda p: (p.moveTo(W + 60, 300), p.cubicTo(1600, 260, x1 + 300, 520, x1, 520)), stroke=WHITE, w=46)
    for k in range(5): pen.ln(x1, 520, x1 - 80, 470 + k * 26, WHITE, 12)
    pen.poly([(x1 - 120, 460), (x1 - 40, 460), (x1 - 80, 620)], fill="#d9a35a", stroke="#8a6a3a", w=4)
    pen.circle(x1 - 80, 430, 62, fill="#f6c9e0"); pen.circle(x1 - 100, 400, 14, fill=WHITE, a=0.7)
    if has(o, "free"): pen.text("FIRST ONE'S FREE", 960, 900, 80, PINK)
    if has(o, "smell"):
        lab = next((x for x in ("cake", "school", "best") if has(o, x)), "cake")
        word = {"cake": "BIRTHDAY CAKE", "school": "LAST DAY OF SCHOOL", "best": "BEST DAY EVER"}[lab]
        for k in range(3):
            ph = (t * 0.7 + k / 3) % 1
            pen.path(lambda p, k=k, ph=ph: (p.moveTo(x1 - 80, 380), p.cubicTo(x1 - 160 + k * 60, 300 - ph * 120, x1 - 20, 220 - ph * 200, x1 - 120 + k * 80, 120 - ph * 200)), stroke=PINK, w=6, a=0.7 * (1 - ph))
        pen.text(word, 960, 950, 70, CREAM)
    if has(o, "nomelt"):
        pen.text("0% MELTED", 400, 200, 60, ACID, "JetBrainsMono-Regular.ttf")
    if has(o, "no"): red_x(pen, t - 0.3, x1 - 80, 500, 160)
    pen.pop()

def red_x(pen, t, x, y, r):
    if t <= 0: return
    k = ease_out(t / 0.2)
    pen.ln(x - r * k, y - r * k, x + r * k, y + r * k, RED, 30, 0.9); pen.ln(x + r * k, y - r * k, x - r * k, y + r * k, RED, 30, 0.9)

def SATURDAY(pen, t, d, gt, s, v, o):
    """The normal daytime truck: bright, sprinkles, dented freezer, friendly guy."""
    comp = v % 4
    camera(pen, t, d, 1.0, 1.05, W / 2, 560, s)
    sky(pen, t, day=True); pen.circle(1650, 160, 80, fill="#fff3b0"); clouds(pen, t, True)
    pen.rect(0, 860, W, 220, fill="#8a8a8a")
    if has(o, "order"):
        head_close(pen, "dad", 700, 480, 200, {"mouth": "grin", "eyes": "happy"}, t, seed=60)
        pen.poly([(1250, 520), (1350, 520), (1300, 760)], fill="#d9a35a"); pen.circle(1300, 480, 70, fill="#7a4a2a")
        pen.text("ONE CHOCOLATE, EXTRA SPRINKLES", 960, 960, 50, "#222222", "JetBrainsMono-Regular.ttf"); pen.pop(); return
    if has(o, "street"):
        pen.rect(0, 860, W, 220, fill="#8a8a8a")
        for i in range(4): pen.rect(120 + i * 480, 520, 360, 340, fill=["#e8c9a0", "#c9d9e8", "#e8e0b0", "#d9c9e8"][i], stroke=GREY, w=4)
        truck(pen, lerp(2200, 1300, smooth(t / d)), 960, 0.6, t, lights=False); pen.pop(); return
    if has(o, "never"):
        truck(pen, 1500, 960, 1.0, t, window=1.0, lights=False)
        figure(pen, "dad", 600, 1000, 1.3, {"face": {"mouth": "flat", "eyes": "dot", "look": (1, 0)}, "armR": (60, 40)}, t, seed=1)
        figure(pen, "you", 820, 1000, 1.1, {"face": {"mouth": "frown", "eyes": "dot", "look": (1, 0)}, "armL": (60, 40)}, t, seed=3)
        pen.text("NOT FROM A TRUCK.", 600, 260, 70, "#222222"); pen.pop(); return
    if has(o, "summer"):
        pen.rect(0, 800, W, 280, fill="#79b35a")
        figure(pen, "dad", 760, 1000, 1.4, {"face": {"mouth": "smile", "eyes": "happy"}, "armR": (120, 10)}, t, seed=1)
        figure(pen, "you", 1120, 1000, 1.2, {"face": {"mouth": "grin", "eyes": "happy"}, "armL": (120, 10)}, t, seed=3)
        for x in (900, 980): pen.rect(x - 20, 520, 40, 90, fill=[PINK, BLUE][x % 2], r=14); pen.rect(x - 5, 600, 10, 40, fill="#e3c08a")
        pen.text("HOMEMADE", 960, 260, 70, "#222222"); pen.pop(); return
    if comp == 0:
        truck(pen, 1100, 960, 1.4, t, window=1.0, lights=False, song=True)
        for i in range(3): figure(pen, "kid", 300 + i * 170, 960, 0.8, {"face": {"mouth": "grin", "eyes": "happy"}}, t, seed=50 + i)
    elif comp == 1:  # sprinkles cone close
        pen.poly([(900, 500), (1020, 500), (960, 900)], fill="#d9a35a", stroke="#8a6a3a", w=5); pen.circle(960, 450, 120, fill="#f6c9e0")
        rnd = random.Random(3)
        for k in range(40): pen.rect(880 + rnd.random() * 160, 360 + rnd.random() * 160, 18, 6, fill=[PINK, BLUE, AMBER, ACID][k % 4], r=3)
    elif comp == 2:  # dented freezer
        pen.rect(560, 380, 800, 500, fill="#dcdcdc", stroke=GREY, w=6, r=20)
        pen.path(lambda p: (p.moveTo(900, 520), p.quadTo(960, 600, 1040, 520)), stroke=GREY, w=8); pen.text("DENT", 970, 480, 40, GREY, "JetBrainsMono-Regular.ttf")
        for k in range(4): pen.oval(800 + k * 120, 360 - ((t * 60 + k * 30) % 80), 40, 16, fill=WHITE, a=0.4)
    else:  # friendly guy who knows your order
        head_close(pen, "dad", 960, 480, 220, {"mouth": "grin", "eyes": "happy"}, t, seed=60)
        pen.rect(1250, 260, 520, 140, fill=WHITE, r=40); pen.text("THE USUAL?", 1510, 355, 70, "#222222")
    pen.pop()

def CLOCK(pen, t, d, gt, s, v, o):
    comp = v % 3
    camera(pen, t, d, 1.0, 1.08, W / 2, 540, s)
    pen.rect(0, 0, W, H, fill="#0a0b12")
    txt = "12:15" if has(o, "1215") else ("7:00" if has(o, "seven") else "12:14")
    if comp == 0:
        pen.rect(560, 340, 800, 400, fill="#050505", stroke="#333", w=8, r=30)
        colon = ":" if (t % 1) < 0.5 else " "
        pen.text(txt.replace(":", colon), 960, 640, 260, RED, "JetBrainsMono-Regular.ttf")
        pen.glow(960, 540, 500, RED, 0.12)
    elif comp == 1:
        wall_clock(pen, 960, 540, 300, (7 * 3600 if has(o, "seven") else CLK) + t * 2)
    else:
        bedroom_bg(pen, t, clock_txt=txt); pen.rect(0, 0, W, H, fill="#000000", a=0.25)
    pen.pop()

def NOTES(pen, t, d, gt, s, v, o):
    """The song as a music staff: slow, missing notes, a note added per window, becoming your mom's lullaby."""
    comp = v % 3
    camera(pen, t, d, 1.0, 1.05, W / 2, 540, s)
    pen.rect(0, 0, W, H, fill=["#0b0710", "#07090f", "#0f0a08"][comp])
    for k in range(5): pen.ln(120, 380 + k * 60, W - 120, 380 + k * 60, GREY, 3, 0.6)
    n = 10 + (int(t * 3) if has(o, "grow") else 0)
    for i in range(n):
        if has(o, "missing") and i % 3 == 1:
            pen.rect(200 + i * 140 - 20, 420, 40, 140, stroke=RED, w=3, a=0.5); continue
        x = 200 + i * 140 - (t * 60 if has(o, "scroll") else 0); y = 380 + ((i * 37) % 5) * 60
        music_note(pen, x, y, 1.2, PINK if not has(o, "mom") else AMBER)
    if has(o, "stop"):
        pen.rect(200 + 6 * 140, 300, 8, 400, fill=RED); pen.text("— silence —", W / 2, 900, 60, RED, "JetBrainsMono-Regular.ttf")
    if has(o, "slow"): pen.text("0.7×", W - 200, 250, 70, ACID, "JetBrainsMono-Regular.ttf")
    if has(o, "mom"): pen.text("YOUR SONG", W / 2, 900, 80, AMBER)
    if has(o, "grow"): pen.text(f"+{int(t * 3)} NOTES", W / 2, 900, 70, ACID, "JetBrainsMono-Regular.ttf")
    pen.pop()

def DAD(pen, t, d, gt, s, v, o):
    """Your dad. opts: yawn, couch, older, counter, pancakes, hug, slippers, robe."""
    comp = v % 3
    camera(pen, t, d, 1.0, 1.05, W / 2, 560, s)
    grey = has(o, "older", "pancakes")
    if has(o, "yawn"):
        pen.rect(0, 0, W, H, fill="#2a2a36"); pen.rect(0, 760, W, 320, fill="#3a3326")
        pen.rect(300 + comp * 100, 700, 900, 40, fill="#cfccc3")
        head_close(pen, "dad", 760 + comp * 120, 480, 220, {"mouth": "open" if (t % 1.4) < 0.9 else "flat", "eyes": "closed"}, t, seed=1)
        pen.rect(1300, 620, 120, 80, fill="#f3efe4", r=10)  # mug
    elif has(o, "mug"):
        pen.rect(0, 0, W, H, fill="#2a2a36"); pen.rect(0, 760, W, 320, fill="#3a3326")
        pen.rect(760, 440, 360, 380, fill="#f3efe4", stroke=GREY, w=6, r=30); pen.arc(1150, 620, 70, 90, -80, 160, GREY, 26)
        pen.text("WORLD'S OKAYEST DAD", 940, 640, 34, "#5a3b1c", "JetBrainsMono-Regular.ttf")
        for k in range(3):
            ph = (t * 0.6 + k / 3) % 1; pen.path(lambda p, k=k, ph=ph: (p.moveTo(880 + k * 60, 430), p.cubicTo(860 + k * 60, 340 - ph * 60, 920 + k * 60, 300 - ph * 80, 890 + k * 60, 220 - ph * 120)), stroke=WHITE, w=6, a=0.6 * (1 - ph))
    elif has(o, "breakfast"):
        pen.rect(0, 0, W, H, fill="#2a2a36"); pen.rect(0, 760, W, 320, fill="#3a3326"); pen.rect(200, 700, 1520, 40, fill="#cfccc3")
        figure(pen, "dad", 700, 740, 1.2, {"face": {"mouth": "open", "eyes": "closed"}, "armL": (150, 20)}, t, seed=1, seated=True)
        pen.oval(1200, 700, 120, 26, fill="#fafaf5", stroke=GREY, w=3); pen.text("YAAAWN", 1100, 300, 80, GREY)
    elif has(o, "eyebags"):
        pen.rect(0, 0, W, H, fill="#1a1a22")
        head_close(pen, "dad", 960, 560, 420, {"mouth": "flat", "eyes": "dot"}, t, seed=1)
        for sx in (-1, 1): pen.arc(960 + sx * 151, 560, 60, 40, 20, 140, "#6a5a7a", 10)
    elif has(o, "dads"):
        pen.rect(0, 0, W, H, fill="#79b35a")
        for i in range(4):
            figure(pen, "dad", 300 + i * 440, 1000, 1.2, {"face": {"mouth": "smile" if i != 2 else "flat", "eyes": "dot"}}, t, seed=100 + i)
        for k in range(5): pen.ln(300 + 2 * 440 - 60 + k * 30, 500, 300 + 2 * 440 - 50 + k * 30, 480, "#bdbdbd", 8)
        pen.circle(300 + 2 * 440, 500, 140, stroke=RED, w=6, a=0.7)
    elif has(o, "handover"):
        pen.rect(0, 0, W, H, fill="#0b0a12"); pen.glow(960, 500, 700, PINK, 0.2)
        pen.oval(700, 600, 120, 80, fill=pen.white, stroke=pen.line, w=5)  # dad's hand
        pen.path(lambda p: (p.moveTo(W + 40, 300), p.cubicTo(1600, 320, 1400, 560, 1200, 560)), stroke=WHITE, w=40)
        for k in range(4): pen.ln(1200, 560, 1100, 520 + k * 26, WHITE, 12)
        k = (t * 0.7) % 1; x = lerp(760, 1120, k); pen.glow(x, 560, 60, "#d8ff8a", 0.8); pen.circle(x, 560, 10, fill="#efffc0")
    elif has(o, "greyhair"):
        pen.rect(0, 0, W, H, fill="#c9b79a"); head_close(pen, "dad", 960, 620, 420, {"mouth": "smile", "eyes": "dot"}, t, seed=1)
        for k in range(9): pen.ln(720 + k * 60, 330, 740 + k * 60, 290, "#e0e0e0", 12)
    elif has(o, "flip"):
        pen.rect(0, 0, W, H, fill="#c9b79a"); y = 600 - 380 * math.sin(math.pi * clamp((t % 1.2) / 1.2))
        pen.rect(700, 760, 520, 40, fill="#555", r=10); pen.ln(1220, 780, 1500, 800, "#3a3a3a", 26)
        pen.push(rot=(t % 1.2) * 300, ox=960, oy=y); pen.oval(960, y, 160, 40, fill="#d9a35a", stroke="#8a6a3a", w=5); pen.pop()
    elif has(o, "plate"):
        pen.rect(0, 0, W, H, fill="#c9b79a"); pen.oval(960, 820, 420, 90, fill="#fafaf5", stroke=GREY, w=5)
        for k in range(5): pen.oval(960, 780 - k * 50, 260, 50, fill="#d9a35a", stroke="#8a6a3a", w=4)
        pen.path(lambda p: (p.moveTo(860, 560), p.quadTo(960, 640, 1060, 560)), stroke="#7a4a1a", w=14)
        for sx in (-1, 1): pen.circle(960 + sx * 60, 520, 16, fill="#7a4a1a")
    elif has(o, "dawn"):
        sh = skia.GradientShader.MakeLinear([(0, 0), (0, 760)], [C("#2b2a4a"), C("#e8a07a")]); pp = skia.Paint(); pp.setShader(sh); pen.c.drawRect(skia.Rect.MakeWH(W, H), pp)
        pen.rect(0, 820, W, 260, fill="#2a2a30"); truck(pen, lerp(1500, 2600, smooth(t / d)), 960, 0.5, t, song=False)
        figure(pen, "dad", 700, 960, 0.9, {"face": {"mouth": "flat", "eyes": "dot"}}, t, seed=1)
    elif has(o, "calendar"):
        pen.rect(0, 0, W, H, fill="#e9e6df"); months = ["JUNE", "JULY", "AUGUST"]
        k = min(2, int(t / max(d, 0.1) * 3))
        pen.rect(560, 160, 800, 760, fill="#ffffff", stroke=GREY, w=6, r=10); pen.rect(560, 160, 800, 180, fill=RED, r=10)
        pen.text(months[k], 960, 290, 110, WHITE)
        for i in range(28): pen.rect(610 + (i % 7) * 104, 380 + (i // 7) * 130, 90, 110, stroke=GREY, w=2)
    elif has(o, "couch"):
        pen.rect(0, 0, W, H, fill="#1e1d26"); sofa(pen, 360, 900, 900)
        figure(pen, "dad", 800, 760, 1.1, {"face": {"eyes": "closed", "mouth": "o"}, "tilt": -20, "armL": (30, 20)}, t, seed=1, seated=True)
        pen.rect(360, 740, 900, 160, fill="#2b2c31", stroke=GREY, w=4, r=26)
        wall_clock(pen, 1600, 300, 90, 19 * 3600 + t * 10)
        zs = (t * 0.8) % 1; pen.text("z", 950 + zs * 60, 420 - zs * 120, 60 + 30 * zs, WHITE, a=1 - zs)
    elif has(o, "older"):
        pen.rect(0, 0, W, H, fill="#1a1a22")
        for i, (mon, xx) in enumerate((("JUNE", 560), ("AUGUST", 1360))):
            head_close(pen, "dad", xx, 520, 200, {"mouth": "flat", "eyes": "dot" if i == 0 else "closed"}, t, seed=1)
            if i == 1:
                for k in range(5): pen.ln(xx - 120 + k * 60, 360, xx - 100 + k * 60, 330, "#bdbdbd", 8)
            pen.text(mon, xx, 140, 70, ACID if i else WHITE, "JetBrainsMono-Regular.ttf")
        pen.ln(W / 2, 0, W / 2, H, GREY, 4)
    elif has(o, "counter", "robe"):
        pen.rect(0, 0, W, H, fill="#0b0a12"); pen.glow(1500, 400, 900, PINK, 0.3)
        truck(pen, 1700, 1100, 1.4, t, window=1.0, arm=0.4, cone=False)
        figure(pen, "dad", 760, 1000, 1.4, {"face": {"mouth": "flat", "eyes": "dot", "look": (1, 0)}, "armR": (95, 20)}, t, seed=1)
        pen.rect(640, 560, 240, 380, fill="#5a4a6a", a=0.85, r=20)  # robe
        if has(o, "jar"):
            for k in range(7):
                a = t * 2.5 + k; x = 1080 + math.cos(a) * 30; y = 560 + math.sin(a * 1.3) * 25 - k * 6
                pen.glow(x, y, 30, "#d8ff8a", 0.6); pen.circle(x, y, 5, fill="#efffc0")
            pen.rect(1030, 520, 100, 120, stroke=WHITE, w=4, r=14, a=0.7)
    elif has(o, "slippers"):
        pen.rect(0, 0, W, H, fill="#1b1d22"); pen.rect(0, 800, W, 280, fill="#2a2d38")
        x = lerp(500, 1500, smooth(t / d))
        for sx in (-1, 1): pen.oval(x + sx * 70 + (20 * math.sin(t * 8) * sx), 860, 90, 34, fill="#6a5a8a", stroke=GREY, w=4)
        pen.text("12:14 AM", 300, 200, 70, RED, "JetBrainsMono-Regular.ttf")
    elif has(o, "pancakes"):
        pen.rect(0, 0, W, H, fill="#c9b79a"); pen.glow(300, 200, 800, "#fff3d6", 0.6)
        figure(pen, "dad", 760, 1000, 1.5, {"face": {"mouth": "smile", "eyes": "dot"}, "armR": (80, 30)}, t, seed=1)
        for k in range(5): pen.ln(660 + k * 50, 400, 680 + k * 50, 370, "#9a9a9a", 10)  # grey hair
        pen.rect(1100, 620, 500, 40, fill="#555", r=10); pen.oval(1350, 610, 150, 24, fill="#d9a35a")
        for k in range(3):
            ph = (t * 0.6 + k / 3) % 1; pen.oval(1350 + k * 30, 560 - ph * 140, 30, 14, fill=WHITE, a=0.5 * (1 - ph))
    elif has(o, "hug"):
        pen.rect(0, 0, W, H, fill="#c9b79a"); pen.glow(960, 300, 800, "#fff3d6", 0.6)
        figure(pen, "dad", 900, 1050, 1.6, {"face": {"mouth": "smile", "eyes": "happy"}, "armL": (120, 10), "armR": (120, 10)}, t, seed=1)
        figure(pen, "you", 1060, 1050, 1.5, {"face": {"mouth": "smile", "eyes": "closed"}, "armL": (120, 10), "armR": (120, 10)}, t, seed=3)
    pen.pop()

def HOUSE(pen, t, d, gt, s, v, o):
    """Inside the house at night: stairs tiptoe, front door (locked/unlocked), shoe rack (dad's shoes there/gone), hallway photo."""
    comp = v % 3
    camera(pen, t, d, 1.0, 1.05, W / 2, 560, s)
    pen.rect(0, 0, W, H, fill="#16130e"); pen.rect(0, 880, W, 200, fill="#2a2219")
    if has(o, "tiptoe"):
        pen.rect(0, 880, W, 200, fill="#6b2a24")
        for sx in (-1, 1):
            lift = 40 * max(0, math.sin(t * 4 + sx * 1.5)); pen.oval(900 + sx * 120 + t * 80, 900 - lift, 110, 40, fill=pen.white, stroke=pen.line, w=4)
        pen.text("shh", 1400, 400, 90, GREY, "Montserrat-VF.ttf"); pen.pop(); return
    if has(o, "parents"):
        pen.rect(700, 180, 520, 700, fill="#3b2f22", stroke="#c9c2b0", w=10); pen.circle(1160, 560, 16, fill=AMBER)
        zs = (t * 0.7) % 1; pen.text("zzz", 1300 + zs * 80, 400 - zs * 120, 70, WHITE, a=1 - zs)
        pen.text("MOM & DAD", 960, 140, 50, ACID, "JetBrainsMono-Regular.ttf"); pen.pop(); return
    if has(o, "rack"):
        pen.rect(260, 520, 1400, 30, fill="#5a4630"); pen.rect(260, 700, 1400, 30, fill="#5a4630")
        for k in range(6): pen.oval(380 + k * 220, 500, 80, 28, fill=["#7a2c26", "#3a5a8a", "#b8b8b8", "#7a5a2a", "#2a2a2a", "#c98f2c"][k])
        pen.ln(960, 900, 960 + 200 * smooth(t / d), 780, pen.white, 40); pen.pop(); return
    if has(o, "there"):
        for sx in (0, 1): pen.oval(760 + sx * 400, 700, 180, 70, fill="#2a2a2a", stroke=GREY, w=5)
        pen.text("STILL THERE", 960, 300, 90, ACID); pen.pop(); return
    if has(o, "born"):
        pen.rect(0, 0, W, H, fill="#dfe7ee"); pen.oval(960, 640, 360, 220, fill="#f3efe4", stroke=GREY, w=5)
        head_close(pen, "toddler", 960, 560, 110, {"eyes": "closed", "mouth": "o"}, t, seed=3, shoulders=False)
        pen.rect(1100, 700, 160, 40, fill="#ffffff", stroke=PINK, w=4, r=12); pen.text("NEW!", 960, 220, 90, PINK); pen.pop(); return
    if has(o, "photo") and has(o, "hall", "kidcu", "conecu", "squint", "flash", "hot"):
        if has(o, "hall"):
            pen.rect(0, 0, W, H, fill="#221d15")
            for (x, y, w_, h_) in ((200, 260, 300, 220), (1420, 240, 300, 220)): pen.rect(x, y, w_, h_, fill="#d9cfb8", stroke="#8a6a3a", w=8)
            pen.rect(760, 300, 400, 320, fill="#e8dcc0", stroke="#8a6a3a", w=10); pen.rect(790, 330, 340, 230, fill="#9fb4d0")
            figure(pen, "kid", 960, 560, 0.6, {"face": {"mouth": "grin"}}, 0, 70)
        else:
            zf = {"kidcu": (2.4, 960, 420), "conecu": (4.0, 1055, 470), "squint": (4.2, 960, 380), "flash": (1.2, 960, 520), "hot": (1.0, 960, 520)}
            key = next(k for k in zf if has(o, k)); z, fx, fy = zf[key]
            pen.c.save(); pen.c.translate(960, 540); pen.c.scale(z, z); pen.c.translate(-fx, -fy)
            pen.rect(640, 260, 640, 520, fill="#e8dcc0", stroke="#8a6a3a", w=14); pen.rect(680, 300, 560, 380, fill="#9fb4d0")
            figure(pen, "kid", 960, 680, 1.1, {"face": {"mouth": "grin", "eyes": "closed"}, "armR": (60, 50)}, t, seed=70)
            pen.poly([(1040, 470), (1070, 470), (1055, 520)], fill="#d9a35a"); pen.circle(1055, 460, 20, fill="#f6c9e0")
            pen.c.restore()
            if key == "flash": pen.rect(0, 0, W, H, fill=WHITE, a=clamp(1 - t / 0.4))
            if key == "hot":
                pen.circle(1600, 200, 90, fill="#fff3b0", a=0.8)
                for k in range(5): pen.path(lambda p, k=k: (p.moveTo(300 + k * 300, 1000), p.cubicTo(320 + k * 300, 900, 280 + k * 300, 860, 300 + k * 300, 780)), stroke="#ffcf73", w=5, a=0.5)
        pen.pop(); return
    if has(o, "stairs"):
        for k in range(8): pen.rect(200 + k * 160, 880 - k * 100, 400, 100, fill="#3a2f22", stroke="#5a4630", w=4)
        x = lerp(1400, 600, smooth(t / d)); bob = abs(math.sin(t * 5)) * 6
        figure(pen, "you", x, 880 - (1400 - x) / 160 * 100 * 0.0 - bob, 1.0, {"face": {"mouth": "flat", "eyes": "wide", "look": (-1, 0)}}, t, seed=3)
    elif has(o, "door"):
        pen.rect(760, 180, 400, 700, fill="#3b2f22", stroke="#c9c2b0", w=10)
        pen.circle(1110, 560, 18, fill=AMBER)
        locked = has(o, "locked")
        pen.rect(1080, 480, 60, 30, fill=AMBER if locked else "#3a3326", stroke=GREY, w=3)
        pen.text("LOCKED" if locked else "UNLOCKED", 960, 140, 70, ACID if locked else RED, "JetBrainsMono-Regular.ttf")
        if has(o, "close"): pen.text("click.", 1300, 560, 60, GREY, "Montserrat-VF.ttf")
    elif has(o, "shoes"):
        pen.rect(460, 640, 1000, 30, fill="#5a4630"); pen.rect(460, 760, 1000, 30, fill="#5a4630")
        for k in range(4):  # family shoes
            pen.oval(560 + k * 220, 620, 70, 26, fill=["#7a2c26", "#3a5a8a", "#b8b8b8", "#7a5a2a"][k])
        gone = has(o, "gone")
        if gone: pen.rect(1100, 690, 260, 60, stroke=RED, w=4, r=10); pen.text("DAD", 1230, 860, 50, RED, "JetBrainsMono-Regular.ttf")
        else:
            for sx in (0, 1): pen.oval(1170 + sx * 110, 740, 60, 24, fill="#2a2a2a")
            pen.text("DAD", 1230, 860, 50, ACID, "JetBrainsMono-Regular.ttf")
    elif has(o, "photo"):
        z = [1.0, 1.4, 1.9][comp]
        pen.push(s=z, ox=960, oy=520)
        pen.rect(640, 260, 640, 520, fill="#e8dcc0", stroke="#8a6a3a", w=14)
        pen.rect(680, 300, 560, 380, fill="#9fb4d0")
        figure(pen, "kid", 960, 680, 1.1, {"face": {"mouth": "grin", "eyes": "closed"}, "armR": (60, 50)}, t, seed=70)
        pen.poly([(1040, 470), (1070, 470), (1055, 520)], fill="#d9a35a"); pen.circle(1055, 460, 20, fill="#f6c9e0")
        pen.text("SUMMER '94", 960, 740, 44, "#5a3b1c", "Montserrat-VF.ttf")
        pen.pop()
    pen.pop()

def MASON(pen, t, d, gt, s, v, o):
    """Fresno case: file card, Mason with a scoop of moon mint, calendar jump, silent smiling at dinner, truck slowing, receipt."""
    comp = v % 3
    camera(pen, t, d, 1.0, 1.05, W / 2, 560, s)
    if has(o, "file"):
        pen.rect(0, 0, W, H, fill="#14110c"); x0 = lerp(-900, 520, ease_out(t / 0.4))
        pen.rect(x0, 180, 880, 680, fill="#c7a46a", stroke="#7a5e2f", w=6, r=10)
        pen.text("CASE FILE 207", x0 + 440, 320, 70, "#3b2b12", "JetBrainsMono-Regular.ttf")
        if t > 0.4: pen.text("FRESNO, CA", x0 + 440, 560, 100, RED)
    elif has(o, "nine", "scoop"):
        pen.rect(0, 0, W, H, fill="#0b0a12"); pen.glow(1700, 300, 800, PINK, 0.25)
        figure(pen, "kid", 820 + comp * 80, 1040, 1.9, {"face": {"mouth": "smile", "eyes": "dot"}, "armR": (70, 50)}, t, seed=80)
        if has(o, "scoop"):
            pen.poly([(1060, 560), (1110, 560), (1085, 650)], fill="#d9a35a"); pen.circle(1085, 540, 40, fill="#bff0d8")
            pen.text("MOON MINT · 1 WEEK", 960, 160, 64, ACID, "JetBrainsMono-Regular.ttf")
        else: pen.text("MASON, 9", 960, 160, 80, WHITE)
    elif has(o, "calendar"):
        pen.rect(0, 0, W, H, fill="#e9e6df")
        days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        k = min(6, int(t / max(d, 0.1) * 7))
        pen.rect(660, 200, 600, 680, fill="#ffffff", stroke=GREY, w=6, r=10); pen.rect(660, 200, 600, 140, fill=RED, r=10)
        pen.text(days[k], 960, 300, 90, WHITE); pen.text(str(14 + k), 960, 700, 300, "#222222")
    elif has(o, "table"):
        pen.rect(0, 0, W, H, fill="#2a2a36"); pen.glow(960, 100, 700, AMBER, 0.35)
        pen.rect(360, 720, 1200, 40, fill="#cfccc3")
        figure(pen, "mom", 560, 760, 1.1, {"face": {"mouth": "talk", "eyes": "dot", "look": (1, 0)}}, t, seed=81, seated=True)
        figure(pen, "kid", 1300, 760, 1.2, {"face": {"mouth": "grin", "eyes": "wide", "blink": False}}, t, seed=80, seated=True)
        if has(o, "quiet"): pen.text("...", 1300, 360, 120, GREY)
    elif has(o, "slows"):
        STREET(pen, t, d, gt, s, 3, "roll,silent"); pen.text("MASON'S HOUSE", 960, 160, 60, ACID, "JetBrainsMono-Regular.ttf"); return
    elif has(o, "receipt"):
        pen.rect(0, 0, W, H, fill="#0b0a12"); L = 760 * ease_out(t / max(0.4, d * 0.7))
        pen.rect(740, 120, 440, L, fill="#f7f5ee", stroke=GREY, w=3)
        for i, (a_, b_) in enumerate((("MOON MINT", "1"), ("PRICE", "1 WK"), ("", ""), ("STATUS:", ""), ("WATCHING", ""))):
            y = 210 + i * 90
            if y < 120 + L - 30:
                pen.text(a_, 780, y, 40, "#222", "JetBrainsMono-Regular.ttf", align="left"); pen.text(b_, 1140, y, 40, "#222", "JetBrainsMono-Regular.ttf", align="right")
    elif has(o, "eat"):
        pen.rect(0, 0, W, H, fill="#2a2a36"); pen.glow(960, 100, 700, AMBER, 0.35)
        head_close(pen, "kid", 960, 460, 230, {"mouth": "open" if (t % 0.6) < 0.3 else "flat", "eyes": "dot", "blink": False}, t, seed=80)
        pen.ln(1200, 900, 1060, 560 + 40 * math.sin(t * 10), GREY, 14); pen.oval(1050, 550 + 40 * math.sin(t * 10), 40, 22, fill=GREY)
    elif has(o, "smile"):
        pen.rect(0, 0, W, H, fill="#2a2a36"); head_close(pen, "kid", 960, 520, 300, {"mouth": "grin", "eyes": "wide", "blink": False}, t, seed=80)
    elif has(o, "blank"):
        pen.rect(0, 0, W, H, fill="#14110c"); head_close(pen, "kid", 960, 480, 230, {"mouth": "flat", "eyes": "dot", "look": (0, -0.5)}, t, seed=80)
        pen.text("?", 1300, 300, 200, GREY)
    pen.rect(0, 0, W, H, fill="#c08a3a", a=0.08)
    pen.pop()

def STICK(pen, t, d, gt, s, v, o):
    """Rule card: an ice-pop melts away to reveal the rule printed on the stick."""
    if o.startswith("w"):  # wrapped ice pop dropping in, before the rule is revealed
        n = int(o[1:]); camera(pen, t, d, 1.0, 1.05, W / 2, 540, s)
        pen.rect(0, 0, W, H, fill="#0b0710"); pen.glow(960, 540, 800, BLUE, 0.2)
        y = lerp(-700, 160, ease_out(t / 0.5)); pen.push(rot=6 * math.sin(t * 6) * math.exp(-t * 3), ox=960, oy=y + 420)
        pen.rect(700, y, 520, 860, fill="#e9e6df", stroke=GREY, w=6, r=40); pen.text(f"#{n}", 960, y + 470, 200, PINK)
        pen.poly([(700, y), (760, y - 50), (820, y), (880, y - 50), (940, y), (1000, y - 50), (1060, y), (1120, y - 50), (1220, y)], fill="#e9e6df")
        pen.pop(); pen.pop(); return
    n = int(o) if o.isdigit() else 0
    camera(pen, t, d, 1.0, 1.05, W / 2, 540, s)
    pen.rect(0, 0, W, H, fill="#0b0710"); pen.glow(960, 540, 800, PINK, 0.2)
    pen.rect(800, 160, 320, 860, fill="#e3c08a", stroke="#a5824a", w=6, r=150)
    pen.text(f"RULE {n}", 960, 330, 66, "#5a3b1c", "JetBrainsMono-Regular.ttf")
    txt = RULES[n].split(); lines, cur = [], ""
    for w_ in txt:
        if len(cur + " " + w_) > 9: lines.append(cur.strip()); cur = ""
        cur += " " + w_
    lines.append(cur.strip())
    for i, ln_ in enumerate(lines): pen.text(ln_, 960, 460 + i * 80, 62, "#3b2b12")
    melt = clamp(t / 0.8)
    top = lerp(80, 980, melt)
    if melt < 1:
        pen.rect(700, top, 520, 980 - top, fill=[PINK, BLUE, "#bff0d8", AMBER, "#f6c9e0", "#9fd0ff", "#ffd27a"][(n - 1) % 7], r=60)
    for k in range(5):
        if melt > 0.1: pen.oval(760 + k * 100, 1000 + 20 * math.sin(t * 3 + k), 40, 16, fill=PINK, a=0.6)
    pen.pop()
RULES = {1: "DON'T GO TO THE WINDOW.", 2: "NEVER TAKE A FREE SAMPLE.", 3: "READ THE PRICES.", 4: "COUNT THE KIDS IN LINE.",
         5: "IF IT PLAYS YOUR SONG, HUM.", 6: "CHECK YOUR DAD'S SHOES.", 7: "DON'T WAIT UP FOR HIM."}

def KT(pen, t, d, gt, s, v, o):
    pen.rect(0, 0, W, H, fill=["#0b0710", "#05080a", "#0a0a03", "#07070c"][v % 4]); pen.glow(960, 540, 700, PINK if v % 2 else BLUE, 0.12)
    kinetic(pen, o.replace("_", " "), t, ACID if v % 3 else WHITE, size=200 if len(o) < 14 else 130)

def YOU(pen, t, d, gt, s, v, o):
    """You close: background bedroom/window/hall; expressions from opts."""
    comp = v % 4
    camera(pen, t, d, 1.0, 1.06, W / 2, 560, s)
    if comp == 0: bedroom_bg(pen, t, lamp=has(o, "lamp")); pen.rect(0, 0, W, H, fill="#000000", a=0.45)
    elif comp == 1: pen.rect(0, 0, W, H, fill="#0b0710"); pen.glow(1600, 300, 900, PINK, 0.28)
    elif comp == 2: pen.rect(0, 0, W, H, fill="#16130e")
    else: pen.rect(0, 0, W, H, fill="#121521"); pen.rect(1300, 120, 420, 420, fill="#0b1020", stroke="#c9c2b0", w=8)
    x = [W / 2, 700, 1220, 820][comp]; r = [230, 260, 210, 280][comp]
    eyes = "closed" if has(o, "shut") else ("wide" if has(o, "scared", "freeze", "wide") else "dot")
    mouth = "o" if has(o, "hum", "count") else ("wobble" if has(o, "scared") else ("smile" if has(o, "smile") else "flat"))
    look = (1, -0.4) if has(o, "look") else ((-1, 0) if has(o, "side") else (0, 0.2))
    head_close(pen, "you", x, 470, r, {"eyes": eyes, "mouth": mouth, "look": look, "blink": not has(o, "freeze", "wide"),
                                      "tremble": 0.8 if has(o, "scared") else 0, "tears": 0.5 if has(o, "tears") else 0}, t, seed=3)
    if has(o, "cone"):
        pen.poly([(x + r * 1.1, 640), (x + r * 1.5, 640), (x + r * 1.3, 900)], fill="#d9a35a", stroke="#8a6a3a", w=5); pen.circle(x + r * 1.3, 600, r * 0.3, fill="#f6c9e0")
    if has(o, "ears"):
        for sx in (-1, 1): pen.oval(x + sx * r * 1.05, 470, r * 0.35, r * 0.5, fill=pen.white, stroke=pen.line, w=4)
    if has(o, "hum"): notes(pen, x + r, 300, t, 3, AMBER)
    if has(o, "count"):
        n = 100 - int(t * 2.5); pen.text(str(n), x + r * 1.9, 400, 150, ACID)
    if has(o, "smell"):
        for k in range(3):
            ph = (t * 0.7 + k / 3) % 1; pen.path(lambda p, k=k, ph=ph: (p.moveTo(x + r * 1.8, 520), p.cubicTo(x + r * 1.4, 520 - k * 30, x + r * 1.2, 500, x + r * 0.3, 490)), stroke=PINK, w=6, a=0.7 * (1 - ph))
    pen.pop()

def COUNTDOWN(pen, t, d, gt, s, v, o):
    camera(pen, t, d, 1.0, 1.05, W / 2, 540, s)
    pen.rect(0, 0, W, H, fill=["#05070c", "#0b0710"][v % 2])
    n = 100 - int(t * 3)
    pen.text(str(n), W / 2, 640, 360, WHITE)
    if has(o, "notune"):
        for k in range(5): pen.ln(220, 820 + k * 30, W - 220, 820 + k * 30, GREY, 3, 0.5)
        red_x(pen, t - 0.3, W / 2, 880, 120); pen.text("NO TUNE", W / 2, 260, 70, ACID, "JetBrainsMono-Regular.ttf")
    pen.pop()

def MOM_SONG(pen, t, d, gt, s, v, o):
    """VHS memory: mom singing to baby you."""
    camera(pen, t, d, 1.0, 1.05, W / 2, 560, s)
    if has(o, "close"):
        pen.rect(0, 0, W, H, fill="#3a3024"); head_close(pen, "mom", 860, 480, 240, {"mouth": "o", "eyes": "happy"}, t, seed=2, tilt=-6)
        notes(pen, 1200, 400, t, 4, AMBER); pen.rect(0, 0, W, H, fill="#c08a3a", a=0.16)
        for y in range(0, H, 6): pen.ln(0, y, W, y, "#000000", 2, 0.16)
        pen.pop(); return
    pen.rect(0, 0, W, H, fill="#3a3024"); pen.rect(0, 860, W, 220, fill="#2a2219")
    pen.rect(600, 640, 520, 240, fill="#8a6a44", stroke="#5a4630", w=6)  # crib
    for k in range(8): pen.ln(620 + k * 64, 640, 620 + k * 64, 860, "#5a4630", 6)
    head_close(pen, "toddler", 860, 620, 70, {"eyes": "closed", "mouth": "flat"}, t, seed=3, shoulders=False)
    figure(pen, "mom", 1300, 1000, 1.3, {"face": {"mouth": "o", "eyes": "happy", "look": (-1, 0.3)}, "tilt": -8}, t, seed=2)
    notes(pen, 1150, 500, t, 4, AMBER)
    pen.rect(0, 0, W, H, fill="#c08a3a", a=0.16)
    for y in range(0, H, 6): pen.ln(0, y, W, y, "#000000", 2, 0.16)
    pen.text("PLAY >", 70, 140, 48, WHITE, "JetBrainsMono-Regular.ttf", 0.85, "left"); pen.text("MAY 2016", W - 70, H - 150, 40, WHITE, "JetBrainsMono-Regular.ttf", 0.85, "right")
    pen.pop()

def FEET(pen, t, d, gt, s, v, o):
    """Your bare feet on the bedroom floor, inching toward the door / the window."""
    camera(pen, t, d, 1.0, 1.06, W / 2, 700, s)
    pen.rect(0, 0, W, H, fill="#121521"); pen.rect(0, 700, W, 380, fill="#2a2d38")
    for k in range(8): pen.ln(0, 720 + k * 50, W, 720 + k * 50, "#3a3e4c", 3)
    x = lerp(700, 1100, smooth(t / d)) if has(o, "walk") else 900
    for sx in (-1, 1):
        lift = 30 * max(0, math.sin(t * 5 + sx)) if has(o, "walk") else 0
        pen.oval(x + sx * 110, 880 - lift, 100, 40, fill=pen.white, stroke=pen.line, w=4)
        pen.ln(x + sx * 110, 860 - lift, x + sx * 100, 500, pen.white, 70); pen.ln(x + sx * 110, 860 - lift, x + sx * 100, 500, "#3a4a7a", 0)
    notes(pen, 1500, 400, t, 3, PINK)
    if has(o, "door"): pen.rect(1500, 100, 300, 620, stroke="#c9c2b0", w=10); pen.text("DOOR", 1650, 80, 40, ACID, "JetBrainsMono-Regular.ttf")
    pen.pop()

def JAR(pen, t, d, gt, s, v, o):
    """A jar of glowing fireflies: his time."""
    camera(pen, t, d, 1.0, 1.08, W / 2, 540, s)
    pen.rect(0, 0, W, H, fill="#06080e")
    pen.rect(700, 260, 520, 620, stroke=WHITE, w=8, r=60, a=0.8); pen.rect(740, 200, 440, 70, fill=GREY, r=14)
    for k in range(16):
        a = t * (1 + k * 0.1) + k; x = 960 + math.cos(a) * 160 * math.sin(k); y = 560 + math.sin(a * 1.3) * 220
        pen.glow(x, y, 50, "#d8ff8a", 0.6); pen.circle(x, y, 7, fill="#efffc0")
    pen.text("HIS TIME", 960, 1000, 60, ACID, "JetBrainsMono-Regular.ttf")
    pen.pop()

BUILDERS = {k: v for k, v in globals().items() if k.isupper() and callable(v) and k not in ("PINK", "BLUE", "CREAM", "CLK", "RULES")}

def draw(pen, t, dur, gt, shot):
    base, _, rest = shot["setup"].partition("#")
    v_str, _, opts = rest.partition(":")
    fn = BUILDERS.get(base)
    if not fn: return None, False
    v = int(v_str or 0); k = v // COMPS.get(base, 1)
    pen.mood = "normal"; pen.c.save()
    if k:  # each further use of a builder reframes the whole picture (tighter, different area)
        z = 1 + 0.2 * k; ox = W / 2 + [0, -260, 260, -140, 140][k % 5]; oy = H / 2 + [0, 80, -80, 40, -40][k % 5]
        pen.c.translate(ox, oy); pen.c.scale(z, z); pen.c.translate(-ox, -oy)
    fn(pen, t, dur, gt, shot, v, opts); pen.c.restore(); return None, True
COMPS = {"STREET": 5, "TRUCK": 6, "MENU": 4, "BEDROOM": 5, "WINDOW_DOWN": 3, "KIDS": 5, "ARM": 4, "SATURDAY": 4, "CLOCK": 3, "NOTES": 3,
         "DAD": 1, "HOUSE": 1, "MASON": 1, "YOU": 4, "COUNTDOWN": 2, "STICK": 1, "KT": 4, "MOM_SONG": 1, "FEET": 1, "JAR": 1}
