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

# ---- shots ----
edl = []
for si, idxs in enumerate(sents):
    plan = sp.PLAN.get(si) or [("HOLD_PREV", "micro-change", "")]
    s0 = 0.0 if si == 0 else words[idxs[0]]["start"]
    s1 = words[sents[si + 1][0]]["start"] if si + 1 < len(sents) else total
    if si > 0:  # cut slightly before the first word so the picture lands with the line
        s0 = max(edl[-1]["start"] + 0.3 if edl else 0, s0 - 0.12)
    n = len(plan)
    starts = [words[i]["start"] for i in idxs]
    bounds = [s0]
    for k in range(1, n):  # word-aligned cuts at even spacing
        target = s0 + (s1 - s0) * k / n
        cand = min((t for t in starts if t > bounds[-1] + 0.35), key=lambda t: abs(t - target), default=target)
        bounds.append(cand)
    bounds.append(s1)
    text = " ".join(words[i]["text"] for i in idxs)
    for k, (setup, motion, note) in enumerate(plan):
        b0, b1 = bounds[k], bounds[k + 1]
        if b1 - b0 < 0.25 and edl:  # too short to read; merge into previous
            edl[-1]["end"] = b1; continue
        if b1 - b0 > MAX_SHOT + 1e-6:  # no auto-splitting / repeating: the plan must supply another shot
            raise SystemExit(f"sentence {si}: shot {setup} would last {b1 - b0:.2f}s > {MAX_SHOT}s - add a new, different shot")
        pieces = 1
        for p in range(pieces):
            q0 = b0 + (b1 - b0) * p / pieces; q1 = b0 + (b1 - b0) * (p + 1) / pieces
            edl.append(dict(start=round(q0, 3), end=round(q1, 3), sentence=si, setup=setup,
                            motion=motion if p == 0 else f"micro-change: {MICRO[(len(edl)) % len(MICRO)]}",
                            note=note if p == 0 else "", text=text))
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
