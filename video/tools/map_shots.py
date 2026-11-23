#!/usr/bin/env python3
"""Re-time a finished shot list onto a translation of the same video.

Usage: python3 tools/map_shots.py <src name> <src script> <dst name> <dst script>
  e.g. python3 tools/map_shots.py humpback script/05-humpback-whale-uk.md humpback-en script/05-humpback-whale-en.md

Both scripts must have the same scenes and the same sentences in the same order (checked).
Every shot keeps its index, so shot i shows the same visual in both videos. A shot's start is
placed at the same point in the narration: the same sentence, the same fraction of the way
through it, or the same fraction of the pause after it. Writes src/<dst>/shots.json.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(__file__))
from sentences import sentences  # noqa: E402
from voiceover import parse  # noqa: E402

MIN = 0.3  # shortest shot, seconds


def spans(script_text, words):
    """(start, end) time of each sentence, from word timings that follow the script word for word."""
    out, i = [], 0
    for s in sentences(script_text):
        n = len(s.split())
        out.append((words[i][1], words[i + n - 1][2]))
        i += n
    if i != len(words):
        raise SystemExit(f"word count mismatch: script {i}, timings {len(words)}")
    return out


def to_pos(t, sp, dur):
    """Time to position: sentence k covers [2k+1, 2k+2], the pause after it [2k+2, 2k+3], the lead-in [0, 1]."""
    if t <= sp[0][0]:
        return t / sp[0][0] if sp[0][0] > 0 else 1.0
    for k, (a, b) in enumerate(sp):
        nxt = sp[k + 1][0] if k + 1 < len(sp) else dur
        if t <= b:
            return 2 * k + 1 + (t - a) / max(b - a, 1e-6)
        if t <= nxt:
            return 2 * k + 2 + (t - b) / max(nxt - b, 1e-6)
    return 2 * len(sp) + 1


def from_pos(p, sp, dur):
    if p <= 1:
        return p * sp[0][0]
    k = int((p - 1) // 2)
    if k >= len(sp):
        return dur
    a, b = sp[k]
    r = p - (2 * k + 1)
    if r <= 1:
        return a + r * (b - a)
    nxt = sp[k + 1][0] if k + 1 < len(sp) else dur
    return b + (r - 1) * (nxt - b)


src, src_script, dst, dst_script = sys.argv[1:5]
st = json.load(open(f"src/{src}/timing-fast.json"))
dt = json.load(open(f"src/{dst}/timing-fast.json"))
srows = json.load(open(f"src/{src}/shots.json"))
stext = {f"{s['n']:02d}": s["text"] for s in parse(src_script)}
dtext = {f"{s['n']:02d}": s["text"] for s in parse(dst_script)}

out = []
for key in sorted(st):
    a, b = sentences(stext[key]), sentences(dtext[key])
    if len(a) != len(b):
        raise SystemExit(f"scene {key}: {len(a)} sentences vs {len(b)}")
    ssp = spans(stext[key], st[key]["words"])
    dsp = spans(dtext[key], dt[key]["words"])
    sdur = st[key]["words"][-1][2]
    ddur = dt[key]["words"][-1][2]
    rows = [r for r in srows if r["scene"] == key]
    starts = [0.0 if j == 0 else from_pos(to_pos(r["t0"], ssp, sdur), dsp, ddur) for j, r in enumerate(rows)]
    # Keep every shot at least MIN long, pushing forward, then back from the end if needed.
    for j in range(1, len(starts)):
        starts[j] = max(starts[j], starts[j - 1] + MIN)
    for j in range(len(starts) - 1, 0, -1):
        limit = (starts[j + 1] if j + 1 < len(starts) else ddur) - MIN
        starts[j] = min(starts[j], limit)
    ends = starts[1:] + [ddur]
    words = dt[key]["words"]
    for j, r in enumerate(rows):
        t0, t1 = round(starts[j], 2), round(ends[j], 2)
        said = [w[0] for w in words if t0 <= w[1] < t1]
        out.append({"scene": key, "t0": t0, "t1": t1, "text": " ".join(said) or "…"})

json.dump(out, open(f"src/{dst}/shots.json", "w"), indent=1, ensure_ascii=False)
longest = max(r["t1"] - r["t0"] for r in out)
print(f"{len(out)} shots mapped, longest {longest:.2f} s, over 2 s: {sum(r['t1'] - r['t0'] > 2.0 for r in out)}")
