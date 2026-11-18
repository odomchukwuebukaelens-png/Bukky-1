"""Video 01 shots, drawn in code. Each SHOT function draws one full frame.
Signature: fn(pen, t, dur, gt, shot) - t = seconds into this shot, gt = global time (for the HUD timecode)."""
import math
from engine import *

CLOCK0 = 19 * 3600 + 42 * 60  # Sunday 7:42 PM on the wall clock

def camera(pen, t, dur, z0=1.0, z1=1.06, fx=W / 2, fy=H / 2, shot=None, rot=0.0):
    """Push/pull camera; micro-change pieces start already offset so every 2s the frame visibly changes."""
    m = (shot or {}).get("motion", "")
    if "micro-change" in m:
        if "punch-in" in m: z0, z1 = z1 * 1.12, z1 * 1.14
        elif "snap-zoom out" in m: z0, z1 = z0 * 0.9, z0 * 0.92
        elif "angle shift" in m: fx += 140; z0 *= 1.05; z1 *= 1.07
        elif "dutch" in m: rot = 4
        elif "reverse drift" in m: z0, z1 = z1, z0
        elif "parallax" in m: fx -= 120
        else: z0, z1 = z0 * 1.08, z1 * 1.08
    z = lerp(z0, z1, smooth(t / max(dur, 0.01)))
    pen.push(s=z, ox=fx, oy=fy, rot=rot)

# ---------------- sets ----------------
def dining_back(pen, t, gt, lamp_on=1.0, flicker=0.0):
    window(pen, 150, 170, 270, 300, t)
    wall_clock(pen, 1720, 230, 72, CLOCK0 + gt)
    frame_pic(pen, 1420, 190)
    pendant_lamp(pen, 960, 250, t, on=lamp_on, flicker=flicker, cone_to=820, spread=430)

FAM = {"dad": 560, "mom": 960, "sis": 1340}

def dining_front(pen, t, gt, faces, mood_t=0.0, poses=None, empty_pull=0.0, lamp_on=1.0, flicker=0.0):
    """POV across the table: dad, mom, sister seated behind it; empty chair at the right end."""
    poses = poses or {}
    dining_back(pen, t, gt, lamp_on, flicker)
    chair_back(pen, 1700 + empty_pull * 40, 860, 1.35, angle=6 + empty_pull * 6)
    for i, (k, x) in enumerate(FAM.items()):
        pose = dict(poses.get(k, {})); pose.setdefault("face", faces.get(k, {}))
        figure(pen, k, x, 900, 1.55 if k != "sis" else 1.75, pose, t, seed=i + 1, seated=True)
    table_front(pen, 960, 880, 1840)
    plate(pen, 560, 975, 0.9); plate(pen, 1340, 975, 0.9); plate(pen, 1680, 960, 0.8, food=False)
    pot(pen, 960, 965, 0.9, lid=1.0)

def frozen_faces(red=0.0, tears=0.0):
    f = lambda: {"eyes": "wide", "mouth": "flat", "blink": False, "tremble": 1.0, "red": red, "tears": tears}
    d = f(); d["mouth"] = "open"
    return {"dad": d, "mom": f(), "sis": f()}

# ---------------- shot functions ----------------
def ECU_MOM_EYES(pen, t, dur, gt, shot):
    pen.mood = "frozen"
    camera(pen, t, dur, 1.0, 1.18, W / 2, 470, shot)
    head_close(pen, "mom", W / 2, 520, 330, {"eyes": "wide", "mouth": "flat", "blink": False, "tremble": 1.4,
                                             "tears": smooth(t / dur) * 0.5, "red": 0.5}, t, seed=2)
    pen.pop()

def WIDE_TABLE_POV(pen, t, dur, gt, shot):
    pen.mood = "frozen"
    camera(pen, t, dur, 1.0, 1.07, W / 2, 600, shot)
    dining_front(pen, t, gt, frozen_faces(0.3), poses={"mom": {"armR": (95, -40)}}, flicker=0.25)
    steam(pen, 960, 880, t, 3, 220)
    pen.pop()

