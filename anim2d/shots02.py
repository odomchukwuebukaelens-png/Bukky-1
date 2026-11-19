"""Video 02 (dog refuses to come inside) - opening shots. Every shot is a distinct composition."""
import math
from engine import *
from scenes import *
from shots01 import camera

CLOCK = 23 * 3600 + 48 * 60

def DOG_EYES_DARK(pen, t, d, gt, s):
    """Pure dark yard; two eyes catching the porch light. They don't blink."""
    camera(pen, t, d, 1.0, 1.12, W / 2, H / 2, s)
    pen.rect(0, 0, W, H, fill="#03050a")
    grass(pen, 760, t, "#0b130c", 60)
    fireflies(pen, t, 8, (0, 300, W, 900))
    for sx in (-1, 1):
        x, y = W / 2 + sx * 90, 470
        pen.glow(x, y, 120, "#d8ff8a", 0.45); pen.oval(x, y, 34, 26, fill="#e9ffb0"); pen.oval(x, y, 9, 22, fill="#0a0a0a")
    pen.pop()

def YARD_WIDE_DOOR_LIGHT(pen, t, d, gt, s):
    camera(pen, t, d, 1.0, 1.05, 960, 600, s)
    backyard(pen, t, door_open=1.0)
    dog(pen, 1180, 830, 0.55, t, facing=-1, tail=0, ears=1, glow=0.6)
    pen.pop()

def CU_YOU_DOOR(pen, t, d, gt, s):
    camera(pen, t, d, 1.0, 1.06, W / 2, 560, s)
    pen.rect(0, 0, W, H, fill="#0b0d14")
    pen.rect(560, 60, 800, 1040, fill="#ffcf73")  # doorway glow behind you
    pen.glow(W / 2, 500, 700, AMBER, 0.25)
    pen.rect(540, 40, 20, 1060, fill="#c9c2b0"); pen.rect(1360, 40, 20, 1060, fill="#c9c2b0")
    m = "open" if t < d * 0.45 else "flat"
    head_close(pen, "you", W / 2, 470, 210, {"mouth": m, "eyes": "dot", "look": (0, 0.3)}, t, seed=3)
    for k in range(3):
        a = t * 3 + k * 2; pen.oval(W / 2 + 380 + math.cos(a) * 60, 220 + math.sin(a) * 40, 6, 4, fill="#e8e1cc")
    pen.pop()

def INS_DOOR_HANDLE(pen, t, d, gt, s):
    camera(pen, t, d, 1.0, 1.08, 1100, 560, s)
    pen.rect(0, 0, W, H, fill="#1a1c24")
    pen.rect(620, 0, 900, H, fill="#3b3f52", stroke="#c9c2b0", w=6)
    pen.rect(760, 80, 620, 440, fill="#0b1020", stroke="#c9c2b0", w=6)  # glass panel: the dark yard
    for k in range(12): pen.circle(780 + (k * 97) % 600, 110 + (k * 61) % 380, 2, fill=WHITE, a=0.5)
    for k in range(3): pen.oval(900 + 200 * math.sin(t * 2 + k), 200 + 80 * math.cos(t * 3 + k), 8, 5, fill="#e8e1cc")  # moths on glass
    pen.rect(1240, 640, 160, 50, fill=AMBER, r=20); pen.circle(1250, 665, 34, fill=AMBER)  # brass handle
    reach = math.sin(math.pi * clamp(t / d)) * 260
    hx, hy = 1700 - reach, 700
    pen.ln(hx + 60, hy + 10, W + 100, hy + 120, pen.line, 120); pen.ln(hx + 60, hy + 10, W + 100, hy + 120, "#cfe0bf", 112)
    pen.circle(hx, hy, 58, fill=pen.white, stroke=pen.line, w=4)
    for k in range(4): pen.oval(hx - 50, hy - 30 + k * 20, 26, 12, fill=pen.white, stroke=pen.line, w=3)  # fingers
    pen.pop()

