"""Проверка качества превью: озвучка, синхронизация субтитров, кадры, читаемость.

Синхронизация проверяется НЕЗАВИСИМО от разметки: Whisper заново слушает
звуковую дорожку готового превью (голос + музыка + эффекты), и для каждого
экрана субтитров сравнивается момент появления текста с моментом, когда
первое слово реально звучит.
"""
import re
from difflib import SequenceMatcher
from pathlib import Path

from . import align
import numpy as np

from .common import SR, duration, read_audio, run

NUMBER_WORDS = {
    "en": set("zero one two three four five six seven eight nine ten eleven twelve thirteen "
              "fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty "
              "sixty seventy eighty ninety hundred thousand million billion dollars dollar".split()),
    "ru": set(),
}
SYNC_OK = 0.25     # сек: расхождение, которое глаз не замечает
MIN_ON_SCREEN = 0.45
MAX_CPS = 22       # символов в секунду — предел комфортного чтения


def _norm_tokens(text, lang):
    toks = re.sub(r"[^\w ]", " ", text.lower().replace("-", " ").replace("ё", "е")).split()
    nums = NUMBER_WORDS.get(lang, set())
    return [t for t in toks if t not in nums and not re.search(r"\d", t)]


def voice_report(tl, lang):
    rows, miss_total, tot = [], 0, 0
    for s in tl["scenes"]:
        heard = " ".join(w for w, _, _ in (align.whisper_words(s["wav"], lang) or []))
        ref, hyp = _norm_tokens(s["say"], lang), _norm_tokens(heard, lang)
        sm = SequenceMatcher(None, ref, hyp, autojunk=False)
        ok = sum(b.size for b in sm.get_matching_blocks())
        missed = [ref[i] for i in range(len(ref))
                  if not any(b.a <= i < b.a + b.size for b in sm.get_matching_blocks())]
        miss_total += len(ref) - ok
        tot += len(ref)
        clip = s["speech"]
        rows.append((s["id"], len(ref), missed, heard, clip))
    return rows, (100 * (tot - miss_total) / tot if tot else 0)


def sync_report(video, tl, lang):
    words, chunk_first = [], []
    for s in tl["scenes"]:
        for ch in s["chunks"]:
            chunk_first.append((len(words), ch))
            words.extend(ch["words"])
    ww = align.whisper_words(video, lang) or []
    # Whisper ставит начало слова после паузы слишком рано (захватывает тишину).
    # Уточняем по энергии чистой дорожки голоса: первое нарастание громкости.
    n = int(tl["total"] * SR) + SR
    voice = np.zeros(n, dtype=np.float32)
    for s in tl["scenes"]:
        a = read_audio(s["wav"])
        i = int(s["start"] * SR)
        voice[i:i + len(a)] += a[: n - i]
    loud = align.loudness_mask(voice, SR)
    snap = lambda t: align.snap_after_pause(t, loud)

    starts, _, mask = align.word_starts(words, video, tl["total"], lang, ww=ww, with_mask=True)
    out = []
    for wi, ch in chunk_first:
        txt = " ".join(w["w"] for w in ch["words"])
        dur = ch["end"] - ch["start"]
        cps = len(txt) / dur if dur > 0 else 99
        if mask[wi]:
            delta = snap(starts[wi]) - ch["start"]
        else:
            delta = None
        out.append((txt, ch["start"], delta, dur, cps))
    return out


def visual_report(project_dir, tl, fmt_w, fmt_h):
    rows = []
    for s in tl["scenes"]:
        need = s["end"] - s["start"]
        if not s["asset"]:
            rows.append((s["id"], s["visual"], "нет кадра", s.get("asset_hint") or ""))
            continue
        f = Path(project_dir) / "assets" / s["asset"]
        info = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                    "stream=width,height", "-of", "csv=p=0", f]).strip().split(",")
        w, h = int(info[0]), int(info[1])
        notes = []
        if f.suffix.lower() in (".mp4", ".mov", ".webm"):
            d = duration(f)
            if d < need:
                notes.append(f"клип {d:.1f} с короче сцены {need:.1f} с — будет зациклен")
        # вертикальный кадр из горизонтального: сколько ширины теряем при кадрировании
        if w / h > fmt_w / fmt_h * 1.05:
            kept = (h * fmt_w / fmt_h) / w
            notes.append(f"горизонтальный {w}×{h}: в 9:16 остаётся {kept:.0%} ширины — "
                         "проверьте, не обрезаны ли лица/объекты")
        if min(w, h) < min(fmt_w, fmt_h) * 0.9:
            notes.append(f"низкое разрешение {w}×{h}")
        rows.append((s["id"], s["visual"], s["asset"], "; ".join(notes) or "ок"))
    return rows


