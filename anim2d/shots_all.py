"""All shots for Video 01. Reuses the hand-tuned opening shots (shots01) and builds the rest from
parametric scene builders. draw(pen, t, dur, gt, shot) is the single entry point."""
import math, random
from engine import *
import shots01 as S1
from shots01 import camera, dining_back, FAM, CLOCK0

RULES = {1: "KEEP EATING.", 2: "DON'T LOOK AT THE EMPTY CHAIR.", 3: "DON'T ASK TO BE EXCUSED.",
         4: "IF IT OFFERS YOU SECONDS, TAKE THEM. DON'T EAT THEM.", 5: "NEVER SAY THANK YOU.",
         6: "WHEN YOUR FAMILY BLINKS, STOP CHEWING.", 7: "BE THE LAST ONE AT THE TABLE."}

def mood_of(si):
    if si < 13 or 164 <= si <= 173: return "normal"
    if 132 <= si <= 141: return "memory"
    if 68 <= si <= 72 or 104 <= si <= 106: return "dark"
    return "frozen"

def set_mood(pen, si):
    m = mood_of(si); pen.mood = "normal" if m == "memory" else m
    return m

# ---------------- generic overlays ----------------
def stamp(pen, text, t, color=RED, x=W / 2, y=H / 2, rot=-12, size=150):
    k = ease_out(t / 0.15); sc = 1.6 - 0.6 * k
    pen.push(s=sc, rot=rot, ox=x, oy=y)
    f = font("Anton-Regular.ttf", size); wdt = f.measureText(text)
    pen.rect(x - wdt / 2 - 30, y - size * 0.95, wdt + 60, size * 1.2, stroke=color, w=12, a=0.9 * k, r=10)
    pen.text(text, x, y, size, color, a=0.9 * k)
    pen.pop()

def red_x(pen, t, x=W / 2, y=H / 2, r=260):
    k = ease_out(t / 0.2)
    pen.ln(x - r * k, y - r * k, x + r * k, y + r * k, RED, 34, 0.9); pen.ln(x + r * k, y - r * k, x - r * k, y + r * k, RED, 34, 0.9)

def vhs(pen, t, label="PLAY >", date="SUN 14 MAR 2014"):
    pen.rect(0, 0, W, H, fill="#c08a3a", a=0.16)
    for y in range(0, H, 6): pen.ln(0, y, W, y, "#000000", 2, 0.18)
    yb = (t * 300) % H; pen.rect(0, yb, W, 26, fill=WHITE, a=0.06)
    pen.text(label, 70, 140, 48, WHITE, "JetBrainsMono-Regular.ttf", 0.85, "left")
    pen.text(date, W - 70, H - 150, 40, WHITE, "JetBrainsMono-Regular.ttf", 0.85, "right")

def shimmer(pen, x, y, t, r=110, a=0.35):
    """Heat-haze 'guest' presence: wobbling concentric rings, head-shaped."""
    for k in range(4):
        rr = r * (0.6 + 0.15 * k) + 6 * math.sin(t * 5 + k)
        pen.oval(x + 4 * math.sin(t * 3 + k), y, rr * 0.8, rr, stroke="#cfe8b0", w=3, a=a * (1 - k * 0.2))

def frozen_faces(red=0.0, tears=0.0, blink_sync=None):
    base = lambda: {"eyes": "wide", "mouth": "flat", "blink": False, "tremble": 1.0, "red": red, "tears": tears}
    d = base(); d["mouth"] = "open"
    f = {"dad": d, "mom": base(), "sis": base()}
    if blink_sync is not None and blink_sync:
        for v in f.values(): v["eyes"] = "closed"
    return f

def normal_faces(t):
    return {"dad": {"mouth": "talk"}, "mom": {"mouth": "smile"}, "sis": {"mouth": "grin" if (t % 2) < 1 else "smile"}}

# ---------------- builders ----------------
def pov(pen, t, dur, gt, shot, faces=None, z=(1.0, 1.06), fy=640, empty_pull=0.0, flicker=0.2, extras=None, lamp_on=1.0, poses=None):
    camera(pen, t, dur, *z, W / 2, fy, shot)
    S1.dining_front(pen, t, gt, faces or frozen_faces(0.3), poses=poses or {"mom": {"armR": (95, -40)}}, empty_pull=empty_pull,
                    flicker=flicker, lamp_on=lamp_on)
    S1.steam(pen, 960, 880, t, 3, 220, 0.45)
    if extras: extras(pen, t)
    pen.pop()

def close(pen, t, dur, gt, shot, kind, f, z=(1.0, 1.08), r=270, y=500, bg=None, tilt=0, extras=None):
    camera(pen, t, dur, *z, W / 2, y + 40, shot)
    if bg: bg(pen, t)
    head_close(pen, kind, W / 2, y, r, f, t, seed={"dad": 1, "mom": 2, "sis": 4, "you": 3}.get(kind, 7), tilt=tilt)
    if extras: extras(pen, t)
    pen.pop()

def ecu_eyes(pen, t, dur, gt, shot, kind, f, extras=None):
    close(pen, t, dur, gt, shot, kind, f, z=(1.0, 1.1), r=520, y=640, extras=extras)

def lamp_bg(pen, t):
    pendant_lamp(pen, 960, 40, t, cone_to=1000, spread=760, flicker=0.15 if pen.mood == "frozen" else 0)

def triptych(pen, t, dur, shot, faces_fn, snap=True):
    camera(pen, t, dur, 1.0, 1.04, W / 2, H / 2, shot)
    for i, k in enumerate(("dad", "mom", "sis")):
        if snap and t < i * 0.18: continue
        x0 = i * W / 3
        pen.c.save(); pen.c.clipRect(skia.Rect.MakeXYWH(x0, 0, W / 3, H))
        head_close(pen, k, x0 + W / 6, 560, 330, faces_fn(k), t, seed=i + 1)
        pen.c.restore()
        if i: pen.ln(x0, 0, x0, H, ACID, 6)
    pen.pop()

def under_table(pen, t, dur, gt, shot, variant="frozen"):
    camera(pen, t, dur, 1.0, 1.05, W / 2, 700, shot)
    pen.rect(-50, 0, W + 100, 240, fill="#d7e4c6" if pen.mood == "frozen" else "#e8e6df")  # underside of cloth
    for x in (160, 1760): pen.rect(x - 22, 230, 44, 700, fill="#3a3326", stroke=GREY, w=3)
    floor(pen, 930)
    # your legs (left), sister's legs (right) seen from under the table
    for sx, x in ((0, 620), (1, 1300)):
        for k in (-1, 1):
            kick = 0
            if variant == "kick" and sx == 1: kick = 120 * abs(math.sin(t * 6)) if k == -1 else 0
            if variant == "frozen_foot" and sx == 1 and k == -1: kick = 140
            if variant == "bounce" and sx == 0: kick = 0
            bx = x + k * 55; by = 930 - (60 * abs(math.sin(t * 18 + k)) if variant == "bounce" and sx == 0 else 0)
            pen.ln(bx, 260, bx - kick * (1 if sx else 0), by - 40, pen.white, 46)
            pen.oval(bx - kick * (1 if sx else 0) + (24 if sx == 0 else -24), by - 18, 46, 20, fill=DIM if sx == 0 else "#7b5aa6")
    if variant == "kick" and (t % 0.5) < 0.12: pen.text("THUD", 960, 520, 90, ACID)
    pen.pop()

def chair_insert(pen, t, dur, gt, shot, variant="empty"):
    camera(pen, t, dur, 1.0, 1.1, 1300, 620, shot)
    dining_back(pen, t, gt, 0.8, 0.35)
    c = "#8b8c90"
    chair_back(pen, 1350, 820, 1.7, angle=8, color=c)
    table_front(pen, 600, 800, 1500)
    if variant == "plate": plate(pen, 1180, 900, 1.3, food=False); pen.glow(1180, 890, 120, WHITE, 0.25 + 0.1 * math.sin(t * 8))
    if variant == "cushion":
        d = 25 * smooth(t / dur); pen.oval(1350, 740 + d / 2, 120, 22 + d * 0.4, fill="#7a2c26", stroke=GREY, w=3)
    if variant == "napkin":
        b = 12 * math.sin(t * 2.4)
        pen.path(lambda p: (p.moveTo(1240, 690 - b), p.quadTo(1350, 650 - b * 1.4, 1460, 690 - b), p.lineTo(1430, 790), p.lineTo(1270, 790), p.close()), fill=WHITE, stroke=GREY, w=3)
    if variant == "shimmer": shimmer(pen, 1350, 520, t, 150, 0.4 + 0.2 * math.sin(t * 4))
    if variant == "legs":
        pen.rect(-50, 0, W + 100, H, fill=BG)
        floor(pen, 930); g = smooth(t / dur) * 60
        for x in (1180, 1480): pen.ln(x + g, 930, x + g, 640, "#8b8c90", 16)
        for k in range(3): pen.ln(1150 + k * 30, 945, 1150 + k * 30 + g, 945, GREY, 4, 0.7)
    if variant == "eyelids":
        pen.rect(-50, 0, W + 100, H, fill="#000000", a=0.55)
        k = 1.0 if (t % 1.6) < 0.15 else 0.0
        for sx in (-1, 1):
            pen.arc(1350 + sx * 70, 500, 50, 18 + 20 * (1 - k), 200, 140, "#cfe8b0", 5, 0.8)
    if variant == "drips":
        for k in range(4):
            ph = (t * 1.1 + k / 4) % 1; pen.circle(1300 + k * 40, 760 + ph * 170, 8, fill=TEAR, a=1 - ph)
        pen.oval(1360, 935, 160, 14, fill=TEAR, a=0.35)
    if variant == "slide":
        pass
    pen.pop()

