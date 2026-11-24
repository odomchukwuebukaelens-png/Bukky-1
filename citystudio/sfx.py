"""Generates an original sound-effects track for a video.

Usage:  python3 sfx.py OUT.wav SECONDS EVENTS.json
EVENTS.json is a list of {"kind": ..., "at": seconds, "dur": seconds, "gain": 1.0}.
Kinds: fire, wind, rain, fireworks, cheer, rumble, horn, bells.
Everything is synthesised here (no recordings), so there are no licence issues.
Runs with the normal system Python (needs numpy).
"""
import json
import os
import subprocess
import sys
import wave

import numpy as np

SR = 44100


def noise(n, rng):
    return rng.standard_normal(n)


def lowpass_fast(x, width):
    k = np.ones(width) / width
    return np.convolve(x, k, mode="same")


def envelope(n, attack, release):
    e = np.ones(n)
    a, r = min(n, int(attack * SR)), min(n, int(release * SR))
    if a:
        e[:a] = np.linspace(0, 1, a)
    if r:
        e[-r:] *= np.linspace(1, 0, r)
    return e


def fire(n, rng):
    roar = lowpass_fast(noise(n, rng), 60) * 2.5
    crackle = np.zeros(n)
    for _ in range(int(n / SR * 35)):
        at = rng.integers(0, max(1, n - 800))
        ln = rng.integers(60, 600)
        crackle[at:at + ln] += noise(ln, rng) * np.exp(-np.arange(ln) / (ln / 4)) * rng.uniform(0.3, 1.0)
    return roar * 0.5 + crackle * 0.35


def wind(n, rng):
    base = lowpass_fast(noise(n, rng), 200) * 6
    t = np.arange(n) / SR
    gust = 0.6 + 0.4 * np.sin(2 * np.pi * 0.13 * t) * np.sin(2 * np.pi * 0.07 * t + 1)
    return base * gust


def rain(n, rng):
    hiss = noise(n, rng) - lowpass_fast(noise(n, rng), 8)
    drops = np.zeros(n)
    for _ in range(int(n / SR * 120)):
        at = rng.integers(0, max(1, n - 300))
        ln = rng.integers(40, 250)
        drops[at:at + ln] += noise(ln, rng) * np.exp(-np.arange(ln) / (ln / 5)) * 0.3
    return hiss * 0.25 + drops


def fireworks(n, rng):
    out = np.zeros(n)
    t = 0
    while t < n:
        ln = min(int(SR * rng.uniform(0.8, 1.6)), n - t)
        k = np.arange(ln) / SR
        boom = np.sin(2 * np.pi * (70 - 25 * k) * k) * np.exp(-k * 5) * 1.2
        pop = noise(ln, rng) * np.exp(-k * 18) * 0.8
        fizz = noise(ln, rng) * np.exp(-k * 2.5) * 0.12 * (k > 0.1)
        out[t:t + ln] += boom + pop + fizz
        t += int(SR * rng.uniform(0.35, 0.9))
    return out


def cheer(n, rng):
    crowd = lowpass_fast(noise(n, rng), 18) * 3
    t = np.arange(n) / SR
    return crowd * (0.7 + 0.3 * np.sin(2 * np.pi * 0.5 * t))


def rumble(n, rng):
    t = np.arange(n) / SR
    deep = lowpass_fast(noise(n, rng), 600) * 14
    return deep * np.exp(-t / max(0.5, n / SR / 2.5))


def horn(n, rng):
    t = np.arange(n) / SR
    tone = sum(np.sin(2 * np.pi * f * t) / (i + 1) for i, f in enumerate((110, 220, 330, 440)))
    return tone * 0.35 * envelope(n, 0.15, 0.6)


def bells(n, rng):
    out = np.zeros(n)
    t0 = 0
    while t0 < n:
        ln = min(int(SR * 2.5), n - t0)
        k = np.arange(ln) / SR
        out[t0:t0 + ln] += sum(np.sin(2 * np.pi * f * k) * np.exp(-k * d) for f, d in
                               ((392, 1.2), (784, 2.0), (1176, 3.0), (523, 1.6))) * 0.25
        t0 += int(SR * 1.1)
    return out


