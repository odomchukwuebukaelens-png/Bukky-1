"""Detailed-but-simple sets (layered, animated). World coordinates are 1920x1080; shots frame parts of them."""
import math, random
from engine import *

def sky(pen, t, top="#05070f", bottom="#121a33", day=False):
    if day: top, bottom = "#6fb3e8", "#cfe8f7"
    sh = skia.GradientShader.MakeLinear([(0, 0), (0, 760)], [C(top), C(bottom)])
    p = skia.Paint(); p.setShader(sh); pen.c.drawRect(skia.Rect.MakeWH(W, H), p)
    if not day:
        rnd = random.Random(7)
        for k in range(70):
            x, y = rnd.random() * W, rnd.random() * 560
            pen.circle(x, y, 1.2 + rnd.random() * 1.6, fill=WHITE, a=0.35 + 0.35 * math.sin(t * (1 + rnd.random() * 2) + k))

def moon(pen, x, y, t, r=55):
    pen.glow(x, y, r * 4, "#fff2c0", 0.22); pen.circle(x, y, r, fill="#f4ecd0")
    for dx, dy, rr in ((-14, -10, 9), (12, 14, 6), (18, -16, 5)): pen.circle(x + dx * r / 55, y + dy * r / 55, rr * r / 55, fill="#e2d8b8")

def clouds(pen, t, day=False, y0=150):
    for k in range(4):
        x = ((k * 560 + t * (18 + 6 * k)) % (W + 700)) - 350; y = y0 + k * 55
        col, a = ("#ffffff", 0.9) if day else ("#2a3350", 0.75)
        for j, (dx, rr) in enumerate(((0, 60), (60, 80), (130, 64), (190, 46))):
            pen.circle(x + dx, y - rr * 0.3, rr, fill=col, a=a)

def treeline(pen, t, y, color, seed, h=160, sway=0.0):
    rnd = random.Random(seed)
    def build(p):
        p.moveTo(-20, H); p.lineTo(-20, y)
        x = -20
        while x < W + 40:
            w_ = 60 + rnd.random() * 90; hh = h * (0.5 + rnd.random() * 0.6)
            sw = math.sin(t * 0.8 + x * 0.01) * sway
            p.quadTo(x + w_ / 2 + sw, y - hh, x + w_, y); x += w_
        p.lineTo(W + 40, H); p.close()
    pen.path(build, fill=color)

def fence(pen, y, t, x0=0, x1=W, color="#5b4a3a", night=True):
    col = "#3a3129" if night else "#c8a57a"; edge = "#6c5a46" if night else "#8a6a44"
    pen.rect(x0, y - 150, x1 - x0, 18, fill=col); pen.rect(x0, y - 70, x1 - x0, 18, fill=col)
    x = x0
    while x < x1:
        pen.poly([(x, y), (x, y - 190), (x + 22, y - 210), (x + 44, y - 190), (x + 44, y)], fill=col, stroke=edge, w=2)
        x += 54

def big_tree(pen, x, y, t, s=1.0, night=True):
    trunk = "#2a2219" if night else "#7a5634"; leaf = "#0f1a14" if night else "#4f8f4a"; leaf2 = "#16261c" if night else "#6aa85e"
    pen.poly([(x - 40 * s, y), (x - 26 * s, y - 380 * s), (x + 26 * s, y - 380 * s), (x + 44 * s, y)], fill=trunk)
    pen.ln(x, y - 300 * s, x + 170 * s, y - 360 * s, trunk, 26 * s)  # branch for the swing
    for k, (dx, dy, r) in enumerate(((-120, -420, 150), (60, -470, 170), (180, -400, 140), (-20, -560, 150), (-200, -330, 110))):
        sw = math.sin(t * 0.9 + k) * 6
        pen.circle(x + dx * s + sw, y + dy * s, r * s, fill=leaf2 if k % 2 else leaf)

def swing(pen, x, y_branch, t, s=1.0, night=True):
    a = math.sin(t * 1.4) * 0.12
    L = 300 * s; ex, ey = x + math.sin(a) * L, y_branch + math.cos(a) * L
    pen.ln(x, y_branch, ex, ey, "#8a8a86" if night else "#555555", 4)
    pen.circle(ex, ey + 30 * s, 42 * s, stroke="#1a1a1a", w=18 * s)  # tyre swing

def grass(pen, y, t, color="#1a2a1a", n=90, h=26, day=False):
    pen.rect(0, y, W, H - y, fill="#0e1710" if not day else "#79b35a")
    rnd = random.Random(3)
    for k in range(n):
        x = rnd.random() * W; yy = y + rnd.random() * (H - y); hh = h * (0.6 + rnd.random())
        sw = math.sin(t * 1.6 + x * 0.02) * 6
        pen.ln(x, yy, x + sw, yy - hh, color if not day else "#5e9a45", 3)

