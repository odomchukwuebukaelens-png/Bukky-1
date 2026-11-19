#!/usr/bin/env python3
"""Cut the short footage pieces a shot list uses from the full Mixkit clips.

Usage: python3 tools/cut_footage.py <shotlist.tsx> <folder of full clips> <output folder>
Every <V id="…" t={…} /> in the shot list becomes <output>/v<id>_<t>.mp4 (3.2 s, 720p, no audio).
"""
import os, re, subprocess, sys
shotlist, src, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
pairs = sorted(set(re.findall(r'<V id="(\d+)"(?: t=\{(\d+(?:\.\d+)?)\})?', open(shotlist).read())))
for vid, t in pairs:
    t = t or "0"
    dst = f"{out}/v{vid}_{t}.mp4"
    if os.path.exists(dst):
        continue
    subprocess.check_call(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", t, "-i", f"{src}/{vid}.mp4", "-t", "3.2", "-an",
                           "-vf", "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720", "-c:v", "libx264",
                           "-crf", "25", "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart", dst])
print(len(pairs), "footage pieces")
