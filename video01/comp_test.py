"""Composite a time range of Video 01 from GPU renders + 2D cards -> test_0-30.mp4.
python3 comp_test.py --t1 30 --renders renders/   (renders/shot_NNN.mp4 from blender/render_shots.py --encode)"""
import argparse, json, os, subprocess, math, shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import art2d

D = os.path.dirname(os.path.abspath(__file__)); P = lambda n: os.path.join(D, n)
FONTS = os.path.join(D, "..", "assets", "fonts")
a = argparse.ArgumentParser(); a.add_argument("--t0", type=float, default=0); a.add_argument("--t1", type=float, default=30)
a.add_argument("--renders", default=P("renders")); a.add_argument("--out", default=P("test_0-30.mp4")); args = a.parse_args()
W, H, FPS = 1920, 1080, 24
ACID = (182, 255, 59)
edl = [s for s in json.load(open(P("edl.json"))) if s["end"] > args.t0 and s["start"] < args.t1]
TMP = P("comp_tmp"); shutil.rmtree(TMP, ignore_errors=True); os.makedirs(TMP)
anton = lambda n: ImageFont.truetype(os.path.join(FONTS, "Anton-Regular.ttf"), n)
mont = lambda n: ImageFont.truetype(os.path.join(FONTS, "Montserrat-VF.ttf"), n)

def frames_for(s):
    return max(1, min(round(s["end"] * FPS), round(args.t1 * FPS)) - round(s["start"] * FPS))

def card_kt(text, n, path, shake=True):
    """Kinetic text slam: scales 140%->100% in 4 frames, shakes, acid green on black."""
    for f in range(n):
        im = Image.new("RGB", (W, H), (8, 10, 8)); d = ImageDraw.Draw(im)
        sc = 1.4 - 0.4 * min(1, f / 4); fnt = anton(int(230 * sc))
        dx = int(12 * math.sin(f * 2.1)) if shake and f < 10 else 0
        d.text((W // 2 + dx, H // 2), text, font=fnt, fill=ACID, anchor="mm")
        im.save(f"{path}/{f:04d}.png")

def card_clock(n, path):
    """Smash to black for 6 frames, then a clock title card that ticks."""
    for f in range(n):
        im = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(im)
        if f >= 6:
            d.text((W // 2, H // 2 - 40), "SUNDAY.", font=anton(170), fill=(240, 240, 240), anchor="mm")
            mm = 42 if f < 18 else 43
            d.text((W // 2, H // 2 + 110), f"7:{mm} PM", font=mont(70), fill=ACID, anchor="mm")
        im.save(f"{path}/{f:04d}.png")

def card_house(n, path):
    """Exterior night: house with one lit window, slow push-in, flickering porch light."""
    base = Image.new("RGB", (W, H)); d = ImageDraw.Draw(base)
    for y in range(H): d.line([(0, y), (W, y)], fill=(8, 14 + y // 60, 38 + y // 30))
    d.ellipse([1500, 120, 1640, 260], fill=(235, 235, 210))
    d.rectangle([0, 860, W, H], fill=(10, 22, 16))
    d.polygon([(560, 520), (960, 260), (1360, 520)], fill=(30, 30, 46), outline=(0, 0, 0))
    d.rectangle([600, 520, 1320, 880], fill=(40, 44, 64), outline=(0, 0, 0), width=6)
    d.rectangle([700, 600, 860, 740], fill=(255, 196, 92), outline=(0, 0, 0), width=6)  # lit dining window
    d.rectangle([1060, 600, 1220, 740], fill=(20, 26, 46), outline=(0, 0, 0), width=6)
    d.rectangle([905, 700, 1015, 880], fill=(60, 34, 24), outline=(0, 0, 0), width=6)
    for f in range(n):
        z = 1 + 0.10 * f / max(1, n - 1); cw, ch = int(W / z), int(H / z)
        cx, cy = 780 + int((W // 2 - 780) / z), 670 + int((H // 2 - 670) / z)
        im = base.crop((cx - cw // 2, cy - ch // 2, cx + cw // 2, cy + ch // 2)).resize((W, H))
        if f % 9 in (0, 1):  # porch flicker
            ImageDraw.Draw(im).rectangle([0, 0, W, H], outline=None)
        im.save(f"{path}/{f:04d}.png")

def kt_text(note):
    """Text between the first and last single quote: "'DON'T LOOK.' green" -> DON'T LOOK."""
    a, b = note.find("'"), note.rfind("'")
    return note[a + 1:b] if b > a >= 0 else "DON'T."
TWO_D = {"KT_TEXT": lambda s, n, p: card_kt(kt_text(s["note"]), n, p),
         "SMASH_BLACK": lambda s, n, p: card_clock(n, p), "EXT_HOUSE_NIGHT": lambda s, n, p: card_house(n, p)}

# ---- assemble a frame-exact sequence ----
SEQ = f"{TMP}/seq"; os.makedirs(SEQ); fi = 0; report = []
prev_render = {}
T1F = round(args.t1 * FPS)
for s in edl:
    n = min(round(s["end"] * FPS), T1F) - fi  # fill up to this shot's exact end frame (absorbs overlaps)
    if n <= 0: continue
    src = f"{TMP}/s{s['n']:03d}"; os.makedirs(src)
    mp4 = os.path.join(args.renders, f"shot_{s['n']:03d}.mp4")
    if art2d.recipe(s["setup"], s["motion"], n, src):
        kind = "2D-ART"
    elif os.path.exists(mp4):
        subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", f"scale={W}:{H}", "-frames:v", str(n), f"{src}/%04d.png"], check=True)
        kind = "3D"
    elif s["setup"] in TWO_D:
        TWO_D[s["setup"]](s, n, src); kind = "2D"
    else:
        card_kt(s["setup"].replace("_", " "), n, src, shake=False); kind = "MISSING"
    got = sorted(os.listdir(src))
    for k in range(n):
        os.symlink(f"{src}/{got[min(k, len(got) - 1)]}", f"{SEQ}/{fi:06d}.png"); fi += 1
    report.append((s["n"], s["setup"], kind, n))

# ---- HUD overlay (transparent png) ----
hud = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(hud)
d.text((48, 36), "SUNDAY DINNER  //  INTRO", font=mont(30), fill=(*ACID, 170))
hud.save(f"{TMP}/hud.png")
dur = fi / FPS
vf = (f"[0:v]noise=alls=7:allf=t,vignette=PI/4.2[v0];[v0][2:v]overlay=0:0[v1];"
      f"[v1]ass={P('captions.ass')}:fontsdir={FONTS}[v]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", f"{SEQ}/%06d.png",
                "-ss", str(args.t0), "-t", f"{dur:.3f}", "-i", P("mix.wav"), "-i", f"{TMP}/hud.png",
                "-filter_complex", vf, "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-af", "afade=t=out:st=%.2f:d=0.6" % (dur - 0.6),
                "-movflags", "+faststart", args.out], check=True)
for r in report: print(*r)
print("wrote", args.out, f"{dur:.2f}s")
