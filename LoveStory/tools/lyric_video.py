#!/usr/bin/env python3
"""«Бізді күткен таң» lyric video.

Фон: бөлімдерге қарай ауысатын анимацияланған түс градиенті (суық шумақтар,
жылы қайырмалар, аутрода таң), пленка түйіршігі мен виньетка. Ән сөздері
scenes/lyrics.csv бойынша уақытқа дәл шығады.

  python3 tools/lyric_video.py            -> output/lyric_video.mp4 (1920x1080)
  python3 tools/lyric_video.py --preview  -> output/lyric_video_preview.mp4 (960x540)
"""
import argparse
import csv
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SONG = ROOT / "music" / "song.mp3"
LYRICS = ROOT / "scenes" / "lyrics.csv"
OUT = ROOT / "output"
FPS = 25
TITLE = "БІЗДІ КҮТКЕН ТАҢ"
ARTIST = "Нагима Кузенбаева"

# (бөлім басталатын уақыт, градиент түстері, қозғалыс жылдамдығы)
SECTIONS = [
    (0.0,   ["0x05070d", "0x141c33", "0x2a3656", "0x0a0f1d"], 0.004),  # кіріспе
    (14.5,  ["0x0b1026", "0x1c2b4a", "0x3a4f6e", "0x0e1a2e"], 0.006),  # 1-шумақ
    (42.9,  ["0x121433", "0x2c2f5a", "0x5a5480", "0x161a36"], 0.008),  # пре-қайырма
    (51.6,  ["0x2a0f1e", "0x7a3b2e", "0xc9874a", "0x3d1a2a"], 0.010),  # қайырма 1
    (82.0,  ["0x07090f", "0x1a2238", "0x2b3550", "0x0a0d18"], 0.005),  # аспаптық
    (94.7,  ["0x0b1026", "0x1c2b4a", "0x3a4f6e", "0x0e1a2e"], 0.006),  # 2-шумақ
    (123.0, ["0x121433", "0x2c2f5a", "0x5a5480", "0x161a36"], 0.008),  # пре-қайырма 2
    (131.0, ["0x2a0f1e", "0x7a3b2e", "0xc9874a", "0x3d1a2a"], 0.010),  # қайырма 2
    (159.7, ["0x1a1630", "0x4a3a5e", "0xb07a5a", "0x22182e"], 0.007),  # көпір
    (176.7, ["0x3a1420", "0xa0503a", "0xe8a85c", "0x4a1c28"], 0.012),  # финал
    (204.3, ["0x241d38", "0xb86e4a", "0xd9a868", "0x4e3550"], 0.006),  # аутро (таң)
]
XFADE = 2.0

# ASS түстері &HAABBGGRR
STYLES = {
    "verse":  ("Inter Light", 64, "&H00F2EDE6"),
    "pre":    ("Inter Light", 64, "&H00F5E6DC"),
    "chorus": ("Inter", 72, "&H00A8DAFF"),
    "bridge": ("Inter Light", 66, "&H00D9E4F5"),
    "outro":  ("Inter Light", 76, "&H00F4F8FC"),
}


