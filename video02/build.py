"""Build the timed edit for Video 01.

Inputs : narration_raw.mp3, narration_words.json, sentences.json, shotplan.py
Outputs: narration.wav   - narration with dramatic pauses inserted
         words_final.json- word timings after pauses
         edl.json        - every shot with start/end (no shot longer than MAX_SHOT)
         shotlist.md     - human-readable shot list
         captions.ass    - styled, word-highlighted captions
Run: python3 build.py
"""
import json, math, subprocess, re, wave, os, importlib.util
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
P = lambda n: os.path.join(HERE, n)
MAX_SHOT = 2.0
SR = 44100
MICRO = ["punch-in 112%", "angle shift (alt camera)", "rack focus", "reverse drift",
         "light flicker / exposure dip", "snap-zoom out", "parallax slide", "dutch tilt 5deg"]

spec = importlib.util.spec_from_file_location("shotplan", P("shotplan.py"))
sp = importlib.util.module_from_spec(spec); spec.loader.exec_module(sp)

# ---- words & sentences (same split rule as when sentences.json was made) ----
d = json.load(open(P("narration_words.json"))); d = d[0] if isinstance(d, list) else d
words = [dict(text=w["text"].strip(), start=w["start"], end=w["end"]) for w in d["words"] if w["type"] == "word"]
sents, cur = [], []
for i, w in enumerate(words):
    cur.append(i)
    if re.search(r'[.?!]["”]?$', w["text"]): sents.append(cur); cur = []
if cur: sents.append(cur)
assert len(sents) == len(json.load(open(P("sentences.json")))), "sentence split changed"

# ---- insert pauses into audio ----
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", P("narration_raw.mp3"), "-ac", "1", "-ar", str(SR),
                      "-f", "s16le", "-"], capture_output=True, check=True).stdout
a = np.frombuffer(pcm, np.int16)
cuts = []  # (time_in_raw, pause)
for si, pause in sorted(sp.PAUSES.items()):
    if pause <= 0 or si == 0: continue
    prev_end = words[sents[si - 1][-1]]["end"]; nxt = words[sents[si][0]]["start"]
    cuts.append(((prev_end + nxt) / 2, pause))
parts, last = [], 0
for t, pause in cuts:
    k = int(t * SR); parts += [a[last:k], np.zeros(int(pause * SR), np.int16)]; last = k
parts.append(a[last:]); out = np.concatenate(parts)
with wave.open(P("narration.wav"), "wb") as wv:
    wv.setnchannels(1); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes(out.tobytes())
total = len(out) / SR

def shift(t):
    return t + sum(p for c, p in cuts if c <= t)
for w in words: w["start"], w["end"] = round(shift(w["start"]), 3), round(shift(w["end"]), 3)
json.dump(words, open(P("words_final.json"), "w"))

# ---- shots: unique variants, pool top-ups, no repeats ----
used, edl = set(), []
ALLPOOL = [x for v in sp.POOL.values() for x in v]
def base_of(spec): return spec.split(":")[0] if ":" in spec else spec
def take(spec, prev_base, filler=False):
    if ":" not in spec:  # approved opening shot, used exactly once
        if spec in used: return None
        used.add(spec); return spec
    b, o = spec.split(":", 1)
    if filler and b == prev_base: return None
    for v in range(sp.MAXV.get(b, 1)):
        key = (b, v, o)
        if key not in used: used.add(key); return f"{b}#{v}:{o}"
    return None
for si, idxs in enumerate(sents):
    s0 = 0.0 if si == 0 else words[idxs[0]]["start"] - 0.12
    s1 = (words[sents[si + 1][0]]["start"] - 0.12) if si + 1 < len(sents) else total
    if edl: s0 = edl[-1]["end"]
    span = s1 - s0
    plan = list(sp.PLAN.get(si, []))
    need = max(1, math.ceil(span / 1.9 - 1e-9))
    maxn = max(1, int(span / 0.5))
    plan = plan[:maxn]
    shots = []
    prev = base_of(edl[-1]["setup"]) if edl else None
    for spec in plan:
        name = take(spec, prev)
        if name is None:  # never repeat: swap in an unused shot from this location's pool
            pool_ = sp.POOL[sp.CTX[si]]
            for alt in pool_[si % len(pool_):] + pool_[:si % len(pool_)]:
                name = take(alt, prev, filler=True)
                if name: break
            print(f"  sentence {si}: '{spec}' exhausted -> using {name}")
            if name is None: raise SystemExit(f"sentence {si}: nothing unused left")
        shots.append(name); prev = base_of(name)
    pool = sp.POOL[sp.CTX[si]]; k = si
    guard = 0
    while len(shots) < need:
        spec = pool[k % len(pool)]; k += 1; guard += 1
        name = take(spec, prev, filler=True)
        if name: shots.append(name); prev = base_of(name)
        if guard > 60 and pool is not ALLPOOL:  # this location is used up: borrow any unused shot from all locations
            pool = ALLPOOL; k = si * 7
        if guard > 2000: raise SystemExit(f"sentence {si}: every pool exhausted")
    n = len(shots); starts = [words[i]["start"] - 0.12 for i in idxs]
    bounds = [s0]
    for j in range(1, n):
        target = s0 + span * j / n
        cand = min((x for x in starts if x > bounds[-1] + 0.45 and x < s1 - 0.45), key=lambda x: abs(x - target), default=target)
        if abs(cand - target) > 0.5: cand = target
        bounds.append(cand)
    bounds.append(s1)
    if max(b_ - a_ for a_, b_ in zip(bounds, bounds[1:])) > 1.95:  # word-snapping made a long piece: cut evenly
        bounds = [s0 + span * j / n for j in range(n + 1)]
    text = " ".join(words[i]["text"] for i in idxs)
    for j, name in enumerate(shots):
        d = bounds[j + 1] - bounds[j]
        if d > MAX_SHOT + 0.05: raise SystemExit(f"sentence {si}: shot {name} {d:.2f}s too long")
        edl.append(dict(start=round(bounds[j], 3), end=round(bounds[j + 1], 3), sentence=si, setup=name, motion="", note="", text=text))
