"""ASS-субтитры в стиле канала: белый текст, ключевые слова акцентным цветом,
крупная «призрачная» цифра сцены (hero) на заднем плане."""
from .common import hex_to_ass


def ts(t):
    t = max(t, 0)
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def esc(text):
    return text.replace("{", "(").replace("}", ")").replace("\\", "/")


def build_ass(timeline, brand, fmt, w, h):
    c = brand["colors"]
    f = brand["font"]
    sb = brand["subtitles"]
    hb = brand["hero"]
    white = hex_to_ass(c["text"])
    gold = hex_to_ass(c["accent"])
    outline = hex_to_ass(c["outline"])
    hero_col = hex_to_ass(c["hero"])
    size = sb["size"][fmt]
    hsize = hb["size"][fmt]
    cx = w // 2
    sy = int(h * sb["y"][fmt])
    hy = int(h * hb["y"][fmt])
    margin = 150 if fmt == "short" else 120  # справа в Shorts кнопки YouTube

    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {w}", f"PlayResY: {h}",
        "WrapStyle: 0", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Sub,{f['family']},{size},{white},{white},{outline},&H96000000,"
        f"0,0,0,0,100,100,0,0,1,{sb['outline']},3,5,{margin},{margin},0,1",
        f"Style: Caption,{f['family']},{max(size // 4, 26)},&H30FFFFFF,&H30FFFFFF,&H00000000,"
        f"&H80000000,0,0,0,0,100,100,0,0,1,2,0,7,{margin},{margin},0,1",
        f"Style: Hero,{f['hero_family']},{hsize},{hero_col},{hero_col},&HFF000000,&HFF000000,"
        f"0,0,0,0,100,100,-4,0,1,0,0,5,40,40,0,1",
        "", "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    alpha = f"&H{int(hb['alpha'] * 255):02X}&"
    for sc in timeline["scenes"]:
        framed = sc.get("asset") and (sc.get("shot") or {}).get("fit") == "contain"
        if sc.get("hero") and not framed:   # над фото в рамке hero не рисуем — не закрываем лицо
            # автоподбор: слово занимает не больше 86% ширины кадра
            # (средняя ширина знака Inter Black ≈ 0.66 кегля, учитываем финальный масштаб 106%)
            fs = min(hsize, int(w * 0.86 / (0.66 * len(sc["hero"]) * 1.06)))
            dur_ms = int((sc["end"] - sc["start"]) * 1000)
            lines.append(
                f"Dialogue: 0,{ts(sc['start'])},{ts(sc['end'])},Hero,,0,0,0,,"
                f"{{\\pos({cx},{hy})\\fs{fs}\\alpha{alpha}\\blur2\\fad(350,300)"
                f"\\fscx96\\fscy96\\t(0,{dur_ms},\\fscx106\\fscy106)}}{esc(sc['hero'])}")
        cap = (sc.get("shot") or {}).get("caption") if sc.get("asset") else None
        if cap:  # подпись источника: слева сверху под зоной поиска YouTube
            lines.append(f"Dialogue: 2,{ts(sc['start'])},{ts(sc['end'])},Caption,,0,0,0,,"
                         f"{{\\pos({margin},{int(h * 0.085)})\\fad(300,200)}}{esc(cap)}")
        for ch in sc["chunks"]:
            words = []
            for wd in ch["words"]:
                t = esc(wd["w"])
                words.append(f"{{\\c{gold}}}{t}{{\\c{white}}}" if wd["key"] else t)
            has_key = any(wd["key"] for wd in ch["words"])
            pop = "\\fscx84\\fscy84\\t(0,130,\\fscx104\\fscy104)\\t(130,220,\\fscx100\\fscy100)" \
                if has_key else "\\fscx92\\fscy92\\t(0,120,\\fscx100\\fscy100)"
            lines.append(
                f"Dialogue: 1,{ts(ch['start'])},{ts(ch['end'])},Sub,,0,0,0,,"
                f"{{\\pos({cx},{sy})\\blur{sb['blur']}\\fad(70,50){pop}}}{' '.join(words)}")
    return "\n".join(lines) + "\n"
