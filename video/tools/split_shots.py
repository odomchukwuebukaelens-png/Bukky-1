#!/usr/bin/env python3
"""Split a video's narration into shots of at most MAX seconds, breaking at word boundaries.

Usage: python3 tools/split_shots.py <name> [max_seconds]   (default 2.0)
Reads src/<name>/timing-fast.json and writes src/<name>/shots.json, one entry per shot with the words
spoken during it, so each shot's visual can be written to match exactly what is being said.
"""
import json, re, sys

name = sys.argv[1]
MAX = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
timing = json.load(open(f"src/{name}/timing-fast.json"))
shots = []
for key in sorted(timing):
    words, dur = timing[key]["words"], timing[key]["duration"]
    start, cur = 0.0, []
    for i, w in enumerate(words):
        nxt = words[i + 1][1] if i + 1 < len(words) else dur
        cur.append(w)
        long_enough = nxt - start >= MAX * 0.75
        sentence_end = re.search(r"[.?!]$", w[0]) and nxt - start >= MAX * 0.5
        too_long_next = i + 1 < len(words) and words[i + 1][2] - start > MAX
        if long_enough or sentence_end or too_long_next or i == len(words) - 1:
            end = nxt if i + 1 < len(words) else dur
            # A pause can still leave a shot too long: split it evenly.
            n = max(1, int((end - start) // MAX + (1 if (end - start) % MAX > 1e-6 else 0)))
            step = (end - start) / n
            for k in range(n):
                shots.append({"scene": key, "t0": round(start + k * step, 2), "t1": round(start + (k + 1) * step, 2), "text": " ".join(x[0] for x in cur) if k == 0 else "…"})
            start, cur = end, []
json.dump(shots, open(f"src/{name}/shots.json", "w"), indent=0)
lens = [s["t1"] - s["t0"] for s in shots]
print(f"{len(shots)} shots, longest {max(lens):.2f} s, average {sum(lens) / len(lens):.2f} s")
