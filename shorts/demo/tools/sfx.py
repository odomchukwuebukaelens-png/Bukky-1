"""Build a sound-effects track from build/info.json cues. usage: python3 -I tools/sfx.py"""
import json, wave, array

RATE = 44100
GAIN = {"whoosh": 0.32, "pop": 0.30, "hit": 0.42, "tick": 0.22, "stamp": 0.6}

def load(name):
    with wave.open(f"build/sfx/{name}.wav") as w:
        a = array.array("h", w.readframes(w.getnframes()))
    return [x / 32768 for x in a]

info = json.load(open("build/info.json"))
n = int((info["duration"] + 1) * RATE)
track = array.array("f", bytes(4 * n))
clips = {k: load(k) for k in GAIN}
last = {}
for kind, t in sorted(info["sfx"], key=lambda c: c[1]):
    if t - last.get(kind, -9) < 0.25: continue  # avoid machine-gun stacking
    last[kind] = t
    s0, g, c = int(t * RATE), GAIN[kind], clips[kind]
    if kind == "whoosh": s0 = max(0, s0 - int(0.25 * RATE))  # lead into the move
    for i, v in enumerate(c):
        j = s0 + i
        if j < n: track[j] += v * g
out = array.array("h", (max(-32767, min(32767, int(v * 32767))) for v in track))
with wave.open("build/sfx.wav", "w") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE); w.writeframes(out.tobytes())
print("sfx cues:", len(info["sfx"]))