def _hits(n, rng, rate, maker):
    out = np.zeros(n)
    t = int(rng.uniform(0, SR * 0.3))
    while t < n:
        sig = maker(rng)
        ln = min(len(sig), n - t)
        out[t:t + ln] += sig[:ln]
        t += int(SR / rate * rng.uniform(0.5, 1.6))
    return out


def _decay(ln, tau):
    return np.exp(-np.arange(ln) / (tau * SR))


def birds(n, rng):
    def chirp(r):
        ln = int(SR * r.uniform(0.05, 0.18))
        k = np.arange(ln) / SR
        f0, f1 = r.uniform(2500, 4200), r.uniform(1800, 5200)
        ph = 2 * np.pi * np.cumsum(f0 + (f1 - f0) * k / k[-1]) / SR
        return np.sin(ph) * np.sin(np.pi * k / k[-1]) * r.uniform(0.2, 0.6)
    return _hits(n, rng, 3.0, chirp) + wind(n, rng) * 0.15


def hammer_wood(n, rng):
    def knock(r):
        ln = int(SR * 0.18)
        k = np.arange(ln) / SR
        f = r.uniform(180, 320)
        return (np.sin(2 * np.pi * f * k) + 0.5 * np.sin(2 * np.pi * f * 2.7 * k)) * _decay(ln, 0.035) + \
            r.standard_normal(ln) * _decay(ln, 0.006) * 0.6
    return _hits(n, rng, 2.2, knock)


def chisel_stone(n, rng):
    def tap(r):
        ln = int(SR * 0.12)
        k = np.arange(ln) / SR
        ring = sum(np.sin(2 * np.pi * f * k) / (i + 1) for i, f in enumerate((2100, 3370, 5150)))
        return ring * _decay(ln, 0.02) * 0.5 + r.standard_normal(ln) * _decay(ln, 0.004)
    return _hits(n, rng, 3.5, tap)


def saw(n, rng):
    t = np.arange(n) / SR
    stroke = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 1.4 * t))
    return (rng.standard_normal(n) - lowpass_fast(rng.standard_normal(n), 6)) * stroke * 0.6


def chatter(n, rng):
    """Babble of many voices: noise shaped by moving 'vowel' formants."""
    out = np.zeros(n)
    t = np.arange(n) / SR
    for v in range(8):
        f0 = rng.uniform(110, 240)
        syl = 0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(3, 5.5) * t + rng.uniform(0, 6))
        gate = (np.sin(2 * np.pi * rng.uniform(0.15, 0.4) * t + rng.uniform(0, 6)) > -0.2).astype(float)
        voice = np.sign(np.sin(2 * np.pi * f0 * (1 + 0.03 * np.sin(2 * np.pi * 4 * t)) * t))
        voice = lowpass_fast(voice, rng.integers(6, 14))
        out += voice * syl * lowpass_fast(gate, 2000) * rng.uniform(0.5, 1.0)
    return out + lowpass_fast(rng.standard_normal(n), 30) * 0.8


def hooves(n, rng):
    def clop(r):
        ln = int(SR * 0.07)
        k = np.arange(ln) / SR
        return (np.sin(2 * np.pi * r.uniform(500, 800) * k) * 0.6 + r.standard_normal(ln) * 0.5) * _decay(ln, 0.012)
    out = np.zeros(n)
    t = 0
    while t < n:
        for d in (0.0, 0.09, 0.3, 0.39):
            at = t + int(d * SR)
            sig = clop(rng)
            ln = min(len(sig), n - at)
            if ln > 0:
                out[at:at + ln] += sig[:ln]
        t += int(SR * 0.6)
    return out