def insert_plate(pen, t, dur, gt, shot, food=1.0, fork_mode=None, extra=None, sc=2.6, top=False):
    camera(pen, t, dur, 1.0, 1.08, W / 2, 640, shot)
    pendant_lamp(pen, 700, 90, t, cone_to=760, spread=520, flicker=0.15 if pen.mood == "frozen" else 0)
    table_front(pen, 960, 600 if top else 760, 2400)
    pen.oval(960, 880 if not top else 800, 90 * sc, (22 if not top else 70) * sc, fill="#fafaf5", stroke=GREY, w=4)
    pen.oval(960, 880 if not top else 800, 58 * sc, (13 if not top else 46) * sc, stroke="#d0d0cb", w=3)
    if food > 0:
        yy = 870 if not top else 790
        pen.oval(950, yy, 34 * sc * (0.3 + 0.7 * food), (10 if not top else 30) * sc * (0.3 + 0.7 * food), fill="#d9682a")
    if fork_mode:
        tremor = wobble(t, 3, 6, 6); hx = 1150 + tremor; hy = 600 + wobble(t, 9, 4, 5)
        if fork_mode == "lift": hy -= 120 * smooth(t / dur)
        if fork_mode == "circle": hx = 960 + 120 * math.cos(t * 4); hy = 760 + 30 * math.sin(t * 4)
        if fork_mode == "across": hx = 960 + 260 * (1 - smooth(t / 0.6)); hy = 760
        pen.ln(hx + 60, hy + 20, W + 80, hy + 330, pen.line, 118); pen.ln(hx + 60, hy + 20, W + 80, hy + 330, pen.white, 110)
        fork(pen, hx - 30, hy + 30, ang=-25 if fork_mode != "across" else -70, s=2.2)
        pen.circle(hx, hy, 58, fill=pen.white, stroke=pen.line, w=4); pen.oval(hx - 45, hy - 10, 22, 34, fill=pen.white, stroke=pen.line, w=4)
    if extra: extra(pen, t)
    pen.pop()

def knife_cut(pen, t, dur, gt, shot, level=1):
    camera(pen, t, dur, 1.0 + 0.3 * (level - 1), 1.08 + 0.3 * (level - 1), W / 2, 760, shot)
    table_front(pen, 960, 500, 2400)
    pen.oval(960, 800, 360, 120, fill="#fafaf5", stroke=GREY, w=4)
    n = [6, 14, 30][level - 1]; rnd = random.Random(level)
    for k in range(n):
        x = 760 + rnd.random() * 400; y = 770 + rnd.random() * 60; sz = [40, 20, 8][level - 1]
        pen.rect(x, y, sz, sz * 0.7, fill="#b8722e", r=3)
    kx = 980 + 40 * math.sin(t * 14)
    pen.poly([(kx, 560), (kx + 20, 560), (kx + 26, 790), (kx - 6, 790)], fill="#cfd2d6", stroke=GREY, w=3)
    pen.rect(kx - 6, 440, 34, 130, fill=DARK, r=8)
    if level == 3: pen.text("1 GRAIN", 1350, 520, 70, ACID)
    pen.pop()

def bowl_shot(pen, t, dur, gt, shot, variant="slide"):
    camera(pen, t, dur, 1.0, 1.06, W / 2, 640, shot)
    dining_back(pen, t, gt, 0.75, 0.3)
    table_front(pen, 960, 720, 2400)
    pos = {"slide": smooth(t / dur), "arrives": 1.0, "still": 0.0}.get(variant, 1.0)
    bx = lerp(1500, 800, pos); by = 860
    for k in range(5): pen.ln(bx + 180 + k * 40, by - 10 + k * 8, bx + 260 + k * 40, by - 10 + k * 8, GREY, 3, 0.4 * (1 - pos))  # cloth wrinkles
    pen.oval(bx, by - 60, 170, 40, fill="#d9682a", stroke=GREY, w=4)
    pen.path(lambda p: (p.moveTo(bx - 170, by - 60), p.quadTo(bx, by + 110, bx + 170, by - 60), p.close()), fill="#3a3b40", stroke=GREY, w=4)
    if variant == "spoon":
        a = -60 * smooth(t / dur); pen.push(rot=a, ox=bx, oy=by - 70); pen.ln(bx, by - 70, bx + 220, by - 190, GREY, 12); pen.pop()
    if variant == "steam":
        for k in range(3):
            ph = (t * 0.5 + k / 3) % 1
            pen.path(lambda p, k=k, ph=ph: (p.moveTo(bx - 40 + k * 40, by - 90), p.cubicTo(bx - 80 + k * 40, by - 220 * ph, bx + 60, by - 300 * ph, bx + 140 * ph - 40, by - 330 * ph)), stroke=WHITE, w=5, a=0.6 * (1 - ph))
        pen.circle(bx + 100, by - 330, 22, stroke=WHITE, w=4, a=0.6)  # the 'beckoning' fingertip
    if variant == "arrives" and t < 0.3: pen.text("CLINK", bx, by - 200, 70, ACID)
    pen.pop()

def rice_macro(pen, t, dur, gt, shot, breathe=0.0, dark=False):
    camera(pen, t, dur, 1.0, 1.12, W / 2, 620, shot)
    sc = 1 + breathe * 0.06 * math.sin(t * 2.2)
    pen.push(s=sc, ox=W / 2, oy=700)
    pen.oval(W / 2, 760, 700, 260, fill="#7a3a17" if dark else "#d9682a", stroke=GREY, w=4)
    rnd = random.Random(4)
    for k in range(140):
        x = W / 2 + (rnd.random() - 0.5) * 1200; y = 700 + (rnd.random() - 0.5) * 300
        tw = 8 * math.sin(t * 9 + k) if (breathe and k % 23 == 0) else 0
        pen.oval(x, y + tw, 16, 6, fill="#f2d3a8" if not dark else "#b88a5a", a=0.9)
    if dark: pen.oval(W / 2 + 120, 640, 220, 50, fill="#ffffff", a=0.12)
    pen.pop(); pen.pop()

def diagram(pen, t, dur, gt, shot, variant="plan"):
    """Blueprint top-down table: explainer mode."""
    camera(pen, t, dur, 1.0, 1.04, W / 2, H / 2, shot)
    pen.rect(0, 0, W, H, fill="#0d1b2a")
    for x in range(0, W, 60): pen.ln(x, 0, x, H, "#16304a", 2)
    for y in range(0, H, 60): pen.ln(0, y, W, y, "#16304a", 2)
    draw_on = ease_out(t / 0.6)
    pen.rect(560, 380, 800 * draw_on, 320, stroke="#9fd0ff", w=5)
    seats = {"DAD": (760, 320), "MOM": (1160, 320), "YOU": (760, 760), "SIS": (1160, 760), "?": (1460, 540)}
    for name, (x, y) in seats.items():
        pen.circle(x, y, 48, stroke="#9fd0ff" if name != "?" else ACID, w=4)
        pen.text(name, x, y + 14, 34, "#9fd0ff" if name != "?" else ACID, "JetBrainsMono-Regular.ttf")
    if variant == "guest":
        k = smooth(t / dur)
        for j in range(int(18 * k)):
            a = j / 18 * math.tau; pen.circle(1460 + math.cos(a) * 90, 540 + math.sin(a) * 90, 6, fill=ACID)
        pen.text("GUEST", 1460, 680, 44, ACID, "JetBrainsMono-Regular.ttf", a=k)
    if variant == "plate":
        pen.circle(760, 640, 60, stroke="#9fd0ff", w=4); pen.circle(760, 640, 34, fill="#d9682a")
        reach = math.sin(math.pi * clamp(t / dur)) * 600
        pen.ln(1460, 540, 1460 - reach, 540 + reach * 0.17, ACID, 10); pen.circle(1460 - reach, 540 + reach * 0.17, 22, stroke=ACID, w=5)
        if reach > 500: pen.text("NOT YET", 900, 460, 50, RED, "JetBrainsMono-Regular.ttf")
    if variant in ("host", "crown_slide", "crown_you", "host_cross", "host_search"):
        cx, cy = {"host": (1160, 230), "crown_slide": (lerp(1160, 1460, smooth(t / dur)), lerp(230, 450, smooth(t / dur))),
                  "crown_you": (lerp(1460, 760, smooth(t / dur)), lerp(450, 670, smooth(t / dur))), "host_cross": (1160, 230),
                  "host_search": (1160 + 300 * math.sin(t * 2), 230 + 60 * math.sin(t * 3))}[variant]
        pen.poly([(cx - 50, cy + 30), (cx - 50, cy - 20), (cx - 25, cy + 5), (cx, cy - 35), (cx + 25, cy + 5), (cx + 50, cy - 20), (cx + 50, cy + 30)], fill=AMBER, stroke=WHITE, w=3)
        pen.text("HOST", cx, cy + 85, 32, AMBER, "JetBrainsMono-Regular.ttf")
        if variant == "host_cross": red_x(pen, t - 0.4, 1160, 260, 90)
    if variant == "sequence":
        steps = ["THANK YOU", "MEAL OVER", "CLEAR TABLE"]
        for i, st in enumerate(steps):
            if t > i * 0.5:
                pen.rect(240 + i * 520, 860, 440, 110, stroke=RED if i == 2 else "#9fd0ff", w=5, r=12)
                pen.text(st, 460 + i * 520, 932, 46, RED if i == 2 else "#9fd0ff", "JetBrainsMono-Regular.ttf")
                if i: pen.ln(180 + i * 520, 915, 240 + i * 520, 915, "#9fd0ff", 6)
    if variant == "sightlines":
        k = smooth(t / dur)
        for (x, y) in (seats["DAD"], seats["MOM"], seats["SIS"]):
            pen.ln(1460, 540, lerp(1460, x, k), lerp(540, y, k), ACID, 6)
        pen.ln(1460, 540, 760, 760, RED, 3, 0.3); red_x(pen, t - 0.8, 760, 760, 60)
    pen.pop()

def menu_card(pen, t, dur, gt, shot, n=None, highlight=None, redact7=True, reveal=False):
    camera(pen, t, dur, 1.0, 1.04, W / 2, H / 2, shot)
    drop = ease_out(t / 0.35); y0 = lerp(-700, 100, drop)
    pen.push(rot=lerp(-8, -2, drop), ox=W / 2, oy=y0 + 440)
    pen.rect(560, y0, 800, 880, fill="#f3efe4", stroke=AMBER, w=8, r=18)
    pen.text("TONIGHT'S MENU", W / 2, y0 + 110, 72, "#2a2a2a")
    pen.ln(660, y0 + 140, 1260, y0 + 140, AMBER, 4)
    if n:  # single rule card
        pen.text(f"COURSE {n}", W / 2, y0 + 300, 64, "#8a5d14", "JetBrainsMono-Regular.ttf")
        words = RULES[n].split(); lines, cur = [], ""
        for w_ in words:
            if len(cur + " " + w_) > 16: lines.append(cur.strip()); cur = ""
            cur += " " + w_
        lines.append(cur.strip())
        for i, ln_ in enumerate(lines): pen.text(ln_, W / 2, y0 + 450 + i * 95, 88, "#1c1c1c")
        if reveal and t < 0.6:
            pen.rect(620, y0 + 360, 680 * (1 - t / 0.6), 300, fill="#1c1c1c")
    else:
        for i in range(7):
            y = y0 + 230 + i * 88; hl = highlight == i + 1
            if hl: pen.rect(600, y - 58, 720, 76, fill=ACID, a=0.35 + 0.25 * math.sin(t * 8), r=8)
            pen.text(f"{i + 1}.", 640, y, 46, "#2a2a2a", "JetBrainsMono-Regular.ttf", align="left")
            if i == 6 and redact7: pen.rect(720, y - 44, 520, 56, fill="#111111"); pen.text("NOT FOR YOU YET", 980, y - 4, 26, RED, "JetBrainsMono-Regular.ttf")
            else: pen.rect(720, y - 34, 380 + (i * 53) % 160, 30, fill="#c9c3b5", r=6)
    pen.pop(); pen.pop()

