#!/usr/bin/env python3
"""Speed up a video's narration without changing pitch, and rescale its word timings.

Usage: python3 tools/tempo.py <name> <factor>
Reads  public/audio/<name>/NN.mp3 and src/<name>/timing.json (the originals, never modified)
Writes public/audio/<name>-fast/NN.mp3 and src/<name>/timing-fast.json
"""
import json, os, subprocess, sys

name, factor = sys.argv[1], float(sys.argv[2])
src_dir, out_dir = f"public/audio/{name}", f"public/audio/{name}-fast"
os.makedirs(out_dir, exist_ok=True)
timing = json.load(open(f"src/{name}/timing.json"))
out = {}
for key, entry in sorted(timing.items()):
    dst = f"{out_dir}/{key}.mp3"
    subprocess.check_call(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", f"{src_dir}/{key}.mp3",
                           "-af", f"atempo={factor}", "-ac", "1", "-b:a", "96k", dst])
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", dst]).strip())
    e = dict(entry)
    e["duration"] = round(dur, 3)
    e["words"] = [[w, round(a / factor, 2), round(b / factor, 2)] for w, a, b in entry["words"]]
    out[key] = e
json.dump(out, open(f"src/{name}/timing-fast.json", "w"), indent=1)
total = sum(e["duration"] for e in out.values())
print(f"{len(out)} scenes, narration {total / 60:.2f} min at x{factor}")