# ---- reorder within each sentence so look-alike shots (same builder + same subject) never sit side by side ----
def look(s_):
    n_ = s_["setup"]; b_ = n_.split("#")[0]
    o_ = n_.split(":", 1)[1] if ":" in n_ else ""
    return (b_, o_.split(",")[0] if b_ in ("DOG_CU", "TULSA", "MEMORY") else "")
for _ in range(3):
    for i in range(1, len(edl)):
        if look(edl[i]) != look(edl[i - 1]): continue
        for j in range(i + 1, len(edl)):
            if edl[j]["sentence"] != edl[i]["sentence"]: break
            if look(edl[j]) != look(edl[i - 1]) and (j + 1 >= len(edl) or look(edl[i]) != look(edl[j + 1])):
                a_, b2 = edl[i]["setup"], edl[j]["setup"]; edl[i]["setup"], edl[j]["setup"] = b2, a_; break
for i, s in enumerate(edl): s["n"] = i + 1; s["dur"] = round(s["end"] - s["start"], 3)
json.dump(edl, open(P("edl.json"), "w"), indent=1)

def tc(t):
    m, s = divmod(t, 60); return f"{int(m):02d}:{s:05.2f}"
durs = [s["dur"] for s in edl]
with open(P("shotlist.md"), "w") as f:
    f.write(f"# Video 01 shot list\n\nRuntime **{tc(total)}** | **{len(edl)} shots** | average shot "
            f"**{sum(durs)/len(durs):.2f}s** | longest **{max(durs):.2f}s**\n\n")
    f.write("| # | Time | Dur | Set-up | Motion / animation | Notes | Narration |\n|---|---|---|---|---|---|---|\n")
    lastsent = None
    for s in edl:
        nar = s["text"] if s["sentence"] != lastsent else "〃"; lastsent = s["sentence"]
        esc = lambda x: str(x).replace("|", "/")
        f.write(f"| {s['n']} | {tc(s['start'])} | {s['dur']:.1f} | `{s['setup']}` | {esc(s['motion'])} | {esc(s['note'])} | {esc(nar)} |\n")

# ---- captions (ASS): 1-4 word chunks, current word highlighted ----
ACC = "&H003BFFB6"  # accent (sickly green) in ASS BGR
hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Montserrat,66,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,1,0,0,0,100,100,1,0,1,5,3,2,80,80,70,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
def at(t):
    h, r = divmod(t, 3600); m, s = divmod(r, 60); return f"{int(h)}:{int(m):02d}:{s:05.2f}"
chunks, cur = [], []
for i, w in enumerate(words):
    cur.append(w)
    brk = re.search(r"[.,?!:;]$", w["text"]) or len(cur) >= 4 or (cur[-1]["end"] - cur[0]["start"]) > 1.4
    if brk: chunks.append(cur); cur = []
if cur: chunks.append(cur)
ev = []
for ci, ch in enumerate(chunks):
    end_chunk = chunks[ci + 1][0]["start"] if ci + 1 < len(chunks) else ch[-1]["end"] + 0.5
    end_chunk = min(end_chunk, ch[-1]["end"] + 0.6)
    for wi, w in enumerate(ch):
        t0 = w["start"]; t1 = ch[wi + 1]["start"] if wi + 1 < len(ch) else end_chunk
        txt = " ".join((f"{{\\c{ACC}}}{x['text'].upper()}{{\\c&H00FFFFFF&}}" if j == wi else x["text"].upper())
                       for j, x in enumerate(ch))
        pop = "{\\fscx108\\fscy108\\t(0,80,\\fscx100\\fscy100)}" if wi == 0 else ""
        ev.append(f"Dialogue: 0,{at(t0)},{at(t1)},Cap,,0,0,0,,{pop}{txt}")
open(P("captions.ass"), "w").write(hdr + "\n".join(ev) + "\n")
print(f"runtime {tc(total)}  shots {len(edl)}  avg {sum(durs)/len(durs):.2f}s  max {max(durs):.2f}s  "
      f"over2s {sum(d > MAX_SHOT + 1e-6 for d in durs)}  caption chunks {len(chunks)}")
