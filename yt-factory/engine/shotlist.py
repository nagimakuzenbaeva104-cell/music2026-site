"""Список необходимых кадров -> assets/README.md (генерируется из scenes.yaml и тайминга)."""
from pathlib import Path

ZONES = {  # доли высоты кадра 9:16, где лежит текст (см. layout.py)
    "hero": (0.30, 0.46),
    "subs": (0.57, 0.72),
}
KIND = {"archival": "📜 реальный кадр", "illustration": "🎨 иллюстрация",
        "graphic": "✏️ графика движка"}
STATUS = {"verified-search": "🟡 по выдержке из поиска — подтвердить на странице",
          "verified": "🟢 проверено на странице", "to-verify": "🔴 НЕ прочитана — не использовать до проверки",
          "n/a": "—"}


def write(project_dir, proj, brand, tl):
    assets = Path(project_dir) / "assets"
    assets.mkdir(exist_ok=True)
    F = brand["formats"][tl["format"]]
    T = brand["transitions"]["duration"]
    rows, details = [], []
    for s in tl["scenes"]:
        sh = s.get("shot") or {}
        sid = int(s["id"])
        dur = s["end"] - s["start"]
        fname = sh.get("file")
        have = "✅ загружен" if s["asset"] else ("—" if not fname else "⬜ ждёт файл")
        on_screen = " / ".join(" ".join(w["w"] for w in ch["words"]) for ch in s["chunks"])
        rows.append(f"| {sid} | {s.get('name', '')} | {dur:.1f} | "
                    f"{('`' + fname + '`') if fname else '—'} | {KIND.get(sh.get('kind'), '')} | "
                    f"{STATUS.get(sh.get('license_status', 'n/a'), '')} | {have} |")
        d = [f"### Сцена {sid}. {s.get('name', '')}", "",
             f"- **Время:** {s['start']:.1f}–{s['end']:.1f} с · **длительность {dur:.1f} с**"
             + (f" (клип — не короче {dur + T:.1f} с)" if fname and fname.endswith((".mp4", ".mov", ".webm")) else ""),
             f"- **Тип:** {KIND.get(sh.get('kind'), '—')}",
             f"- **Что найти:** {sh.get('find', '—')}",
             f"- **Имя файла:** {('`assets/' + fname + '`') if fname else 'не нужен'}"]
        if sh.get("page"):
            d.append(f"- **Где взять:** {sh['page']}")
        if sh.get("where"):
            d.append(f"- **Где взять:** {sh['where']}")
        if sh.get("author"):
            d.append(f"- **Автор:** {sh['author']}")
        if sh.get("license"):
            d.append(f"- **Лицензия:** {sh['license']} · {STATUS.get(sh.get('license_status', 'n/a'), '')}")
        if sh.get("fit"):
            d.append(f"- **Подача:** {'фото в рамке над субтитрами (12–55% высоты), без hero' if sh['fit'] == 'contain' else 'на весь экран'}")
        if sh.get("caption"):
            d.append(f"- **Подпись в кадре:** «{sh['caption']}»")
        d.append(f"- **Текст на экране:** hero «{s['hero'] or '—'}» · субтитры: {on_screen}")
        if sh.get("note"):
            d.append(f"- ⚠️ {sh['note']}")
        if sh.get("alt"):
            a = sh["alt"]
            d.append(f"- **Запасной вариант:** {a.get('find')} — {a.get('where')} ({a.get('license')})")
        details += d + [""]
    lines = [
        f"# Кадры для «{proj.get('title')}»",
        "",
        "Сгенерировано командой `storyboard` из `scenes.yaml` (блок `shot`). Правьте `scenes.yaml`, "
        "а не этот файл.",
        "",
        "## Сводка",
        "",
        "| # | Сцена | Сек | Файл | Тип | Лицензия | Статус |",
        "|---|---|---|---|---|---|---|",
        *rows,
        "",
        "## Правила",
        "",
        "1. **Имена файлов** — строго как в таблице; движок подхватит их сам. Видео/фото в git не попадают.",
        "2. **Лицензия.** Перед скачиванием откройте страницу источника и прочитайте раздел Licensing. "
        "Финальный рендер с любым загруженным файлом 🟡/🔴 заблокирован, пока вы не прочитаете "
        "лицензию на странице и не поменяете `license_status` на `verified` в `scenes.yaml`.",
        "3. **Ссылки на источники** уже записаны в `scenes.yaml`; титры для описания YouTube — "
        "в `yt-output/.../credits.txt` (CC BY / CC BY-SA требуют указать автора и лицензию).",
        "4. **Не выдавать других людей за Безоса.** На иллюстрациях — никаких лиц, которые можно "
        "принять за него. Его лицо — только на реальных фото с подписью года.",
        "5. **Год в кадре.** Фото не из того года, о котором говорит диктор, всегда с подписью года.",
        "6. **Чужие видео** (CNET, KIRO 7, ABC7, CBS, C-SPAN, YouTube-перезаливы) — не использовать: "
        "это не свободные лицензии; для монетизируемого канала нужна платная лицензия.",
        f"7. **Формат:** 9:16 от {F['w']}×{F['h']} для «на весь экран»; горизонтальное видео "
        "обрежется до центральной трети. Hero-цифра — 30–46% высоты, субтитры — 57–72%: "
        "лица и важные объекты держите вне этих полос.",
        "8. **Музыка:** `assets/music.mp3` (YouTube Audio Library). Без файла — без музыки.",
        "",
        "## Сцены подробно",
        "",
        *details,
    ]
    (assets / "README.md").write_text("\n".join(lines), encoding="utf-8")