def ass_time(t):
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def build_ass(path, w, h, total):
    k = h / 1080
    head = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {w}", f"PlayResY: {h}",
        "WrapStyle: 0", "", "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour,"
        " Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline,"
        " Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
    ]
    for name, (font, size, col) in STYLES.items():
        head.append(f"Style: {name},{font},{round(size * k)},{col},&H000000FF,&H90000000,&HA0000000,"
                    f"0,0,0,0,100,100,{round(2 * k)},0,1,{max(1, round(3 * k))},{max(1, round(3 * k))},5,80,80,0,1")
    head.append(f"Style: title,Inter Thin,{round(96 * k)},&H00F5EEE6,&H000000FF,&H80000000,&H00000000,"
                f"0,0,0,0,100,100,{round(18 * k)},0,1,{max(1, round(2 * k))},0,5,80,80,0,1")
    head.append(f"Style: artist,Inter Light,{round(40 * k)},&H00C8D2DC,&H000000FF,&H80000000,&H00000000,"
                f"0,0,0,0,100,100,{round(8 * k)},0,1,1,0,5,80,80,0,1")
    head += ["", "[Events]",
             "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]

    cx, cy = w // 2, h // 2
    rise = round(18 * k)
    ev = []

    def title_card(a, b):
        ev.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},title,,0,0,0,,"
                  f"{{\\pos({cx},{cy - round(30 * k)})\\fad(1800,1500)\\blur6\\t(0,1800,\\blur0.6)}}{TITLE}")
        ev.append(f"Dialogue: 0,{ass_time(a + 1.2)},{ass_time(b)},artist,,0,0,0,,"
                  f"{{\\pos({cx},{cy + round(70 * k)})\\fad(1500,1500)}}{ARTIST}")

    title_card(0.6, 13.6)
    with open(LYRICS, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            a, b = float(r["start"]) - 0.25, float(r["end"])
            fade_out = 600 if r["kind"] != "outro" else 2500
            ev.append(
                f"Dialogue: 1,{ass_time(a)},{ass_time(b)},{r['kind']},,0,0,0,,"
                f"{{\\move({cx},{cy + rise},{cx},{cy},0,700)\\fad(500,{fade_out})"
                f"\\blur4\\t(0,600,\\blur0.6)}}{r['text']}")
    title_card(216.0, total - 0.3)
    path.write_text("\n".join(head + ev) + "\n", encoding="utf-8")


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("ffmpeg қатесі:\n" + r.stderr[-3000:])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--preview", action="store_true")
    a = p.parse_args()
    w, h = (960, 540) if a.preview else (1920, 1080)
    total = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(SONG)],
        capture_output=True, text=True).stdout)

    tmp = Path(tempfile.mkdtemp(prefix="lyric_"))
    bounds = [s[0] for s in SECTIONS] + [total]
    n = len(SECTIONS)
    inputs, labels = [], []
    for i, (start, cols, speed) in enumerate(SECTIONS):
        end = bounds[i + 1]
        length = (end - start) + (XFADE if 0 < i < n - 1 else XFADE / 2)
        if n == 1:
            length = end - start
        c = ":".join(f"c{j}={col}" for j, col in enumerate(cols))
        inputs += ["-f", "lavfi", "-i",
                   f"gradients=s=480x270:r={FPS}:{c}:nb_colors={len(cols)}:type=radial:"
                   f"speed={speed}:d={length:.3f}:x0=120:y0=60:x1=400:y1=240:seed={i + 7}"]
        labels.append(f"[{i}:v]")

    chain, prev = [], labels[0]
    for i in range(1, n):
        out = f"[x{i}]"
        chain.append(f"{prev}{labels[i]}xfade=transition=fade:duration={XFADE}:"
                     f"offset={bounds[i] - XFADE / 2:.3f}{out}")
        prev = out

    ass = tmp / "lyrics.ass"
    build_ass(ass, w, h, total)
    chain.append(
        f"{prev}gblur=sigma=6,scale={w}:{h}:flags=bicubic,"
        f"noise=alls=7:allf=t+u,vignette=angle=PI/4.5,"
        f"subtitles={ass}:fontsdir=/usr/share/fonts,"
        f"fade=t=in:st=0:d=1.5,fade=t=out:st={total - 3:.2f}:d=3,format=yuv420p[v]")

    OUT.mkdir(exist_ok=True)
    out = OUT / ("lyric_video_preview.mp4" if a.preview else "lyric_video.mp4")
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-i", str(SONG),
         "-filter_complex", ";".join(chain), "-map", "[v]", "-map", f"{n}:a",
         "-c:v", "libx264", "-preset", "veryfast" if a.preview else "medium", "-crf", "18",
         "-c:a", "aac", "-b:a", "256k", "-t", f"{total:.3f}", "-movflags", "+faststart", str(out)])
    print(f"Дайын: {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