def hallway(pen, t, dur, gt, shot, variant="walk"):
    camera(pen, t, dur, 1.0, 1.05, W / 2, H / 2, shot)
    vx, vy = W / 2, 470
    speed = {"walk": 0.9, "infinite": 2.2}.get(variant, 0.3)
    for k in range(9):  # receding door frames along both walls
        d = ((k + t * speed) % 9) / 9
        z = 0.08 + 0.92 * d ** 2
        for sx in (-1, 1):
            x0 = vx + sx * 900 * z; w_ = 220 * z
            pen.rect(x0 - (w_ if sx < 0 else 0), vy - 300 * z, w_, 560 * z, stroke=pen.white, w=max(2, 6 * z), a=0.3 + 0.7 * z)
    for sx in (-1, 1):
        pen.ln(vx, vy, vx + sx * 1100, H + 40, pen.white, 5); pen.ln(vx, vy - 40, vx + sx * 1100, -60, pen.white, 4, 0.6)
    pen.glow(vx, vy, 160, "#cfe8b0", 0.15)
    if variant == "doorway":
        pen.rect(0, 0, 640, H, fill=BG); pen.rect(W - 640, 0, 640, H, fill=BG)
        pen.rect(640, 120, 640, 900, stroke=pen.white, w=10)
        pen.circle(980, 900, 10, fill=AMBER, a=0.8)  # nightlight
    if variant in ("bathroom", "bedroom"):
        pen.rect(1300, 260, 330, 640, stroke=pen.white, w=8)
        pen.text("BATHROOM" if variant == "bathroom" else "YOUR ROOM", 1465, 230, 44, ACID, "JetBrainsMono-Regular.ttf")
    if variant == "figures":
        for k in range(4):
            x = vx + (k - 1.5) * 26; s = 0.18; bob = abs(math.sin(t * 8 + k)) * 3
            figure(pen, "kid", x, vy + 80 - bob, s, {"face": {"eyes": "dot"}}, t, seed=k)
    if variant == "old_man":
        bob = abs(math.sin(t * 6)) * 10
        figure(pen, "old", W / 2, 1000 - bob, 1.6, {"face": {"eyes": "dot", "mouth": "flat"}, "armL": (10 + 15 * math.sin(t * 6), 5), "armR": (10 - 15 * math.sin(t * 6), 5)}, t, seed=9)
        for k in range(5): pen.ln(W / 2 - 120, 600 + k * 70, W / 2 + 120, 600 + k * 70, "#7fa8ff", 6, 0.6)  # pyjama stripes
    if variant == "footprints":
        for k in range(6):
            if t * 3 > k:
                y = 1000 - k * 90; x = vx + (40 if k % 2 else -40) * (1 - k / 8)
                pen.oval(x, y, 34 - k * 3, 14 - k, fill="#000000", stroke=GREY, w=2, a=0.9)
    pen.pop()

def front_door(pen, t, dur, gt, shot, opening=True):
    camera(pen, t, dur, 1.0, 1.05, W / 2, 560, shot)
    floor(pen, 930)
    k = smooth(t / min(dur, 1.2)); op = k if opening else 1 - k
    pen.rect(760, 230, 400, 700, fill="#0b1020" if op > 0.02 else BG, stroke=pen.white, w=8)
    if op > 0.02:
        for j in range(8): pen.circle(800 + j * 47, 300 + (j * 73) % 300, 3, fill=WHITE, a=0.7)
        for j in range(4):
            ph = (t * 0.8 + j / 4) % 1; pen.ln(760 + 400 * ph, 500 + j * 60, 790 + 400 * ph, 495 + j * 60, WHITE, 3, 0.5)
    pen.poly([(760, 230), (760 + 400 * (1 - op), 230 + 30 * op), (760 + 400 * (1 - op), 930 - 30 * op), (760, 930)], fill="#1d2233", stroke=pen.white, w=6)
    if not opening and t > 1.2 and t < 1.5: pen.text("THUD", W / 2, 180, 90, ACID)
    pen.pop()