def cart(n, rng):
    t = np.arange(n) / SR
    rumble = lowpass_fast(rng.standard_normal(n), 120) * 4 * (0.8 + 0.2 * np.sin(2 * np.pi * 3 * t))
    creak = np.sin(2 * np.pi * (400 + 60 * np.sin(2 * np.pi * 0.7 * t)) * t) * (np.sin(2 * np.pi * 0.7 * t) > 0.9) * 0.2
    return rumble + creak + hooves(n, rng) * 0.6


def traffic(n, rng):
    t = np.arange(n) / SR
    hum = lowpass_fast(rng.standard_normal(n), 250) * 8
    swish = np.zeros(n)
    at = 0
    while at < n:
        ln = min(int(SR * rng.uniform(1.5, 3.0)), n - at)
        k = np.arange(ln) / ln
        swish[at:at + ln] += (rng.standard_normal(ln) - lowpass_fast(rng.standard_normal(ln), 4)) * np.sin(np.pi * k) ** 2 * 0.25
        at += int(SR * rng.uniform(0.6, 2.0))
    engine = np.sin(2 * np.pi * (55 + 8 * np.sin(2 * np.pi * 0.2 * t)) * t) * 0.15
    return hum + swish + engine


def carhorn(n, rng):
    out = np.zeros(n)
    at = int(SR * rng.uniform(0, 0.8))
    while at < n:
        ln = min(int(SR * rng.uniform(0.25, 0.7)), n - at)
        k = np.arange(ln) / SR
        f = rng.choice([392.0, 440.0, 349.0])
        tone = np.sign(np.sin(2 * np.pi * f * k)) * 0.5 + np.sign(np.sin(2 * np.pi * f * 1.26 * k)) * 0.5
        out[at:at + ln] += lowpass_fast(tone, 5) * envelope(ln, 0.01, 0.05)
        at += int(SR * rng.uniform(1.5, 4.0))
    return out


def scooter(n, rng):
    out = np.zeros(n)
    at = 0
    while at < n:
        ln = min(int(SR * rng.uniform(2.0, 4.0)), n - at)
        k = np.arange(ln) / SR
        f = 90 + 70 * np.sin(np.pi * k / k[-1]) + rng.uniform(-10, 10)
        ph = 2 * np.pi * np.cumsum(f) / SR
        buzz = (ph / np.pi % 2 - 1) * 0.5
        out[at:at + ln] += lowpass_fast(buzz, 4) * np.sin(np.pi * k / k[-1]) ** 2
        at += int(SR * rng.uniform(2.5, 6.0))
    return out


def siren(n, rng):
    t = np.arange(n) / SR
    f = 650 + 350 * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 0.7 * t)))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.6


def sword(n, rng):
    def clash(r):
        ln = int(SR * 0.6)
        k = np.arange(ln) / SR
        ring = sum(np.sin(2 * np.pi * f * k + r.uniform(0, 6)) / (i + 1)
                   for i, f in enumerate(r.uniform(1800, 2200) * np.array([1, 2.76, 5.4, 8.9])))
        return ring * _decay(ln, 0.09) * 0.6 + r.standard_normal(ln) * _decay(ln, 0.01)
    return _hits(n, rng, 4.0, clash)


def shouts(n, rng):
    def yell(r):
        ln = int(SR * r.uniform(0.4, 0.9))
        k = np.arange(ln) / SR
        f = r.uniform(140, 260) * (1 + 0.25 * np.sin(np.pi * k / k[-1]))
        v = lowpass_fast(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)), 8)
        return v * np.sin(np.pi * k / k[-1]) * r.uniform(0.3, 0.7)
    return _hits(n, rng, 6.0, yell) + chatter(n, rng) * 0.4


def march(n, rng):
    out = np.zeros(n)
    beat = int(SR * 0.5)
    for at in range(0, n, beat):
        ln = min(int(SR * 0.12), n - at)
        out[at:at + ln] += lowpass_fast(rng.standard_normal(ln), 40) * 6 * _decay(ln, 0.03)
        jl = min(int(SR * 0.1), n - at)
        out[at:at + jl] += (rng.standard_normal(jl) - lowpass_fast(rng.standard_normal(jl), 3)) * _decay(jl, 0.02) * 0.3
    return out


