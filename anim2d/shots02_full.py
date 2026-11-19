"""Video 02 full: 'If Your Dog Ever Refuses To Come Inside At Night... DON'T CALL HIM AGAIN'.
Shot names are 'BUILDER#variant:opts'. Every builder changes its composition with the variant number,
so every shot in the video is a distinct picture."""
import math, random
from engine import *
from scenes import *
from shots01 import camera
import shots02 as T  # the approved opening shots

CLOCK = 23 * 3600 + 48 * 60

# ---------------- variant camera ----------------
VC = [(1.00, 0, 0, 0), (1.18, -160, -40, 0), (1.32, 180, 30, 0), (1.12, 90, -60, -3), (1.45, -220, 40, 0),
      (1.25, 0, 80, 3), (1.6, 120, -20, 0), (1.08, -60, 20, 2), (1.38, -120, -70, 0), (1.22, 220, 60, -2)]
def vcam(pen, t, d, v, fx=W / 2, fy=H / 2, push=0.06, s=None):
    z, dx, dy, rot = VC[v % len(VC)]
    zz0 = z; zz1 = z * (1 + (push if v % 3 != 2 else -push))
    camera(pen, t, d, zz0, zz1, fx + dx, fy + dy, s, rot=rot)
def mirror(pen, v):
    pen.c.save()
    if v % 2: pen.c.translate(W, 0); pen.c.scale(-1, 1)
def unmirror(pen): pen.c.restore()

def ears_of(o):
    return 0 if "flat" in o else (0.5 if "one" in o else 1)

