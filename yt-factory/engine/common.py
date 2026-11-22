"""Общие утилиты: пути, загрузка проекта и бренда, ffmpeg, аудио-ввод/вывод."""
import hashlib
import json
import subprocess
import wave
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / "fonts"
CHANNELS = ROOT / "channels"
CACHE = ROOT / ".cache"
VOICES = ROOT / "voices"
SR = 48000


class FactoryError(RuntimeError):
    pass


def run(cmd, quiet=True):
    """Запуск внешней команды; при ошибке показываем хвост stderr."""
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if r.returncode != 0:
        tail = "\n".join(r.stderr.strip().splitlines()[-15:])
        raise FactoryError(f"Команда упала: {' '.join(map(str, cmd[:4]))} ...\n{tail}")
    return r.stdout


def duration(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "default=nw=1:nk=1", path])
    return float(out.strip())


def digest(*parts):
    h = hashlib.sha1()
    for p in parts:
        h.update(json.dumps(p, sort_keys=True, ensure_ascii=False).encode())
    return h.hexdigest()[:16]


def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_project(project_dir):
    project_dir = Path(project_dir).resolve()
    sc = project_dir / "scenes.yaml"
    if not sc.exists():
        raise FactoryError(f"Нет файла {sc}")
    proj = load_yaml(sc)
    brand_path = CHANNELS / proj["channel"] / "brand.yaml"
    if not brand_path.exists():
        raise FactoryError(f"Нет бренда канала: {brand_path}")
    brand = load_yaml(brand_path)
    fmt_name = proj.get("format", "short")
    if fmt_name not in brand["formats"]:
        raise FactoryError(f"Формат {fmt_name} не описан в brand.yaml")
    validate(proj)
    return project_dir, proj, brand, fmt_name


def validate(proj):
    import re
    for i, s in enumerate(proj["scenes"], 1):
        if not s.get("text"):
            raise FactoryError(f"Сцена {i}: пустой text")
        if s["text"].count("[") != s["text"].count("]"):
            raise FactoryError(f"Сцена {i}: непарные [ ] в ключевых словах")
        if re.search(r"\d", s["text"]) and not s.get("say"):
            raise FactoryError(
                f"Сцена {i}: в тексте есть цифры — добавьте поле say с числами "
                f"прописью в нужном падеже, иначе озвучка прочтёт их неверно")


def hex_to_ass(hex_color, alpha=0.0):
    """#RRGGBB -> &HAABBGGRR (ASS). alpha: 0 непрозрачно, 1 прозрачно."""
    h = hex_color.lstrip("#")
    r, g, b = h[0:2], h[2:4], h[4:6]
    a = int(round(alpha * 255))
    return f"&H{a:02X}{b}{g}{r}".upper()


def read_audio(path, sr=SR):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "s16le",
                          "-ac", "1", "-ar", str(sr), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


def write_wav(path, data, sr=SR):
    data = np.clip(np.nan_to_num(data), -1, 1)
    pcm = (data * 32767).astype(np.int16)
    if pcm.ndim == 2:
        ch = pcm.shape[1]
    else:
        ch = 1
    with wave.open(str(path), "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())