def drums(n, rng):
    out = np.zeros(n)
    pattern = (0.0, 0.5, 0.75, 1.0, 1.5)
    t = 0
    while t < n:
        for d in pattern:
            at = t + int(d * SR)
            ln = min(int(SR * 0.4), n - at) if at < n else 0
            if ln > 0:
                k = np.arange(ln) / SR
                out[at:at + ln] += np.sin(2 * np.pi * (90 - 40 * k) * k) * _decay(ln, 0.12)
        t += int(SR * 2.0)
    return out


def bomb(n, rng):
    out = np.zeros(n)
    at = 0
    while at < n:
        wl = min(int(SR * 1.2), n - at)
        k = np.arange(wl) / SR
        out[at:at + wl] += np.sin(2 * np.pi * np.cumsum(1800 - 1100 * k / 1.2) / SR) * 0.12 * (k / 1.2)
        b = at + wl
        bl = min(int(SR * 2.5), n - b)
        if bl > 0:
            kb = np.arange(bl) / SR
            out[b:b + bl] += (lowpass_fast(rng.standard_normal(bl), 300) * 18 + rng.standard_normal(bl) * np.exp(-kb * 30)) \
                * np.exp(-kb * 1.6)
        at += int(SR * rng.uniform(2.5, 4.5))
    return out


def cannon(n, rng):
    def boom(r):
        ln = int(SR * 2.0)
        k = np.arange(ln) / SR
        return (lowpass_fast(r.standard_normal(ln), 200) * 14 + r.standard_normal(ln) * np.exp(-k * 40)) * np.exp(-k * 2.2)
    return _hits(n, rng, 0.5, boom)


def gunfire(n, rng):
    def shot(r):
        ln = int(SR * 0.3)
        k = np.arange(ln) / SR
        return r.standard_normal(ln) * np.exp(-k * 35) + lowpass_fast(r.standard_normal(ln), 60) * 4 * np.exp(-k * 12)
    return _hits(n, rng, 3.0, shot)


def tram(n, rng):
    t = np.arange(n) / SR
    rumble = lowpass_fast(rng.standard_normal(n), 200) * 6
    clack = np.zeros(n)
    for at in range(0, n, int(SR * 0.9)):
        ln = min(int(SR * 0.05), n - at)
        clack[at:at + ln] += rng.standard_normal(ln) * 0.4
    bell = np.zeros(n)
    for at in range(int(SR * 1.5), n, int(SR * 9)):
        ln = min(int(SR * 0.8), n - at)
        k = np.arange(ln) / SR
        bell[at:at + ln] += (np.sin(2 * np.pi * 1320 * k) + 0.4 * np.sin(2 * np.pi * 2640 * k)) * np.exp(-k * 5) * 0.3
    return rumble + clack + bell


def water(n, rng):
    return lowpass_fast(rng.standard_normal(n), 25) * 2 + (rng.standard_normal(n) - lowpass_fast(rng.standard_normal(n), 3)) * 0.08


def chant(n, rng):
    """Many voices shouting together on a beat (an army's war cry, e.g. "Ei! Ei! O!")."""
    out = np.zeros(n)
    t = int(SR * 0.2)
    k = 0
    while t < n:
        ln = min(int(SR * (0.35 if k % 3 < 2 else 0.8)), n - t)
        kk = np.arange(ln) / SR
        voice = np.zeros(ln)
        for v in range(14):
            f = rng.uniform(110, 190) * (1.0 if k % 3 < 2 else 1.25)
            voice += lowpass_fast(np.sign(np.sin(2 * np.pi * f * (1 + 0.04 * kk) * kk + rng.uniform(0, 6))), 7)
        env = np.minimum(1, kk / 0.03) * np.exp(-kk / (0.25 if k % 3 < 2 else 0.6))
        out[t:t + ln] += voice * env / 14 + rng.standard_normal(ln) * env * 0.15
        t += int(SR * (0.55 if k % 3 < 2 else 1.6))
        k += 1
    return out