def fireflies(pen, t, n=14, region=(0, 380, W, 900)):
    rnd = random.Random(11)
    x0, y0, x1, y1 = region
    for k in range(n):
        bx, by = x0 + rnd.random() * (x1 - x0), y0 + rnd.random() * (y1 - y0)
        x = bx + 40 * math.sin(t * 0.7 + k * 1.9); y = by + 25 * math.sin(t * 0.9 + k)
        on = 0.5 + 0.5 * math.sin(t * 2.3 + k * 2.1)
        if on > 0.25:
            pen.glow(x, y, 26, "#d8ff8a", 0.55 * on); pen.circle(x, y, 3, fill="#efffc0", a=on)

def house_back(pen, t, x1=760, ground=880, door_open=1.0, door_x=470, lit=True):
    """Back wall of the house occupying x<x1: siding, curtained lit window, porch, light, open back door."""
    pen.rect(-20, 120, x1 + 20, ground - 120, fill="#1b1d26")
    for y in range(140, ground, 26): pen.ln(-20, y, x1, y, "#232634", 3)  # siding
    pen.poly([(-20, 120), (x1 + 40, 120), (x1 - 40, 60), (-20, 60)], fill="#141620")  # roof edge
    # window with curtains
    wx, wy = 90, 330
    pen.rect(wx, wy, 220, 200, fill="#ffcf73" if lit else "#11131a", stroke="#c9c2b0", w=6)
    if lit: pen.glow(wx + 110, wy + 100, 260, AMBER, 0.18)
    for sx in (0, 1):
        pen.path(lambda p, sx=sx: (p.moveTo(wx + sx * 220, wy), p.quadTo(wx + sx * 220 + (70 if sx == 0 else -70), wy + 100, wx + sx * 220 + (40 if sx == 0 else -40), wy + 200),
                                   p.lineTo(wx + sx * 220, wy + 200), p.close()), fill="#c0603a")
    pen.ln(wx + 110, wy, wx + 110, wy + 200, "#c9c2b0", 5); pen.rect(wx - 10, wy + 200, 240, 16, fill="#c9c2b0")
    # door + light spill
    dw, dh = 170, 330; dy = ground - 60 - dh
    if door_open > 0:
        pen.rect(door_x, dy, dw, dh, fill="#ffcf73")
        pen.poly([(door_x, ground - 60), (door_x + dw, ground - 60), (door_x + dw + 520 * door_open, H + 40), (door_x - 120 * door_open, H + 40)], fill=AMBER, a=0.22 * door_open, blur=14)
        pen.poly([(door_x + dw, dy), (door_x + dw + 70 * door_open, dy + 20), (door_x + dw + 70 * door_open, ground - 80), (door_x + dw, ground - 60)], fill="#3b3f52", stroke="#c9c2b0", w=4)
    else:
        pen.rect(door_x, dy, dw, dh, fill="#3b3f52", stroke="#c9c2b0", w=4)
    pen.rect(door_x - 10, dy - 10, dw + 20, 10, fill="#c9c2b0")
    # porch deck + steps
    pen.rect(-20, ground - 60, x1 + 40, 24, fill="#4a3a2b", stroke="#6c5a46", w=3)
    for k in range(3): pen.rect(door_x - 20 + k * 0, ground - 36 + k * 30, dw + 40, 26, fill="#3e3024", stroke="#6c5a46", w=3)
    pen.rect(door_x + 25, ground - 64, dw - 50, 10, fill="#7a2c26")  # doormat
    # porch light with moths
    lx, ly = door_x + dw + 60, dy + 40
    pen.rect(lx - 16, ly - 30, 32, 44, fill="#ffe7a0", stroke="#c9c2b0", w=3); pen.glow(lx, ly, 140, "#ffe7a0", 0.45)
    for k in range(5):
        a = t * (3 + k * 0.7) + k * 1.3; mx, my = lx + math.cos(a) * (40 + k * 9), ly + math.sin(a * 1.3) * (30 + k * 6)
        pen.oval(mx, my, 5, 3, fill="#e8e1cc", a=0.9)
    # potted plant + boots on porch
    pen.rect(30, ground - 130, 70, 70, fill="#8a4a2a", r=6)
    for k in range(5): pen.ln(65, ground - 128, 65 + (k - 2) * 22, ground - 210 + abs(k - 2) * 14, "#2f5a33", 9)

