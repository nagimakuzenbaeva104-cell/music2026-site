"""Original kids instrumental for the Kokbala Short. 120 BPM, 36 s, C major.
Timeline (seconds): 0-2 hook, 2-18 verse 1 (4 lines x 4 s), 18-34 verse 2, 34-36 outro.
"""
import sys
import wave
import numpy as np

SR = 44100
BPM = 120
BEAT = 60 / BPM  # 0.5 s
TOTAL = 36.0
out = np.zeros(int(SR * TOTAL) + SR, dtype=np.float64)
rng = np.random.default_rng(7)


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def add(sig, t, gain=1.0):
    i = int(t * SR)
    out[i:i + len(sig)] += sig[: len(out) - i] * gain


def xylo(m, dur=0.45):
    n = int(SR * max(dur, 0.35))
    t = np.arange(n) / SR
    f = midi_hz(m)
    env = np.exp(-t * 9)
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 3.98 * t) * np.exp(-t * 25)
    att = np.minimum(1, t / 0.003)
    return s * env * att


def pluck(m, dur=0.9):
    """Karplus-Strong ukulele-ish pluck."""
    f = midi_hz(m)
    n = int(SR * dur)
    p = int(SR / f)
    buf = rng.uniform(-1, 1, p)
    y = np.zeros(n)
    for i in range(n):
        y[i] = buf[i % p]
        buf[i % p] = 0.5 * (buf[i % p] + buf[(i + 1) % p]) * 0.996
    return y * np.exp(-np.arange(n) / SR * 2.5)


def bass(m, dur=0.45):
    n = int(SR * dur)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * midi_hz(m) * t) * np.exp(-t * 4) * np.minimum(1, t / 0.01)


def clap():
    n = int(SR * 0.12)
    t = np.arange(n) / SR
    s = rng.uniform(-1, 1, n) * np.exp(-t * 40)
    # crude band emphasis
    return np.convolve(s, [1, -0.6], mode="same")


def kick():
    n = int(SR * 0.18)
    t = np.arange(n) / SR
    f = 110 * np.exp(-t * 25) + 45
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18)


def horn(dur=0.18):
    n = int(SR * dur)
    t = np.arange(n) / SR
    s = np.sign(np.sin(2 * np.pi * 440 * t)) * 0.5 + np.sign(np.sin(2 * np.pi * 554 * t)) * 0.5
    env = np.minimum(1, t / 0.01) * np.minimum(1, (dur - t) / 0.03)
    return s * env


CHORDS = {"C": [60, 64, 67], "F": [60, 65, 69], "G": [59, 62, 67]}
ROOT = {"C": 48, "F": 41, "G": 43}

# 4-second lines: (melody [(beat, midi, beats)], chords per 2-second bar)
LINE_A = ([(0, 72, 1), (1, 76, 1), (2, 79, 1), (3, 79, 1), (4, 81, 1), (5, 79, 1), (6, 76, 2)], ["C", "F"])
LINE_B = ([(0, 79, .5), (.5, 79, .5), (1, 79, 1), (2, 76, .5), (2.5, 76, .5), (3, 76, 1),
           (4, 74, .5), (4.5, 74, .5), (5, 74, 1), (6, 72, 2)], ["C", "G"])
LINE_C = ([(0, 72, 1), (1, 76, 1), (2, 79, 1), (3, 79, 1), (4, 81, 1), (5, 79, 1), (6, 84, 2)], ["C", "F"])
LINE_D = ([(0, 77, 1), (1, 76, 1), (2, 74, 1), (3, 71, 1), (4, 72, 4)], ["G", "C"])
VERSE = [LINE_A, LINE_B, LINE_C, LINE_D]


def play_line(start, line, mel_gain=0.32):
    mel, chords = line
    for b, m, d in mel:
        add(xylo(m, d * BEAT), start + b * BEAT, mel_gain)
    for bar, ch in enumerate(chords):
        t0 = start + bar * 4 * BEAT
        for beat in range(4):
            for k, m in enumerate(CHORDS[ch]):
                add(pluck(m, 0.6), t0 + beat * BEAT + k * 0.012, 0.11)
            add(bass(ROOT[ch] + (7 if beat % 2 else 0)), t0 + beat * BEAT, 0.35)
            add(kick() if beat % 2 == 0 else clap(), t0 + beat * BEAT, 0.35 if beat % 2 == 0 else 0.18)


# Hook 0-2 s: three horn beeps "би-би-бип" + glissando
for t, d in [(0.15, 0.16), (0.55, 0.16), (0.95, 0.45)]:
    add(horn(d), t, 0.16)
for i, m in enumerate([72, 74, 76, 77, 79, 81, 83, 84]):
    add(xylo(m, 0.3), 1.5 + i * 0.0625, 0.18)

# Verse 1 (wheels) and verse 2 (horn)
for v, vstart in enumerate([2.0, 18.0]):
    for i, line in enumerate(VERSE):
        play_line(vstart + i * 4.0, line)
    if v == 1:  # horn beeps on the "би-би-бип" lyric spots (end of lines 1-3)
        for ls in [18.0, 22.0, 26.0]:
            off = 2.0 if ls != 22.0 else 0.0
            for k, d in enumerate([0.14, 0.14, 0.3]):
                add(horn(d), ls + off + k * 0.5, 0.10)

# Outro 34-36: final C chord + sparkle
for k, m in enumerate([60, 64, 67, 72]):
    add(pluck(m, 1.8), 34.0 + k * 0.03, 0.15)
add(bass(36, 1.5), 34.0, 0.4)
for i, m in enumerate([84, 88, 91, 96]):
    add(xylo(m, 0.4), 34.2 + i * 0.12, 0.15)

mix = out[: int(SR * TOTAL)]
fade = int(SR * 0.6)
mix[-fade:] *= np.linspace(1, 0, fade)
mix = mix / np.max(np.abs(mix)) * 0.89
pcm = (mix * 32767).astype(np.int16)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("ok", len(pcm) / SR, "s")