def _hand(pen, x, y, s=1.0):
    pen.oval(x, y, 60 * s, 46 * s, fill=pen.white, stroke=pen.line, w=4)
    for k in range(3): pen.ln(x - 40 * s + k * 30 * s, y - 30 * s, x - 40 * s + k * 30 * s, y - 50 * s, pen.line, 3)

def INS_FORK_HAND(pen, t, dur, gt, shot):
    pen.mood = "frozen"
    camera(pen, t, dur, 1.0, 1.08, W / 2, 620, shot)
    pendant_lamp(pen, 700, 90, t, cone_to=760, spread=520, flicker=0.2)
    table_front(pen, 960, 760, 2400)
    plate(pen, 900, 880, 2.6)
    tremor = wobble(t, 3, 7, 6)
    hx, hy = 1150 + tremor, 600 + wobble(t, 9, 5, 5) - 50 * smooth(t / 0.5)
    pen.ln(hx + 60, hy + 20, W + 80, hy + 330, pen.line, 118); pen.ln(hx + 60, hy + 20, W + 80, hy + 330, "#cfe0bf", 110)  # hoodie sleeve
    fork(pen, hx - 30, hy + 30, ang=-25, s=2.2)
    pen.circle(hx, hy, 58, fill=pen.white, stroke=pen.line, w=4)  # fist
    pen.oval(hx - 45, hy - 10, 22, 34, fill=pen.white, stroke=pen.line, w=4)  # thumb
    if t < 0.9: kinetic(pen, "DON'T", t, size=180)
    pen.pop()

def CU_YOU_MOUTH(pen, t, dur, gt, shot):
    pen.mood = "frozen"
    camera(pen, t, dur, 1.0, 1.08, W / 2, 560, shot)
    m = "open" if 0.25 < t < 0.9 else "flat"
    head_close(pen, "you", W / 2, 470, 270, {"eyes": "wide", "mouth": m, "look": (math.sin(t * 7) * 0.6, 0), "tremble": 0.6}, t, seed=3)
    pen.pop()

def INS_EMPTY_CHAIR(pen, t, dur, gt, shot):
    pen.mood = "frozen"
    camera(pen, t, dur, 1.0, 1.12, 1500, 640, shot)
    dining_back(pen, t, gt, 0.8, 0.5)
    pull = smooth(t / dur)
    chair_back(pen, 1450 + pull * 30, 780, 1.6, angle=6 + pull * 4, color="#8b8c90")
    table_front(pen, 700, 760, 1500)
    plate(pen, 1300, 880, 1.4, food=False)
    vignette(pen, 0.5 + 0.25 * abs(math.sin(t * 3)))
    pen.pop()

def KT_TEXT(pen, t, dur, gt, shot):
    note = shot.get("note", ""); a, b = note.find("'"), note.rfind("'")
    kinetic(pen, note[a + 1:b] if b > a >= 0 else "DON'T.", t)

def LIVING_TV_DAD(pen, t, dur, gt, shot):
    pen.mood = "normal"
    camera(pen, t, dur, 1.0, 1.06, 900, 620, shot)
    floor(pen, 900)
    tv(pen, 1380, 380, 360, 230, t)
    pen.ln(1560, 610, 1560, 900, GREY, 6)
    sofa(pen, 300, 900)
    figure(pen, "dad", 610, 760, 1.05, {"face": {"eyes": "closed", "mouth": "open", "blink": False}, "tilt": -18 + 3 * math.sin(t * 1.3),
                                        "armL": (35, 25), "armR": (40, 40), "breathe": 3}, t, seed=1, seated=True)
    pen.rect(300, 740, 620, 160, fill="#2b2c31", stroke=GREY, w=4, r=26)  # sofa seat in front of his legs
    zs = (t * 0.8) % 1.0
    pen.text("z", 760 + zs * 60, 470 - zs * 120, 60 + 30 * zs, WHITE, a=1 - zs)
    pen.poly([(1380, 420), (1380, 580), (800, 760), (800, 300)], fill=TV, a=0.08 + 0.05 * math.sin(t * 9), blur=30)
    pen.pop()

