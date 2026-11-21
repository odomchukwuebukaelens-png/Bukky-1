"""Video 03 mix. Music ONLY from assets/music (never regenerated); SFX from this video + video01 library."""
import json, os, re, subprocess, wave
import numpy as np
D = os.path.dirname(os.path.abspath(__file__)); P = lambda n: os.path.join(D, n)
MUSIC = os.path.join(D, "..", "assets", "music"); SFXD = [P("audio/sfx"), os.path.join(D, "..", "video01", "audio", "sfx")]
SR = 44100
def load(path, offset=0.0):
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(offset), "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.float32).reshape(-1, 2).copy()
def sfx(name):
    for d in SFXD:
        f = os.path.join(d, name + ".mp3")
        if os.path.exists(f): return f
db = lambda x: 10 ** (x / 20)
voice = load(P("narration.wav")); N = len(voice) + 2 * SR
out = np.zeros((N, 2), np.float32); out[:len(voice)] += voice
words = json.load(open(P("words_final.json"))); edl = json.load(open(P("edl.json")))
T = {}
for s in edl: T.setdefault(s["sentence"], s["start"])
end = len(voice) / SR + 1.5
def bed(a, b, name, off, g, fi=1.0, fo=1.2, src=None):
    n = int((b - a) * SR); m = load(src or os.path.join(MUSIC, name + ".mp3"), off)
    if len(m) < n: m = np.concatenate([m] * (n // len(m) + 1))
    m = m[:n] * db(g); env = np.ones(n, np.float32); k1, k2 = int(fi * SR), int(fo * SR)
    env[:k1] = np.linspace(0, 1, k1); env[-k2:] = np.minimum(env[-k2:], np.linspace(1, 0, k2))
    i0 = int(a * SR); return i0, m * env[:, None]
music = np.zeros_like(out)
for a, b, name, off, g in [(0.0, T[4], "m5_end_lullaby_a", 40, -24), (T[4], T[5], "m1_sunday_warm_b", 90, -20), (T[5], T[30], "m2_dread_bed_a", 30, -24),
                           (T[30], T[66], "m3_tension_pulse_a", 10, -24), (T[66], T[72], "m4_memory_piano_a", 60, -21), (T[72], T[93], "m2_dread_bed_b", 150, -24),
                           (T[93], T[116], "m3_tension_pulse_b", 40, -24), (T[116], T[124], "m4_memory_piano_b", 90, -20), (T[124], T[131], "m2_dread_bed_a", 120, -24),
                           (T[131], T[135], "m1_sunday_warm_a", 120, -21), (T[135], end, "m4_memory_piano_a", 140, -20)]:
    i0, m = bed(a, b, name, off, g); music[i0:i0 + len(m)] += m
duck = np.ones(N, np.float32)
for w in words: duck[int(w["start"] * SR):int(w["end"] * SR)] = db(-6)
k = int(0.12 * SR); duck = np.convolve(duck, np.ones(k) / k, mode="same").astype(np.float32)
out += music * duck[:, None]
# diegetic beds: the truck's jingle where the story says the song is playing; engine idling while parked; crickets all night
for a, b, name, g in [(T[0], T[4], "truck_jingle", -22), (T[9], T[16], "truck_jingle", -20), (T[31], T[38], "truck_jingle", -24),
                      (T[94], T[103], "truck_jingle", -22), (T[16], T[124], "engine_idle", -30), (0, end, "crickets", -27)]:
    i0, m = bed(a, b, None, 0, g, 0.8, 1.0, sfx(name)); out[i0:i0 + len(m)] += m * duck[i0:i0 + len(m), None]
RULES = [(r"^STICK#\d+:\d", "stinger_card", -9), (r"^STICK#\d+:w", "whoosh", -14), (r"^KT", "text_slam", -10), (r"bell", "bell_ding", -8),
         (r":open", "window_slide", -10), (r"coin", "coins", -10), (r"close", "door_soft", -8), (r"pancakes|flip", "sizzle", -14),
         (r"hum", "kid_hum", -14), (r"^MASON#\d+:file", "stamp", -10), (r"^CLOCK", "clock_tick", -14), (r"flash", "glitch", -14),
         (r"^COUNTDOWN", "heartbeat", -12), (r"tiptoe|stairs", "footsteps", -14), (r"receipt", "receipt", -12), (r"jar|handover", "buzz", -20)]
last, hits, cache = {}, 0, {}
for s in edl:
    for pat, name, g in RULES:
        if re.search(pat, s["setup"]) and s["start"] - last.get(name, -9) > 1.2 and sfx(name):
            if name not in cache: cache[name] = load(sfx(name))
            x = cache[name] * db(g); i0 = int(s["start"] * SR); out[i0:i0 + len(x)] += x[:max(0, N - i0)]
            last[name] = s["start"]; hits += 1; break
out = np.clip(out, -1, 1)
with wave.open(P("mix_raw.wav"), "wb") as wv:
    wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes((out * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", P("mix_raw.wav"), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), P("mix.wav")], check=True)
os.remove(P("mix_raw.wav")); print("mixed", hits, "sfx hits")
