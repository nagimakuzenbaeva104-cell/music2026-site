"""Звук: голос + фоновая музыка (с приглушением под речь) + SFX на ключевых словах.

Если в brand.yaml задан audio.music (например трек из YouTube Audio Library),
используется он. Иначе синтезируется нейтральный эмбиент — это временная
замена, а не «готовая музыка».
"""
import numpy as np

from .common import ROOT, SR, read_audio


def db(x):
    return 10 ** (x / 20)


def one_pole_lowpass(x, cutoff):
    """Простой ФНЧ; cutoff может быть массивом (меняющаяся частота)."""
    cutoff = np.broadcast_to(np.asarray(cutoff, dtype=np.float32), x.shape)
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a[i]) * x[i] + a[i] * acc
        y[i] = acc
    return y


def whoosh(dur=0.55, seed=0):
    n = int(dur * SR)
    rng = np.random.default_rng(seed)
    noise = rng.standard_normal(n).astype(np.float32)
    t = np.linspace(0, 1, n, dtype=np.float32)
    cutoff = 300 + 5000 * np.sin(np.pi * t) ** 2
    y = one_pole_lowpass(noise, cutoff) - one_pole_lowpass(noise, cutoff * 0.25)
    env = np.clip(np.sin(np.pi * t), 0, 1) ** 1.5
    y = y * env
    return y / (np.abs(y).max() + 1e-9)


def hit(dur=0.45):
    """Мягкий «удар» под появление ключевого слова: низ + короткий клик."""
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float32) / SR
    f = 90 * np.exp(-t * 6) + 45
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    click = np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 120) * 0.25
    y = body + click
    return y / np.abs(y).max()


def ambient(total, seed=1):
    """Синт-эмбиент: медленные аккорды Am–F–C–G + низкий пульс. Временная замена музыки."""
    n = int(total * SR)
    t = np.arange(n, dtype=np.float32) / SR
    chords = [[110.0, 164.81, 220.0, 261.63], [87.31, 130.81, 174.61, 220.0],
              [130.81, 196.0, 261.63, 329.63], [98.0, 146.83, 196.0, 246.94]]
    seg = 4.0
    y = np.zeros(n, dtype=np.float32)
    for ci in range(int(np.ceil(total / seg)) + 1):
        start = ci * seg - 1.0
        ch = chords[ci % 4]
        a, b = max(int(start * SR), 0), min(int((start + seg + 2.0) * SR), n)
        if a >= b:
            continue
        tt = t[a:b] - start
        env = np.clip(tt / 1.5, 0, 1) * np.clip((seg + 2.0 - tt) / 1.5, 0, 1)
        tone = sum(np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 1.003 * tt)
                   for f in ch)
        y[a:b] += tone * env / len(ch)
    beat = 60 / 84  # 84 BPM, «напряжённый» документальный пульс
    ph = (t % beat)
    pulse = np.sin(2 * np.pi * 55 * ph) * np.exp(-ph * 14)
    y = 0.6 * y + 0.5 * pulse
    fade = np.clip(t / 1.5, 0, 1) * np.clip((total - t) / 1.5, 0, 1)
    return y * fade / (np.abs(y).max() + 1e-9)


def envelope(x, win=0.25):
    k = max(int(win * SR), 1)
    e = np.sqrt(np.convolve(x ** 2, np.ones(k) / k, mode="same"))
    return e


def build_mix(scene_wavs, scene_starts, total, sfx_events, brand):
    """Возвращает стерео-микс (n, 2) float32. Нормализация LUFS — при мультиплексе."""
    cfg = brand["audio"]
    n = int(total * SR) + SR
    voice = np.zeros(n, dtype=np.float32)
    for wav, st in zip(scene_wavs, scene_starts):
        a = read_audio(wav)
        i = int(st * SR)
        voice[i:i + len(a)] += a[: max(n - i, 0)]
    voice /= (np.abs(voice).max() + 1e-9)
    voice *= db(-3)

    if cfg.get("music"):
        m = read_audio(ROOT / cfg["music"])
        reps = int(np.ceil(n / len(m)))
        music = np.tile(m, reps)[:n]
        tt = np.arange(n) / SR
        music *= np.clip(tt / 1.0, 0, 1) * np.clip((total - tt) / 1.5, 0, 1)
        music /= (np.abs(music).max() + 1e-9)
    else:
        music = np.pad(ambient(total), (0, n - int(total * SR)))
    # приглушение музыки под речь (ducking)
    env = envelope(voice)
    talk = np.clip(env / (env.max() + 1e-9) * 4, 0, 1)
    talk = np.convolve(talk, np.ones(int(0.3 * SR)) / int(0.3 * SR), mode="same")
    duck = db(cfg.get("duck_db", -8)) ** talk
    music = music * db(cfg.get("music_db", -24)) * duck

    sfx = np.zeros(n, dtype=np.float32)
    for kind, at in sfx_events:
        s = whoosh(seed=int(at * 10)) if kind == "whoosh" else hit()
        # whoosh центрируем на склейке, hit — точно в момент слова
        i = int((at - (0.28 if kind == "whoosh" else 0.0)) * SR)
        i = max(i, 0)
        seg = s[: max(n - i, 0)]
        sfx[i:i + len(seg)] += seg * (0.7 if kind == "whoosh" else 1.0)
    sfx *= db(cfg.get("sfx_db", -16))

    mono = voice + music + sfx
    # лёгкая стереобаза для музыки/эффектов: голос по центру
    side = (music + sfx) * 0.15
    left, right = mono + side, mono - side
    return np.stack([left, right], axis=1)[: int(total * SR)]
