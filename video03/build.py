"""Build the timed edit for Video 01.

Inputs : narration_raw.mp3, narration_words.json, sentences.json, shotplan.py
Outputs: narration.wav   - narration with dramatic pauses inserted
         words_final.json- word timings after pauses
         edl.json        - every shot with start/end (no shot longer than MAX_SHOT)
         shotlist.md     - human-readable shot list
         captions.ass    - styled, word-highlighted captions
Run: python3 build.py
"""
import json, math, subprocess, re, wave, os, importlib.util, sys
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

# ---- phrases: every <=1.9s piece of narration gets its OWN authored shot (no filler, no pools) ----
def phrases():
    out = []
    for si, idxs in enumerate(sents):
        s0 = 0.0 if si == 0 else words[idxs[0]]["start"] - 0.12
        s1 = (words[sents[si + 1][0]]["start"] - 0.12) if si + 1 < len(sents) else total
        cuts, a_ = [], s0
        while s1 - a_ > 1.9:
            cands = [words[i]["start"] - 0.05 for i in idxs if a_ + 0.6 < words[i]["start"] - 0.05 <= a_ + 1.9]
            if not cands: cut = a_ + min(1.9, (s1 - a_) / 2)
            else:
                punct = [words[i]["start"] - 0.05 for i in idxs[1:] if re.search(r"[,;:]$", words[idxs[idxs.index(i) - 1]]["text"])
                         and a_ + 0.9 <= words[i]["start"] - 0.05 <= a_ + 1.9]
                cut = max(punct) if punct else max(cands)
            if s1 - cut < 0.5: cut = (a_ + s1) / 2
            cuts.append(cut); a_ = cut
        bounds = [s0] + cuts + [s1]
        for j in range(len(bounds) - 1):
            ws = [words[i]["text"] for i in idxs if bounds[j] - 0.01 <= words[i]["start"] - 0.05 < bounds[j + 1] - 0.01]
            out.append(dict(start=round(bounds[j], 3), end=round(bounds[j + 1], 3), sentence=si, text=" ".join(ws)))
    return out
PH = phrases()
if len(sys.argv) > 1 and sys.argv[1] == "phrases":
    for k, p in enumerate(PH): print(f"{k:3d} [{p['end'] - p['start']:.2f}] s{p['sentence']:<3d} {p['text']}")
    sys.exit(0)
used, edl, missing = set(), [], []
for k, p in enumerate(PH):
    spec = sp.PLAN.get(k)
    if not spec: missing.append(k); continue
    b_, _, o_ = spec.partition(":")
    for v in range(sp.MAXV.get(b_, 1)):
        if (b_, v, o_) not in used: used.add((b_, v, o_)); name = f"{b_}#{v}:{o_}"; break
    else:
        missing.append(f"{k}:{spec}:'{p['text']}'"); continue
    edl.append(dict(start=p["start"], end=p["end"], sentence=p["sentence"], setup=name, motion="", note="", text=p["text"]))
if missing: raise SystemExit(f"{len(missing)} problems:\n" + "\n".join(map(str, missing)))
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
