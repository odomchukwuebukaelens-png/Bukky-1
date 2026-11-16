#!/usr/bin/env python3
"""Check that every cue phrase used by the scenes exists in the narration timings."""
import glob, json, re, sys

norm = lambda s: re.sub(r"[^a-z0-9]+", "", s.lower())
timing = json.load(open("src/octopus/timing.json"))
bad = 0
for path in sorted(glob.glob("src/octopus/scenes*.tsx")):
    src = open(path).read()
    for num, phrase in re.findall(r'\bc(\d+)\("([^"]+)"', src):
        key = f"{int(num):02d}"
        if key not in timing:
            print(f"scene {key}: no audio yet"); bad += 1; continue
        words = [norm(w[0]) for w in timing[key]["words"]]
        target = [norm(t) for t in phrase.split() if norm(t)]
        hits = [i for i in range(len(words) - len(target) + 1) if words[i:i + len(target)] == target]
        if not hits:
            print(f"scene {key}: MISSING  {phrase!r}"); bad += 1
print("missing:", bad)
sys.exit(1 if bad else 0)
