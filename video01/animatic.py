"""Timing animatic: one labelled placeholder card per shot + captions + final mix -> animatic.mp4.
Real renders can replace any card: put renders/shot_NNN.mp4 (or .png) and they are used instead."""
import json, os, subprocess, textwrap
from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__)); P = lambda n: os.path.join(D, n)
FONTS = os.path.join(D, "..", "assets", "fonts")
W, H = 1280, 720
edl = json.load(open(P("edl.json")))
RULE_AT = [23, 45, 59, 73, 104, 118, 146]
def rule_no(si): return sum(si >= r for r in RULE_AT)
def mood(si):
    if si < 13: return (52, 38, 22), "WARM"
    if 132 <= si < 146: return (70, 58, 40), "MEMORY / VHS"
    if 164 <= si < 169: return (60, 40, 20), "WARM (RELIEF)"
    if si >= 169: return (18, 22, 40), "NIGHT"
    return (20, 40, 16), "FROZEN GREEN"
big = ImageFont.truetype(os.path.join(FONTS, "Anton-Regular.ttf"), 64)
mid = ImageFont.truetype(os.path.join(FONTS, "Montserrat-VF.ttf"), 30)
sml = ImageFont.truetype(os.path.join(FONTS, "Montserrat-VF.ttf"), 22)
os.makedirs(P("animatic_frames"), exist_ok=True)
lines = []
for s in edl:
    bg, mname = mood(s["sentence"])
    if s["motion"].startswith("micro-change"):  # show the micro-change visibly: shift tone
        bg = tuple(min(255, c + 18) for c in bg)
    im = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(im)
    rn = rule_no(s["sentence"])
    d.text((30, 18), f"SUNDAY DINNER // {'INTRO' if rn == 0 else f'RULE {rn} OF 7'}", font=sml, fill=(182, 255, 59))
    d.text((W - 30, 18), f"#{s['n']}  {int(s['start']//60)}:{s['start']%60:05.2f}  ({s['dur']:.1f}s)", font=sml, fill=(220, 220, 220), anchor="ra")
    d.text((W // 2, 230), s["setup"].replace("_", " "), font=big, fill=(255, 255, 255), anchor="mm")
    y = 310
    for t, f, col in ((s["motion"], mid, (182, 255, 59)), (s["note"], sml, (230, 230, 230))):
        for ln in textwrap.wrap(t, 70):
            d.text((W // 2, y), ln, font=f, fill=col, anchor="mm"); y += 38
    d.text((30, H - 150), mname, font=sml, fill=(160, 160, 160))
    fn = P(f"animatic_frames/s{s['n']:03d}.png"); im.save(fn)
    lines += [f"file '{fn}'", f"duration {s['dur']:.3f}"]
# frame-exact sequence: shot k covers frames round(start*24) .. round(end*24)-1
import shutil
SEQ = P("animatic_frames/seq"); shutil.rmtree(SEQ, ignore_errors=True); os.makedirs(SEQ)
fi = 0
for s in edl:
    n_end = round(s["end"] * 24)
    while fi < n_end:
        os.symlink(P(f"animatic_frames/s{s['n']:03d}.png"), f"{SEQ}/{fi:06d}.png"); fi += 1
cmd = ["ffmpeg", "-v", "error", "-y", "-framerate", "24", "-i", f"{SEQ}/%06d.png", "-i", P("mix.wav"),
       "-vf", f"ass={P('captions.ass')}:fontsdir={FONTS}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "26",
       "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", P("animatic.mp4")]
subprocess.run(cmd, check=True)
print("animatic.mp4 done")
