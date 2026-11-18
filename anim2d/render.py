"""Render a time range of a video from its EDL with the 2D engine, straight to MP4 with captions + audio.
python3 render.py --video ../video01 --t0 0 --t1 30 --out ../video01/test2d_0-30.mp4"""
import argparse, json, os, subprocess, sys, time
import skia
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *
import shots01

a = argparse.ArgumentParser()
a.add_argument("--video", default=os.path.join(ROOT, "video01")); a.add_argument("--t0", type=float, default=0)
a.add_argument("--t1", type=float, default=30); a.add_argument("--out", default=None)
a.add_argument("--label", default="KEEP EATING  ·  SUNDAY 01"); a.add_argument("--crf", default="20")
args = a.parse_args()
V = lambda n: os.path.join(args.video, n)
edl = json.load(open(V("edl.json")))
RULE_AT = [23, 45, 59, 73, 104, 118, 146]
F0, F1 = round(args.t0 * FPS), round(args.t1 * FPS)

# frame -> (shot, first frame of shot, frames in shot), same overlap rule as the animatic
spans, fi = [], 0
for s in edl:
    end = round(s["end"] * FPS)
    if end > fi: spans.append((s, fi, end)); fi = end
def shot_at(f):
    for s, a_, b_ in spans:
        if a_ <= f < b_: return s, a_, b_
    return spans[-1]

out = args.out or V(f"test2d_{int(args.t0)}-{int(args.t1)}.mp4")
dur = (F1 - F0) / FPS
cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
       "-ss", str(args.t0), "-t", f"{dur:.3f}", "-i", V("mix.wav"),
       "-vf", f"noise=alls=4:allf=t,ass={V('captions.ass')}:fontsdir={FONTS}",
       "-c:v", "libx264", "-preset", "medium", "-crf", args.crf, "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", out]
ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
surf = skia.Surface(W, H); missing = set(); t_start = time.time()
for f in range(F0, F1):
    s, a_, b_ = shot_at(f)
    t, d, gt = (f - a_) / FPS, (b_ - a_) / FPS, f / FPS
    c = surf.getCanvas(); c.clear(C(BG)); pen = Pen(c)
    fn = shots01.SHOTS.get(s["setup"])
    if fn: fn(pen, t, d, gt, s)
    else:
        missing.add(s["setup"]); pen.text(s["setup"].replace("_", " "), W / 2, H / 2, 70, DIM)
    pen.mood = "normal"
    rn = sum(s["sentence"] >= r for r in RULE_AT)
    hud(pen, f"{args.label}  ·  {'INTRO' if rn == 0 else f'RULE {rn}'}", gt)
    ff.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())
ff.stdin.close(); ff.wait()
print(f"wrote {out}  {F1 - F0} frames in {time.time() - t_start:.0f}s; not yet drawn: {sorted(missing)}")
