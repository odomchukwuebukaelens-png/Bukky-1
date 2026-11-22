#!/usr/bin/env python3
"""Report the longest stretch without a visual change in each scene.

A visual change is a narration cue a scene reacts to, plus (for videos with src/<name>/edit.json)
every caption change and filler camera move from captions.json, and the scene cut itself.

Usage: python3 tools/check_beats.py --video=<name> [max_seconds] [scene-file-glob]
Exits non-zero if any gap is longer than the limit.
"""
import glob, json, os, re, sys

NAME = next((a.split("=")[1] for a in sys.argv if a.startswith("--video=")), "octopus")
sys.argv = [a for a in sys.argv if not a.startswith("--video=")]
LIMIT = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0
PATTERN = sys.argv[2] if len(sys.argv) > 2 else f"src/{NAME}/scenes*.tsx"
UNTIL = {"02": 13.6} if "proto" in PATTERN else {}
norm = lambda s: re.sub(r"[^a-z0-9]+", "", s.lower())

edit_path = f"src/{NAME}/edit.json"
edit = json.load(open(edit_path)) if os.path.exists(edit_path) else None
timing = json.load(open(f"src/{NAME}/{edit['timing'] if edit else 'timing.json'}"))
lead, tail = (edit["lead"], edit["tail"]) if edit else (0.0, 0.0)
caps = json.load(open(f"src/{NAME}/captions.json")) if edit else {}

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
for key in sorted(set(cues) | set(caps)):
    end = UNTIL.get(key, timing[key]["duration"])
    ev = set(cues.get(key, set()))
    shots_path = f"src/{NAME}/shots.json"
    if os.path.exists(shots_path):
        # A shot list: visual changes are shot starts, plus the cut-in halfway through shots over 2 s.
        rows = [r for r in json.load(open(shots_path)) if r["scene"] == key]
        ev = set()
        for j, r in enumerate(rows):
            # Scene seconds: the first shot also covers the lead-in before the narration.
            a = -lead if j == 0 else r["t0"]
            if j > 0:
                ev.add(r["t0"])
            if r["t1"] - a > 1.8:
                ev.add(a + (r["t1"] - a) / 2)
    elif key in caps:
        ev |= {c["t0"] for c in caps[key]["captions"]} | set(caps[key]["punches"])
    # Times in scene seconds: the scene cut at 0, narration starts after the lead-in.
    pts = sorted({0.0} | {lead + t for t in ev if t < end} | {lead + end + tail})
    gaps = [(b - a, a) for a, b in zip(pts, pts[1:])]
    total += len(gaps)
    over = [g for g in gaps if g[0] > LIMIT + 1e-6]
    long += len(over)
    worst += [(g, key, at) for g, at in over]
    print(f"scene {key}: {len(gaps)} changes, longest {max(g for g, _ in gaps):.2f}s, over limit: {len(over)}")
print(f"\n{long} of {total} gaps exceed {LIMIT:g}s")
for g, key, at in sorted(worst, reverse=True)[:8]:
    print(f"  scene {key} at {at:.1f}s: {g:.2f}s")
sys.exit(1 if long else 0)
