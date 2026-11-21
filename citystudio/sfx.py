"""Generates an original sound-effects track for a video.

Usage:  python3 sfx.py OUT.wav SECONDS EVENTS.json
EVENTS.json is a list of {"kind": ..., "at": seconds, "dur": seconds, "gain": 1.0}.
Kinds: fire, wind, rain, fireworks, cheer, rumble, horn, bells.
Everything is synthesised here (no recordings), so there are no licence issues.
Runs with the normal system Python (needs numpy).
"""
import json
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


KINDS = {"fire": fire, "wind": wind, "rain": rain, "fireworks": fireworks, "cheer": cheer, "rumble": rumble,
         "horn": horn, "bells": bells}
LEVEL = {"fire": 0.35, "wind": 0.30, "rain": 0.30, "fireworks": 0.45, "cheer": 0.25, "rumble": 0.55,
         "horn": 0.25, "bells": 0.20}


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
        sig = KINDS[ev["kind"]](n, rng)
        sig = sig / max(1e-9, np.max(np.abs(sig)))
        sig *= envelope(n, min(1.0, ev["dur"] / 4), min(1.5, ev["dur"] / 3)) * LEVEL[ev["kind"]] * ev.get("gain", 1.0)
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
