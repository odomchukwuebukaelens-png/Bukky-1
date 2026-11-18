"""Mix narration + music + SFX into mix.wav (stereo 44.1k, loudness-normalised to -14 LUFS).
Run after build.py (needs narration.wav, words_final.json, edl.json, sentences.json)."""
import json, os, re, subprocess, wave
import numpy as np

D = os.path.dirname(os.path.abspath(__file__)); P = lambda n: os.path.join(D, n)
SR = 44100

def load(path):
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.float32).reshape(-1, 2).copy()
db = lambda x: 10 ** (x / 20)

voice = load(P("narration.wav")); N = len(voice) + SR * 2
out = np.zeros((N, 2), np.float32); out[:len(voice)] += voice
words = json.load(open(P("words_final.json"))); edl = json.load(open(P("edl.json")))

# sentence start times (shifted), from the edl's first shot of each sentence
sent_t = {}
for s in edl: sent_t.setdefault(s["sentence"], s["start"])
T = lambda i: sent_t[i]

# ---- music sections: (start, end, file, gain_db, fade_in, fade_out) ----
end = len(voice) / SR + 1.5
SECT = [(0.0, T(7), "m2_dread_bed_b", -24, 0.3, 0.4),
        (T(7), T(12) + 2.6, "m1_sunday_warm_a", -22, 0.6, 0.02),       # hard stop on "they stop"
        (T(13), T(73), "m2_dread_bed_a", -23, 2.0, 1.5),
        (T(73), T(132), "m3_tension_pulse_a", -24, 1.5, 1.2),
        (T(132), T(146), "m4_memory_piano_a", -20, 1.0, 1.5),
        (T(146), T(158) + 0.9, "m3_tension_pulse_b", -23, 1.2, 0.02),  # cut to silence after "Dinner is over."
        (T(162), T(164), "m2_dread_bed_b", -26, 0.5, 0.5),
        (T(164), T(169), "m1_sunday_warm_b", -21, 1.0, 1.5),
        (T(169), end, "m5_end_lullaby_a", -21, 1.0, 2.5)]
music = np.zeros_like(out)
for a, b, name, g, fi, fo in SECT:
    m = load(P(f"audio/music/{name}.mp3")); n = int((b - a) * SR)
    if len(m) < n: m = np.concatenate([m] * (n // len(m) + 1))
    m = m[:n] * db(g); env = np.ones(n, np.float32)
    k1, k2 = int(fi * SR), int(fo * SR)
    if k1: env[:k1] = np.linspace(0, 1, k1)
    if k2: env[-k2:] = np.minimum(env[-k2:], np.linspace(1, 0, k2))
    i0 = int(a * SR); music[i0:i0 + n] += m * env[:, None]
# duck music 6 dB while words are spoken (smoothed)
duck = np.ones(N, np.float32)
for w in words:
    duck[int(w["start"] * SR):int(w["end"] * SR)] = db(-6)
k = int(0.12 * SR); duck = np.convolve(duck, np.ones(k) / k, mode="same").astype(np.float32)
out += music * duck[:, None]

# ---- SFX from shot cues ----
RULES = [(r"rule_card", "stinger_card", -10), (r"kt_text|smash_black_text|text slam", "text_slam", -10),
         (r"whip", "whoosh", -14), (r"hard freeze", "freeze_cut", -8), (r"drone hit", "drone_hit", -8),
         (r"grain lands|tick sfx", "tick_grain", -4), (r"heartbeat", "heartbeat", -10), (r"scrape", "chair_scrape", -8),
         (r"chew", "chew_wet", -10), (r"clink", "clink", -12), (r"buzz", "buzz", -16), (r"crickets", "crickets", -18),
         (r"walla|chatter", "walla", -20), (r"laugh", "laugh_family", -18), (r"clock", "clock_tick", -14),
         (r"candles flare|whoomp", "candle_whoomp", -10), (r"door opens", "door_open", -10), (r"door shuts|thud\b", "door_close", -10),
         (r"footsteps|footprints", "footsteps", -12), (r"vhs|rewind", "vhs_rewind", -16), (r"stamp", "stamp", -10),
         (r"receipt", "receipt", -12), (r"gulp|swallow", "gulp", -8), (r"kick", "kick_thud", -10),
         (r"gasp|breathing", "breath_gasp", -12), (r"metronome|click", "metronome", -10), (r"glitch|flash", "glitch", -18),
         (r"snap-zoom|whisked", "whoosh", -16)]
cache, placed, last = {}, [], {}
for s in edl:
    if s["motion"].startswith("micro-change"): continue
    cue = f"{s['setup']} {s['motion']} {s['note']}".lower()
    for pat, name, g in RULES:
        if re.search(pat, cue):
            f = P(f"audio/sfx/{name}.mp3")
            if not os.path.exists(f) or s["start"] - last.get(name, -9) < 0.6: continue
            if name not in cache: cache[name] = load(f)
            x = cache[name] * db(g); i0 = int(s["start"] * SR)
            out[i0:i0 + len(x)] += x[:max(0, N - i0)]; last[name] = s["start"]; placed.append((round(s["start"], 2), name))
# a bed of dread room tone under the frozen section
rt = P("audio/sfx/room_tone_dread.mp3")
if os.path.exists(rt):
    r = load(rt) * db(-26); a, b = int(T(13) * SR), int(T(164) * SR)
    rr = np.concatenate([r] * ((b - a) // len(r) + 1))[:b - a]; out[a:b] += rr

out = np.clip(out, -1, 1)
with wave.open(P("mix_raw.wav"), "wb") as wv:
    wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes((out * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", P("mix_raw.wav"), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                "-ar", str(SR), P("mix.wav")], check=True)
os.remove(P("mix_raw.wav"))
json.dump(placed, open(P("sfx_placed.json"), "w"))
print(f"mixed {len(placed)} sfx hits; missing sfx files: {sorted({n for _, n, _ in RULES} - {f[:-4] for f in os.listdir(P('audio/sfx'))})}")
