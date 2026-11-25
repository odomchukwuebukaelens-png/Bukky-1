"""Join segment audio with pauses and build timeline.json with per-word timings on the script's display text.
usage: python3 -I tools/timeline.py script.json"""
import json, sys, re, subprocess, difflib

GAP, LEAD = 0.8, 0.6   # pause between segments, silence before first word

def norm(w): return re.sub(r"[^a-z0-9']", "", w.lower().replace("’", "'"))

def dur(f): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)

def align(display, spoken):
    """display: list of tokens; spoken: list of {text,start,end}. Returns list of (t0,t1) per display token."""
    a = [norm(w) for w in display]; b = [norm(w["text"]) for w in spoken]
    out = [None] * len(a)
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            for k in range(i2 - i1): out[i1 + k] = (spoken[j1 + k]["start"], spoken[j1 + k]["end"])
        elif op in ("replace", "delete") and i2 > i1:
            if j2 > j1: t0, t1 = spoken[j1]["start"], spoken[j2 - 1]["end"]
            else:  # no spoken counterpart: squeeze between neighbours
                t0 = spoken[j1 - 1]["end"] if j1 > 0 else 0; t1 = spoken[j1]["start"] if j1 < len(spoken) else t0 + 0.2
            n = i2 - i1
            for k in range(n): out[i1 + k] = (t0 + (t1 - t0) * k / n, t0 + (t1 - t0) * (k + 1) / n)
    return out

if __name__ == "__main__":
    S = json.load(open(sys.argv[1]))
    t, segs, inputs, filt = LEAD, [], [], []
    for i, seg in enumerate(S["segments"]):
        f = f"audio/{seg['id']}.mp3"; d = dur(f)
        words = [w for w in json.load(open(f"audio/{seg['id']}.json"))[0]["words"] if w["type"] == "word"]
        disp = seg["text"].split()
        tm = align(disp, words)
        segs.append({"id": seg["id"], "start": round(t, 3), "end": round(t + d, 3),
                     "words": [{"w": w, "t0": round(t + a, 3), "t1": round(t + b, 3)} for w, (a, b) in zip(disp, tm)]})
        inputs += ["-i", f]; filt.append(f"[{i}:a]adelay={int(t*1000)}|{int(t*1000)},aresample=44100[a{i}]")
        t += d + GAP
    total = t - GAP + 4.0  # tail for end screen
    filt.append("".join(f"[a{i}]" for i in range(len(segs))) + f"amix=inputs={len(segs)}:normalize=0,apad=whole_dur={total}[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filt), "-map", "[out]", "-t", str(total), "-ar", "44100", "-ac", "2", "narration.wav"], check=True)
    json.dump({"duration": round(total, 3), "segments": segs}, open("timeline.json", "w"), indent=1)
    print("total", round(total, 1), "s")
    for s in segs: print(s["id"], s["start"], s["end"])
