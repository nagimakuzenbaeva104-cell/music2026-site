"""Разбивка текста на субтитры и привязка ко времени озвучки.

Текст субтитров всегда берётся из сценария (орфография автора).
Whisper используется только чтобы узнать, КОГДА прозвучало каждое слово.
"""
import os
import re
from difflib import SequenceMatcher

from .common import read_audio

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")  # Xet-хранилище HF бывает недоступно через прокси

_MODEL = None
VOWELS = set("аеёиоуыэюяaeiouy")
END_PUNCT = re.compile(r"[.,!?:;…—–-]$")


def parse_words(text):
    """'Ушёл с [Уолл-стрит].' -> [{'w':'Ушёл','key':False}, ..., {'w':'Уолл-стрит.','key':True}]"""
    words, key = [], False
    for tok in re.findall(r"\[|\]|[^\s\[\]]+", text):
        if tok == "[":
            key = True
        elif tok == "]":
            key = False
        else:
            # пунктуация после ']' и отдельное тире приклеиваются к предыдущему слову
            if re.fullmatch(r"[.,!?:;…—–]+", tok) and words:
                words[-1]["w"] += tok if tok[0] not in "—–" else " " + tok
                continue
            words.append({"w": tok, "key": key})
    return words


def chunk(words, max_words, max_chars):
    """Слова -> экраны субтитров. Режем по пунктуации и по лимитам."""
    chunks, cur = [], []
    for w in words:
        cand = cur + [w]
        text_len = len(" ".join(x["w"] for x in cand))
        if cur and (len(cand) > max_words or text_len > max_chars):
            chunks.append(cur)
            cur = [w]
        else:
            cur = cand
        if END_PUNCT.search(w["w"]) and len(cur) >= 1:
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    # короткий предлог/союз в конце экрана переносим на следующий экран
    for i in range(len(chunks) - 1):
        last = chunks[i][-1]["w"]
        if len(chunks[i]) > 1 and len(last) <= 2 and not END_PUNCT.search(last):
            chunks[i + 1].insert(0, chunks[i].pop())
    # «висячее» одно короткое слово приклеиваем к предыдущему экрану, если влезает
    out = []
    for c in chunks:
        if out and len(c) == 1 and len(c[0]["w"]) <= 4 and \
                len(out[-1]) < max_words + 1 and not END_PUNCT.search(out[-1][-1]["w"]):
            out[-1] = out[-1] + c
        else:
            out.append(c)
    return out


def norm(w):
    w = w.lower().replace("ё", "е")
    return re.sub(r"[^\w]", "", w)


def syllables(w):
    n = sum(1 for ch in w.lower() if ch in VOWELS)
    if re.search(r"\d", w):
        n += 3 * len(re.findall(r"\d", w))
    return max(n, 1)


def whisper_words(wav_path, lang):
    """[(слово, начало, конец)] или None, если Whisper недоступен."""
    global _MODEL
    try:
        from faster_whisper import WhisperModel
        if _MODEL is None:
            _MODEL = WhisperModel("small", device="cpu", compute_type="int8")
        audio = read_audio(wav_path, 16000)
        segs, _ = _MODEL.transcribe(audio, language=lang, word_timestamps=True,
                                    vad_filter=False, beam_size=5)
        return [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]
    except Exception as e:  # noqa: BLE001 — фоллбэк на пропорциональную разметку
        print(f"  ! Whisper недоступен ({e.__class__.__name__}), тайминг по слогам")
        return None


def loudness_mask(audio, sr, thr=0.02):
    """Покадрово (10 мс): звучит ли голос."""
    import numpy as np
    fr = sr // 100
    return np.sqrt(np.convolve(audio ** 2, np.ones(fr) / fr, mode="same"))[::fr] > thr


def snap_after_pause(t, loud):
    """Whisper ставит начало слова после паузы слишком рано — на хвост предыдущего.
    Если в первые 0.12 с после отметки начинается тишина ≥ 0.1 с, слово на самом деле
    начинается там, где голос возвращается."""
    k = int(t * 100)
    j = k
    while j < min(k + 13, len(loud) - 10):   # провалы короче 0.1 с (микропаузы) пропускаем
        if loud[j]:
            j += 1
            continue
        end = j
        while end < len(loud) and not loud[end]:
            end += 1
        if end - j >= 10 and end < len(loud):
            return end / 100
        j = end
    return t


def word_starts(words, wav_path, speech_dur, lang, ww=None, with_mask=False):
    """Время начала каждого слова сценария. with_mask: + список «услышано ли слово»."""
    weights = [syllables(w["w"]) for w in words]
    total = sum(weights)
    prop, acc = [], 0.0
    for wt in weights:  # пропорциональная оценка (запасной вариант)
        prop.append(speech_dur * acc / total)
        acc += wt

    if ww is None:
        ww = whisper_words(wav_path, lang)
    if not ww:
        return (prop, "слоги", [False] * len(words)) if with_mask else (prop, "слоги")
    # Посимвольное сопоставление: устойчиво к тому, что Whisper склеивает/дробит
    # слова («Уолл-стрит» -> «Нолл Аль Стрит»). Текст сценария не меняется.
    a_str, a_pos = "", []
    for w in words:
        a_pos.append(len(a_str))
        a_str += norm(w["w"]) + " "
    b_str, b_time = "", []
    for txt, t0, t1 in ww:
        n = norm(txt)
        for ci, ch in enumerate(n):
            b_str += ch
            b_time.append(t0 + (t1 - t0) * ci / max(len(n), 1))
        b_str += " "
        b_time.append(t1)
    amap = {}
    for blk in SequenceMatcher(None, a_str, b_str, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            amap[blk.a + k] = b_time[blk.b + k]
    starts = [None] * len(words)
    matched = 0
    for i, p0 in enumerate(a_pos):
        n = len(norm(words[i]["w"]))
        hits = [amap[p0 + k] - k * 0.06 for k in range(min(n, 3)) if p0 + k in amap]
        if hits:
            starts[i] = max(min(hits), 0.0)
            matched += 1
    mask = [x is not None for x in starts]
    if starts[0] is None:
        starts[0] = ww[0][1]
    i = 0
    while i < len(starts):  # непривязанные слова: интерполяция по слогам
        if starts[i] is None:
            j = i
            while j < len(starts) and starts[j] is None:
                j += 1
            t0 = starts[i - 1]
            t1 = starts[j] if j < len(starts) else speech_dur
            tot = sum(weights[i - 1:j])
            acc = weights[i - 1]
            for k in range(i, j):
                starts[k] = t0 + (t1 - t0) * acc / tot
                acc += weights[k]
            i = j
        else:
            i += 1
    loud = loudness_mask(read_audio(wav_path, 16000), 16000)
    starts = [starts[0]] + [snap_after_pause(t, loud) for t in starts[1:]]
    for k in range(1, len(starts)):  # монотонность
        starts[k] = max(starts[k], starts[k - 1] + 0.05)
    method = f"whisper {matched}/{len(words)} слов"
    return (starts, method, mask) if with_mask else (starts, method)
