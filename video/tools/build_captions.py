#!/usr/bin/env python3
"""Build caption chunks, emphasis words, impact moments and filler camera moves from word timings.

Usage: python3 tools/build_captions.py <name> [timing-file]
Writes src/<name>/captions.json. Every scene gets an event at least every MAX_GAP seconds.
"""
import json, re, sys

MAX_GAP = 1.6          # seconds between filler events (the check allows 2.0)
MAX_WORDS = 4          # words per caption chunk
MAX_CHUNK = 1.6        # seconds per caption chunk

STOP = set("a an the and or but so of to in on at by for with from as is are was were be been it its it's this that these those you your you're i we they he she his her their them our not no do does did can could will would just very than then there here what when how who which into onto over under up out about after before once one".split())
IMPACT = set("eyes strike strikes bite bites bit jaws snap snaps death deadly kill kills killed fatal attack attacks attacked drown drowned crush crushes eaten took fight myth sink sinks sank rolled spins grips explode strongest".split())
SPLASH = set("water sink sinks sank splash surface dive under underwater swim swam".split())
NUM = re.compile(r"^\d[\d,\.]*$|^(one|two|three|four|five|six|seven|eight|nine|ten|twenty|fifty|hundred|thousand|million|sixteen|ninety-two|seventy-nine)$")

name = sys.argv[1]
tfile = sys.argv[2] if len(sys.argv) > 2 else f"src/{name}/timing-fast.json"
timing = json.load(open(tfile))
norm = lambda w: re.sub(r"[^a-z0-9\-']", "", w.lower())

def emphasis(words):
    best, score = 0, -1
    for i, w in enumerate(words):
        n = norm(w)
        sc = 0 if n in STOP else len(n)
        if NUM.match(n) or any(ch.isdigit() for ch in w): sc += 20
        if n in IMPACT: sc += 15
        if sc > score: best, score = i, sc
    return best

out = {}
for key, entry in sorted(timing.items()):
    words = entry["words"]
    chunks, cur = [], []
    for w in words:
        if cur and (len(cur) >= MAX_WORDS or w[2] - cur[0][1] > MAX_CHUNK or w[1] - cur[-1][2] > 0.35):
            chunks.append(cur); cur = []
        cur.append(w)
        if re.search(r"[.?!,;:]$", w[0]) and len(cur) >= 2:
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    caps = []
    for c in chunks:
        texts = [w[0].rstrip(",;:") for w in c]
        caps.append({"t0": c[0][1], "t1": c[-1][2], "words": [[t, w[1]] for t, w in zip(texts, c)], "em": emphasis(texts)})
    # Impact moments at most every 10 s, splashes at most every 20 s, so each one still lands.
    impacts, splashes, last_i, last_s = [], [], -9, -9
    for w in words:
        n = norm(w[0])
        if n in IMPACT and w[1] - last_i > 10:
            impacts.append(w[1]); last_i = w[1]
        elif n in SPLASH and w[1] - last_s > 20:
            splashes.append(w[1]); last_s = w[1]
    # Filler camera moves wherever captions alone leave a gap longer than MAX_GAP.
    events = sorted([0.0] + [c["t0"] for c in caps] + [entry["duration"] + 0.4])
    punches = []
    for a, b in zip(events, events[1:]):
        t = a + MAX_GAP
        while t < b - 0.05:
            punches.append(round(t, 2)); t += MAX_GAP
    out[key] = {"captions": caps, "impacts": impacts, "splashes": splashes, "punches": punches}
json.dump(out, open(f"src/{name}/captions.json", "w"), indent=1)
n = sum(len(v["captions"]) for v in out.values())
print(f"{n} caption chunks, {sum(len(v['impacts']) for v in out.values())} impacts, {sum(len(v['punches']) for v in out.values())} filler moves")