def backyard(pen, t, door_open=1.0, day=False, house=True, ground=880):
    sky(pen, t, day=day)
    if day: pen.glow(1600, 170, 260, "#fff6c8", 0.6); pen.circle(1600, 170, 70, fill="#fff3b0")
    else: moon(pen, 1450, 190, t)
    clouds(pen, t, day)
    treeline(pen, t, 640, "#0a0f14" if not day else "#3d6e48", 1, 180)
    treeline(pen, t, 700, "#0d1418" if not day else "#4f8a55", 2, 120, 3)
    fence(pen, 760, t, night=not day)
    big_tree(pen, 1500, ground - 40, t, 1.0, night=not day)
    swing(pen, 1670, ground - 400, t, 1.0, night=not day)
    grass(pen, ground - 120, t, day=day)
    pen.rect(1180, ground - 40, 46, 30, fill="#6a6a70" if not day else "#888", r=6)  # garden gnome base
    pen.poly([(1186, ground - 40), (1203, ground - 110), (1220, ground - 40)], fill=RED)
    if house: house_back(pen, t, door_open=door_open, lit=not day)
    if not day: fireflies(pen, t)

def kitchen(pen, t, clock_s, dog_bowl=True):
    pen.rect(0, 0, W, H, fill="#14161c")
    for y in range(0, 560, 60):  # tiled backsplash band
        for x in range((y // 60 % 2) * 40, W, 80): pen.rect(x, 430 + (y % 120), 76, 56, stroke="#232633", w=2)
    pen.rect(0, 130, 1300, 250, fill="#2a2d38", stroke="#3a3e4c", w=3)  # upper cabinets
    for x in range(20, 1300, 260):
        pen.rect(x, 145, 240, 220, stroke="#3f4352", w=3, r=6); pen.circle(x + 215, 255, 7, fill=GREY)
    pen.rect(0, 640, 1300, 300, fill="#2a2d38", stroke="#3a3e4c", w=3)  # lower cabinets
    pen.rect(-10, 620, 1320, 30, fill="#cfccc3")  # counter
    for x in range(20, 1300, 260):
        pen.rect(x, 670, 240, 250, stroke="#3f4352", w=3, r=6); pen.rect(x + 95, 700, 50, 8, fill=GREY, r=3)
    # window with moon + plant
    pen.rect(420, 410, 300, 200, fill="#0b1020", stroke="#c9c2b0", w=6); pen.ln(570, 410, 570, 610, "#c9c2b0", 5)
    moon(pen, 650, 470, t, 26)
    pen.rect(450, 570, 60, 50, fill="#8a4a2a", r=6)
    for k in range(4): pen.ln(480, 572, 480 + (k - 1.5) * 18, 520 + abs(k - 1.5) * 10, "#2f5a33", 7)
    # hanging pans
    pen.ln(860, 120, 1180, 120, GREY, 5)
    for k, (x, r) in enumerate(((900, 46), (1010, 58), (1130, 40))):
        sw = math.sin(t * 1.3 + k) * 3
        pen.ln(x, 120, x + sw, 170, GREY, 3); pen.circle(x + sw, 170 + r, r, fill="#3a3b40", stroke=GREY, w=4)
    # fridge with child's drawing
    pen.rect(1340, 160, 280, 780, fill="#d8d8d2", stroke="#9b9b98", w=4, r=16)
    pen.ln(1340, 470, 1620, 470, "#9b9b98", 4); pen.rect(1590, 240, 12, 140, fill=GREY, r=5); pen.rect(1590, 520, 12, 200, fill=GREY, r=5)
    pen.rect(1400, 250, 120, 100, fill="#ffffff", stroke="#c9c2b0", w=2)
    figure(pen, "you", 1435, 340, 0.22, {"face": {"mouth": "smile"}, "blink": False}, 0, 3)
    dog(pen, 1490, 340, 0.17, 0)
    pen.circle(1405, 245, 8, fill=RED)  # magnet
    # clock
    wall_clock(pen, 1110, 330, 60, clock_s)
    # back door with glass + leash hook
    pen.rect(1660, 260, 230, 680, fill="#3b3f52", stroke="#c9c2b0", w=5)
    pen.rect(1700, 300, 150, 200, fill="#0b1020", stroke="#c9c2b0", w=4)
    pen.circle(1690, 640, 12, fill=AMBER)
    pen.ln(1640, 360, 1640, 380, GREY, 6); pen.path(lambda p: (p.moveTo(1640, 380), p.quadTo(1610, 520, 1650, 600)), stroke=RED, w=7)
    # floor + dog bowl (full, untouched)
    pen.rect(0, 940, W, 140, fill="#1d1f27")
    for x in range(0, W, 120): pen.ln(x, 940, x - 80, H, "#262934", 3)
    if dog_bowl:
        pen.oval(1500, 975, 90, 22, fill="#7a2c26", stroke=GREY, w=3); pen.oval(1500, 965, 64, 14, fill="#8a5a2a")
        pen.text("BRUNO", 1500, 1015, 26, WHITE, "JetBrainsMono-Regular.ttf")
    pendant_lamp(pen, 700, 70, t, cone_to=960, spread=420)