def PORCH_STEPS_POV(pen, t, d, gt, s):
    """Looking down at your sneakers on the threshold; steps drop into dark grass."""
    camera(pen, t, d, 1.0, 1.05, W / 2, 700, s)
    pen.rect(0, 0, W, H, fill="#070a0f")
    grass(pen, 0, t, "#122014", 120, 40)
    pen.rect(0, 0, W, 420, fill="#070a0f", a=0.6)
    for k in range(3): pen.rect(560 - k * 40, 300 + k * 150, 800 + k * 80, 120, fill="#3e3024", stroke="#6c5a46", w=4)
    pen.poly([(600, 300), (1320, 300), (1700, H), (220, H)], fill=AMBER, a=0.16, blur=10)
    pen.rect(380, 760, 1160, 340, fill="#4a3a2b", stroke="#6c5a46", w=4)  # threshold
    edge = 6 * math.sin(t * 9)
    for sx in (-1, 1):
        x = W / 2 + sx * 170
        pen.oval(x, 930 + edge * (sx > 0), 120, 70, fill="#e9e9e4", stroke=GREY, w=4); pen.oval(x, 975, 120, 22, fill="#5a5a5a")
        for k in range(3): pen.ln(x - 50, 900 + k * 20, x + 50, 900 + k * 20, GREY, 3)
    pen.pop()

def KT_DONT_GO(pen, t, d, gt, s):
    pen.rect(0, 0, W, H, fill="#03050a"); grass(pen, 860, t, "#0b130c", 50); fireflies(pen, t, 6, (0, 700, W, 1000))
    kinetic(pen, "DON'T GO OUT.", t, size=190)

def SQUIRREL_DAY(pen, t, d, gt, s):
    camera(pen, t, d, 1.0, 1.04, 1150, 640, s)
    backyard(pen, t, day=True, house=False)
    run = (t * 2.2) % 1
    dog(pen, 900 + 500 * run, 860, 0.7, t, facing=1, tail=1.6, step=1.4, mouth="growl")
    squirrel(pen, 1150 + 500 * run, 840, 1.2, t, facing=1)
    for k in range(3): pen.ln(700 + 500 * run - k * 60, 800 + k * 10, 760 + 500 * run - k * 60, 800 + k * 10, WHITE, 4, 0.7)
    pen.pop()

def SQUIRREL_TREE(pen, t, d, gt, s):
    camera(pen, t, d, 1.15, 1.2, 1500, 520, s)
    backyard(pen, t, day=True, house=False)
    squirrel(pen, 1610, 470 + 4 * math.sin(t * 8), 1.1, t, facing=-1)
    jump = abs(math.sin(t * 7)) * 70
    dog(pen, 1420, 860 - jump, 0.8, t, facing=1, tail=2.0, mouth="growl")
    if (t % 0.5) < 0.3: pen.text("WOOF!", 1220, 560, 90, ACID)
    pen.pop()

def EYES_GONE(pen, t, d, gt, s):
    """The eyes in the dark yard switch off - leaving only fireflies (pattern break before the story)."""
    pen.rect(0, 0, W, H, fill="#03050a"); grass(pen, 760, t, "#0b130c", 60)
    if t < 0.35:
        for sx in (-1, 1):
            x = W / 2 + sx * 90; pen.glow(x, 470, 120, "#d8ff8a", 0.45 * (1 - t / 0.35)); pen.oval(x, 470, 34, 26 * (1 - t / 0.35), fill="#e9ffb0")
    fireflies(pen, t, 5, (0, 300, W, 900))

def CLOCK_CARD(pen, t, d, gt, s):
    pen.rect(0, 0, W, H, fill="#05070c")
    wall_clock(pen, W / 2, H / 2 - 70, 170, CLOCK + t)
    pen.text("11:48 PM", W / 2, H / 2 + 230, 72, ACID, "JetBrainsMono-Regular.ttf")

def KITCHEN_NIGHT_WIDE(pen, t, d, gt, s):
    camera(pen, t, d, 1.0, 1.04, 1100, 560, s)
    kitchen(pen, t, CLOCK + gt)
    x = lerp(900, 1400, smooth(t / d))
    figure(pen, "you", x, 960, 1.15, {"face": {"mouth": "flat", "look": (1, 0)}, "bob": abs(math.sin(t * 9)) * 8}, t, seed=3)
    pen.pop()