def write_report(project_dir, tl, brand, video):
    lang = brand.get("language", "ru")
    F = brand["formats"][tl["format"]]
    lines = [f"# Проверка качества: {tl['title']}", "",
             f"Файл: `{Path(video).name}` · {duration(video):.1f} с · формат {tl['format']} "
             f"(финал {F['w']}×{F['h']})", ""]

    rows, intel = voice_report(tl, lang)
    lines += ["## 1. Озвучка", "",
              f"Голос `{brand['voice']['model']}`. Разборчивость (Whisper узнал слов, без чисел): "
              f"**{intel:.0f}%**", "",
              "| Сцена | Слов | Не распознано | Что услышал Whisper |", "|---|---|---|---|"]
    for sid, n, missed, heard, _ in rows:
        lines.append(f"| {sid} | {n} | {', '.join(missed) or '—'} | {heard.strip()} |")
    lines += ["", "_Whisper не знает редких имён (Cadabra) — это не всегда ошибка диктора. "
              "Естественность интонации автоматически не измеряется: нужна проверка на слух._", ""]

    sync = sync_report(video, tl, lang)
    measured = [d for _, _, d, _, _ in sync if d is not None]
    bad = [x for x in sync if x[2] is not None and abs(x[2]) > SYNC_OK]
    lines += ["## 2. Синхронизация субтитров", "",
              f"Проверено экранов: {len(measured)} из {len(sync)} (остальные Whisper не узнал "
              "в миксе с музыкой). "
              + (f"Среднее |расхождение|: **{sum(abs(d) for d in measured) / len(measured):.2f} с**, "
                 f"максимум {max(abs(d) for d in measured):.2f} с. " if measured else "")
              + f"Порог незаметности: {SYNC_OK} с.", "",
              "| Субтитр | Появляется | Звучит | Δ, с | На экране, с | Символов/с |",
              "|---|---|---|---|---|---|"]
    for txt, st, d, dur, cps in sync:
        flag = ""
        if d is not None and abs(d) > SYNC_OK:
            flag += " ⚠️"
        if dur < MIN_ON_SCREEN or cps > MAX_CPS:
            flag += " 👁"
        lines.append(f"| {txt}{flag} | {st:.2f} | "
                     f"{(st + d):.2f} | {d:+.2f} |" if d is not None else
                     f"| {txt}{flag} | {st:.2f} | — | — |")
        lines[-1] += f" {dur:.2f} | {cps:.0f} |"
    lines += ["", "⚠️ — Whisper в миксе с музыкой услышал слово раньше/позже порога. Whisper "
              "систематически ставит начало слова после паузы на хвост предыдущего, поэтому "
              "⚠️ = «проверить на слух», а не доказанная ошибка. · 👁 — слишком быстро для чтения "
              f"(< {MIN_ON_SCREEN} с или > {MAX_CPS} симв/с)", ""]

    vis = visual_report(project_dir, tl, F["w"], F["h"])
    missing = [r for r in vis if r[2] == "нет кадра"]
    lines += ["## 3. Кадры и соответствие сценарию", "",
              f"Сцен с кадрами: **{len(vis) - len(missing)} из {len(vis)}**.", "",
              "| Сцена | Нужен кадр по сценарию | Файл | Замечания / запрос для поиска |",
              "|---|---|---|---|"]
    for sid, visual, asset, note in vis:
        lines.append(f"| {sid} | {visual} | {asset} | {note} |")
    lines += ["", "_Совпадение содержимого клипа со сценой автоматически не проверяется "
              "(нет зрения у конвейера) — проверка глазами по контактному листу._", ""]

    sb = brand["subtitles"]
    lines += ["## 4. Безопасные зоны Shorts", "",
              f"- Субтитры: центр строки на {sb['y'][tl['format']]:.0%} высоты, поля по 150 px "
              "справа/слева (кнопки YouTube справа, подпись канала снизу ~25% кадра).",
              f"- Hero-слово: {brand['hero']['y'][tl['format']]:.0%} высоты, ширина ≤ 86% кадра.",
              ""]
    out = Path(project_dir) / "qa.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out, intel, measured, bad, missing
