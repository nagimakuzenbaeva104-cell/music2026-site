"""YT Factory — конвейер производства видео.

  python3 -m engine.factory storyboard <проект>   озвучка + тайминг -> storyboard.md
  python3 -m engine.factory preview    <проект>   черновой рендер 540p + контактный лист
  python3 -m engine.factory check      <проект>   отчёт качества превью -> qa.md
  python3 -m engine.factory layout     <проект>   пример расположения текста + зоны интерфейса Shorts
  python3 -m engine.factory final      <проект>   финальный MP4 (только если approved: true)

  --format short|long   переопределить формат проекта (9:16 / 16:9)
"""
import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

from . import align, audio, qa, subs, tts, visuals
from .common import (FONTS, FactoryError, deliverables_dir, duration, load_project,
                     music_file, run, write_wav)
from . import layout, shotlist

TRANSITIONS = {"fade", "fadeblack", "dissolve", "smoothleft", "smoothright", "smoothup",
               "smoothdown", "slideleft", "slideup", "circleopen", "wipeleft", "zoomin"}


def plain(text):
    return text.replace("[", "").replace("]", "")


ASSET_EXT = (".mp4", ".mov", ".webm", ".jpg", ".jpeg", ".png", ".webp")


def find_asset(project_dir, scene, idx):
    """Явный asset из scenes.yaml или файл assets/sNN.* (NN = id сцены)."""
    if scene.get("asset"):
        if not (project_dir / "assets" / scene["asset"]).exists():
            raise FactoryError(f"Сцена {idx}: нет файла assets/{scene['asset']}")
        return scene["asset"]
    sid = scene.get("id", idx)
    for ext in ASSET_EXT:
        f = project_dir / "assets" / f"s{int(sid):02d}{ext}"
        if f.exists():
            return f.name
    return None


def merge_fast(chunks, speech_end, sb):
    """Склеивает экраны, которые мелькают слишком быстро (< min_on_screen или > max_cps),
    с соседним, если вместе они не длиннее merge_max_chars и не разрывают предложение."""
    min_on = sb.get("min_on_screen", 0.6)
    max_cps = sb.get("max_cps", 20)
    limit = sb.get("merge_max_chars", 24)
    txt = lambda c: " ".join(w["w"] for w in c["words"])
    changed = True
    while changed:
        changed = False
        for j in range(len(chunks)):
            end = chunks[j + 1]["start"] if j + 1 < len(chunks) else speech_end
            dur = end - chunks[j]["start"]
            fast = dur < min_on or len(txt(chunks[j])) / max(dur, 0.01) > max_cps
            if not fast:
                continue
            # склеиваем с соседом, если не пересекаем конец предложения
            cand = []
            if j + 1 < len(chunks) and not re.search(r"[.!?]$", chunks[j]["words"][-1]["w"]):
                cand.append(j)
            if j > 0 and not re.search(r"[.!?]$", chunks[j - 1]["words"][-1]["w"]):
                cand.append(j - 1)
            for a in cand:
                merged = chunks[a]["words"] + chunks[a + 1]["words"]
                if len(" ".join(w["w"] for w in merged)) <= limit:
                    chunks[a] = {"words": merged, "start": chunks[a]["start"],
                                 "wstarts": chunks[a]["wstarts"] + chunks[a + 1]["wstarts"]}
                    del chunks[a + 1]
                    changed = True
                    break
            if changed:
                break
    # служебное слово в конце экрана («in», «a», «the», «в») переносим на следующий экран
    weak = {"the", "and", "but", "for", "of", "to", "at", "on", "in", "an", "a", "with", "by",
            "и", "в", "на", "с", "к", "по", "о", "а", "но"}
    for j in range(len(chunks) - 1):
        last = chunks[j]["words"][-1]["w"]
        if len(chunks[j]["words"]) > 1 and last.lower() in weak:
            chunks[j + 1]["words"].insert(0, chunks[j]["words"].pop())
            moved_t = chunks[j]["wstarts"].pop()
            chunks[j + 1]["wstarts"].insert(0, moved_t)
            chunks[j + 1]["start"] = moved_t      # экран начинается вместе с перенесённым словом
    return chunks