def DOOR_OPENS_OUT(pen, t, d, gt, s):
    """Tight on the back door from outside: it swings open, warm light floods out, moths scatter."""
    camera(pen, t, d, 1.0, 1.06, W / 2, 540, s)
    pen.rect(0, 0, W, H, fill="#1b1d26")
    for y in range(0, H, 34): pen.ln(0, y, W, y, "#232634", 4)  # siding
    op = ease_out(t / 0.7)
    pen.rect(620, 90, 680, 900, fill="#ffcf73")  # light inside
    pen.glow(960, 540, 900 * op + 1, AMBER, 0.35 * op)
    pen.poly([(620, 90), (620 + 680 * (1 - op), 90 + 40 * op), (620 + 680 * (1 - op), 990 - 40 * op), (620, 990)], fill="#3b3f52", stroke="#c9c2b0", w=6)
    if op < 0.9: pen.circle(620 + 680 * (1 - op) - 60, 560, 26, fill=AMBER)
    pen.rect(600, 70, 720, 22, fill="#c9c2b0"); pen.rect(598, 70, 22, 940, fill="#c9c2b0"); pen.rect(1300, 70, 22, 940, fill="#c9c2b0")
    pen.rect(1420, 220, 70, 96, fill="#ffe7a0", stroke="#c9c2b0", w=4); pen.glow(1455, 268, 220, "#ffe7a0", 0.5)
    for k in range(7):  # moths scatter as the door opens
        a = t * (3 + k * 0.6) + k; rr = 60 + k * 14 + 220 * op
        pen.oval(1455 + math.cos(a) * rr, 268 + math.sin(a * 1.2) * rr * 0.6, 7, 4, fill="#e8e1cc")
    pen.rect(560, 990, 800, 90, fill="#4a3a2b", stroke="#6c5a46", w=4)
    pen.pop()

def CU_YOU_CALL(pen, t, d, gt, s):
    camera(pen, t, d, 1.0, 1.05, W / 2, 560, s)
    backyard(pen, t, door_open=1.0)
    pen.rect(0, 0, W, H, fill="#000000", a=0.35)
    head_close(pen, "you", 700, 480, 200, {"mouth": "open", "eyes": "dot", "look": (1, 0)}, t, seed=3, tilt=-4)
    k = ease_out(t / 0.3)
    pen.rect(980, 230, 520 * k, 160, fill=WHITE, r=40)
    pen.poly([(1000, 360), (960, 430), (1060, 380)], fill=WHITE)
    if k > 0.8: pen.text("BRUNO!", 1240, 345, 100, "#111111")
    pen.pop()

def YARD_FROM_PORCH(pen, t, d, gt, s):
    """Your view out through the door frame, past the porch rail: the dog alone on the lawn."""
    camera(pen, t, d, 1.0, 1.05, W / 2, 560, s)
    sky(pen, t); moon(pen, 1300, 170, t, 48); clouds(pen, t)
    treeline(pen, t, 600, "#0a0f14", 21, 160); fence(pen, 690, t)
    grass(pen, 650, t)
    pen.poly([(700, 650), (1220, 650), (1700, H), (220, H)], fill=AMBER, a=0.12, blur=12)  # door light on the lawn
    dog(pen, 1000, 800, 0.62, t, facing=-1, tail=0, ears=1, glow=0.7)
    fireflies(pen, t, 12, (200, 380, 1700, 800))
    pen.rect(0, 860, W, 34, fill="#4a3a2b", stroke="#6c5a46", w=3)  # porch rail
    for x in range(40, W, 110): pen.rect(x, 894, 26, 200, fill="#4a3a2b", stroke="#6c5a46", w=3)
    pen.rect(0, 0, 230, H, fill="#2a2418"); pen.rect(W - 230, 0, 230, H, fill="#2a2418")  # door frame (inside)
    pen.rect(210, 0, 22, H, fill="#c9c2b0"); pen.rect(W - 232, 0, 22, H, fill="#c9c2b0")
    pen.rect(0, 0, W, 60, fill="#2a2418"); pen.rect(0, 58, W, 16, fill="#c9c2b0")
    pen.pop()

def DOG_SIDE_MED(pen, t, d, gt, s):
    camera(pen, t, d, 1.0, 1.05, W / 2, 620, s)
    sky(pen, t); moon(pen, 1580, 200, t, 70); clouds(pen, t)
    treeline(pen, t, 700, "#0a0f14", 5, 160); fence(pen, 770, t)
    grass(pen, 760, t)
    dog(pen, 900, 960, 1.7, t, facing=1, tail=0, ears=1, eyes="dot")
    fireflies(pen, t, 10, (0, 400, W, 900))
    pen.pop()

def DOG_HEAD_TURN(pen, t, d, gt, s):
    camera(pen, t, d, 1.0, 1.05, W / 2, 560, s)
    sky(pen, t); treeline(pen, t, 760, "#0a0f14", 6, 200)
    ht = smooth(t / 0.6)
    pen.push(s=2.6, ox=900, oy=1100)
    dog(pen, 900, 1100, 1.0, t, facing=1, head_turn=ht, tail=0, ears=1)
    pen.pop()
    pen.pop()

