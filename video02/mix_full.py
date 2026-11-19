"""Video 02 full mix. Music ONLY from assets/music (never regenerated), varied takes/offsets; SFX cued from shot content."""
import json, os, re, subprocess, wave
import numpy as np
D = os.path.dirname(os.path.abspath(__file__)); P = lambda n: os.path.join(D, n)
MUSIC = os.path.join(D, "..", "assets", "music"); SFX = [P("audio/sfx"), os.path.join(D, "..", "video01", "audio", "sfx")]
SR = 44100
def load(path, offset=0.0):
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(offset), "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.float32).reshape(-1, 2).copy()
db = lambda x: 10 ** (x / 20)
voice = load(P("narration.wav")); N = len(voice) + 2 * SR
out = np.zeros((N, 2), np.float32); out[:len(voice)] += voice
words = json.load(open(P("words_final.json"))); edl = json.load(open(P("edl.json")))
T = {}
for s in edl: T.setdefault(s["sentence"], s["start"])
first = lambda name: next(s["start"] for s in edl if s["setup"] == name)
end = len(voice) / SR + 1.5
SECT = [(0.0, first("SQUIRREL_DAY"), "m2_dread_bed_a", 75, -23, 0.4, 0.3),
        (first("SQUIRREL_DAY"), first("EYES_GONE"), "m1_sunday_warm_b", 42, -20, 0.15, 0.02),
        (first("EYES_GONE") + 0.4, T[27], "m3_tension_pulse_b", 20, -24, 1.2, 1.0),
        (T[27], T[59], "m2_dread_bed_b", 100, -23, 1.0, 1.2),
        (T[59], T[80], "m3_tension_pulse_a", 60, -24, 1.2, 1.2),
        (T[80], T[95], "m2_dread_bed_a", 140, -23, 1.0, 1.2),
        (T[95], T[112], "m3_tension_pulse_b", 80, -24, 1.0, 1.0),
        (T[112], T[126], "m4_memory_piano_b", 30, -20, 1.2, 1.5),
        (T[126], T[139], "m2_dread_bed_b", 20, -23, 1.0, 1.5),
        (T[139], T[144], "m1_sunday_warm_a", 60, -21, 1.5, 1.0),
        (T[144], end, "m5_end_lullaby_b", 10, -21, 1.0, 2.5)]
music = np.zeros_like(out)
for a, b, name, off, g, fi, fo in SECT:
    n = int((b - a) * SR); m = load(os.path.join(MUSIC, name + ".mp3"), off)
    if len(m) < n: m = np.concatenate([m] * (n // len(m) + 1))
    m = m[:n] * db(g); env = np.ones(n, np.float32); k1, k2 = int(fi * SR), int(fo * SR)
    env[:k1] = np.linspace(0, 1, k1); env[-k2:] = np.minimum(env[-k2:], np.linspace(1, 0, k2))
    i0 = int(a * SR); music[i0:i0 + n] += m * env[:, None]
duck = np.ones(N, np.float32)
for w in words: duck[int(w["start"] * SR):int(w["end"] * SR)] = db(-6)
k = int(0.12 * SR); duck = np.convolve(duck, np.ones(k) / k, mode="same").astype(np.float32)
out += music * duck[:, None]
RULES = [(r"^TAGS#\d+:\d", "stinger_card", -9), (r"^KT", "text_slam", -10), (r"growl", "dog_growl", -8), (r"^WHISTLE", "whistle", -8),
         (r"knock", "knock_pattern", -6), (r"^CLOCK", "clock_tick", -14), (r"voice", "whoosh", -16), (r"^CURTAIN#\d+:move", "whoosh", -14),
         (r"^WOODS.*lead|foot", "footsteps", -12), (r"^NEIGHBORS", "glitch", -16), (r"eat$", "chew_wet", -12), (r"^DOG_FULL#\d+:wag|duke,wag", "dog_woof", -16),
         (r"^COUNT", "heartbeat", -10), (r"collar", "clink", -10), (r"cold", "buzz", -18), (r"^ARM_HAIR", "room_tone_dread", -18),
         (r"^SQUIRREL", "dog_woof", -10), (r"DOOR_OPENS_OUT", "door_open", -9), (r"DOG_EYES_DARK|DOORWAY_BEHIND", "drone_hit", -9),
         (r"EYES_GONE", "freeze_cut", -8), (r"^MEMORY", "vhs_rewind", -20), (r"HALL_PUSH", "room_tone_dread", -16)]
cache, last, hits = {}, {}, 0
def sfx(name):
    for d in SFX:
        f = os.path.join(d, name + ".mp3")
        if os.path.exists(f): return f
for s in edl:
    for pat, name, g in RULES:
        if re.search(pat, s["setup"]) and s["start"] - last.get(name, -9) > 1.2:
            f = sfx(name)
            if not f: continue
            if name not in cache: cache[name] = load(f)
            x = cache[name] * db(g); i0 = int(s["start"] * SR); out[i0:i0 + len(x)] += x[:max(0, N - i0)]
            last[name] = s["start"]; hits += 1; break
cr = load(sfx("crickets")) * db(-26); i0 = 0
while i0 < N: L = min(len(cr), N - i0); out[i0:i0 + L] += cr[:L]; i0 += len(cr)  # night ambience bed
out = np.clip(out, -1, 1)
with wave.open(P("mix_raw.wav"), "wb") as wv:
    wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes((out * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", P("mix_raw.wav"), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), P("mix.wav")], check=True)
os.remove(P("mix_raw.wav")); print("mixed", hits, "sfx hits")
