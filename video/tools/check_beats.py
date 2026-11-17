#!/usr/bin/env python3
"""Report gaps between visual beats. A beat is any narration cue a scene reacts to.

Usage: python3 tools/check_beats.py [max_seconds]   (default 5)
Exits non-zero if any gap is longer than the limit.
"""
import glob, json, re, sys

NAME = next((a.split("=")[1] for a in sys.argv if a.startswith("--video=")), "octopus")
sys.argv = [a for a in sys.argv if not a.startswith("--video=")]
LIMIT = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0
PATTERN = sys.argv[2] if len(sys.argv) > 2 else f"src/{NAME}/scenes*.tsx"  # which scene files to check
UNTIL = {"02": 13.6} if "proto" in PATTERN else {}  # the prototype uses only the start of scene 2
norm = lambda s: re.sub(r"[^a-z0-9]+", "", s.lower())
timing = json.load(open(f"src/{NAME}/timing.json"))
cues = {}
for path in sorted(glob.glob(PATTERN)):
    for num, phrase, nth in re.findall(r'\bc(\d+)\("([^"]+)"(?:,\s*(\d+))?\)', open(path).read()):
        key = f"{int(num):02d}"
        words = [norm(w[0]) for w in timing[key]["words"]]
        target = [norm(t) for t in phrase.split() if norm(t)]
        hits = [i for i in range(len(words) - len(target) + 1) if words[i:i + len(target)] == target]
        if hits:
            cues.setdefault(key, set()).add(timing[key]["words"][hits[int(nth or 0)]][1])

total = long = 0
worst = []
for key in sorted(cues):
    end = UNTIL.get(key, timing[key]["duration"])
    pts = [0.0] + sorted(c for c in cues[key] if c < end) + [end]
    gaps = [(b - a, a) for a, b in zip(pts, pts[1:])]
    total += len(gaps)
    over = [g for g in gaps if g[0] > LIMIT]
    long += len(over)
    worst += [(g, key, at) for g, at in over]
    print(f"scene {key}: {len(gaps)} beats, longest {max(g for g, _ in gaps):.1f}s, over limit: {len(over)}")
print(f"\n{long} of {total} beats exceed {LIMIT:.0f}s")
for g, key, at in sorted(worst, reverse=True)[:8]:
    print(f"  scene {key} at {at:.0f}s: {g:.1f}s")
sys.exit(1 if long else 0)