KINDS = {"fire": fire, "wind": wind, "rain": rain, "fireworks": fireworks, "cheer": cheer, "rumble": rumble,
         "horn": horn, "bells": bells, "birds": birds, "hammer": hammer_wood, "chisel": chisel_stone, "saw": saw,
         "chatter": chatter, "hooves": hooves, "cart": cart, "traffic": traffic, "carhorn": carhorn, "scooter": scooter,
         "siren": siren, "sword": sword, "shouts": shouts, "march": march, "drums": drums, "bomb": bomb,
         "cannon": cannon, "gunfire": gunfire, "tram": tram, "water": water, "chant": chant}
LEVEL = {"fire": 0.35, "wind": 0.30, "rain": 0.30, "fireworks": 0.45, "cheer": 0.25, "rumble": 0.55,
         "horn": 0.25, "bells": 0.20, "birds": 0.18, "hammer": 0.22, "chisel": 0.15, "saw": 0.10, "chatter": 0.22,
         "hooves": 0.18, "cart": 0.20, "traffic": 0.28, "carhorn": 0.16, "scooter": 0.14, "siren": 0.10,
         "sword": 0.30, "shouts": 0.30, "march": 0.30, "drums": 0.35, "bomb": 0.55, "cannon": 0.50,
         "gunfire": 0.30, "tram": 0.18, "water": 0.12, "chant": 0.40}


REAL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "sfx")
_real_cache = {}


def real_sound(kind):
    """A recorded sound for this kind, if one was supplied (assets/sfx/<kind>*.mp3|wav), as stereo float."""
    if kind in _real_cache:
        return _real_cache[kind]
    found = None
    if os.path.isdir(REAL_DIR):
        for f in sorted(os.listdir(REAL_DIR)):
            if f.lower().startswith(kind) and f.lower().rsplit(".", 1)[-1] in ("mp3", "wav", "ogg", "m4a", "flac"):
                found = os.path.join(REAL_DIR, f)
                break
    data = None
    if found:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", found, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                             capture_output=True, check=True).stdout
        data = np.frombuffer(raw, dtype="<f4").reshape(-1, 2).astype(np.float64)
        data /= max(1e-9, np.max(np.abs(data)))
    _real_cache[kind] = data
    return data


def build(seconds, events, seed=5):
    rng = np.random.default_rng(seed)
    total = int(seconds * SR)
    left = np.zeros(total)
    right = np.zeros(total)
    for ev in events:
        at = int(ev["at"] * SR)
        if at >= total or ev["kind"] not in KINDS:
            continue
        n = min(int(ev["dur"] * SR), total - at)
        if n <= SR // 10:
            continue
        env = envelope(n, min(1.0, ev["dur"] / 4), min(1.5, ev["dur"] / 3)) * ev.get("gain", 1.0)
        rec = real_sound(ev["kind"])
        if rec is not None:
            reps = int(np.ceil(n / len(rec)))
            off = int(rng.integers(0, len(rec)))
            loop = np.roll(np.tile(rec, (reps + 1, 1)), -off, axis=0)[:n]
            left[at:at + n] += loop[:, 0] * env * 0.55
            right[at:at + n] += loop[:, 1] * env * 0.55
            continue
        sig = KINDS[ev["kind"]](n, rng)
        sig = sig / max(1e-9, np.max(np.abs(sig)))
        sig *= env * LEVEL[ev["kind"]]
        pan = rng.uniform(-0.3, 0.3)
        left[at:at + n] += sig * (1 - pan)
        right[at:at + n] += sig * (1 + pan)
    st = np.stack([left, right], axis=1)
    peak = np.max(np.abs(st))
    if peak > 0.95:
        st *= 0.95 / peak
    return st


def write(path, st):
    data = (np.clip(st, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


if __name__ == "__main__":
    out, secs, path = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    with open(path) as f:
        events = json.load(f)
    write(out, build(secs, events))
    print("[city-studio] Sound effects written: %s (%d effects)" % (out, len(events)))