def build_timeline(project_dir, proj, brand, fmt):
    voice = brand["voice"]
    sb = brand["subtitles"]
    pad = voice.get("pad_after", 0.3)
    t, scenes, sfx = 0.0, [], []
    for i, s in enumerate(proj["scenes"], 1):
        say = s.get("say") or plain(s["text"])
        wav = tts.synth(say, voice)
        speech = duration(wav)
        words = align.parse_words(s["text"])
        starts, method = align.word_starts(words, wav, speech, brand.get("language", "ru"))
        chunks = align.chunk(words, sb["max_words"], sb["max_chars"])
        slot = speech + pad
        out_chunks, k = [], 0
        for ch in chunks:
            ws = [round(t + x, 3) for x in starts[k:k + len(ch)]]
            k += len(ch)
            out_chunks.append({"words": ch, "start": ws[0], "wstarts": ws})
        out_chunks = merge_fast(out_chunks, t + speech + 0.2, sb)
        for j, ch in enumerate(out_chunks):
            nxt = out_chunks[j + 1]["start"] if j + 1 < len(out_chunks) else t + speech + 0.2
            ch["end"] = round(min(nxt, t + slot), 3)
            # звук на начало каждой группы ключевых слов
            first_key = next((idx for idx, w in enumerate(ch["words"]) if w["key"]), None)
            if first_key is not None:
                prev_key = ch["words"][first_key - 1]["key"] if first_key > 0 else (
                    j > 0 and out_chunks[j - 1]["words"][-1]["key"])
                if not prev_key:
                    sfx.append(("hit", ch["start"]))
        if i > 1:
            sfx.append(("whoosh", t))
        scenes.append({
            "id": s.get("id", i), "start": round(t, 3), "end": round(t + slot, 3),
            "speech": round(speech, 3), "wav": str(wav), "say": say, "text": s["text"],
            "hero": s.get("hero"), "visual": s.get("visual", ""),
            "asset": find_asset(project_dir, s, i), "asset_hint": s.get("asset_hint"),
            "transition": s.get("transition", brand["transitions"]["default"]),
            "chunks": out_chunks, "align": method, "source": s.get("source"),
        })
        t += slot
    total = t + 0.4
    scenes[-1]["end"] = round(total, 3)
    return {"title": proj.get("title"), "format": fmt, "total": round(total, 3),
            "target": proj.get("target_seconds"), "scenes": scenes, "sfx": sfx}