def OTS_DOG_TO_HOUSE(pen, t, d, gt, s):
    """Behind the dog, looking back at the house: you, tiny, in the lit doorway."""
    camera(pen, t, d, 1.0, 1.04, 700, 600, s)
    backyard(pen, t, door_open=1.0)
    figure(pen, "you", 555, 820, 0.62, {"face": {"mouth": "flat"}}, t, seed=3)
    pen.push(s=2.2, ox=1300, oy=1180)
    dog(pen, 1300, 1180, 1.0, t, facing=-1, tail=0, ears=1)
    pen.pop()
    pen.pop()

def DOORWAY_BEHIND_YOU(pen, t, d, gt, s):
    """Closer on the doorway: behind you, the hallway is dark - and one shape is darker."""
    camera(pen, t, d, 1.0, 1.1, W / 2, 520, s)
    pen.rect(0, 0, W, H, fill="#0b0d14")
    pen.rect(560, 60, 800, 1040, fill="#2a2418")
    pen.poly([(700, 60), (1220, 60), (1080, 700), (840, 700)], fill="#0c0b09")  # hallway receding into dark
    k = 0.10 + 0.05 * math.sin(t * 2)
    pen.oval(960, 360, 70, 90, fill="#000000", a=0.6 + k)  # the shape in the hall (barely there)
    pen.rect(890, 440, 140, 260, fill="#000000", a=0.55 + k)
    pen.rect(540, 40, 20, 1060, fill="#c9c2b0"); pen.rect(1360, 40, 20, 1060, fill="#c9c2b0")
    figure(pen, "you", 760, 1120, 1.5, {"face": {"mouth": "flat", "look": (0.8, 0)}}, t, seed=3)
    pen.pop()

def DOG_BACKS_AWAY(pen, t, d, gt, s):
    camera(pen, t, d, 1.0, 1.06, W / 2, 700, s)
    sky(pen, t); moon(pen, 300, 220, t, 60); treeline(pen, t, 720, "#0a0f14", 8, 160); fence(pen, 790, t)
    grass(pen, 780, t)
    x = lerp(1100, 760, smooth(t / d))
    dog(pen, x, 990, 1.6, t, facing=1, tail=-1, ears=0, crouch=0.6, step=-0.8, mouth="growl")
    if (t % 1.0) < 0.6: pen.text("grrrr", x + 520, 560, 70, GREY, a=0.8)
    fireflies(pen, t, 8, (0, 400, W, 900))
    pen.pop()

SHOTS = {k: v for k, v in globals().items() if k.isupper() and callable(v) and k != "CLOCK"}

def HALL_PUSH(pen, t, d, gt, s):
    """Into the house: push down the hallway - photos, coat rack, runner rug - toward the dark end."""
    camera(pen, t, d, 1.0, 1.25, W / 2, 500, s)
    pen.rect(0, 0, W, H, fill="#16130e")
    vx, vy = W / 2, 470
    pen.poly([(0, 0), (vx - 140, vy - 170), (vx - 140, vy + 170), (0, H)], fill="#221d15")
    pen.poly([(W, 0), (vx + 140, vy - 170), (vx + 140, vy + 170), (W, H)], fill="#1d1912")
    pen.poly([(0, H), (vx - 140, vy + 170), (vx + 140, vy + 170), (W, H)], fill="#2a2219")
    pen.poly([(560, H), (vx - 60, vy + 170), (vx + 60, vy + 170), (1360, H)], fill="#6b2a24")  # runner rug
    pen.rect(vx - 140, vy - 170, 280, 340, fill="#050403")  # the dark end
    pen.oval(vx, vy - 40, 34, 44, fill="#000000"); pen.rect(vx - 40, vy, 80, 150, fill="#000000")  # something standing there
    for k, (x, y, w_, h_) in enumerate(((170, 260, 170, 140), (430, 330, 110, 90), (1580, 270, 170, 140), (1380, 340, 100, 80))):
        pen.rect(x, y, w_, h_, fill="#d9cfb8", stroke="#8a6a3a", w=6)
        pen.circle(x + w_ * 0.35, y + h_ * 0.5, h_ * 0.16, fill="#7a7468"); pen.circle(x + w_ * 0.65, y + h_ * 0.5, h_ * 0.16, fill="#7a7468")
    pen.ln(1700, 420, 1700, 900, "#5a4630", 10)  # coat rack
    for k in range(3): pen.oval(1700 + (k - 1) * 40, 470 + k * 10, 50, 120, fill="#3b4a6a" if k == 1 else "#4a3a2b")
    pen.glow(vx, 120, 300, AMBER, 0.12 * (0.6 + 0.4 * math.sin(t * 17) * math.sin(t * 5)))  # failing hall light
    pen.pop()

SHOTS = {k: v for k, v in globals().items() if k.isupper() and callable(v) and k != "CLOCK"}
