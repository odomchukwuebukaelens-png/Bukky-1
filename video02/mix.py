"""Video 02 mix: narration + library music (never regenerated) + SFX cued per shot -> mix.wav (-14 LUFS)."""
import json, os, subprocess, wave
import numpy as np

D = os.path.dirname(os.path.abspath(__file__)); P = lambda n: os.path.join(D, n)
MUSIC = os.path.join(D, "..", "assets", "music"); SFX1 = os.path.join(D, "..", "video01", "audio", "sfx"); SFX2 = P("audio/sfx")
SR = 44100
def load(path, offset=0.0):
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(offset), "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.float32).reshape(-1, 2).copy()
db = lambda x: 10 ** (x / 20)
voice = load(P("narration.wav")); N = len(voice) + SR
out = np.zeros((N, 2), np.float32); out[:len(voice)] += voice
words = json.load(open(P("words_final.json"))); edl = json.load(open(P("edl.json")))
start = {s["setup"]: s["start"] for s in edl}; end = len(voice) / SR + 1.0

# music from the shared library, different takes/offsets than Video 01
SECT = [(0.0, start["SQUIRREL_DAY"], "m2_dread_bed_a", 75.0, -23, 0.4, 0.3),
        (start["SQUIRREL_DAY"], start["EYES_GONE"], "m1_sunday_warm_b", 42.0, -20, 0.15, 0.02),  # comedy beat
        (start["EYES_GONE"] + 0.4, end, "m3_tension_pulse_b", 20.0, -24, 1.2, 1.0)]
music = np.zeros_like(out)
for a, b, name, off, g, fi, fo in SECT:
    m = load(os.path.join(MUSIC, name + ".mp3"), off); n = int((b - a) * SR); m = m[:n] * db(g)
    env = np.ones(len(m), np.float32); k1, k2 = int(fi * SR), int(fo * SR)
    if k1: env[:k1] = np.linspace(0, 1, min(k1, len(env)))
    if k2: env[-k2:] = np.minimum(env[-k2:], np.linspace(1, 0, k2))
    i0 = int(a * SR); music[i0:i0 + len(m)] += m * env[:, None]
duck = np.ones(N, np.float32)
for w in words: duck[int(w["start"] * SR):int(w["end"] * SR)] = db(-6)
k = int(0.12 * SR); duck = np.convolve(duck, np.ones(k) / k, mode="same").astype(np.float32)
out += music * duck[:, None]

CUES = [("DOG_EYES_DARK", "drone_hit", -9, 0), ("YARD_WIDE_DOOR_LIGHT", "crickets", -20, 0), ("INS_DOOR_HANDLE", "clink", -14, 0.5),
        ("KT_DONT_GO", "text_slam", -9, 0), ("SQUIRREL_DAY", "dog_woof", -10, 0.2), ("SQUIRREL_TREE", "dog_woof", -10, 0.1),
        ("EYES_GONE", "freeze_cut", -8, 0), ("CLOCK_CARD", "clock_tick", -14, 0), ("DOOR_OPENS_OUT", "door_open", -9, 0),
        ("YARD_FROM_PORCH", "crickets", -18, 0), ("DOG_HEAD_TURN", "whoosh", -16, 0), ("DOORWAY_BEHIND_YOU", "heartbeat", -11, 0),
        ("HALL_PUSH", "room_tone_dread", -16, 0), ("DOG_BACKS_AWAY", "dog_growl", -6, 0)]
for setup, name, g, dt in CUES:
    f = os.path.join(SFX2 if os.path.exists(os.path.join(SFX2, name + ".mp3")) else SFX1, name + ".mp3")
    x = load(f) * db(g); i0 = int((start[setup] + dt) * SR); out[i0:i0 + len(x)] += x[:max(0, N - i0)]
out = np.clip(out, -1, 1)
with wave.open(P("mix_raw.wav"), "wb") as wv:
    wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes((out * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", P("mix_raw.wav"), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), P("mix.wav")], check=True)
os.remove(P("mix_raw.wav")); print("mixed", len(CUES), "sfx cues")
