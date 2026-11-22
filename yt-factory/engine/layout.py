"""Пример расположения текста: реальные кадры в полном разрешении + зоны интерфейса Shorts.

Зоны интерфейса YouTube приблизительные: они зависят от телефона, длины подписи
и версии приложения. Это ориентир, а не спецификация YouTube.
"""
import shutil
import tempfile
from pathlib import Path

from . import subs, visuals
from .common import FONTS, run
from .shotlist import ZONES

# доли кадра 9:16: (x0, y0, x1, y1, подпись)
UI_ZONES = [
    (0.00, 0.00, 1.00, 0.07, "поиск / меню"),
    (0.87, 0.45, 1.00, 0.86, "кнопки"),
    (0.00, 0.78, 0.87, 1.00, "канал, подпись, звук, навигация"),
]


def _frame(tl, brand, scene_idx, t, w, h, fps, tmp):
    s = tl["scenes"][scene_idx]
    length = s["end"] - s["start"]
    clip = visuals.scene_clip(s, scene_idx, length, w, h, fps, brand, Path("."),
                              tmp / f"bg{scene_idx}.mp4", fast=True) if not s["asset"] else None
    if clip is None:
        raise RuntimeError("layout рассчитан на фон без ассета")
    ass = tmp / "subs.ass"
    ass.write_text(subs.build_ass(tl, brand, tl["format"], w, h), encoding="utf-8")
    out = tmp / f"f{scene_idx}.png"
    run(["ffmpeg", "-y", "-v", "error", "-i", clip, "-vf",
         f"setpts=PTS+{s['start']:.3f}/TB,ass={ass}:fontsdir={FONTS},select='gte(t\\,{t:.3f})'",
         "-frames:v", "1", out])
    return out


def _annotate(src, w, h, out):
    font = FONTS / "InterDisplay-Bold.otf"
    cmd = ["convert", src, "-font", font, "-pointsize", "34"]
    for x0, y0, x1, y1, label in UI_ZONES:
        X0, Y0, X1, Y1 = int(x0 * w), int(y0 * h), int(x1 * w) - 1, int(y1 * h) - 1
        cmd += ["-fill", "rgba(255,60,60,0.30)", "-stroke", "rgba(255,90,90,0.9)",
                "-strokewidth", "3", "-draw", f"rectangle {X0},{Y0} {X1},{Y1}",
                "-stroke", "none", "-fill", "white",
                "-annotate", f"+{X0 + 14}+{Y0 + 44}", label]
    for key, label, color in (("hero", "HERO: цифра/слово сцены", "rgba(80,200,255,0.95)"),
                              ("subs", "СУБТИТРЫ", "rgba(90,255,140,0.95)")):
        y0, y1 = ZONES[key]
        Y0, Y1 = int(y0 * h), int(y1 * h)
        # субтитры: поля по 150 px; hero: до 86% ширины (автоподбор кегля в subs.py)
        X0, X1 = (int(0.07 * w), int(0.93 * w)) if key == "hero" else (int(0.139 * w), int(0.861 * w))
        cmd += ["-fill", "none", "-stroke", color, "-strokewidth", "4",
                "-draw", f"rectangle {X0},{Y0} {X1},{Y1}",
                "-stroke", "none", "-fill", color, "-pointsize", "30",
                "-annotate", f"+{X0 + 8}+{Y0 - 12}", label, "-pointsize", "34"]
    run(cmd + [out])


def render(tl, brand, out_dir):
    F = brand["formats"][tl["format"]]
    w, h, fps = F["w"], F["h"], F["fps"]
    tmp = Path(tempfile.mkdtemp(prefix="ytf_lay_"))
    try:
        # сцена 1 — одна строка + hero-цифра; самая длинная строка субтитров — вторая панель
        s1 = 0
        c1 = tl["scenes"][s1]["chunks"][-1]
        longest = max(((i, ch) for i, sc in enumerate(tl["scenes"]) for ch in sc["chunks"]
                       if sc.get("hero")),
                      key=lambda x: len(" ".join(w["w"] for w in x[1]["words"])))
        f1 = _frame(tl, brand, s1, (c1["start"] + c1["end"]) / 2, w, h, fps, tmp)
        f2 = _frame(tl, brand, longest[0], (longest[1]["start"] + longest[1]["end"]) / 2,
                    w, h, fps, tmp)
        a1, a2 = tmp / "a1.png", tmp / "a2.png"
        _annotate(f1, w, h, a1)
        _annotate(f2, w, h, a2)
        out = Path(out_dir) / "layout_shorts_1080x1920.png"
        run(["montage", f1, a1, a2, "-tile", "3x1", "-geometry", f"{w // 2}x{h // 2}+12+12",
             "-background", "#111111", out])
        shutil.copy(f1, Path(out_dir) / "frame_scene1_1080x1920.png")
        return out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