def ECU_DAD_TV_REFLECT(pen, t, dur, gt, shot):
    pen.mood = "normal"
    camera(pen, t, dur, 1.0, 1.1, W / 2, 500, shot)
    head_close(pen, "dad", W / 2, 520, 320, {"eyes": "wide", "mouth": "open", "blink": False, "look": (0.3, -0.1)}, t, seed=1)
    k = 0.5 + 0.5 * abs(math.sin(t * 6.1))
    for sx in (-1, 1):  # TV glow reflected in each eye
        pen.rect(W / 2 + sx * 115 - 14, 470, 26, 18, fill=TV, a=0.8 * k, r=3)
    pen.rect(0, 0, W, H, fill=TV, a=0.06 * k)
    pen.pop()

def SIS_STARE_CONTEST(pen, t, dur, gt, shot):
    pen.mood = "normal"
    camera(pen, t, dur, 1.0, 1.05, W / 2, H / 2, shot)
    twitch = 0.3 if (t % 1.3) < 0.08 else 0
    head_close(pen, "sis", W * 0.27, 560, 230, {"eyes": "wide", "mouth": "flat", "blink": False, "tremble": twitch * 6}, t, seed=4)
    head_close(pen, "you", W * 0.73, 560, 230, {"eyes": "wide", "mouth": "flat", "blink": False}, t, seed=3)
    pen.ln(W / 2, 0, W / 2, H, ACID, 8)
    pen.pop()

def SIS_LAUGH(pen, t, dur, gt, shot):
    pen.mood = "normal"
    camera(pen, t, dur, 1.0, 1.06, W / 2, 600, shot)
    floor(pen, 930)
    bounce = abs(math.sin(t * 11)) * 18
    figure(pen, "sis", W / 2, 930, 2.6, {"face": {"eyes": "happy", "mouth": "grin"}, "bob": bounce,
                                         "armR": (100 + 10 * math.sin(t * 11), 30), "armL": (25, 60), "tilt": 6 * math.sin(t * 5)}, t, seed=4)
    for k in range(3):
        ph = (t * 1.4 + k / 3) % 1
        pen.text("HA", W / 2 + 330 + k * 40, 380 - ph * 160, 70, ACID, a=1 - ph)
    pen.pop()

def SMASH_BLACK(pen, t, dur, gt, shot):
    if t < 0.25: return
    pen.text("SUNDAY.", W / 2, H / 2 + 10, 170, WHITE)
    mm = 42 if t < 0.9 else 43
    pen.text(f"7:{mm} PM", W / 2, H / 2 + 130, 64, ACID, "JetBrainsMono-Regular.ttf")

def EXT_HOUSE_NIGHT(pen, t, dur, gt, shot):
    pen.mood = "normal"
    camera(pen, t, dur, 1.0, 1.25, 815, 700, shot)
    pen.glow(1380, 260, 160, "#fff2c0", 0.25); pen.circle(1380, 260, 55, fill="#f4ecd0")
    for k in range(18):
        x = (k * 397) % W; y = (k * 211) % 420 + 40
        pen.circle(x, y, 2.2, fill=WHITE, a=0.4 + 0.4 * math.sin(t * 3 + k))
    floor(pen, 900)
    house(pen, 960, 900, t)
    for k in range(5):  # crickets: tiny grass blades moving
        x = 200 + k * 380
        pen.ln(x, 900, x + 8 * math.sin(t * 4 + k), 870, DIM, 4)
    pen.pop()