def write_storyboard(project_dir, proj, brand, tl, out_dir, music):
    lines = [f"# Раскадровка: {proj.get('title')}", "",
             f"- Канал: **{brand['name']}** · формат **{tl['format']}** · голос `{brand['voice']['model']}`",
             f"- Длительность: **{tl['total']:.1f} с**" +
             (f" (цель {tl['target']} с)" if tl.get("target") else ""),
             f"- Ключевые слова: цвет `{brand['colors']['accent']}` · шрифт {brand['font']['family']}",
             f"- Музыка: {('`' + Path(music).name + '`') if music and music != 'synth' else ('синт-заглушка' if music else 'нет (положите assets/music.mp3)')}",
             f"- Статус: {'✅ одобрено' if proj.get('approved') else '⏳ ждёт подтверждения «ДА»'}", ""]
    tgt = tl.get("target")
    if tgt and abs(tl["total"] - tgt) > 2:
        lines += [f"> ⚠️ Длительность отличается от цели на {tl['total'] - tgt:+.1f} с. "
                  "Варианты: изменить voice.length_scale в brand.yaml или сократить текст "
                  "(только с вашего согласия).", ""]
    for s in tl["scenes"]:
        subs_txt = " / ".join(
            " ".join(f"**{w['w']}**" if w["key"] else w["w"] for w in ch["words"])
            for ch in s["chunks"])
        snd = "whoosh на входе" if s["id"] != tl["scenes"][0]["id"] else (
            "старт музыки" if music else "без музыки")
        if any(w["key"] for ch in s["chunks"] for w in ch["words"]):
            snd += " · мягкий удар на ключевых словах"
        lines += [
            f"## Сцена {s['id']} · {s['start']:.1f}–{s['end']:.1f} с ({s['end'] - s['start']:.1f} с)",
            "",
            f"- **Визуал:** {s['visual'] or '—'}" + (f" · файл `{s['asset']}`" if s['asset']
                                                    else f" · ⚠️ нет кадра: положите `assets/s{int(s['id']):02d}.mp4` (или .jpg) — сейчас фирменный градиент"),
            f"- **Hero-элемент:** {s['hero'] or '—'}",
            f"- **Озвучка:** «{s['say']}»",
            f"- **Субтитры:** {subs_txt}  ",
            f"  _(жирным = цвет {brand['colors']['accent']}; привязка: {s['align']})_",
            f"- **Переход:** {s['transition']}",
            f"- **Звук:** {snd}" + (" · музыка приглушена под голос" if music else ""),
        ]
        if s.get("source"):
            lines.append(f"- **Источник факта:** {s['source']}")
        lines.append("")
    if proj.get("sources"):
        lines += ["## Источники", ""] + [f"- {x}" for x in proj["sources"]] + [""]
    (out_dir / "storyboard.md").write_text("\n".join(lines), encoding="utf-8")


