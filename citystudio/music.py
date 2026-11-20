"""Generates an original ambient score: slow pads, bass, a soft arpeggio and
reverb, in a minor key, for any length. Nothing is sampled or copied.

Usage:  python3 music.py OUT.wav SECONDS [SEED] [BUILD_AT_SECONDS]
Runs with the normal system Python (needs numpy), not inside Blender.
"""
import sys
import wave

import numpy as np

SR = 44100
BPM = 66.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
# D minor: i - VI - III - VII, then i - iv - VI - V
PROGRESSION = [
    (38, [57, 62, 65, 69]), (34, [58, 62, 65, 70]), (41, [57, 60, 65, 69]), (36, [55, 60, 64, 67]),
    (38, [57, 62, 65, 69]), (43, [55, 62, 67, 70]), (34, [58, 62, 65, 70]), (33, [57, 61, 64, 69]),
]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def env(n, attack, release):
    e = np.ones(n)
    a, r = int(attack * SR), int(release * SR)
    if a:
        e[:a] = np.linspace(0, 1, a) ** 2
    if r:
        e[-r:] *= np.linspace(1, 0, r) ** 1.5
    return e


def pad_voice(freq, n, rng):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for detune in (-0.0018, 0.0018):
        f = freq * (1 + detune)
        vib = 1 + 0.0015 * np.sin(2 * np.pi * rng.uniform(4.5, 5.5) * t + rng.uniform(0, 6))
        ph = 2 * np.pi * np.cumsum(f * vib) / SR
        for k in range(1, 9):
            out += np.sin(k * ph + rng.uniform(0, 6)) / k ** 1.7
    return out


def pluck(freq, n):
    t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * freq * t) + 0.32 * np.sin(4 * np.pi * freq * t) + 0.08 * np.sin(6 * np.pi * freq * t)
    return tone * np.exp(-t * 2.4) * np.minimum(1, t / 0.004)


def reverb(x, seconds, seed):
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * (6.9 / seconds))
    ir = np.convolve(ir, np.ones(12) / 12, mode="same")          # darken the tail
    ir[: int(0.02 * SR)] = 0
    ir /= np.sqrt(np.sum(ir ** 2))
    # overlap-add so long scores fit in memory
    block = 1 << 18
    size = 1 << int(np.ceil(np.log2(block + n)))
    H = np.fft.rfft(ir, size)
    out = np.zeros(len(x) + n)
    for i in range(0, len(x), block):
        seg = x[i:i + block]
        y = np.fft.irfft(np.fft.rfft(seg, size) * H, size)[: len(seg) + n]
        out[i:i + len(y)] += y
    return out[: len(x)]


def compose(seconds, seed=1, build_at=4.0):
    rng = np.random.default_rng(seed)
    total = int(seconds * SR)
    pads = np.zeros(total + SR * 3)
    bass = np.zeros_like(pads)
    arp = np.zeros_like(pads)
    bar_n = int(BAR * SR)
    bars = int(np.ceil(seconds / BAR)) + 1
    for b in range(bars):
        root, tones = PROGRESSION[b % len(PROGRESSION)]
        start = b * bar_n
        n = bar_n + int(1.6 * SR)                                   # overlap into next chord
        if start >= len(pads):
            break
        n = min(n, len(pads) - start)
        e = env(n, 1.4, 1.6)
        for m in tones:
            pads[start:start + n] += pad_voice(hz(m), n, rng) * e * 0.10
        t = np.arange(n) / SR
        bass[start:start + n] += (np.sin(2 * np.pi * hz(root) * t) + 0.25 * np.sin(4 * np.pi * hz(root) * t)) * e * 0.30
        # arpeggio in eighth notes, entering once the story starts moving
        pattern = [tones[0] + 12, tones[1] + 12, tones[2] + 12, tones[3] + 12, tones[2] + 12, tones[1] + 12,
                   tones[2] + 12, tones[3] + 12]
        for k, m in enumerate(pattern):
            at = start + int(k * BEAT / 2 * SR)
            if at / SR < build_at or at >= len(arp):
                continue
            ln = min(int(1.8 * SR), len(arp) - at)
            arp[at:at + ln] += pluck(hz(m), ln) * rng.uniform(0.75, 1.0) * 0.16
    # a low swell where the story begins
    if 0 < build_at < seconds:
        at = int(build_at * SR)
        ln = min(int(3.0 * SR), len(pads) - at)
        t = np.arange(ln) / SR
        boom = np.sin(2 * np.pi * (52 - 10 * t) * t) * np.exp(-t * 1.6) * np.minimum(1, t / 0.03)
        bass[at:at + ln] += boom * 0.45
    arp_ramp = np.clip((np.arange(len(arp)) / SR - build_at) / 6.0, 0, 1)
    dry = pads + bass + arp * arp_ramp
    left = 0.62 * dry + 0.55 * reverb(dry, 3.2, seed)
    right = 0.62 * dry + 0.55 * reverb(dry, 3.2, seed + 7)
    st = np.stack([left, right], axis=1)[:total]
    fade_in, fade_out = int(1.2 * SR), int(min(2.5, seconds / 4) * SR)
    st[:fade_in] *= np.linspace(0, 1, fade_in)[:, None]
    st[-fade_out:] *= np.linspace(1, 0, fade_out)[:, None]
    st /= max(1e-9, np.max(np.abs(st))) / 0.89                       # peak about -1 dBFS
    return st


def write(path, st):
    data = (np.clip(st, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


if __name__ == "__main__":
    out, secs = sys.argv[1], float(sys.argv[2])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    build = float(sys.argv[4]) if len(sys.argv) > 4 else 4.0
    write(out, compose(secs, seed, build))
    print("[city-studio] Music written: %s (%.1f s)" % (out, secs))