def INT_DINING_WIDE(pen, t, dur, gt, shot):
    """Side-on wide of the dining room: dad and sister sit; mom walks in carrying the pot."""
    pen.mood = "normal"
    camera(pen, t, dur, 1.0, 1.04, W / 2, 600, shot)
    floor(pen, 900)
    window(pen, 160, 230, 230, 260, t); wall_clock(pen, 1660, 220, 62, CLOCK0 + gt); frame_pic(pen, 760, 200, 110, 80)
    pendant_lamp(pen, 960, 260, t, cone_to=900, spread=330)
    door(pen, 1600, 580, 150, 320, open_=0.0)
    for x in (650, 1270): chair_side(pen, x, 900, 1.0, 1 if x < 960 else -1)
    figure(pen, "dad", 760, 820, 1.0, {"face": {"mouth": "talk", "look": (0.8, 0)}, "armR": (60, 50)}, t, seed=1, seated=True)
    figure(pen, "sis", 1160, 830, 1.0, {"face": {"mouth": "smile", "look": (-0.8, 0)}}, t, seed=4, seated=True)
    pen.rect(700, 760, 520, 22, fill=WHITE, stroke=GREY, w=3)
    for x in (730, 1190): pen.ln(x, 782, x, 900, WHITE, 8)
    mx = lerp(1700, 1010, ease_out(t / dur)); step = abs(math.sin(t * 9)) * 10
    hands = figure(pen, "mom", mx, 900, 1.0, {"face": {"mouth": "smile", "look": (-0.8, 0)}, "bob": step,
                                              "armL": (70, 30), "armR": (70, 30)}, t, seed=2)
    pot(pen, mx, 700 - step, 0.55, lid=0.0)
    steam(pen, mx, 640 - step, t, 2, 90, 0.4)
    pen.pop()

def INS_RICE_POT(pen, t, dur, gt, shot):
    pen.mood = "normal"
    camera(pen, t, dur, 1.0, 1.08, W / 2, 620, shot)
    pendant_lamp(pen, 960, 120, t, cone_to=700, spread=520)
    table_front(pen, 960, 820, 2400)
    first = "micro-change" not in shot.get("motion", "")
    lid = ease_out(t / 0.45) if first else 1.0
    pot(pen, 960, 900, 2.6, lid=lid, t=t)
    steam(pen, 960, 680, t, 5, 360 if first else 260, 0.7, 70)
    if first and t < 0.5:
        for k in range(8):
            a = k / 8 * math.tau; d = 120 + 500 * ease_out(t / 0.5)
            pen.circle(960 + math.cos(a) * d, 640 + math.sin(a) * d * 0.5, 26 * (1 - t / 0.5), fill=WHITE, a=0.5)
    pen.pop()

def CU_MOM_SMILE(pen, t, dur, gt, shot):
    pen.mood = "normal"
    camera(pen, t, dur, 1.0, 1.06, W / 2, 560, shot)
    pendant_lamp(pen, 960, 60, t, cone_to=900, spread=700)
    hum = "o" if (int(t * 3) % 2) else "smile"
    head_close(pen, "mom", W / 2 + 20 * math.sin(t * 3), 540, 250, {"eyes": "happy" if (t % 1.2) < 0.6 else "dot", "mouth": hum}, t, seed=2,
               tilt=6 * math.sin(t * 3))
    for k in range(2):
        ph = (t * 0.9 + k / 2) % 1
        music_note(pen, W / 2 + 330 + k * 70, 400 - ph * 180, 1.0, AMBER, 1 - ph)
    pen.pop()

def CU_DAD_TALK(pen, t, dur, gt, shot):
    pen.mood = "normal"
    camera(pen, t, dur, 1.0, 1.05, W / 2, 600, shot)
    floor(pen, 940)
    figure(pen, "dad", W / 2, 940, 2.1, {"face": {"mouth": "talk", "eyes": "dot"}, "armR": (70 + 25 * math.sin(t * 8), 40), "armL": (20, 10)}, t, seed=1)
    for k in range(3):  # 'blah' squiggles popping out
        ph = (t * 1.6 + k / 3) % 1
        x0, y0 = W / 2 + 230 + ph * 220, 330 - k * 40
        pen.path(lambda p, x0=x0, y0=y0: (p.moveTo(x0, y0), [p.lineTo(x0 + j * 14, y0 + (8 if j % 2 else -8)) for j in range(1, 7)]), stroke=WHITE, w=4, a=1 - ph)
    pen.pop()

SHOTS = {k: v for k, v in globals().items() if k.isupper() and callable(v)}
