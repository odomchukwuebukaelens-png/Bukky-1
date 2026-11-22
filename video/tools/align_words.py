#!/usr/bin/env python3
"""Put the script's own words onto the TTS word timings.

Usage: python3 tools/align_words.py script/<file> <name>

The TTS transcript can differ from the script: numbers rewritten ("дві тисячі двадцять п'ятого" comes
back as "двадцять двадцять п'ять"), or a scene heard in the wrong language ("рыба" for "риба").
Captions must show what the script says, so the two texts are matched letter by letter: each script
word takes the time span of the transcript letters it lines up with, and words with no match are
spread evenly between their neighbours.
Rewrites src/<name>/timing.json (the original is kept as timing.raw.json).
"""
import difflib, json, os, re, shutil, sys

sys.path.insert(0, os.path.dirname(__file__))
from voiceover import parse  # noqa: E402

# Letters that differ between Russian and Ukrainian spellings of the same sound.
FOLD = str.maketrans({"ы": "и", "и": "і", "э": "е", "є": "е", "ё": "е", "ї": "і", "ъ": "", "ь": "", "’": "'", "ґ": "г"})
norm = lambda w: re.sub(r"[^\w']", "", w.lower()).translate(FOLD)


def align(words, said):
    # Transcript letters, each with a time inside its word.
    tc, tt = [], []
    for w, a, b in said:
        n = norm(w) or "_"
        for i, ch in enumerate(n):
            tc.append(ch)
            tt.append(a + (b - a) * (i + 0.5) / len(n))
    sc, owner = [], []
    for j, w in enumerate(words):
        for ch in norm(w) or "_":
            sc.append(ch)
            owner.append(j)
    span = [[None, None] for _ in words]
    for blk in difflib.SequenceMatcher(None, "".join(sc), "".join(tc), autojunk=False).get_matching_blocks():
        for i in range(blk.size):
            j, t = owner[blk.a + i], tt[blk.b + i]
            s = span[j]
            s[0] = t if s[0] is None else min(s[0], t)
            s[1] = t if s[1] is None else max(s[1], t)
    end = said[-1][2] if said else 0.0
    out = []
    j = 0
    while j < len(words):
        if span[j][0] is not None:
            a, b = span[j]
            out.append([words[j], round(a - 0.04, 2), round(max(b + 0.04, a + 0.06), 2)])
            j += 1
            continue
        k = j
        while k < len(words) and span[k][0] is None:
            k += 1
        t0 = out[-1][2] if out else 0.0
        t1 = span[k][0] - 0.04 if k < len(words) else end
        step = max(t1 - t0, 0.05 * (k - j)) / (k - j)
        out += [[words[j + i], round(t0 + i * step, 2), round(t0 + (i + 1) * step, 2)] for i in range(k - j)]
        j = k
    # Keep times increasing.
    for i in range(1, len(out)):
        out[i][1] = max(out[i][1], out[i - 1][1] + 0.01)
        out[i][2] = max(out[i][2], out[i][1] + 0.05)
    return out


script, name = sys.argv[1], sys.argv[2]
path = f"src/{name}/timing.json"
raw = f"src/{name}/timing.raw.json"
if not os.path.exists(raw):
    shutil.copy(path, raw)
timing = json.load(open(raw))
for s in parse(script):
    key = f"{s['n']:02d}"
    if key in timing:
        timing[key]["words"] = align(s["text"].split(), timing[key]["words"])
json.dump(timing, open(path, "w"), indent=1, ensure_ascii=False)
print(f"aligned {len(timing)} scenes to the script")