def twins_room(pen, t, dur, gt, shot, variant="table", night=False):
    """The Houston twins' kitchen table (side view): Tobi (kid), Tola, parents."""
    pen.mood = "dark" if night else "normal"
    camera(pen, t, dur, 1.0, 1.05, W / 2, 600, shot)
    floor(pen, 900)
    window(pen, 1500, 200, 230, 260, t, moon=night)
    if not night: pen.rect(1500, 200, 230, 260, fill="#9fd0ff", a=0.25)
    pendant_lamp(pen, 960, 260, t, on=1.0 if night else 0.0, cone_to=900, spread=330)
    pen.rect(560, 760, 800, 22, fill=WHITE, stroke=GREY, w=3)
    for x in (590, 1330): pen.ln(x, 782, x, 900, WHITE, 8)
    if variant == "table":
        figure(pen, "kid", 700, 820, 1.0, {"face": {"mouth": "flat", "look": (0.8, 0)}}, t, seed=11, seated=True)
        figure(pen, "tola", 1220, 820, 1.0, {"face": {"mouth": "o", "eyes": "dot", "look": (-0.6, 0.4)}}, t, seed=12, seated=True)
        pos = smooth(t / dur); bx = lerp(1300, 1150, pos)
        pen.oval(bx, 745, 70, 18, fill="#d9682a", stroke=GREY, w=3)
    if variant == "laugh":
        figure(pen, "dad", 680, 900, 0.95, {"face": {"mouth": "grin", "eyes": "happy"}, "bob": abs(math.sin(t * 9)) * 8}, t, seed=13)
        figure(pen, "mom", 1240, 900, 0.95, {"face": {"mouth": "grin", "eyes": "happy"}}, t, seed=14)
        figure(pen, "kid", 940, 900, 1.0, {"face": {"mouth": "grin", "eyes": "dot"}}, t, seed=11)
        figure(pen, "tola", 1080, 900, 1.0, {"face": {"mouth": "smile", "eyes": "dot"}}, t, seed=12)
    if variant in ("night", "night_wide", "cut", "slide"):
        figure(pen, "tola", 1160, 820, 1.0, {"face": {"mouth": "flat", "eyes": "dot", "look": (0.9, 0.3), "blink": False}}, t, seed=12, seated=True)
        chair_side(pen, 1380, 900, 1.0, -1, color=GREY)
        pen.oval(1300, 750, 70, 16, fill="#fafaf5", stroke=GREY, w=3)
        if variant in ("cut", "slide"):
            n = int(t * 4) if variant == "slide" else 0
            for k in range(min(n, 6)): pen.rect(1270 + (k % 3) * 20, 738 - (k // 3) * 8, 12, 8, fill="#d9682a")
    if variant == "older":
        figure(pen, "tola", 1160, 800, 1.15, {"face": {"mouth": "flat", "eyes": "dot", "look": (0.9, 0.2), "blink": False}}, t, seed=12, seated=True)
        chair_side(pen, 1380, 900, 1.0, -1, color=GREY); pen.oval(1300, 750, 70, 16, fill="#fafaf5", stroke=GREY, w=3)
    pen.pop()

def memory(pen, t, dur, gt, shot, scene="eat", date="SUN 14 MAR 2014"):
    pen.mood = "normal"
    camera(pen, t, dur, 1.0, 1.05, W / 2, 600, shot)
    floor(pen, 900)
    pendant_lamp(pen, 960, 240, t, cone_to=900, spread=330)
    pen.rect(560, 760, 800, 22, fill=WHITE, stroke=GREY, w=3)
    for x in (590, 1330): pen.ln(x, 782, x, 900, WHITE, 8)
    if scene in ("toddler", "kid", "serve", "dad_done", "steal", "ask_more", "glance", "birthday"):
        kid_kind, ks = ("toddler", 1.2) if scene == "toddler" else ("you", 0.9)
        chew = {"mouth": "talk" if scene != "glance" else "flat", "eyes": "dot"}
        figure(pen, kid_kind, 820, 830, ks, {"face": chew, "armR": (70, 50)}, t, seed=3, seated=True)
        pen.oval(860, 752, 70, 16, fill="#fafaf5", stroke=GREY, w=3)
        pen.oval(860, 744, 40, 10, fill="#d9682a")
    if scene in ("serve", "dad_done", "steal", "glance", "kid"):
        mom_pose = {"face": {"mouth": "smile", "look": (-0.8, 0) if scene != "glance" else (1, 0)}, "armL": (80 if scene == "serve" else 10, 40)}
        figure(pen, "mom", 1150, 900, 0.95, mom_pose, t, seed=2)
    if scene in ("dad_done", "glance"):
        figure(pen, "dad", 600, 900, 0.95, {"face": {"mouth": "talk" if scene == "dad_done" else "flat", "look": (1, 0)}, "armR": (120 if scene == "dad_done" else 10, 30)}, t, seed=1)
    if scene in ("steal", "glance"):
        sx = 990 if scene == "steal" else 1000
        figure(pen, "sis", sx, 840, 0.8, {"face": {"mouth": "grin", "eyes": "dot", "look": (-1, 0) if scene == "steal" else (1, 0)}, "armL": (95, 20) if scene == "steal" else (10, 5)}, t, seed=4, seated=True)
    if scene == "glance":
        chair_side(pen, 1500, 900, 1.0, -1, color=GREY)
        pen.circle(1560, 640, 60, stroke=RED, w=6, a=0.5 + 0.5 * math.sin(t * 6))
    if scene == "birthday":
        pen.rect(840, 690, 120, 60, fill="#f3efe4", stroke=GREY, w=3)
        for k in range(3):
            pen.ln(870 + k * 30, 690, 870 + k * 30, 660, WHITE, 5); pen.circle(870 + k * 30, 650, 8 + 2 * math.sin(t * 20 + k), fill=AMBER)
    if scene == "ask_more":
        pen.oval(860, 600 - 30 * abs(math.sin(t * 3)), 70, 16, fill="#fafaf5", stroke=GREY, w=3)
    vhs(pen, t, date=date)
    pen.pop()

def wall_shot(pen, t, dur, gt, shot, variant="nod"):
    camera(pen, t, dur, 1.0, 1.05, W / 2, 560, shot)
    pen.rect(0, 0, W, H, fill="#141519")
    pen.glow(400, 300, 900, AMBER, 0.18)
    sx, sy = 1100, 640
    pen.rect(sx - 110, sy - 40, 220, 360, fill="#050506", a=0.8)  # chair shadow
    nod = 18 * math.sin(t * 3) if variant == "nod" else 0
    pen.oval(sx, sy - 160 + nod, 95, 110, fill="#050506", a=0.85)
    if variant == "jaw":
        j = 20 * abs(math.sin(t * 6)); pen.oval(sx, sy - 90 + j, 60, 20 + j / 2, fill="#050506", a=0.9)
    pen.pop()

def clock_shot(pen, t, dur, gt, shot, fast=True):
    camera(pen, t, dur, 1.0, 1.08, W / 2, H / 2, shot)
    wall_clock(pen, W / 2, H / 2, 300, CLOCK0 + gt + (t * 3600 * 2 if fast else 0))
    for i, x in enumerate((420, 1500)):
        h_ = 260 - 200 * smooth(t / dur) if fast else 260
        pen.rect(x - 30, 900 - h_, 60, h_, fill="#f3efe4", stroke=GREY, w=3)
        pen.circle(x, 880 - h_, 14 + 3 * math.sin(t * 20 + i), fill=AMBER)
    pen.pop()

def candle_shot(pen, t, dur, gt, shot, mode="lean"):
    camera(pen, t, dur, 1.0, 1.1, W / 2, 600, shot)
    table_front(pen, 960, 820, 2400)
    for i, x in enumerate((560, 960, 1360)):
        pen.rect(x - 34, 480, 68, 340, fill="#f3efe4", stroke=GREY, w=4)
        lean = -30 * smooth(t / dur) if mode == "lean" else 0
        size = 1 + (1.6 * math.exp(-t * 3) if mode == "flare" else 0)
        pen.push(rot=lean, ox=x, oy=480)
        pen.glow(x, 430, 120 * size, AMBER, 0.4)
        pen.path(lambda p, x=x, size=size: (p.moveTo(x, 480), p.cubicTo(x - 30 * size, 440, x - 10, 400 - 60 * size, x, 360 - 50 * size), p.cubicTo(x + 10, 400 - 60 * size, x + 30 * size, 440, x, 480)), fill=AMBER)
        pen.pop()
    pen.pop()

def glass_shot(pen, t, dur, gt, shot):
    camera(pen, t, dur, 1.0, 1.1, W / 2, 600, shot)
    table_front(pen, 960, 860, 2400)
    pen.rect(760, 300, 400, 560, stroke=WHITE, w=6, r=20, a=0.8)
    lvl = 520
    pen.rect(766, lvl, 388, 860 - lvl, fill="#7fb6ff", a=0.25)
    for k in range(3):
        rr = ((t * 1.5 + k / 3) % 1) * 190
        pen.oval(960, lvl, rr, rr * 0.15, stroke=WHITE, w=3, a=1 - rr / 190)
    pen.pop()

def salt_shot(pen, t, dur, gt, shot, push=False):
    camera(pen, t, dur, 1.0, 1.08, W / 2, 620, shot)
    table_front(pen, 960, 760, 2400)
    x = 1100 - (300 * smooth(t / dur) if push else 0)
    pen.rect(x - 60, 540, 120, 220, fill="#f3efe4", stroke=GREY, w=4, r=30)
    for k in range(5): pen.circle(x - 30 + k * 15, 560, 5, fill=GREY)
    pen.oval(1450, 760, 120, 50, fill="#e3f0d6", stroke=GREY, w=4)  # sister's frozen hand
    pen.pop()

def receipt(pen, t, dur, gt, shot):
    camera(pen, t, dur, 1.0, 1.04, W / 2, H / 2, shot)
    L = 760 * ease_out(t / max(0.4, dur * 0.7))
    pen.rect(740, 120, 440, L, fill="#f7f5ee", stroke=GREY, w=3)
    rows = [("TABLE", "5"), ("GUEST", "1"), ("SECONDS", "x1"), ("", ""), ("BALANCE OWED:", ""), ("1 SPOONFUL", "")]
    for i, (a_, b_) in enumerate(rows):
        y = 210 + i * 90
        if y < 120 + L - 30:
            pen.text(a_, 780, y, 40, "#222222", "JetBrainsMono-Regular.ttf", align="left")
            pen.text(b_, 1140, y, 40, "#222222", "JetBrainsMono-Regular.ttf", align="right")
    pen.pop()

def casefile(pen, t, dur, gt, shot, variant="file"):
    camera(pen, t, dur, 1.0, 1.05, W / 2, H / 2, shot)
    pen.rect(0, 0, W, H, fill="#14110c")
    x0 = lerp(-900, 520, ease_out(t / 0.4))
    pen.rect(x0, 180, 880, 680, fill="#c7a46a", stroke="#7a5e2f", w=6, r=10)
    pen.text("CASE FILE 041", x0 + 440, 320, 70, "#3b2b12", "JetBrainsMono-Regular.ttf")
    if t > 0.4: stamp(pen, "HOUSTON, TX", t - 0.4, RED, x0 + 440, 560, -8, 90)
    if variant in ("polaroid", "push"):
        pen.push(rot=6, ox=1300, oy=560)
        pen.rect(1060, 300, 480, 540, fill="#f7f5ee", stroke=GREY, w=3)
        pen.rect(1090, 330, 420, 400, fill="#22262e")
        figure(pen, "kid", 1210, 720, 0.75, {"face": {"mouth": "smile"}}, t, seed=11)
        figure(pen, "tola", 1390, 720, 0.75, {"face": {"mouth": "smile"}}, t, seed=12)
        if variant == "push": pen.text("12", 1300, 800, 60, RED, "JetBrainsMono-Regular.ttf")
        pen.pop()
    pen.pop()

def flashback(pen, t, dur, gt, shot, who="grandma"):
    pen.mood = "normal"
    camera(pen, t, dur, 1.0, 1.05, W / 2, 600, shot)
    floor(pen, 900)
    if who == "grandma":
        figure(pen, "old", 820, 900, 1.0, {"face": {"mouth": "talk", "look": (1, 0.3)}, "armR": (60, 40)}, t, seed=9)
        figure(pen, "kid", 1060, 900, 1.0, {"face": {"mouth": "o", "look": (-1, -0.3)}}, t, seed=11)
    elif who == "tola_alone":
        door(pen, 700, 580, 160, 320)
        figure(pen, "tola", 1160, 900, 1.0, {"face": {"mouth": "flat", "look": (-1, 0)}}, t, seed=12)
    elif who == "mom_teach":
        figure(pen, "mom", 820, 900, 1.0, {"face": {"mouth": "talk"}, "armR": (150 + 15 * math.sin(t * 10), 10)}, t, seed=2)
        figure(pen, "toddler", 1060, 900, 1.1, {"face": {"mouth": "o"}}, t, seed=3)
    elif who == "thankyou":
        figure(pen, "old", 820, 900, 1.0, {"face": {"mouth": "smile", "eyes": "happy"}}, t, seed=9)
        figure(pen, "toddler", 1060, 900, 1.1, {"face": {"mouth": "talk"}}, t, seed=3)
        pen.text("THANK YOU!", 1150, 560, 60, WHITE, a=smooth(t / 0.4))
    pen.rect(0, 0, W, H, fill="#c08a3a", a=0.18)
    pen.pop()

def kt(pen, t, text, color=ACID):
    kinetic(pen, text, t, color, size=200 if len(text) < 12 else 120)

def counter(pen, t, dur, start=1, end=3, over=False, gt=0, shot=None):
    if over:
        pov(pen, t, dur, gt, shot, frozen_faces(0.4))
        pen.rect(0, 0, W, H, fill="#000000", a=0.35)
    n = int(lerp(start, end + 0.999, t / dur))
    sc = 1.3 - 0.3 * ease_out((t * (end - start + 1) / dur) % 1)
    pen.push(s=sc, ox=W / 2, oy=H / 2)
    pen.text(str(n), W / 2, H / 2 + 120, 330, WHITE)
    pen.pop()

def split_faces(pen, t, dur, shot):
    camera(pen, t, dur, 1.0, 1.04, W / 2, H / 2, shot)
    kinds = ["dad", "mom", "sis", "you", "kid", "old"]
    for i, k in enumerate(kinds):
        x0, y0 = (i % 3) * W / 3, (i // 3) * H / 2
        pen.c.save(); pen.c.clipRect(skia.Rect.MakeXYWH(x0, y0, W / 3, H / 2))
        look = clamp(t / 0.6) * 1.0
        head_close(pen, k, x0 + W / 6, y0 + H / 4 + 10, 160, {"eyes": "wide", "mouth": "flat", "look": (look, 0), "blink": False}, t, seed=i)
        pen.c.restore()
    for k in (1, 2): pen.ln(k * W / 3, 0, k * W / 3, H, ACID, 4)
    pen.ln(0, H / 2, W, H / 2, ACID, 4)
    pen.pop()

def xray_mouth(pen, t, dur, gt, shot):
    camera(pen, t, dur, 1.0, 1.05, W / 2, H / 2, shot)
    pen.rect(0, 0, W, H, fill="#0d1b2a")
    pen.circle(W / 2, 520, 330, stroke="#9fd0ff", w=6)
    pen.oval(W / 2 + 120, 640, 120, 70, stroke="#9fd0ff", w=5)
    for k in range(9): pen.oval(W / 2 + 80 + (k % 3) * 40, 620 + (k // 3) * 22, 18, 8, fill="#d9682a")
    pen.text("HOLD", W / 2 + 120, 790, 50, ACID, "JetBrainsMono-Regular.ttf")
    pen.pop()

def photo_wall(pen, t, dur, gt, shot, flip=False):
    camera(pen, t, dur, 1.0, 1.06, W / 2, H / 2, shot)
    for i, (x, y) in enumerate(((420, 260), (900, 230), (1380, 280), (640, 620), (1160, 640))):
        k = clamp((t - i * 0.15) / 0.3) if flip else 0
        wf = abs(math.cos(k * math.pi)) if flip else 1
        pen.rect(x - 160 * wf, y - 120, 320 * wf, 240, fill="#f3efe4", stroke=AMBER, w=6)
        if wf > 0.3:
            pen.push(s=0.32, ox=x, oy=y + 100)
            for j, kind in enumerate(("dad", "mom", "you", "sis")):
                figure(pen, kind, x - 300 + j * 200, y + 100, 1.0, {"face": {"mouth": "smile"}}, 0, seed=j)
            if k > 0.5:
                chair_side(pen, x + 420, y + 100, 1.0, -1, color=RED)
            pen.pop()
    pen.pop()

def recipe_card(pen, t, dur, gt, shot):
    camera(pen, t, dur, 1.0, 1.06, W / 2, H / 2, shot)
    pen.push(rot=-4, ox=W / 2, oy=H / 2)
    pen.rect(520, 160, 880, 760, fill="#f3e6c8", stroke="#8a5d14", w=6, r=8)
    pen.text("Grandma's Sunday Rice", W / 2, 260, 56, "#5a3b0c", "Montserrat-VF.ttf")
    lines = ["1. keep eating", "2. never look at the end chair", "3. nobody leaves the table", "4. take, but don't eat", "5. no thank-yous", "6. watch the blinking", "7. ...the slow one hosts"]
    for i, l in enumerate(lines):
        if t > i * 0.12: pen.text(l, 600, 360 + i * 76, 44, "#3b2b12", "Montserrat-VF.ttf", align="left")
    pen.pop(); pen.pop()

def waveform(pen, t, dur, gt, shot):
    pov(pen, t, dur, gt, shot, frozen_faces(0.3), flicker=0.3)
    pen.rect(0, 380, W, 320, fill="#000000", a=0.55)
    pts = [(x, 540 + math.sin(x * 0.02 + t * 4) * 90 * math.sin(x * 0.003 + t)) for x in range(0, W + 20, 20)]
    pen.poly(pts, stroke=ACID, w=6, closed=False)

def top_table(pen, t, dur, gt, shot, labels=0, four=False, bowl=False, crown=False):
    camera(pen, t, dur, 1.0, 1.05, W / 2, H / 2, shot)
    pendant_lamp(pen, W / 2, -200, t, on=0.6, cone_to=H, spread=900)
    pen.rect(560, 330, 800, 420, fill="#e8e6df" if pen.mood == "normal" else "#d7e4c6", stroke=GREY, w=5, r=10)
    seats = {"dad": (760, 270), "mom": (1160, 270), "you": (760, 810), "sis": (1160, 810), "x": (1440, 540)}
    for k, (x, y) in seats.items():
        pen.rect(x - 70, y - 50, 140, 100, stroke=GREY, w=5, r=12)
        if k != "x" or four:
            if k != "x":
                pen.circle(x, y, 52, fill=pen.white, stroke=pen.line, w=3)
                pen.arc(x, y, 52, 52, 200, 140, DARK, 14)
        pen.oval(x, y + (110 if y < 540 else -110) if k != "x" else y, 60, 40, fill="#fafaf5", stroke=GREY, w=3)
    if bowl:
        bx = lerp(1300, 760, smooth(t / dur)); pen.circle(bx, 540, 70, fill="#d9682a", stroke=GREY, w=4)
        pen.ln(bx + 80, 540, bx + 300, 540, ACID, 4, 0.6)
    if labels:
        nums = ["dad", "mom", "you", "sis"] + (["x"] if labels == 5 else [])
        for i, k in enumerate(nums):
            if t > i * 0.3:
                x, y = seats[k]; pen.circle(x + 70, y - 60, 40, fill=ACID if k != "x" else RED)
                pen.text(str(i + 1), x + 70, y - 40, 50, "#111111")
    pen.pop()

def white_flash(pen, t, dur):
    pen.rect(0, 0, W, H, fill=WHITE, a=clamp(1 - t / 0.5))

def ghost_clear(pen, t, dur, gt, shot, everything=False):
    pov(pen, t, dur, gt, shot, frozen_faces(0.3))
    k = smooth(t / dur)
    for x in ((560, 1340) if everything else (960,)):
        pen.ln(x, 980, x + 900 * k, 980 - 400 * k, WHITE, 40 * (1 - k), 0.5)
    if everything and k > 0.5:
        pen.rect(0, 0, W, H, fill=BG, a=(k - 0.5) * 1.2)

def pov_you_empty(pen, t, dur, gt, shot):
    pen.mood = "frozen"
    camera(pen, t, dur, 1.0, 1.05, W / 2, 640, shot)
    dining_back(pen, t, gt, 0.8, 0.4)
    chair_back(pen, W / 2, 1000, 2.4, angle=0, color="#8b8c90")
    k = smooth(t / dur); pen.path(lambda p: (p.moveTo(800, 700 + 300 * k), p.lineTo(1120, 700 + 300 * k), p.lineTo(1080, 780 + 300 * k), p.lineTo(840, 780 + 300 * k), p.close()), fill=WHITE)
    pen.pop()

def family_unfreeze(pen, t, dur, gt, shot, hug=False):
    pen.mood = "normal"
    camera(pen, t, dur, 1.0, 1.06 if not hug else 0.92, W / 2, 640, shot)
    if hug:
        floor(pen, 930); pendant_lamp(pen, 960, 240, t, cone_to=930, spread=420)
        for i, (k, x) in enumerate((("dad", 700), ("mom", 900), ("you", 1080), ("sis", 1240))):
            figure(pen, k, x, 930, 1.0, {"face": {"eyes": "happy", "mouth": "smile"}, "armL": (120, 10), "armR": (120, 10), "lean": (-1) ** i * 3}, t, seed=i + 1)
        pen.pop(); return
    faces = {"dad": {"mouth": "open", "eyes": "dot"}, "mom": {"mouth": "wobble", "eyes": "dot", "tears": 0.6}, "sis": {"mouth": "open", "eyes": "dot"}}
    S1.dining_front(pen, t, gt, faces, poses={"dad": {"tilt": -6}, "mom": {"tilt": 5}}, flicker=0)
    pen.pop()

def normal_table(pen, t, dur, gt, shot, notice=False, fifth=False):
    pen.mood = "normal"
    camera(pen, t, dur, 1.0, 1.06, W / 2, 640, shot)
    S1.dining_front(pen, t, gt, normal_faces(t), poses={"dad": {"armR": (60 + 20 * math.sin(t * 6), 40)}}, flicker=0)
    if fifth:
        pen.oval(1680, 950, 60 * (1 - 0.5 * smooth(t / dur)), 14, fill="#d9682a")
    if notice: pen.circle(1700, 760, 140, stroke=RED, w=8, a=0.6 + 0.4 * math.sin(t * 5))
    pen.pop()

# ---------------- mapping: set-up -> drawer ----------------
F = frozen_faces
def P(**kw): return lambda pen, t, d, gt, s: pov(pen, t, d, gt, s, **kw)
def CL(kind, **f): return lambda pen, t, d, gt, s: close(pen, t, d, gt, s, kind, dict(f), bg=lamp_bg)
def EC(kind, **f): return lambda pen, t, d, gt, s: ecu_eyes(pen, t, d, gt, s, kind, dict(f))
def KT(text, color=ACID): return lambda pen, t, d, gt, s: kt(pen, t, text, color)
FROZ = dict(eyes="wide", mouth="flat", blink=False, tremble=1.0)

MAP = {
    "WIDE_TABLE": P(z=(0.92, 0.98), fy=600), "WIDE_TABLE_DARK": P(lamp_on=0.4, flicker=0.6), "WIDE_POV_STARE": P(z=(1.0, 1.15)),
    "CU_DAD": CL("dad", eyes="wide", mouth="open", blink=False, tremble=0.8), "MCU_MOM_SPOON": lambda pen, t, d, gt, s: pov(pen, t, d, gt, s, z=(1.5, 1.6), fy=520),
    "ECU_SPOON": lambda pen, t, d, gt, s: insert_plate(pen, t, d, gt, s, extra=lambda p, t: p.oval(960, 400 + 400 * smooth(t / d), 20, 9, fill="#f2d3a8")),
    "INS_GRAIN_LANDS": lambda pen, t, d, gt, s: insert_plate(pen, t, d, gt, s, extra=lambda p, t: (p.oval(1300, 760, 26, 10, fill="#f2d3a8"), t < 0.3 and p.text("TICK", 1300, 640, 70, ACID))),
    "TRIPTYCH_EYES": lambda pen, t, d, gt, s: triptych(pen, t, d, s, lambda k: dict(FROZ)),
    "ECU_SIS_EYES": EC("sis", **FROZ), "KT_COUNTER": lambda pen, t, d, gt, s: counter(pen, t, d, 1, 3),
    "COUNTER_OVER_FAMILY": lambda pen, t, d, gt, s: counter(pen, t, d, 4, 9, True, gt, s),
    "INS_CUSHION": lambda pen, t, d, gt, s: chair_insert(pen, t, d, gt, s, "cushion"),
    "MENU_CARD_ALL": lambda pen, t, d, gt, s: menu_card(pen, t, d, gt, s), "MENU_CARD_HL2": lambda pen, t, d, gt, s: menu_card(pen, t, d, gt, s, highlight=2),
    "MENU_CARD_HL7": lambda pen, t, d, gt, s: menu_card(pen, t, d, gt, s, highlight=7),
    "CU_YOU_EYES_SIDE": CL("you", eyes="wide", mouth="flat", look=(1, 0), blink=False),
    "INS_PLATE_YOU": lambda pen, t, d, gt, s: insert_plate(pen, t, d, gt, s, food=1.0),
    **{f"RULE_CARD_{n}": (lambda n: lambda pen, t, d, gt, s: menu_card(pen, t, d, gt, s, n=n, reveal=(n == 7)))(n) for n in range(1, 8)},
    "INS_FORK_PICKUP": lambda pen, t, d, gt, s: insert_plate(pen, t, d, gt, s, fork_mode="lift"),
    "INS_BITE_POV": lambda pen, t, d, gt, s: insert_plate(pen, t, d, gt, s, fork_mode="lift", sc=1.6),
    "CU_YOU_CHEW": CL("you", eyes="dot", mouth="talk"), "ECU_THROAT_SWALLOW": CL("you", eyes="closed", mouth="flat"),
    "INS_FORK_SCOOP": lambda pen, t, d, gt, s: insert_plate(pen, t, d, gt, s, fork_mode="circle"),
    "FASTFWD_GAG": lambda pen, t, d, gt, s: (close(pen, t * 3, d, gt, s, "you", {"mouth": "talk", "eyes": "dot"}), pen.text("2x", 1700, 200, 90, ACID), t > 0.4 and red_x(pen, t - 0.4)),
    "CU_YOU_SHAKING": lambda pen, t, d, gt, s: (insert_plate(pen, t, d, gt, s, fork_mode="lift"), t > 0.5 and red_x(pen, t - 0.5)),
    "WIDE_TABLE_YOU": P(z=(0.9, 0.95)), "OTS_CHAIR_FG": lambda pen, t, d, gt, s: chair_insert(pen, t, d, gt, s, "empty"),
    "INS_STEAM": lambda pen, t, d, gt, s: S1.INS_RICE_POT(pen, t, d, gt, {"motion": "micro-change"}),
    "VOID_DIAGRAM": lambda pen, t, d, gt, s: diagram(pen, t, d, gt, s), "DIAGRAM_GUEST_SILHOUETTE": lambda pen, t, d, gt, s: diagram(pen, t, d, gt, s, "guest"),
    "INS_CUTLERY_ETIQUETTE": lambda pen, t, d, gt, s: chair_insert(pen, t, d, gt, s, "plate"),
    "DIAGRAM_PLATE_FULL": lambda pen, t, d, gt, s: diagram(pen, t, d, gt, s, "plate"),
    "INS_EMPTY_CHAIR_DARK": lambda pen, t, d, gt, s: (setattr(pen, "mood", "dark"), chair_insert(pen, t, d, gt, s, "empty")),
    "CLOCK_WALL": lambda pen, t, d, gt, s: clock_shot(pen, t, d, gt, s), "CLOCK_TIMELAPSE": lambda pen, t, d, gt, s: clock_shot(pen, t, d, gt, s),
    "POV_PLATE_EMPTYING": lambda pen, t, d, gt, s: insert_plate(pen, t, d, gt, s, food=1 - smooth(t / d)),
    "GHOST_HANDS_CLEAR": lambda pen, t, d, gt, s: ghost_clear(pen, t, d, gt, s), "GHOST_HANDS_CLEAR_ALL": lambda pen, t, d, gt, s: ghost_clear(pen, t, d, gt, s, True),
    "WIDE_EMPTY_CHAIR_YOURS": pov_you_empty,
    "INS_PLATE_LOW": lambda pen, t, d, gt, s: insert_plate(pen, t, d, gt, s, food=0.2), "TOP_PLATE": lambda pen, t, d, gt, s: insert_plate(pen, t, d, gt, s, food=0.5, fork_mode="circle", top=True),
    "INS_KNIFE_CUT": lambda pen, t, d, gt, s: knife_cut(pen, t, d, gt, s, 1), "INS_KNIFE_CUT_2": lambda pen, t, d, gt, s: knife_cut(pen, t, d, gt, s, 2),
    "INS_KNIFE_CUT_3": lambda pen, t, d, gt, s: knife_cut(pen, t, d, gt, s, 3),
    "INS_FORK_FOOD": lambda pen, t, d, gt, s: (insert_plate(pen, t, d, gt, s, fork_mode="lift"), stamp(pen, "DINER", t, ACID, 600, 300)),
    "INS_EMPTY_PLATE_REFLECT": lambda pen, t, d, gt, s: (insert_plate(pen, t, d, gt, s, food=0), stamp(pen, "DISHES", t, RED, 600, 300)),
    "MONTAGE_CHAIRS": lambda pen, t, d, gt, s: chair_insert(pen, t, d, gt, s, ["empty", "plate", "cushion"][int(t / d * 3) % 3]),
    "CHAIR_GRANDMA": lambda pen, t, d, gt, s: (chair_insert(pen, t, d, gt, s, "empty"), frame_pic(pen, 1290, 640, 120, 90)),
    "CHAIR_BAGS": lambda pen, t, d, gt, s: (chair_insert(pen, t, d, gt, s, "empty"), pen.rect(1260, 560 + 160 * (1 - ease_out(t / 0.4)), 180, 170, fill="#4a6a8a", stroke=GREY, w=4, r=20)),
    "CHAIR_END_FAR": lambda pen, t, d, gt, s: P(z=(1.5, 1.62), fy=640)(pen, t, d, gt, s),
    "INS_CHAIR_LEGS": lambda pen, t, d, gt, s: chair_insert(pen, t, d, gt, s, "legs"),
    "CU_YOU_EAR": CL("you", eyes="dot", mouth="flat", look=(1, 0)), "CU_YOU_EYES": CL("you", eyes="wide", mouth="flat", look=(0.8, 0), blink=False),
    "SPLIT_FACES": lambda pen, t, d, gt, s: split_faces(pen, t, d, s),
    "REPLAY_VHS": lambda pen, t, d, gt, s: (P()(pen, t, d, gt, s), vhs(pen, t, "<< REWIND", ""), stamp(pen, "RULE 2: BROKEN", t, RED)),
    "POV_LOOK_CHAIR": lambda pen, t, d, gt, s: chair_insert(pen, t, d, gt, s, "empty"), "INS_CLEAN_PLATE": lambda pen, t, d, gt, s: chair_insert(pen, t, d, gt, s, "plate"),
    "MCU_CHAIR_PLATE": lambda pen, t, d, gt, s: chair_insert(pen, t, d, gt, s, "plate"), "INS_CUSHION_DENT": lambda pen, t, d, gt, s: chair_insert(pen, t, d, gt, s, "cushion"),
    "INS_NAPKIN_FLOAT": lambda pen, t, d, gt, s: chair_insert(pen, t, d, gt, s, "napkin"), "POV_CHAIR_PUSH": lambda pen, t, d, gt, s: chair_insert(pen, t, d, gt, s, "shimmer"),
    "POV_SNAP_BACK_PLATE": lambda pen, t, d, gt, s: insert_plate(pen, t, d, gt, s), "WIDE_FAMILY_STARE": P(z=(1.1, 1.2)),
    "ECU_DAD_EYES": EC("dad", eyes="wide", mouth="flat", blink=False, tremble=1, tears=0.3),
    "UNDER_TABLE": lambda pen, t, d, gt, s: under_table(pen, t, d, gt, s, "kick" if s["sentence"] < 13 else "frozen_foot"),
    "UNDER_TABLE_LEGS": lambda pen, t, d, gt, s: under_table(pen, t, d, gt, s, "bounce"), "UNDER_TABLE_KICK": lambda pen, t, d, gt, s: (setattr(pen, "mood", "normal"), under_table(pen, t, d, gt, s, "kick")),
    "HALL_DOORWAY": lambda pen, t, d, gt, s: hallway(pen, t, d, gt, s, "doorway"),
    "MONTAGE_EXCUSED": lambda pen, t, d, gt, s: memory(pen, t, d, gt, s, ["toddler", "kid", "kid"][int(t / d * 3) % 3], "AGE " + ["4", "8", "12"][int(t / d * 3) % 3]),
    "CU_YOU_MOUTH_OPEN": CL("you", eyes="wide", mouth="o", blink=False), "KT_SPEECH": lambda pen, t, d, gt, s: (kt(pen, t, "CAN I BE EXCUSED?", WHITE), t > 0.6 and red_x(pen, t - 0.6)),
    "SMASH_BLACK_TEXT": KT("DON'T.", RED), "DIAGRAM_HOST": lambda pen, t, d, gt, s: diagram(pen, t, d, gt, s, "host_cross" if s["sentence"] >= 150 and "crossed" in s["note"] else "host_search" if "search" in s["note"] else "host"),
    "CU_MOM_FROZEN": CL("mom", **FROZ), "ECU_MOM_LIPS": EC("mom", eyes="wide", mouth="wobble", blink=False),
    "TOP_CROWN_SLIDE": lambda pen, t, d, gt, s: diagram(pen, t, d, gt, s, "crown_slide"),
    "WIDE_TABLE_END": lambda pen, t, d, gt, s: P(z=(1.3, 1.45), fy=640, flicker=0.4)(pen, t, d, gt, s),
    "INS_GLASS_RIPPLE": glass_shot, "WAVEFORM_OVERLAY": waveform, "CANDLE_LEAN": lambda pen, t, d, gt, s: candle_shot(pen, t, d, gt, s, "lean"),
    "WALL_SHADOW_NOD": lambda pen, t, d, gt, s: wall_shot(pen, t, d, gt, s, "nod"), "WALL_SHADOW_JAW": lambda pen, t, d, gt, s: wall_shot(pen, t, d, gt, s, "jaw"),
    "POV_STAND": lambda pen, t, d, gt, s: P(z=(1.0, 0.85), fy=640 + 200 * smooth(t / d))(pen, t, d, gt, s),
    "HALL_WALK": lambda pen, t, d, gt, s: hallway(pen, t, d, gt, s, "walk"), "HALL_BATHROOM": lambda pen, t, d, gt, s: hallway(pen, t, d, gt, s, "bathroom"),
    "HALL_BEDROOM": lambda pen, t, d, gt, s: hallway(pen, t, d, gt, s, "bedroom"), "HALL_INFINITE": lambda pen, t, d, gt, s: hallway(pen, t, d, gt, s, "infinite"),
    "HALL_INF_FIGURES": lambda pen, t, d, gt, s: hallway(pen, t, d, gt, s, "figures"), "HALL_INF_FIGURE_CU": lambda pen, t, d, gt, s: hallway(pen, t, d, gt, s, "old_man"),
    "INS_BOWL": lambda pen, t, d, gt, s: bowl_shot(pen, t, d, gt, s, "still"), "INS_BOWL_SLIDE": lambda pen, t, d, gt, s: bowl_shot(pen, t, d, gt, s, "slide"),
    "TOP_TABLE": lambda pen, t, d, gt, s: top_table(pen, t, d, gt, s, bowl=True), "INS_BOWL_ARRIVES": lambda pen, t, d, gt, s: bowl_shot(pen, t, d, gt, s, "arrives"),
    "WIDE_FAMILY": P(z=(0.95, 1.0)), "INS_SERVING_SPOON": lambda pen, t, d, gt, s: bowl_shot(pen, t, d, gt, s, "spoon"),
    "INS_BOWL_STEAM": lambda pen, t, d, gt, s: bowl_shot(pen, t, d, gt, s, "steam"),
    "INS_SPOON_TAKE": lambda pen, t, d, gt, s: insert_plate(pen, t, d, gt, s, fork_mode="lift", extra=lambda p, t: p.oval(1250, 860, 50, 16, fill="#7a3a17")),
    "TOP_PLATE_EDGE": lambda pen, t, d, gt, s: insert_plate(pen, t, d, gt, s, top=True, extra=lambda p, t: p.oval(1150, 770, 60, 30, fill="#7a3a17")),
    "INS_CANDLE_FLARE": lambda pen, t, d, gt, s: candle_shot(pen, t, d, gt, s, "flare"),
    "INS_FORK_HOVER": lambda pen, t, d, gt, s: insert_plate(pen, t, d, gt, s, fork_mode="lift", extra=lambda p, t: p.oval(1250, 860, 50, 16, fill="#7a3a17")),
    "TOP_PLATE_AROUND": lambda pen, t, d, gt, s: insert_plate(pen, t, d, gt, s, top=True, fork_mode="circle", extra=lambda p, t: p.oval(1150, 770, 60, 30, fill="#7a3a17")),
    "POV_GLANCE": lambda pen, t, d, gt, s: rice_macro(pen, t, d, gt, s, 0, True), "INS_RICE_DARK": lambda pen, t, d, gt, s: rice_macro(pen, t, d, gt, s, 0, True),
    "ECU_RICE": lambda pen, t, d, gt, s: rice_macro(pen, t, d, gt, s, 0.5, True), "ECU_RICE_BREATH": lambda pen, t, d, gt, s: rice_macro(pen, t, d, gt, s, 1.0, True),
    "KT_RECEIPT": receipt, "CASEFILE_CARD": casefile, "POLAROID_TWINS": lambda pen, t, d, gt, s: casefile(pen, t, d, gt, s, "polaroid"),
    "POLAROID_PUSH": lambda pen, t, d, gt, s: casefile(pen, t, d, gt, s, "push"),
    "FLASHBACK_GRANDMA": lambda pen, t, d, gt, s: flashback(pen, t, d, gt, s, "grandma"), "FLASHBACK_TOLA_ALONE": lambda pen, t, d, gt, s: flashback(pen, t, d, gt, s, "tola_alone"),
    "TWINS_TABLE_WIDE": lambda pen, t, d, gt, s: twins_room(pen, t, d, gt, s, "table", True),
    "CU_TOLA_HUNGRY": lambda pen, t, d, gt, s: (setattr(pen, "mood", "dark"), close(pen, t, d, gt, s, "tola", {"mouth": "o", "eyes": "dot", "look": (0.5, 0.6)})),
    "INS_TOLA_SPOON": lambda pen, t, d, gt, s: (setattr(pen, "mood", "dark"), insert_plate(pen, t, d, gt, s, fork_mode="lift")),
    "ECU_TOLA_MOUTH": lambda pen, t, d, gt, s: (setattr(pen, "mood", "dark"), ecu_eyes(pen, t, d, gt, s, "tola", {"mouth": "talk", "eyes": "closed"}), t < 0.15 and white_flash(pen, t, d)),
    "TWINS_KITCHEN_MORNING": lambda pen, t, d, gt, s: twins_room(pen, t, d, gt, s, "laugh"), "TWINS_FAMILY_LAUGH": lambda pen, t, d, gt, s: twins_room(pen, t, d, gt, s, "laugh"),
    "TWINS_BATHROOM_DOOR": lambda pen, t, d, gt, s: (setattr(pen, "mood", "normal"), hallway(pen, t, d, gt, s, "bathroom"), pen.text("BANG BANG", 1465, 620, 70, ACID, a=0.5 + 0.5 * math.sin(t * 20))),
    "INS_TOLA_TOAST_FULL": lambda pen, t, d, gt, s: (setattr(pen, "mood", "normal"), insert_plate(pen, t, d, gt, s, food=0, extra=lambda p, t: p.rect(860, 800, 200, 60, fill="#c8964a", r=10))),
    "INS_LUNCHBOX_FULL": lambda pen, t, d, gt, s: (setattr(pen, "mood", "normal"), insert_plate(pen, t, d, gt, s, food=1.0)),
    "CU_TOLA_FLAT": lambda pen, t, d, gt, s: (setattr(pen, "mood", "normal"), close(pen, t, d, gt, s, "tola", {"mouth": "flat", "eyes": "dot", "blink": False})),
    "TWINS_TABLE_NIGHT": lambda pen, t, d, gt, s: twins_room(pen, t, d, gt, s, "night", True), "INS_EXTRA_PLATE": lambda pen, t, d, gt, s: twins_room(pen, t, d, gt, s, "night", True),
    "TWINS_TABLE_NIGHT_WIDE": lambda pen, t, d, gt, s: twins_room(pen, t, d, gt, s, "night_wide", True),
    "INS_TOLA_CUT": lambda pen, t, d, gt, s: (setattr(pen, "mood", "dark"), knife_cut(pen, t, d, gt, s, 2)), "INS_PIECES_SLIDE": lambda pen, t, d, gt, s: twins_room(pen, t, d, gt, s, "slide", True),
    "CU_TOLA_SIDE": lambda pen, t, d, gt, s: (setattr(pen, "mood", "dark"), close(pen, t, d, gt, s, "tola", {"mouth": "flat", "eyes": "dot", "look": (1, 0), "blink": False})),
    "CU_TOBI_ASK": lambda pen, t, d, gt, s: (setattr(pen, "mood", "dark"), close(pen, t, d, gt, s, "kid", {"mouth": "talk", "eyes": "dot", "look": (-0.6, 0)})),
    "CU_TOLA_DOWN": lambda pen, t, d, gt, s: (setattr(pen, "mood", "dark"), close(pen, t, d, gt, s, "tola", {"mouth": "flat", "eyes": "closed", "blink": False}, tilt=8)),
    "ECU_TOLA_LIPS": lambda pen, t, d, gt, s: (setattr(pen, "mood", "dark"), ecu_eyes(pen, t, d, gt, s, "tola", {"mouth": "talk", "eyes": "dot", "look": (0, 0.8)})),
    "TOLA_19_WIDE": lambda pen, t, d, gt, s: twins_room(pen, t, d, gt, s, "older", True), "INS_PLATE_SET_19": lambda pen, t, d, gt, s: twins_room(pen, t, d, gt, s, "older", True),
    "TIMELAPSE_WINDOW": lambda pen, t, d, gt, s: (pen.rect(0, 0, W, H, fill="#9fd0ff" if (t * 3) % 2 < 1 else "#0a0f1e", a=0.35), window(pen, 760, 260, 400, 460, t * 5, moon=(t * 3) % 2 >= 1)),
    "INS_PLATE_CLEAN": lambda pen, t, d, gt, s: (setattr(pen, "mood", "dark"), insert_plate(pen, t, d, gt, s, food=0), pen.glow(960, 860, 300, WHITE, 0.2)),
    "CU_YOU_EAR_TWITCH": CL("you", eyes="dot", mouth="flat", look=(1, 0), tremble=0.6),
    "INS_DRIPS_UNDER_CHAIR": lambda pen, t, d, gt, s: chair_insert(pen, t, d, gt, s, "drips"),
    "CU_YOU_MANNERS": lambda pen, t, d, gt, s: (close(pen, t, d, gt, s, "you", {"mouth": "o", "eyes": "dot"}), stamp(pen, "MANNERS: ON", t, ACID, W / 2, 250, -4, 80)),
    "FLASHBACK_MOM_TEACH": lambda pen, t, d, gt, s: flashback(pen, t, d, gt, s, "mom_teach"), "FLASHBACK_THANKYOU": lambda pen, t, d, gt, s: flashback(pen, t, d, gt, s, "thankyou"),
    "DIAGRAM_SEQUENCE": lambda pen, t, d, gt, s: diagram(pen, t, d, gt, s, "sequence"),
    "CU_YOU_MOUTH_TH": CL("you", eyes="wide", mouth="o", blink=False),
    "KT_MORPH": lambda pen, t, d, gt, s: kt(pen, t, "THANK—" if t < d * 0.45 else "PASS THE SALT", WHITE if t < d * 0.45 else ACID),
    "CU_YOU_COUGH": lambda pen, t, d, gt, s: (close(pen, t, d, gt, s, "you", {"mouth": "open", "eyes": "closed"}), [pen.circle(1180 + k * 50 + t * 300, 620 - k * 30, 10, fill="#d9682a", a=clamp(1 - t)) for k in range(4)]),
    "INS_SALT": salt_shot, "INS_SALT_PUSH": lambda pen, t, d, gt, s: salt_shot(pen, t, d, gt, s, True),
    "CU_SIS_FROZEN": CL("sis", **FROZ), "ECU_SIS_EYE_TEAR": EC("sis", **dict(FROZ, tears=0.8)), "CU_YOU": CL("you", eyes="wide", mouth="flat", blink=False),
    "ECU_DAD_BLINK": EC("dad", eyes="closed", mouth="flat"), "ECU_MOM_BLINK": EC("mom", eyes="closed", mouth="flat"), "ECU_SIS_BLINK": EC("sis", eyes="closed", mouth="flat"),
    "CU_YOU_RELIEF": lambda pen, t, d, gt, s: (setattr(pen, "mood", "normal"), close(pen, t, d, gt, s, "you", {"mouth": "wobble", "eyes": "dot", "tears": smooth(t / d) * 0.5}, bg=lamp_bg)),
    "TRIPTYCH_SYNC_BLINK": lambda pen, t, d, gt, s: triptych(pen, t, d, s, lambda k: dict(FROZ, eyes="closed" if (t % 0.8) < 0.14 else "wide"), snap=False),
    "WIDE_FAMILY_SYNC": lambda pen, t, d, gt, s: pov(pen, t, d, gt, s, faces=frozen_faces(0.3, blink_sync=(t % 0.8) < 0.14),
                                                     poses={k: {"tilt": 10 * math.sin(t * 2)} for k in FAM}),
    "ABOVE_CHAIR_EYELIDS": lambda pen, t, d, gt, s: chair_insert(pen, t, d, gt, s, "eyelids"),
    "METRONOME_EYES": lambda pen, t, d, gt, s: close(pen, t, d, gt, s, "mom", dict(FROZ, look=(math.sin(t * 4), 0), tremble=0)),
    "CU_YOU_STOP": CL("you", eyes="wide", mouth="flat", blink=False), "XRAY_MOUTH": xray_mouth,
    "ECU_THROAT": lambda pen, t, d, gt, s: (close(pen, t, d, gt, s, "you", dict(FROZ)), red_x(pen, t - 0.2, W / 2, 900, 120)),
    "ECU_LIPS_SEALED": EC("you", eyes="wide", mouth="flat", blink=False),
    "WIDE_TABLE_ALL_FROZEN": P(z=(0.95, 1.0)), "ECU_YOU_EYES": EC("you", eyes="wide", mouth="flat", blink=False, tears=0.4, red=0.4),
    "TOP_TABLE_FOUR": lambda pen, t, d, gt, s: top_table(pen, t, d, gt, s),
    "POV_FROM_CHAIR": lambda pen, t, d, gt, s: (P(z=(1.0, 1.05))(pen, t, d, gt, s), shimmer(pen, 300 + 1300 * (0.5 + 0.5 * math.sin(t * 2)), 500, t, 120, 0.4)),
    "WHITE_FLASH": lambda pen, t, d, gt, s: (memory(pen, t, d, gt, s, "toddler"), white_flash(pen, t, d)),
    "MEMORY_TODDLER_EAT": lambda pen, t, d, gt, s: memory(pen, t, d, gt, s, "toddler", "SUN 02 JUN 2016"),
    "MEMORY_KID_EAT": lambda pen, t, d, gt, s: memory(pen, t, d, gt, s, "kid", "SUN 17 MAR 2020"),
    "MEMORY_MOM_SERVE": lambda pen, t, d, gt, s: memory(pen, t, d, gt, s, "serve"), "MEMORY_DAD_DONE": lambda pen, t, d, gt, s: memory(pen, t, d, gt, s, "dad_done"),
    "MEMORY_DAD_SMILE": lambda pen, t, d, gt, s: (setattr(pen, "mood", "normal"), close(pen, t, d, gt, s, "dad", {"mouth": "talk", "eyes": "happy"}), vhs(pen, t)),
    "MEMORY_SIS_STEAL": lambda pen, t, d, gt, s: memory(pen, t, d, gt, s, "steal"), "MEMORY_YOU_ASK_MORE": lambda pen, t, d, gt, s: memory(pen, t, d, gt, s, "ask_more"),
    "FAMILY_PHOTO_WALL": lambda pen, t, d, gt, s: photo_wall(pen, t, d, gt, s), "PHOTO_FLIP": lambda pen, t, d, gt, s: photo_wall(pen, t, d, gt, s, True),
    "MEMORY_MONTAGE_GLANCE": lambda pen, t, d, gt, s: memory(pen, t, d, gt, s, "glance"),
    "MEMORY_VHS_PAUSE": lambda pen, t, d, gt, s: (memory(pen, 0.3, d, gt, s, "glance"), pause_bars(pen, 140, 250, 70)),
    "GRANDMA_RECIPE_CARD": recipe_card,
    "CU_MOM_MEMORY": lambda pen, t, d, gt, s: (setattr(pen, "mood", "normal"), close(pen, t, d, gt, s, "mom", {"mouth": "smile", "eyes": "dot"}), vhs(pen, t)),
    "MEMORY_BIRTHDAY": lambda pen, t, d, gt, s: memory(pen, t, d, gt, s, "birthday", "SAT 09 SEP 2023"),
    "MATCH_CUT_PRESENT": P(z=(1.0, 1.08)), "DIAGRAM_SIGHTLINES": lambda pen, t, d, gt, s: diagram(pen, t, d, gt, s, "sightlines"),
    "CU_MOM": CL("mom", **dict(FROZ, tears=0.3)), "ECU_MOM_EYES_RED": EC("mom", **dict(FROZ, red=1.0)),
    "ECU_MOM_TEAR": EC("mom", **dict(FROZ, red=0.8, tears=1.0)), "ECU_MOM_EYE_STRAIN": EC("mom", **dict(FROZ, red=1.0, tears=1.0, tremble=2.5)),
    "POV_MOM_TO_YOU": CL("you", eyes="wide", mouth="flat", blink=False, look=(0, -0.6)),
    "INS_PLATE_LAST_BITE": lambda pen, t, d, gt, s: insert_plate(pen, t, d, gt, s, food=0.12),
    "ECU_SIS_EYE_TWITCH": EC("sis", **dict(FROZ, tremble=3.0, red=0.6)),
    "MENU_CARD_7_REVEAL": lambda pen, t, d, gt, s: menu_card(pen, t, d, gt, s, n=7, reveal=True),
    "DIAGRAM_CROWN_TO_YOU": lambda pen, t, d, gt, s: diagram(pen, t, d, gt, s, "crown_you"),
    "CU_YOU_LIT": lambda pen, t, d, gt, s: close(pen, t, d, gt, s, "you", {"mouth": "flat", "eyes": "dot", "blink": False},
                                                 bg=lambda p, t: pendant_lamp(p, 960, 40, t, on=smooth(t / 0.6), cone_to=1000, spread=760)),
    "MEMORY_FLASHES": lambda pen, t, d, gt, s: memory(pen, t, d, gt, s, ["toddler", "kid", "ask_more", "birthday"][int(t * 5) % 4]),
    "INS_LAST_BITE": lambda pen, t, d, gt, s: insert_plate(pen, t, d, gt, s, food=0.05, fork_mode="lift"),
    "CU_YOU_CHEW_SLOW": lambda pen, t, d, gt, s: close(pen, t * 0.4, d, gt, s, "you", {"mouth": "talk", "eyes": "dot", "blink": False}),
    "INS_FORK_ACROSS": lambda pen, t, d, gt, s: (insert_plate(pen, t, d, gt, s, food=0, fork_mode="across"), t < 0.8 and t > 0.55 and pen.text("CLINK", 960, 500, 80, ACID)),
    "TOP_PLATE_FORK": lambda pen, t, d, gt, s: insert_plate(pen, t, d, gt, s, food=0, top=True, extra=lambda p, t: fork(p, 1100, 860, -60, 2.0)),
    "POV_CHAIR_PERIPHERAL": lambda pen, t, d, gt, s: (chair_insert(pen, t, d, gt, s, "empty"), pen.rect(0, 0, W * 0.55, H, fill=BG, a=0.6)),
    "CU_YOU_SPEAK": CL("you", eyes="dot", mouth="talk", blink=False),
    "ECU_YOU_EYES_DOWN": EC("you", eyes="wide", mouth="flat", blink=False, look=(0, 1)), "ECU_LIPS_PRESSED": EC("you", eyes="closed", mouth="flat", blink=False),
    "WIDE_TABLE_STILL": P(z=(1.0, 1.01), flicker=0.0),
    "INS_CHAIR_SLIDE_BACK": lambda pen, t, d, gt, s: (chair_insert(pen, t, d, gt, s, "legs"), t < 0.5 and pen.text("SCRRRK", 1300, 520, 80, ACID)),
    "HALL_FOOTPRINTS": lambda pen, t, d, gt, s: hallway(pen, t, d, gt, s, "footprints"),
    "FRONT_DOOR_OPEN": lambda pen, t, d, gt, s: front_door(pen, t, d, gt, s, True), "FRONT_DOOR_CLOSE": lambda pen, t, d, gt, s: front_door(pen, t, d, gt, s, False),
    "ECU_MOM_BLINK_REAL": lambda pen, t, d, gt, s: (setattr(pen, "mood", "normal"), ecu_eyes(pen, t, d, gt, s, "mom", {"eyes": "closed" if 0.2 < t < 0.4 else "dot", "mouth": "flat", "blink": False, "tears": 0.6})),
    "ECU_DAD_BLINK_REAL": lambda pen, t, d, gt, s: (setattr(pen, "mood", "normal"), ecu_eyes(pen, t, d, gt, s, "dad", {"eyes": "closed" if 0.1 < t < 0.3 else "dot", "mouth": "flat", "blink": False})),
    "ECU_SIS_BLINK_REAL": lambda pen, t, d, gt, s: (setattr(pen, "mood", "normal"), ecu_eyes(pen, t, d, gt, s, "sis", {"eyes": "closed" if 0.3 < t < 0.45 else "dot", "mouth": "flat", "blink": False})),
    "WIDE_TABLE_UNFREEZE": family_unfreeze, "CU_FAMILY_GASP": family_unfreeze,
    "CU_MOM_CRY": lambda pen, t, d, gt, s: (setattr(pen, "mood", "normal"), close(pen, t, d, gt, s, "mom", {"mouth": "wobble", "eyes": "closed", "tears": 1.0}, bg=lamp_bg)),
    "CU_DAD_LAUGH": lambda pen, t, d, gt, s: (setattr(pen, "mood", "normal"), close(pen, t, d, gt, s, "dad", {"mouth": "grin", "eyes": "happy"}, bg=lamp_bg, tilt=8 * math.sin(t * 10))),
    "WIDE_FAMILY_HUG": lambda pen, t, d, gt, s: family_unfreeze(pen, t, d, gt, s, True),
    "TOP_TABLE_COUNT": lambda pen, t, d, gt, s: (setattr(pen, "mood", "normal"), top_table(pen, t, d, gt, s, labels=5 if "chairs" in s["note"] else 4, four=True)),
    "INS_MOM_SERVE_5": lambda pen, t, d, gt, s: (setattr(pen, "mood", "normal"), top_table(pen, t, d, gt, s, labels=5, four=True)),
    "WIDE_FAMILY_NORMAL": lambda pen, t, d, gt, s: normal_table(pen, t, d, gt, s), "CU_YOU_NOTICE": lambda pen, t, d, gt, s: normal_table(pen, t, d, gt, s, notice=True),
    "INS_FIFTH_PLATE": lambda pen, t, d, gt, s: normal_table(pen, t, d, gt, s, fifth=True),
    "WIDE_TABLE_PULLBACK": lambda pen, t, d, gt, s: (setattr(pen, "mood", "normal"), camera(pen, t, d, 1.0, 0.45, W / 2, 600, s),
                                                     S1.dining_front(pen, t, gt, normal_faces(t)), pen.pop()),
    "CHAIR_COUNT_KT": lambda pen, t, d, gt, s: (normal_table(pen, t, d, gt, s), [pen.text(str(i + 1), x, 640, 90, ACID if i < 4 else RED) for i, x in enumerate((560, 960, 1340, 760, 1700)) if t > i * 0.25],
                                               t > 1.5 and pen.rect(0, 0, W, H, fill=BG, a=clamp((t - 1.5) / 0.15))),
}

def fallback(pen, t, d, gt, shot):
    """Never leave a frame blank: infer from the set-up name."""
    n = shot["setup"]
    for k in ("MOM", "DAD", "SIS", "YOU", "TOLA", "TOBI"):
        if k in n:
            kind = {"TOBI": "kid"}.get(k, k.lower())
            return close(pen, t, d, gt, shot, kind, dict(FROZ) if pen.mood == "frozen" else {"mouth": "smile"}, bg=lamp_bg)
    return pov(pen, t, d, gt, shot)

def draw(pen, t, dur, gt, shot):
    set_mood(pen, shot["sentence"])
    fn = S1.SHOTS.get(shot["setup"]) if shot["start"] < 31 else None
    if shot["setup"] in ("EXT_HOUSE_NIGHT", "INS_RICE_POT", "CU_DAD_TALK", "KT_TEXT", "ECU_MOM_EYES", "INS_FORK_HAND", "INS_EMPTY_CHAIR") and not fn:
        fn = S1.SHOTS[shot["setup"]]
    if fn: return fn(pen, t, dur, gt, shot), True
    fn = MAP.get(shot["setup"])
    if fn: return fn(pen, t, dur, gt, shot), True
    fallback(pen, t, dur, gt, shot); return None, False