def render(project_dir, proj, brand, tl, final, out_dir, music):
    fmt = tl["format"]
    F = brand["formats"][fmt]
    W, H, fps = F["w"], F["h"], F["fps"]
    scale = 1 if final else 0.5
    w, h = int(W * scale) // 2 * 2, int(H * scale) // 2 * 2
    T = brand["transitions"]["duration"]
    tmp = Path(tempfile.mkdtemp(prefix="ytf_"))
    try:
        clips = []
        n = len(tl["scenes"])
        for i, s in enumerate(tl["scenes"]):
            length = (s["end"] - s["start"]) + (T if i < n - 1 else 0)
            print(f"  кадр сцены {s['id']} ({length:.1f} с)")
            clips.append(visuals.scene_clip(s, i, length, w, h, fps, brand,
                                            project_dir / "assets", tmp / f"c{i:02d}.mp4",
                                            fast=not final))
        ass = tmp / "subs.ass"
        ass.write_text(subs.build_ass(tl, brand, fmt, W, H), encoding="utf-8")
        # цепочка переходов
        inputs, fl, last = [], [], "[0:v]"
        for c in clips:
            inputs += ["-i", c]
        for i in range(1, n):
            tr = tl["scenes"][i]["transition"]
            if tr not in TRANSITIONS:
                raise FactoryError(f"Неизвестный переход {tr}; доступны: {sorted(TRANSITIONS)}")
            off = tl["scenes"][i]["start"]
            fl.append(f"{last}[{i}:v]xfade=transition={tr}:duration={T}:offset={off:.3f}[x{i}]")
            last = f"[x{i}]"
        total = tl["total"]
        fl.append(f"{last}ass={ass}:fontsdir={FONTS},fade=t=in:d=0.25,"
                  f"fade=t=out:st={total - 0.5:.3f}:d=0.5,format=yuv420p[v]")
        mix = audio.build_mix([s["wav"] for s in tl["scenes"]],
                              [s["start"] for s in tl["scenes"]], total, tl["sfx"], brand,
                              music_path=music)
        write_wav(tmp / "mix.wav", mix)
        name = re.sub(r"[^\w-]+", "_", project_dir.name)
        out = out_dir / (f"{name}_{fmt}_final.mp4" if final else f"{name}_{fmt}_preview.mp4")
        lufs = brand["audio"].get("lufs", -14)
        enc = (["-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high"]
               if final else ["-c:v", "libx264", "-preset", "veryfast", "-crf", "28"])
        print("  монтаж, субтитры, звук ...")
        run(["ffmpeg", "-y", "-v", "error", *inputs, "-i", tmp / "mix.wav",
             "-filter_complex", ";".join(fl), "-map", "[v]", "-map", f"{n}:a",
             "-af", f"loudnorm=I={lufs}:TP=-1.5:LRA=11", "-ar", "48000",
             *enc, "-r", str(fps), "-c:a", "aac", "-b:a", "192k",
             "-t", f"{total:.3f}", "-movflags", "+faststart", out])
        if not final:
            contact_sheet(out, tl, out_dir / f"{name}_{fmt}_storyboard.jpg")
        return out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def contact_sheet(video, tl, out):
    tmp = Path(tempfile.mkdtemp(prefix="ytf_cs_"))
    try:
        frames = []
        for s in tl["scenes"]:
            # кадр в момент, когда на экране последний субтитр сцены
            t = (s["chunks"][-1]["start"] + s["chunks"][-1]["end"]) / 2
            f = tmp / f"f{s['id']:02d}.jpg"
            run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", video,
                 "-frames:v", "1", "-q:v", "3", f])
            frames.append(f)
        run(["montage", *frames, "-tile", f"{min(len(frames), 4)}x", "-geometry", "+8+8",
             "-background", "#111111", "-label", "", out])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("cmd", choices=["storyboard", "preview", "check", "layout", "final"])
    ap.add_argument("project")
    ap.add_argument("--format", choices=["short", "long"])
    a = ap.parse_args(argv)
    try:
        project_dir, proj, brand, fmt = load_project(a.project)
        fmt = a.format or fmt
        if a.cmd == "final" and not proj.get("approved"):
            raise FactoryError("Финальный рендер заблокирован: в scenes.yaml нет approved: true. "
                               "Сначала одобрите раскадровку и превью.")
        print(f"▶ {proj.get('title')} [{fmt}] — озвучка и тайминг ...")
        tl = build_timeline(project_dir, proj, brand, fmt)
        build = project_dir / "build"
        build.mkdir(exist_ok=True)
        (build / f"timeline_{fmt}.json").write_text(
            json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
        out_dir = deliverables_dir(project_dir, proj)
        music = music_file(project_dir, brand)
        write_storyboard(project_dir, proj, brand, tl, out_dir, music)
        shotlist.write(project_dir, proj, brand, tl)
        print(f"  раскадровка: {out_dir / 'storyboard.md'} · {tl['total']:.1f} с")
        print(f"  список кадров: {project_dir / 'assets' / 'README.md'}")
        if a.cmd in ("preview", "final"):
            out = render(project_dir, proj, brand, tl, a.cmd == "final", out_dir, music)
            print(f"✔ {out} ({duration(out):.1f} с)")
        if a.cmd == "check":
            name = re.sub(r"[^\w-]+", "_", project_dir.name)
            video = out_dir / f"{name}_{fmt}_preview.mp4"
            if not video.exists():
                raise FactoryError("Сначала соберите превью: factory preview <проект>")
            rep, intel, measured, bad, missing = qa.write_report(project_dir, tl, brand, video, out_dir)
            print(f"  озвучка: {intel:.0f}% слов распознано · синхронизация: "
                  f"{len(measured)} экранов измерено, {len(bad)} с расхождением > {qa.SYNC_OK} с · "
                  f"кадров нет в {len(missing)} сценах")
            print(f"✔ отчёт: {rep}")
        if a.cmd == "layout":
            print(f"✔ {layout.render(tl, brand, out_dir)}")
    except FactoryError as e:
        print(f"✖ {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