# ---------------- locations ----------------
def YARD(pen, t, d, gt, s, v, o):
    """8 distinct compositions of the moonlit yard (x2 mirrored). Dog pose from opts."""
    comp = v % 8; flip = (v // 8) % 2
    tail = -1 if "tuck" in o else (1.2 if "wag" in o else 0); ears = ears_of(o)
    away = "away" in o; nodog = "nodog" in o
    camera(pen, t, d, 1.0, 1.05, W / 2, 560, s)
    pen.c.save()
    if flip: pen.c.translate(W, 0); pen.c.scale(-1, 1)
    if comp == 0:   # establishing wide: house, porch, lawn, dog
        backyard(pen, t, door_open=0.0 if "closed" in o else 1.0)
        x = lerp(1150, 1800, smooth(t / d)) if away else ({"edge": 1750}.get("edge" if "edge" in o else "", 1150))
        if not nodog: dog(pen, x, 840, 0.55, t, facing=1 if away else -1, tail=tail, ears=ears, glow=0.5, step=0.6 if away else 0)
    elif comp == 1:  # grass level: huge blades in front, dog mid-distance, big sky
        sky(pen, t); moon(pen, 1450, 260, t, 70); clouds(pen, t); treeline(pen, t, 760, "#0a0f14", 51, 140)
        grass(pen, 820, t)
        if not nodog: dog(pen, 1000 + (300 * smooth(t / d) if away else 0), 900, 0.9, t, facing=1 if away else -1, tail=tail, ears=ears, glow=0.5, step=0.6 if away else 0)
        for k in range(16):
            x = k * 130 + 40; sw = math.sin(t * 1.5 + k) * 18
            pen.path(lambda p_, x=x, sw=sw: (p_.moveTo(x - 26, H + 10), p_.quadTo(x + sw, 760, x + 30 + sw, 640 + (k * 37) % 120), p_.quadTo(x + 10, 800, x + 26, H + 10), p_.close()), fill="#0f1c10")
    elif comp == 2:  # silhouette against a huge moon
        sky(pen, t); pen.glow(960, 520, 700, "#fff2c0", 0.25); pen.circle(960, 520, 300, fill="#f1e8c8")
        pen.path(lambda p_: (p_.moveTo(-20, H), p_.lineTo(-20, 840), p_.quadTo(960, 700, W + 20, 840), p_.lineTo(W + 20, H), p_.close()), fill="#05080a")
        if not nodog:
            pen.mood = "dark"; dog(pen, 960 + (300 * smooth(t / d) if away else 0), 760, 1.0, t, facing=1 if away else -1, tail=tail, ears=ears, step=0.6 if away else 0)
            pen.rect(0, 0, W, H, fill="#000000", a=0.0); pen.mood = "normal"
    elif comp == 3:  # through the fence slats
        backyard(pen, t, door_open=1.0, house=True)
        if not nodog: dog(pen, 1000, 860, 0.8, t, facing=-1, tail=tail, ears=ears, glow=0.5)
        for x in range(-40, W, 230): pen.rect(x, 0, 150, H, fill="#2b241c", stroke="#3a3129", w=4)
        pen.rect(0, 300, W, 40, fill="#2b241c"); pen.rect(0, 760, W, 40, fill="#2b241c")
    elif comp == 4:  # from under the tree: trunk + leaves framing, swing, dog far right
        sky(pen, t); moon(pen, 1300, 200, t, 50); treeline(pen, t, 700, "#0a0f14", 52, 150); fence(pen, 770, t); grass(pen, 760, t)
        swing(pen, 900, 120, t, 1.4)
        if not nodog: dog(pen, 1450, 900, 0.75, t, facing=-1, tail=tail, ears=ears, glow=0.5)
        pen.rect(60, 0, 190, H, fill="#1d1710"); pen.ln(250, 140, 1300, 40, "#1d1710", 60)
        for k in range(8): pen.circle(150 + k * 230, 30 + (k % 3) * 40, 170, fill="#0d1612" if k % 2 else "#121f17")
    elif comp == 5:  # from the porch steps: boards in front, lawn beyond
        sky(pen, t); moon(pen, 1500, 180, t, 48); treeline(pen, t, 600, "#0a0f14", 53, 150); fence(pen, 680, t); grass(pen, 660, t)
        pen.poly([(700, 660), (1220, 660), (1700, H), (220, H)], fill=AMBER, a=0.12, blur=12)
        if not nodog: dog(pen, 960 + (500 * smooth(t / d) if away else 0), 800, 0.6, t, facing=1 if away else -1, tail=tail, ears=ears, glow=0.6, step=0.6 if away else 0)
        for k in range(3): pen.rect(-20, 860 + k * 70, W + 40, 64, fill="#3e3024", stroke="#6c5a46", w=4)
    elif comp == 6:  # high angle: lawn fills frame, long shadow from the door light
        pen.rect(0, 0, W, H, fill="#0e1710"); grass(pen, 0, t, "#1a2a1a", 160, 30)
        pen.poly([(0, 0), (900, 0), (1500, H), (0, H)], fill=AMBER, a=0.10, blur=20)
        if not nodog:
            x = 960 + (400 * smooth(t / d) if away else 0)
            pen.oval(x + 260, 760, 360, 40, fill="#000000", a=0.55)
            dog(pen, x, 760, 0.9, t, facing=1 if away else -1, tail=tail, ears=ears, step=0.6 if away else 0)
        fireflies(pen, t, 10, (0, 0, W, H))
    else:  # through the kitchen window: frame, plant, the yard beyond
        sky(pen, t); moon(pen, 1200, 260, t, 50); treeline(pen, t, 640, "#0a0f14", 54, 160); fence(pen, 720, t); grass(pen, 700, t)
        if not nodog: dog(pen, 1000, 860, 0.7, t, facing=-1, tail=tail, ears=ears, glow=0.6)
        pen.rect(0, 0, W, 160, fill="#14161c"); pen.rect(0, 920, W, 200, fill="#2a2d38"); pen.rect(0, 0, 220, H, fill="#14161c"); pen.rect(W - 220, 0, 220, H, fill="#14161c")
        pen.rect(210, 150, W - 420, 780, stroke="#c9c2b0", w=16); pen.ln(W / 2, 150, W / 2, 930, "#c9c2b0", 12)
        pen.rect(280, 820, 120, 100, fill="#8a4a2a", r=10)
        for k in range(5): pen.ln(340, 822, 340 + (k - 2) * 40, 700 + abs(k - 2) * 26, "#2f5a33", 12)
    if "mist" in o:
        k = smooth(t / d)
        for j in range(6): pen.oval(lerp(400, 1800, k) - j * 60, 700 - j * 8, 140, 46, fill="#cfe8ff", a=0.13)
    pen.c.restore(); pen.pop()

def DOORFRAME_VIEW(pen, t, d, gt, s, v, o):
    """Looking out through the open back door at the lawn (variants move dog/moon/framing)."""
    vcam(pen, t, d, v, W / 2, 560, 0.04, s)
    sky(pen, t); moon(pen, [1300, 600, 1500, 900][v % 4], 170, t, 48); clouds(pen, t)
    treeline(pen, t, 600, "#0a0f14", 21 + v, 160); fence(pen, 690, t); grass(pen, 650, t)
    pen.poly([(700, 650), (1220, 650), (1700, H), (220, H)], fill=AMBER, a=0.12, blur=12)
    dx = [1000, 760, 1240, 960][v % 4]
    if "away" in o: dx = lerp(dx, 1700, smooth(t / d))
    dog(pen, dx, 800, 0.62, t, facing=1 if "away" in o else -1, tail=-1 if "tuck" in o else 0, ears=ears_of(o), glow=0.7)
    fireflies(pen, t, 12, (200, 380, 1700, 800))
    pen.rect(0, 860, W, 34, fill="#4a3a2b", stroke="#6c5a46", w=3)
    for x in range(40, W, 110): pen.rect(x, 894, 26, 200, fill="#4a3a2b", stroke="#6c5a46", w=3)
    pen.rect(0, 0, 230, H, fill="#2a2418"); pen.rect(W - 230, 0, 230, H, fill="#2a2418")
    pen.rect(210, 0, 22, H, fill="#c9c2b0"); pen.rect(W - 232, 0, 22, H, fill="#c9c2b0")
    pen.rect(0, 0, W, 60, fill="#2a2418"); pen.rect(0, 58, W, 16, fill="#c9c2b0")
    pen.pop()

def KITCHEN(pen, t, d, gt, s, v, o):
    fx, fy = [(1000, 560), (560, 470), (1480, 420), (1100, 300), (1500, 960), (1770, 500), (980, 180), (300, 760), (760, 800), (1250, 600)][v % 10]
    z = [1.0, 1.6, 1.7, 2.2, 2.4, 1.8, 2.0, 1.9, 1.6, 1.3][v % 10]
    camera(pen, t, d, z, z * 1.05, fx, fy, s)
    kitchen(pen, t, CLOCK + gt)
    if "you" in o: figure(pen, "you", 1460, 960, 1.15, {"face": {"mouth": "flat", "look": (1, 0)}}, t, seed=3)
    if "hum" in o:
        for k in range(3): pen.arc(300 + k * 30, 720, 20 + k * 22, 20 + k * 22, -40, 80, WHITE, 3, 0.5 + 0.4 * math.sin(t * 6 + k))
    pen.pop()

def BOWL(pen, t, d, gt, s, v, o):
    vcam(pen, t, d, v, W / 2, 620, 0.06, s)
    pen.rect(0, 0, W, H, fill="#1d1f27")
    for x in range(-200, W, 160): pen.ln(x, 620, x - 300, H, "#262934", 4)
    pen.rect(0, 0, W, 620, fill="#14161c"); pen.rect(0, 600, W, 24, fill="#2a2d38")
    eaten = smooth(t / d) if "eat" in o else (1.0 if "empty" in o else 0.0)
    name = "DUKE" if "duke" in o else "BRUNO"
    pen.oval(960, 820, 420, 110, fill="#7a2c26" if name == "BRUNO" else "#2c4a7a", stroke=GREY, w=5)
    if eaten < 1: pen.oval(960, 790, 300 * (1 - eaten * 0.8), 60 * (1 - eaten * 0.8), fill="#8a5a2a")
    for k in range(int(14 * (1 - eaten))): pen.circle(860 + (k * 37) % 220, 770 + (k * 23) % 40, 10, fill="#6a4220")
    pen.text(name, 960, 920, 60, WHITE, "JetBrainsMono-Regular.ttf")
    if "eat" in o:
        dog(pen, 1500, 900, 1.3, t, facing=-1, tail=1.5, ears=1)
    pen.pop()

def CLOCKS(pen, t, d, gt, s, v, o):
    vcam(pen, t, d, v, W / 2, 500, 0.05, s)
    pen.rect(0, 0, W, H, fill="#14161c")
    for y in range(500, 1100, 60):
        for x in range((y // 60 % 2) * 40, W, 80): pen.rect(x, y, 76, 56, stroke="#232633", w=2)
    pen.rect(560, 760, 800, 320, fill="#2a2d38", stroke="#3a3e4c", w=3)  # stove
    for k in range(4): pen.circle(700 + k * 170, 800, 34, stroke=GREY, w=4)
    wall_clock(pen, W / 2, 420, 220, CLOCK + gt + (t * 1800 if "fast" in o else 0))
    pen.pop()

def HALL(pen, t, d, gt, s, v, o):
    """Hallway in five distinct compositions; the darker shape at varying distance."""
    comp = v % 5
    camera(pen, t, d, 1.0, 1.1, W / 2, 500, s)
    near = {"far": 0.3, "mid": 0.6, "near": 1.0}.get(next((k for k in ("far", "mid", "near") if k in o), "far"), 0.3)
    shape = "empty" not in o
    vx, vy = W / 2, 470
    if comp in (0, 4):  # straight down the hall (4 = seen from a side doorway)
        pen.rect(0, 0, W, H, fill="#16130e")
        pen.poly([(0, 0), (vx - 140, vy - 170), (vx - 140, vy + 170), (0, H)], fill="#221d15")
        pen.poly([(W, 0), (vx + 140, vy - 170), (vx + 140, vy + 170), (W, H)], fill="#1d1912")
        pen.poly([(0, H), (vx - 140, vy + 170), (vx + 140, vy + 170), (W, H)], fill="#2a2219")
        pen.poly([(560, H), (vx - 60, vy + 170), (vx + 60, vy + 170), (1360, H)], fill="#6b2a24")
        pen.rect(vx - 140, vy - 170, 280, 340, fill="#050403")
        if shape: sc = 0.5 + near; pen.oval(vx, vy - 40 * sc, 34 * sc, 44 * sc, fill="#000000"); pen.rect(vx - 40 * sc, vy, 80 * sc, 150 * sc, fill="#000000")
        for (x, y, w_, h_) in ((170, 260, 170, 140), (430, 330, 110, 90), (1580, 270, 170, 140), (1380, 340, 100, 80)):
            pen.rect(x, y, w_, h_, fill="#d9cfb8", stroke="#8a6a3a", w=6)
        if comp == 4:
            pen.rect(0, 0, 620, H, fill="#0d0b08"); pen.rect(600, 0, 40, H, fill="#c9c2b0")
            pen.rect(1300, 0, W - 1300, H, fill="#0d0b08"); pen.rect(1280, 0, 40, H, fill="#c9c2b0")
    elif comp == 1:  # floor level on the runner
        pen.rect(0, 0, W, H, fill="#100d09")
        pen.poly([(0, H), (vx - 30, 380), (vx + 30, 380), (W, H)], fill="#6b2a24")
        for k in range(8): pen.ln(0, H - k * 40, W, H - k * 40, "#8a3a30", 3, 0.5)
        pen.rect(vx - 120, 140, 240, 240, fill="#050403")
        if shape: pen.rect(vx - 30, 230 - 60 * near, 60, 150 + 60 * near, fill="#000000")
        if "foot" in o:
            for j in range(int(t * 3) % 6): pen.oval(vx + (60 if j % 2 else -60), 520 + j * 90, 40 + j * 8, 16 + j * 3, fill="#000000", stroke=GREY, w=2)
    elif comp == 2:  # family photos close: glass catches the shape behind you
        pen.rect(0, 0, W, H, fill="#221d15")
        for i, (x, y) in enumerate(((260, 200), (980, 160), (620, 620), (1340, 600))):
            pen.rect(x, y, 520, 380, fill="#d9cfb8", stroke="#8a6a3a", w=12)
            for j in range(3): pen.circle(x + 120 + j * 140, y + 200, 50, fill="#7a7468")
            pen.poly([(x + 40, y + 20), (x + 160, y + 20), (x + 60, y + 360), (x + 20, y + 360)], fill="#ffffff", a=0.12)
        if shape: pen.oval(1180, 330, 60, 80, fill="#000000", a=0.35 + 0.25 * near)
    else:  # the flickering ceiling light
        pen.rect(0, 0, W, H, fill="#120f0b")
        on = 0.5 + 0.5 * math.sin(t * 17) * math.sin(t * 5.3)
        pen.ln(vx, 0, vx, 300, GREY, 6); pen.oval(vx, 330, 160, 60, fill="#ffe7a0" if on > 0.3 else "#3a3326")
        pen.glow(vx, 360, 700, AMBER, 0.35 * on)
        pen.rect(0, 880, W, 200, fill="#2a2219")
        if shape: pen.rect(vx + 300, 880 - 260 * near, 120 * near, 260 * near, fill="#000000", a=0.8)
    pen.glow(vx, 120, 300, AMBER, 0.08)
    if "voice" in o:
        for k in range(4):
            r = ((t * 1.2 + k / 4) % 1) * 420; pen.circle(vx, vy, r, stroke=ACID, w=4, a=1 - r / 420)
    pen.pop()

def YOU_CU(pen, t, d, gt, s, v, o):
    """Close-ups of you: angle/background/side vary with v; expression from opts."""
    bgk = v % 4
    camera(pen, t, d, 1.0, 1.06, W / 2, 560, s)
    if bgk == 0:
        pen.rect(0, 0, W, H, fill="#0b0d14"); pen.rect(560, 60, 800, 1040, fill="#ffcf73"); pen.glow(W / 2, 500, 700, AMBER, 0.25)
    elif bgk == 1: kitchen(pen, t, CLOCK + gt); pen.rect(0, 0, W, H, fill="#000000", a=0.45)
    elif bgk == 2: backyard(pen, t, 1.0); pen.rect(0, 0, W, H, fill="#000000", a=0.4)
    else: pen.rect(0, 0, W, H, fill="#16130e"); pen.poly([(700, 0), (1220, 0), (1080, 700), (840, 700)], fill="#0c0b09")
    x = [W / 2, 640, 1280, 760, 1160][v % 5]; r = [220, 260, 200, 300, 240][v % 5]
    eyes = "wide" if any(k in o for k in ("scared", "wide")) else ("closed" if "shut" in o else "dot")
    mouth = "open" if "call" in o else ("o" if "whistle" in o else ("wobble" if "scared" in o else ("smile" if "smile" in o else "flat")))
    look = (1, 0) if "side" in o else ((-1, 0) if "back" in o else (0, 0.3))
    head_close(pen, "you", x, 470, r, {"eyes": eyes, "mouth": mouth, "look": look, "blink": "wide" not in o,
                                      "tremble": 0.8 if "scared" in o else 0, "tears": 0.6 if "tears" in o else 0}, t, seed=3, tilt=[-4, 3, 0, -6, 5][v % 5])
    if "call" in o:
        k = ease_out(t / 0.3); bx = x + r * 1.3
        pen.rect(bx, 230, 460 * k, 140, fill=WHITE, r=40)
        if k > 0.8: pen.text("BRUNO!", bx + 230, 335, 90, "#111111")
    if "cold" in o:
        for k in range(5):
            ph = (t * 0.7 + k / 5) % 1; pen.oval(x + r * 0.2 + ph * 120, 470 + r * 0.6 - ph * 60, 40 + ph * 60, 20 + ph * 20, fill="#dfefff", a=0.35 * (1 - ph))
    pen.pop()

def YOU_FULL(pen, t, d, gt, s, v, o):
    """You standing in the lit doorway, from the yard, various distances."""
    z = [1.4, 1.9, 2.4, 1.6, 2.1][v % 5]
    camera(pen, t, d, z, z * 1.04, 555, 640, s)
    backyard(pen, t, 1.0)
    figure(pen, "you", 555, 820, 0.62, {"face": {"mouth": "flat", "eyes": "wide" if "scared" in o else "dot"},
                                        "armR": (150, 10) if "frame" in o else (8, 4)}, t, seed=3)
    if "shape" in o: pen.oval(600, 600, 40, 60, fill="#000000", a=0.5 + 0.1 * math.sin(t * 2))
    pen.pop()

def HANDS(pen, t, d, gt, s, v, o):
    """Hands: gripping the doorframe / whistle fingers / knocking / reaching for the lock."""
    vcam(pen, t, d, v, W / 2, 560, 0.05, s)
    pen.rect(0, 0, W, H, fill="#1a1c24")
    pen.rect(820, 0, 120, H, fill="#c9c2b0", stroke="#8a8478", w=4)  # doorframe
    pen.rect(940, 0, W - 940, H, fill="#0b1020")
    for k in range(10): pen.circle(1000 + (k * 113) % 860, 80 + (k * 97) % 900, 2, fill=WHITE, a=0.5)
    if "knock" in o:
        ph = t * 3 % 1.6; hit = ph < 0.12 or 0.45 < ph < 0.57 or 1.1 < ph < 1.22
        hx = 760 - (0 if hit else 50)
        pen.circle(hx, 520, 70, fill=pen.white, stroke=pen.line, w=4)
        for k in range(4): pen.oval(hx + 50, 470 + k * 32, 30, 14, fill=pen.white, stroke=pen.line, w=3)
        if hit: pen.text("KNOCK", 600, 380, 70, ACID)
        pen.ln(hx - 50, 540, -100, 760, pen.line, 118); pen.ln(hx - 50, 540, -100, 760, "#cfe0bf", 110)
    elif "lock" in o:
        pen.rect(860, 500, 40, 90, fill=AMBER, r=10)
        reach = math.sin(math.pi * clamp(t / d)) * 200; hx = 520 + reach
        pen.ln(hx - 50, 560, -100, 760, pen.line, 118); pen.ln(hx - 50, 560, -100, 760, "#cfe0bf", 110)
        pen.circle(hx, 540, 64, fill=pen.white, stroke=pen.line, w=4)
        if t > d * 0.6: red_cross(pen, t - d * 0.6, 870, 540, 120)
    else:  # grip on the frame, knuckles whitening
        for k in range(4): pen.oval(800, 380 + k * 70, 70, 30, fill=pen.white, stroke=pen.line, w=4)
        pen.oval(700, 470, 110, 140, fill=pen.white, stroke=pen.line, w=4)
        pen.ln(640, 560, -100, 900, pen.line, 140); pen.ln(640, 560, -100, 900, "#cfe0bf", 130)
    pen.pop()

def red_cross(pen, t, x, y, r):
    if t <= 0: return
    k = ease_out(t / 0.2)
    pen.ln(x - r * k, y - r * k, x + r * k, y + r * k, RED, 24, 0.9); pen.ln(x + r * k, y - r * k, x - r * k, y + r * k, RED, 24, 0.9)

def WHISTLE(pen, t, d, gt, s, v, o):
    camera(pen, t, d, 1.0, 1.06, W / 2, 560, s)
    backyard(pen, t, 1.0); pen.rect(0, 0, W, H, fill="#000000", a=0.45)
    x = [760, 1160][v % 2]
    head_close(pen, "you", x, 460, 230, {"eyes": "dot", "mouth": "o", "look": (0, 0)}, t, seed=3)
    pen.oval(x, 560, 44, 26, fill=pen.white, stroke=pen.line, w=4)  # two fingers
    for k in range(4):
        r = ((t * 1.5 + k / 4) % 1) * 600; pen.arc(x, 560, r, r * 0.6, -30, 60, ACID, 5, 1 - r / 600)
    pen.text("FWEEEEET", x + 520, 380, 80, ACID, a=0.6 + 0.4 * math.sin(t * 20))
    pen.pop()

def ARM_HAIR(pen, t, d, gt, s, v, o):
    """Your forearm: hoodie sleeve, skin, hand - the hairs stand up as the cold arrives."""
    vcam(pen, t, d, v % 3, W / 2, 560, 0.04, s)
    pen.rect(0, 0, W, H, fill="#0d1018")
    pen.path(lambda p: (p.moveTo(420, 380), p.cubicTo(900, 350, 1300, 400, 1560, 470), p.lineTo(1540, 640), p.cubicTo(1300, 620, 900, 640, 420, 700), p.close()),
             fill=pen.white, stroke=pen.line, w=5)
    pen.oval(1640, 560, 150, 110, fill=pen.white, stroke=pen.line, w=5)  # hand
    for k in range(4): pen.oval(1780, 480 + k * 50, 70, 24, fill=pen.white, stroke=pen.line, w=4)
    pen.rect(-40, 330, 520, 420, fill="#5fa39a", stroke="#3f7a72", w=5, r=40)  # teal hoodie sleeve
    k = smooth(t / max(0.6, d * 0.6))
    for j in range(30):
        x = 520 + j * 34; y = 420 + (j % 3) * 8 - j * 1.2
        a = math.radians(160 - 90 * k); pen.ln(x, y, x + math.cos(a) * 26, y - math.sin(a) * 26, INK, 3)
    for j in range(5):
        ph = (t * 0.5 + j / 5) % 1; pen.oval(W * ph, 220 + j * 30, 120, 30, fill="#dfefff", a=0.18 * (1 - ph))
    pen.pop()

def DOG_CU(pen, t, d, gt, s, v, o):
    """True close-ups of one part of the dog (head/face/ears/tail/paws/eyes), framed per variant."""
    kind = o.split(",")[0] if o else "head"
    camera(pen, t, d, 1.0, 1.06, W / 2, 540, s)
    bg = v % 3
    if bg == 0: sky(pen, t); moon(pen, 1600, 200, t, 70); treeline(pen, t, 820, "#0a0f14", 60 + v, 200)
    elif bg == 1: pen.rect(0, 0, W, H, fill="#1b1d26"); pen.glow(300, 200, 700, AMBER, 0.35); pen.circle(300, 200, 40, fill="#ffe7a0")
    else: pen.rect(0, 0, W, H, fill="#06090c"); fireflies(pen, t, 14, (0, 0, W, H))
    ears = ears_of(o); tail = -1 if "tuck" in o else (1.4 if "wag" in o else 0)
    f = 1 if (v // 3) % 2 == 0 else -1
    ht = {"face": 1.0, "head": 0.0, "ears": 1.0}.get(kind, 0.0)
    if kind == "head" and v % 4 == 3: ht = 0.5
    L = 220
    anchor = {"head": (f * L * (0.52 - 0.1 * ht), -203), "face": (f * L * 0.42, -203), "ears": (f * L * 0.42, -265),
              "tail": (-f * L * 0.62, -160), "paws": (0, -30)}.get(kind, (0, -140))
    k = {"head": [2.8, 3.4, 4.0], "face": [3.0, 3.6, 4.2], "ears": [4.2, 5.0, 4.6], "tail": [2.6, 3.2, 3.0], "paws": [2.6, 3.2, 2.9]}.get(kind, [3, 3, 3])[v % 3]
    X = [960, 760, 1160][(v // 2) % 3]; Y = {"paws": 820, "tail": 560}.get(kind, 560)
    if kind == "eyes":
        pen.rect(0, 0, W, H, fill="#05070c")
        lx = 0.8 if "shoulder" in o else 0
        tint = ["#5a3b1c", "#6a4a22", "#3b2a14"][v % 3]; sq = [1.0, 0.8, 0.9][v % 3]
        for sx in (-1, 1):
            x = W / 2 + sx * 260; pen.oval(x, 520, 190, 150 * sq, fill="#f1f1ee", stroke=GREY, w=6)
            pen.circle(x + lx * 90, 520 - lx * 50, 90 * sq, fill=tint); pen.circle(x + lx * 90, 520 - lx * 50, (50 + 12 * (v % 3)) * sq, fill="#000000")
            pen.circle(x + lx * 90 - 25, 490 - lx * 50, 18, fill="#ffffff")
            if bg == 1: pen.circle(x + lx * 90 + 30, 500 - lx * 50, 12, fill=AMBER, a=0.8)  # porch light reflected
        if "shoulder" in o: pen.text("YOUR SHOULDER", W / 2, 900, 60, ACID, "JetBrainsMono-Regular.ttf")
        pen.pop(); return
    pen.c.save(); pen.c.translate(X, Y); pen.c.scale(k, k); pen.c.translate(-anchor[0], -anchor[1])
    dog(pen, 0, 0, 1.0, t, facing=f, head_turn=ht, tail=tail, ears=ears, glow=0.4 if bg != 1 else 0,
        mouth="growl" if "growl" in o else "closed", step=-0.8 if "back" in o else 0)
    pen.c.restore()
    pen.pop()

def DOG_FULL(pen, t, d, gt, s, v, o):
    """Whole dog in four distinct compositions x scales."""
    comp = v % 4
    camera(pen, t, d, 1.0, 1.05, W / 2, 600, s)
    tail = -1 if "tuck" in o else (1.4 if "wag" in o else 0); ears = ears_of(o)
    step = -0.8 if "back" in o else (0.8 if "away" in o else 0)
    mv = (-380 if "back" in o else 600 if "away" in o else 0) * smooth(t / d)
    face = 1 if "away" in o else (-1 if (v // 4) % 2 else 1)
    kw = dict(tail=tail, ears=ears, step=step, crouch=0.5 if "back" in o else 0, mouth="growl" if "growl" in o else "closed")
    if comp == 0:  # medium in the yard
        sky(pen, t); moon(pen, 1580, 200, t, 60); clouds(pen, t); treeline(pen, t, 700, "#0a0f14", 40 + v, 170); fence(pen, 770, t); grass(pen, 760, t)
        dog(pen, 900 + mv, 960, 1.6, t, facing=face, glow=0.4, **kw)
    elif comp == 1:  # low angle, horizon low, big starry sky
        sky(pen, t); moon(pen, 400, 260, t, 90); pen.rect(0, 1000, W, 80, fill="#0e1710")
        dog(pen, 1000 + mv, 1010, 2.2, t, facing=face, glow=0.5, **kw)
    elif comp == 2:  # by the fence, side-on, small, lots of yard
        sky(pen, t); moon(pen, 960, 160, t, 45); treeline(pen, t, 620, "#0a0f14", 70 + v, 150); fence(pen, 700, t); grass(pen, 690, t)
        big_tree(pen, 1650, 880, t, 0.9); swing(pen, 1810, 480, t, 0.9)
        dog(pen, 700 + mv, 860, 0.9, t, facing=face, glow=0.4, **kw)
    else:  # porch-light rim: warm light from one side, dog large, dark lawn
        pen.rect(0, 0, W, H, fill="#070a0c"); pen.glow(0, 300, 1200, AMBER, 0.28); grass(pen, 820, t)
        dog(pen, 1100 + mv, 1000, 1.9, t, facing=face, **kw)
    if "growl" in o and (t % 1) < 0.6: pen.text("grrrr", 1500, 520, 70, GREY, a=0.8)
    fireflies(pen, t, 8, (0, 300, W, 900))
    pen.pop()

def WINDOW(pen, t, d, gt, s, v, o):
    """The black kitchen window as a mirror: you in the doorway, and the room behind you."""
    vcam(pen, t, d, v, W / 2, 540, 0.05, s)
    pen.rect(0, 0, W, H, fill="#14161c")
    pen.rect(360, 140, 1200, 800, fill="#05070c", stroke="#c9c2b0", w=10); pen.ln(960, 140, 960, 940, "#c9c2b0", 8)
    pen.c.save(); pen.c.clipRect(skia.Rect.MakeXYWH(365, 145, 1190, 790))
    pen.rect(365, 145, 1190, 790, fill="#ffcf73", a=0.08)
    figure(pen, "you", 820, 940, 1.0, {"face": {"mouth": "flat", "eyes": "dot"}}, t, seed=3)
    if "shape" in o:
        k = 0.35 + 0.15 * math.sin(t * 1.5)
        pen.oval(1180, 330, 70, 95, fill="#000000", a=k + 0.3); pen.rect(1110, 410, 140, 420, fill="#000000", a=k + 0.25)
    pen.c.restore()
    pen.rect(360, 940, 1200, 40, fill="#cfccc3")
    pen.pop()

def CURTAIN(pen, t, d, gt, s, v, o):
    vcam(pen, t, d, v, W / 2, 540, 0.05, s)
    pen.rect(0, 0, W, H, fill="#1a1c24")
    pen.rect(520, 60, 880, 980, fill="#3b3f52", stroke="#c9c2b0", w=6)
    pen.rect(620, 140, 680, 460, fill="#0b1020")
    for k in range(9): pen.circle(650 + (k * 87) % 640, 170 + (k * 53) % 400, 2, fill=WHITE, a=0.5)
    sway = (math.sin(t * 2.2) * 50 + math.sin(t * 5) * 12) if "move" in o else 4 * math.sin(t)
    pen.path(lambda p: (p.moveTo(600, 120), p.lineTo(1320, 120), p.cubicTo(1320 + sway, 330, 1300 - sway, 500, 1310 + sway * 1.5, 640),
                        p.lineTo(610 + sway, 640), p.cubicTo(600 - sway, 480, 620 + sway, 300, 600, 120), p.close()), fill="#c0603a", a=0.92)
    for k in range(6): pen.ln(660 + k * 110, 130, 660 + k * 110 + sway * 0.7, 630, "#8a3f22", 4)
    pen.pop()

def DIAGRAM(pen, t, d, gt, s, v, o):
    """Blueprint of house + yard: door, porch line, dog, hallway."""
    vcam(pen, t, d, v % 3, W / 2, H / 2, 0.04, s)
    pen.rect(0, 0, W, H, fill="#0d1b2a")
    for x in range(0, W, 60): pen.ln(x, 0, x, H, "#16304a", 2)
    for y in range(0, H, 60): pen.ln(0, y, W, y, "#16304a", 2)
    B = "#9fd0ff"; k = ease_out(t / 0.6)
    pen.rect(160, 200, 720 * k, 680, stroke=B, w=5)  # house
    pen.text("KITCHEN", 420, 560, 40, B, "JetBrainsMono-Regular.ttf"); pen.text("HALL", 300, 300, 32, B, "JetBrainsMono-Regular.ttf")
    pen.rect(880, 470, 14, 160, fill=AMBER)  # door
    pen.rect(894, 420, 140, 260, stroke=B, w=3); pen.text("PORCH", 964, 410, 28, B, "JetBrainsMono-Regular.ttf")
    pen.rect(1040, 160, 760, 760, stroke="#4f8a55", w=4); pen.text("YARD", 1420, 210, 40, "#4f8a55", "JetBrainsMono-Regular.ttf")
    dx = 1420 if "edge" not in o else 1760
    pen.circle(dx, 550, 30, fill=WHITE); pen.text("BRUNO", dx, 620, 30, WHITE, "JetBrainsMono-Regular.ttf")
    if "guard" in o:
        pen.ln(dx, 550, 894, 550, ACID, 6); pen.text("CAN'T PASS", 1150, 520, 34, ACID, "JetBrainsMono-Regular.ttf")
    if "line" in o:
        pen.ln(1034, 160, 1034, 920, RED, 8); pen.text("THE LINE", 1034, 140, 36, RED, "JetBrainsMono-Regular.ttf")
    if "shape" in o:
        sx = lerp(260, 840, smooth(t / d)) if "move" in o else 300
        pen.circle(sx, 300, 26, fill=RED); pen.text("?", sx, 310, 30, BG)
    if "you" in o: pen.circle(860, 550, 24, fill=AMBER); pen.text("YOU", 820, 520, 26, AMBER, "JetBrainsMono-Regular.ttf")
    if "closed" in o: red_cross(pen, t - 0.3, 887, 550, 70)
    pen.pop()

def EAR_CHART(pen, t, d, gt, s, v, o):
    vcam(pen, t, d, v % 3, W / 2, H / 2, 0.04, s)
    pen.rect(0, 0, W, H, fill="#0d1b2a")
    states = [("UP", 1, "IT'S MOVING"), ("FLAT", 0, "IT'S CLOSE"), ("ONE UP", 0.5, "DECIDING")]
    hi = {"up": 0, "flat": 1, "one": 2}.get(next((k for k in ("up", "flat", "one") if k in o), ""), -1)
    for i, (lab, e, mean) in enumerate(states):
        x = 360 + i * 600; a = 1.0 if hi in (-1, i) else 0.3
        pen.push(s=1.6, ox=x, oy=900); dog(pen, x, 900, 1.0, t, facing=1, head_turn=1.0, ears=e); pen.pop()
        pen.text(lab, x, 200, 60, ACID if hi == i else WHITE, a=a)
        pen.text(mean, x, 1000, 40, ACID if hi == i else "#9fd0ff", "JetBrainsMono-Regular.ttf", a=a)
    pen.pop()

def WAVE(pen, t, d, gt, s, v, o):
    vcam(pen, t, d, v % 3, W / 2, H / 2, 0.04, s)
    pen.rect(0, 0, W, H, fill="#06080e")
    for row, (lab, col, sp) in enumerate((("YOU", AMBER, 1.0), ("IT", ACID, 0.82))):
        if row == 1 and "both" not in o and "it" not in o: continue
        y = 380 + row * 340
        pts = [(x, y + math.sin(x * 0.03 * sp + t * 6) * 110 * math.sin(x * 0.004 + 0.3) * (0.8 + 0.2 * math.sin(t * 3))) for x in range(80, W - 80, 12)]
        pen.poly(pts, stroke=col, w=6, closed=False)
        pen.text(lab, 140, y - 140, 50, col, "JetBrainsMono-Regular.ttf", align="left")
    pen.text("B-R-U-N-O", W / 2, 1000, 50, WHITE, "JetBrainsMono-Regular.ttf", a=0.7)
    pen.pop()

def TAGS(pen, t, d, gt, s, v, o):
    """Rule cards as engraved dog tags jingling on Bruno's collar."""
    camera(pen, t, d, 1.0, 1.05, W / 2, 520, s)
    pen.rect(0, 0, W, H, fill="#0b0d12"); pen.glow(W / 2, 300, 900, AMBER, 0.08)
    pen.path(lambda p: (p.moveTo(-50, 120), p.quadTo(W / 2, 330, W + 50, 120)), stroke=RED, w=70)  # collar
    for k in range(14): pen.circle(80 + k * 140, 150 + 0.00028 * (80 + k * 140 - W / 2) ** 2 * -1 + 120, 6, fill="#5a1a14")
    n = int(o) if o.isdigit() else 0
    hi = int(o[2:]) if o.startswith("hi") else 0
    if hi:  # zoom onto one tag of the seven, glowing
        x = 300 + (hi - 1) * 220
        pen.pop(); camera(pen, t, d, 1.7, 1.9, x, 420, s)
        pen.rect(-W, -H, 3 * W, 3 * H, fill="#0b0d12")
        for i in range(7):
            xx = 300 + i * 220
            pen.ln(xx, 230, xx, 300, GREY, 6)
            pen.circle(xx, 400, 90, fill="#c9ccd2" if i < 6 else "#222222", stroke="#7f8590", w=6, a=1.0 if i + 1 == hi else 0.35)
            pen.text(str(i + 1) if i < 6 else "?", xx, 435, 90, "#2a2d33" if i < 6 else RED, a=1.0 if i + 1 == hi else 0.35)
        pen.glow(x, 400, 200, ACID if hi < 7 else RED, 0.35 + 0.2 * math.sin(t * 8))
    elif n == 0:  # all seven tags; 7th blacked out
        for i in range(7):
            x = 300 + i * 220; sw = math.sin(t * 6 + i) * 8 * math.exp(-t)
            pen.push(rot=sw, ox=x, oy=260)
            pen.ln(x, 230, x, 300, GREY, 6)
            pen.circle(x, 400, 90, fill="#c9ccd2" if i < 6 else "#222222", stroke="#7f8590", w=6)
            pen.text(str(i + 1) if i < 6 else "?", x, 435, 90, "#2a2d33" if i < 6 else RED)
            pen.pop()
        pen.text("SEVEN RULES", W / 2, 760, 110, WHITE)
    else:
        sw = math.sin(t * 9) * 14 * math.exp(-t * 2.5); drop = ease_out(t / 0.3)
        pen.push(rot=sw, ox=W / 2, oy=230)
        pen.ln(W / 2, 230, W / 2, 330 * drop + 30, GREY, 8)
        pen.path(lambda p: (p.addRoundRect(skia.Rect.MakeXYWH(W / 2 - 420, 330 * drop, 840, 520), 260, 260)), fill="#c9ccd2", stroke="#7f8590", w=8)
        pen.circle(W / 2, 330 * drop + 50, 22, fill="#0b0d12")
        pen.text(f"RULE {n}", W / 2, 330 * drop + 190, 80, "#2a2d33", "JetBrainsMono-Regular.ttf")
        words = RULE_TEXT[n].split(); lines, cur = [], ""
        for w_ in words:
            if len(cur + " " + w_) > 18: lines.append(cur.strip()); cur = ""
            cur += " " + w_
        lines.append(cur.strip())
        for i, ln_ in enumerate(lines): pen.text(ln_, W / 2, 330 * drop + 300 + i * 90, 78, "#1b1d22")
        pen.pop()
        pen.glow(W / 2 + 250, 420, 60, WHITE, 0.5 * max(0, math.sin(t * 4)))  # glint
    pen.pop()
RULE_TEXT = {1: "DON'T CALL HIM AGAIN.", 2: "DON'T TURN AROUND.", 3: "LEAVE THE BACK DOOR OPEN.", 4: "READ HIS EARS.",
             5: "NEVER STEP OFF THE PORCH.", 6: "IF YOU HEAR YOUR OWN VOICE, WHISTLE.", 7: "WHEN HE WALKS AWAY, LET HIM GO."}

def KT(pen, t, d, gt, s, v, o):
    pen.rect(0, 0, W, H, fill=["#03050a", "#0b0608", "#05080a", "#0a0a03"][v % 4])
    if v % 2: grass(pen, 900, t, "#0b130c", 40)
    kinetic(pen, o.replace("_", " "), t, ACID if v % 3 else WHITE, size=200 if len(o) < 14 else 130)

def COUNT(pen, t, d, gt, s, v, o):
    DOG_FULL(pen, t, d, gt, s, v + 3, "tuck")
    pen.rect(0, 0, W, H, fill="#000000", a=0.35)
    n = int(lerp(1, 5.999, t / d)); sc = 1.3 - 0.3 * ease_out((t * 5 / d) % 1)
    pen.push(s=sc, ox=W / 2, oy=H / 2); pen.text(str(n), W / 2, H / 2 + 120, 330, WHITE); pen.pop()

def TULSA(pen, t, d, gt, s, v, o):
    """The Tulsa story: sepia-toned case scenes."""
    kind = o.split(",")[0] if o else "file"
    vcam(pen, t, d, v % 4, W / 2, 560, 0.05, s)
    if kind == "file":
        pen.rect(0, 0, W, H, fill="#14110c")
        x0 = lerp(-900, 520, ease_out(t / 0.4)); pen.rect(x0, 180, 880, 680, fill="#c7a46a", stroke="#7a5e2f", w=6, r=10)
        pen.text("CASE FILE 112", x0 + 440, 320, 70, "#3b2b12", "JetBrainsMono-Regular.ttf")
        if t > 0.4: pen.text("TULSA, OK", x0 + 440, 560, 110, RED)
    elif kind == "duke":
        backyard(pen, t, 1.0, house=v % 2 == 0); pen.push(s=1.5, ox=1100, oy=900)
        dog(pen, 1100, 900, 1.0, t, facing=-1, tail=1.3 if "wag" in o else 0, ears=1); pen.pop()
        pen.text("DUKE", 1100, 400, 90, AMBER)
    elif kind == "man":
        backyard(pen, t, 1.0); pen.push(s=2.2, ox=555, oy=820)
        figure(pen, "dad", 555, 820, 0.6, {"face": {"mouth": "talk" if "call" in o else "flat", "eyes": "wide" if "scared" in o else "dot"}}, t, seed=21); pen.pop()
    elif kind == "past":  # Duke walking past him into the house
        pen.rect(0, 0, W, H, fill="#16130e"); pen.rect(560, 60, 800, 1040, fill="#2a2418")
        figure(pen, "dad", 760, 1080, 1.4, {"face": {"mouth": "o", "eyes": "wide", "look": (1, 0)}}, t, seed=21)
        x = lerp(1700, 1050, smooth(t / d)); pen.push(s=1.2, ox=x, oy=1060); dog(pen, x, 1060, 1.0, t, facing=-1, tail=1.6, step=1.0); pen.pop()
    elif kind == "collar":
        BOWL(pen, t, d, gt, s, v, "duke")
        pen.oval(1350, 950, 180, 40, stroke=RED, w=26); pen.circle(1350, 990, 22, fill=AMBER)
        pen.pop(); pen.pop(); return
    elif kind == "night":
        pen.rect(0, 0, W, H, fill="#0a0c12"); pen.rect(300, 640, 1300, 200, fill="#2a2d38", r=30)
        head_close(pen, "dad", 760, 560, 160, {"eyes": "wide", "mouth": "flat", "blink": False}, t, seed=21, shoulders=False)
        pen.rect(820, 600, 760, 260, fill="#c7c9d2", r=40)  # blanket
        for k in range(3):
            ph = (t * 0.7 + k / 3) % 1; pen.text("good boy", 1500 + ph * 120, 400 - ph * 160, 50, ACID, "Montserrat-VF.ttf", a=1 - ph)
    pen.rect(0, 0, W, H, fill="#c08a3a", a=0.12)
    pen.pop()

def NEIGHBORS(pen, t, d, gt, s, v, o):
    """Street of back yards: porch lights going out, one by one, toward you."""
    camera(pen, t, d, 1.0, 1.05, W / 2, 560, s)
    sky(pen, t); moon(pen, 1600, 160, t, 40); treeline(pen, t, 560, "#0a0f14", 77, 120)
    out = int(t * 2.2) + (v % 2)
    for i in range(5):
        x = 200 + i * 380; y = 760
        pen.rect(x - 140, y - 220, 280, 220, fill="#14161c", stroke=GREY, w=3); pen.poly([(x - 160, y - 220), (x, y - 330), (x + 160, y - 220)], fill="#101218", stroke=GREY, w=3)
        on = i < 5 - out
        pen.rect(x - 30, y - 150, 60, 150, fill="#1d2233" if not on else "#ffcf73")
        if on: pen.glow(x + 60, y - 140, 90, "#ffe7a0", 0.5); pen.circle(x + 60, y - 140, 10, fill="#ffe7a0")
    grass(pen, 760, t)
    pen.pop()

def WOODS(pen, t, d, gt, s, v, o):
    """Edge of the yard and the trees: night, pre-dawn, dawn (opts)."""
    camera(pen, t, d, 1.0, 1.05, W / 2 + [0, -200, 200][v % 3], 600, s)
    dawn = "dawn" in o
    sh = skia.GradientShader.MakeLinear([(0, 0), (0, 760)], [C("#2b2a4a" if dawn else "#05070f"), C("#e8a07a" if dawn else "#121a33")])
    p = skia.Paint(); p.setShader(sh); pen.c.drawRect(skia.Rect.MakeWH(W, H), p)
    if not dawn: moon(pen, 1500, 180, t, 50)
    for k in range(9):
        x = 100 + k * 220 + (k * 37) % 60
        pen.rect(x - 22, 300, 44, 600, fill="#0b0f0c" if not dawn else "#2a2a2a")
        pen.circle(x, 300, 120, fill="#0d1612" if not dawn else "#3a4a3a")
    grass(pen, 860, t)
    if "lead" in o:
        x = lerp(1400, 900, smooth(t / d)); dog(pen, x, 960, 1.1, t, facing=-1, step=0.8, tail=0, ears=1)
        for j in range(5): pen.oval(x + 260 + j * 80, 860 - j * 12, 90, 40, fill="#cfe8ff", a=0.14)
    if "return" in o:
        x = lerp(700, 1150, smooth(t / d)); bob = abs(math.sin(t * 6)) * 10
        dog(pen, x, 960 - bob, 1.2, t, facing=1, step=0.6, tail=1.4, ears=1)
        for j in range(6): pen.circle(x - 100 + j * 50, 900, 10, fill="#4a3a2b")  # mud
    pen.pop()

def BEDROOM_DOOR(pen, t, d, gt, s, v, o):
    """Your bedroom door from the hallway; the dog asleep on the floor in front of it, facing out."""
    z = 1.0 + 0.1 * (v % 3) + 0.45 * (v // 3)
    camera(pen, t, d, z, z * 1.06, W / 2 + [0, -180, 180][v % 3], 600 + 260 * (v // 3), s)
    night = "day" not in o
    pen.rect(0, 0, W, H, fill="#16130e" if night else "#4a4038")
    pen.rect(700, 160, 520, 820, fill="#3b2f22", stroke="#c9c2b0", w=8); pen.circle(1160, 600, 14, fill=AMBER)
    pen.rect(0, 980, W, 100, fill="#2a2219")
    if night: pen.rect(700, 970, 520, 12, fill="#ffcf73", a=0.6)  # light under the door
    if "puppy" in o:
        pen.rect(780, 860, 360, 140, fill="#8a6a44", stroke="#5a4630", w=4)
        pen.push(s=0.55, ox=960, oy=900); dog(pen, 960, 900, 1.0, t, facing=1, head_turn=0.8, eyes="closed" if "sleep" in o else "dot", tail=0.3, ears=0.5); pen.pop()
    else:
        pen.push(s=1.0, ox=960, oy=1040); dog(pen, 960, 1040, 1.0, t, facing=1, head_turn=1.0, eyes="dot", tail=0, ears=1, glow=0.3 if night else 0); pen.pop()
    pen.pop()

def MEMORY(pen, t, d, gt, s, v, o):
    """VHS home video: bringing the puppy home."""
    vcam(pen, t, d, v % 3, W / 2, 600, 0.04, s)
    pen.rect(0, 0, W, H, fill="#3a3024")
    floor(pen, 900)
    kind = o.split(",")[0] if o else "box"
    if kind == "box":
        pen.oval(960, 930, 700, 60, fill="#6b2a24")
        pen.push(s=1.6, ox=960, oy=900)
        pen.rect(760, 700, 400, 200, fill="#b8915a", stroke="#7a5e2f", w=6)
        dog(pen, 960, 760, 0.8, t, facing=1, head_turn=1.0, ears=0.5, tail=0.6); pen.rect(760, 760, 400, 140, fill="#b8915a", stroke="#7a5e2f", w=6)
        pen.pop()
        pen.text("ARF?", 1250, 600, 60, WHITE, a=0.7)
    elif kind == "cry":
        pen.oval(960, 930, 600, 50, fill="#6b2a24"); pen.rect(200, 300, 300, 260, fill="#0b1020", stroke="#c9c2b0", w=8)
        dog(pen, 960, 920, 1.5, t, facing=1, head_turn=1.0, ears=0.0, tail=-1)
        for k in range(3):
            ph = (t + k / 3) % 1; pen.text("awoo", 1180 + ph * 80, 600 - ph * 140, 54, WHITE, "Montserrat-VF.ttf", a=1 - ph)
    elif kind == "room":
        sofa(pen, 160, 900, 760); pen.oval(1200, 920, 520, 60, fill="#6b2a24")
        pen.ln(1700, 900, 1700, 520, GREY, 6); pen.poly([(1640, 520), (1760, 520), (1730, 450), (1670, 450)], fill="#c98f2c"); pen.glow(1700, 500, 260, AMBER, 0.3)
        dog(pen, 1200, 900, 1.1, t, facing=-1, head_turn=0.5, ears=0, tail=-1)
    elif kind == "move":
        x = lerp(500, 1300, smooth(t / d))
        figure(pen, "you", x, 900, 1.0, {"face": {"mouth": "smile"}, "armL": (70, 30), "armR": (70, 30)}, t, seed=3)
        pen.rect(x - 120, 640, 240, 80, fill="#8a6a44", stroke="#5a4630", w=4)
        pen.rect(1400, 380, 300, 520, fill="#3b2f22", stroke="#c9c2b0", w=6)
    pen.rect(0, 0, W, H, fill="#c08a3a", a=0.16)
    for y in range(0, H, 6): pen.ln(0, y, W, y, "#000000", 2, 0.16)
    pen.text("PLAY >", 70, 140, 48, WHITE, "JetBrainsMono-Regular.ttf", 0.85, "left")
    pen.text("JUN 03 2019", W - 70, H - 150, 40, WHITE, "JetBrainsMono-Regular.ttf", 0.85, "right")
    pen.pop()

def PORCH(pen, t, d, gt, s, v, o):
    """Porch details: boards edge, steps, rail, doormat, boots, light."""
    kind = v % 5
    camera(pen, t, d, 1.0, 1.06, W / 2, 600, s)
    if kind == 0:  # sneakers at the very edge of the boards
        T.PORCH_STEPS_POV(pen, t, d, gt, s)
    elif kind == 1:  # the board line close-up: wood vs grass
        pen.rect(0, 0, W, H, fill="#070a0f"); grass(pen, 560, t, "#122014", 120, 40)
        for k in range(6): pen.rect(-20, 120 + k * 72, W + 40, 66, fill="#4a3a2b", stroke="#6c5a46", w=4)
        pen.ln(0, 552, W, 552, RED if "line" in o else "#6c5a46", 10)
    elif kind == 2:  # porch light + moths
        pen.rect(0, 0, W, H, fill="#1b1d26")
        for y in range(0, H, 34): pen.ln(0, y, W, y, "#232634", 4)
        pen.rect(880, 360, 160, 220, fill="#ffe7a0", stroke="#c9c2b0", w=6); pen.glow(960, 470, 420, "#ffe7a0", 0.45)
        for k in range(9):
            a = t * (2.6 + k * 0.5) + k; pen.oval(960 + math.cos(a) * (150 + k * 22), 470 + math.sin(a * 1.3) * (90 + k * 14), 12, 7, fill="#e8e1cc")
    elif kind == 3:  # doormat + boots + plant
        pen.rect(0, 0, W, H, fill="#1b1d26"); pen.rect(0, 620, W, 460, fill="#4a3a2b")
        for k in range(10): pen.ln(0, 640 + k * 44, W, 640 + k * 44, "#6c5a46", 3)
        pen.rect(640, 700, 640, 200, fill="#7a2c26", r=10); pen.text("HOME", 960, 840, 90, "#c9a07a")
        for k in range(2): pen.rect(1420 + k * 110, 600, 90, 200, fill="#2a2a2a", r=20)
        pen.rect(300, 520, 160, 160, fill="#8a4a2a", r=10)
        for k in range(5): pen.ln(380, 522, 380 + (k - 2) * 50, 360 + abs(k - 2) * 30, "#2f5a33", 14)
    else:  # porch rail with the yard beyond
        T.YARD_FROM_PORCH(pen, t, d, gt, s)
    pen.pop()

def SKY(pen, t, d, gt, s, v, o):
    """Ambient cutaways: moon through branches, fireflies over grass, clouds over the roofline."""
    camera(pen, t, d, 1.0, 1.08, W / 2, 500, s)
    k = v % 3
    sky(pen, t)
    if k == 0:
        moon(pen, 960, 420, t, 140)
        for j in range(5): pen.ln(-50 + j * 100, H, 400 + j * 160, 120 + j * 40, "#0b100c", 30 - j * 4)
    elif k == 1:
        grass(pen, 600, t, "#122014", 160, 50); fireflies(pen, t, 26, (0, 300, W, 1000))
    else:
        clouds(pen, t, False, 300); pen.poly([(0, H), (0, 760), (700, 500), (1400, 760), (1400, H)], fill="#0a0b10")
        pen.rect(1100, 560, 60, 200, fill="#0a0b10")
    pen.pop()

def DAWN_KITCHEN(pen, t, d, gt, s, v, o):
    """Grey morning light in the kitchen."""
    KITCHEN(pen, t, d, gt, s, v + 3, o)
    pen.rect(0, 0, W, H, fill="#9fb4d0", a=0.15)

BUILDERS = {k: v for k, v in globals().items() if k.isupper() and callable(v)}

def draw(pen, t, dur, gt, shot):
    name = shot["setup"]
    if name in T.SHOTS:  # approved opening shots (used once each)
        pen.mood = "normal"; T.SHOTS[name](pen, t, dur, gt, shot); return None, True
    base, _, rest = name.partition("#")
    v_str, _, opts = rest.partition(":")
    fn = BUILDERS.get(base)
    if not fn: return None, False
    pen.mood = "normal"; fn(pen, t, dur, gt, shot, int(v_str or 0), opts); return None, True
