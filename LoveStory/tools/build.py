#!/usr/bin/env python3
"""LoveStory клип құрастырушы.

Командалар (LoveStory/ папкасынан іске қос):
  python3 tools/build.py check              кадрлар, уақыт, жетіспейтін видеолар
  python3 tools/build.py storyboard         scenes/storyboard.md жасау (дайын промпттар)
  python3 tools/build.py analyze            әннің битін табу -> scenes/beats.json
  python3 tools/build.py render [--preview] [--grade] [--snap]
                                            output/lovestory.mp4 (немесе _preview.mp4)

Видео жоқ кадрдың орнына кадр нөмірі мен сипаттамасы жазылған сұр экран қойылады,
сондықтан аниматикті (ритм тексеру үшін) бір видеосыз-ақ жинауға болады.
"""
import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "scenes" / "shots.csv"
TOKENS = ROOT / "scenes" / "tokens.json"
BEATS = ROOT / "scenes" / "beats.json"
STORYBOARD = ROOT / "scenes" / "storyboard.md"
VIDEOS = ROOT / "videos"
SONG = ROOT / "music" / "song.mp3"
OUT = ROOT / "output"
FPS = 24
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

GRADES = {
    "warm": "colorbalance=rs=0.04:bs=-0.04:rm=0.03:bm=-0.03,eq=saturation=1.06:contrast=1.03",
    "cold": "colorbalance=rs=-0.03:bs=0.05:rm=-0.02:bm=0.03,eq=saturation=0.88:contrast=1.02",
    "dream": "eq=brightness=0.04:saturation=0.9,gblur=sigma=1.2",
}


def fmt(t):
    return f"{int(t // 60)}:{t % 60:05.2f}"


def load_shots():
    with open(SHOTS, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    t = 0.0
    for r in rows:
        r["dur"] = float(r["dur"])
        r["clip_in"] = float(r.get("clip_in") or 1.0)
        r["start"] = t
        t += r["dur"]
        r["file"] = VIDEOS / f"{r['id']}.mp4"
    return rows


def expand(prompt, tokens):
    def sub(m):
        key = m.group(1)
        if key not in tokens:
            sys.exit(f"Белгісіз токен {{{key}}} промптта")
        return tokens[key]
    return re.sub(r"\{([A-Z_]+)\}", sub, prompt)


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return None


def snap_to_beats(shots):
    """Кадр шекараларын ең жақын битке (±0.6 с) жылжытады."""
    if not BEATS.exists():
        sys.exit("scenes/beats.json жоқ. Алдымен: python3 tools/build.py analyze")
    beats = json.loads(BEATS.read_text())["beats"]
    bounds = [s["start"] for s in shots] + [shots[-1]["start"] + shots[-1]["dur"]]
    new = [bounds[0]]
    for b in bounds[1:-1]:
        near = min(beats, key=lambda x: abs(x - b))
        new.append(near if abs(near - b) <= 0.6 and near > new[-1] + 1.0 else b)
    new.append(bounds[-1])
    for s, a, b in zip(shots, new, new[1:]):
        s["start"], s["dur"] = a, b - a
    return shots


def cmd_check(_):
    shots = load_shots()
    total = shots[-1]["start"] + shots[-1]["dur"]
    print(f"{'бөлім':<12}{'басы':>9}{'ұзақт.':>8}{'кадр':>6}")
    sec, order = {}, []
    for s in shots:
        if s["section"] not in sec:
            sec[s["section"]] = [s["start"], 0.0, 0]
            order.append(s["section"])
        sec[s["section"]][1] += s["dur"]
        sec[s["section"]][2] += 1
    for name in order:
        a, d, n = sec[name]
        print(f"{name:<12}{fmt(a):>9}{d:>7.1f}с{n:>6}")
    print(f"Барлығы: {len(shots)} кадр, {fmt(total)}")

    song = probe_duration(SONG) if SONG.exists() else None
    if song is None:
        print("! music/song.mp3 жоқ")
    elif abs(song - total) > 0.5:
        print(f"! Ән {fmt(song)}, ал кадрлар {fmt(total)}: айырмасы {song - total:+.1f} с")
    else:
        print(f"Ән ұзақтығы сәйкес: {fmt(song)}")

    missing, short = [], []
    for s in shots:
        if not s["file"].exists():
            missing.append(s["id"])
            continue
        d = probe_duration(s["file"]) or 0
        if d < s["clip_in"] + s["dur"]:
            short.append(f"{s['id']} ({d:.1f}с < {s['clip_in'] + s['dur']:.1f}с керек)")
    print(f"Дайын видео: {len(shots) - len(missing)}/{len(shots)}")
    if missing:
        print("Жоқ: " + ", ".join(missing))
    if short:
        print("Қысқа (соңғы кадр қатып тұрады): " + "; ".join(short))


def cmd_storyboard(_):
    shots = load_shots()
    tokens = json.loads(TOKENS.read_text(encoding="utf-8"))
    lines = ["# Бізді күткен таң: раскадровка", "",
             "Бұл файлды `python3 tools/build.py storyboard` жасайды. Қолмен өзгертпе:",
             "өзгерісті `scenes/shots.csv` немесе `scenes/tokens.json` ішіне енгіз.", "",
             "Әр кадрдың промптын Google Flow-ға толық көшір. Дайын видеоны",
             "`videos/<id>.mp4` деп сақта (мысалы `videos/s01.mp4`).", ""]
    current = None
    for s in shots:
        if s["section"] != current:
            current = s["section"]
            lines += [f"## {current}", ""]
        end = s["start"] + s["dur"]
        lines += [f"### {s['id']} · {fmt(s['start'])}–{fmt(end)} · {s['dur']:.1f} с · {s['look']}",
                  "", f"**Ән сөзі:** {s.get('lyric', '')}  ",
                  f"**Камера:** {s['camera']}  ", f"**Көрініс:** {s['scene_kk']}", "",
                  "```", expand(s["prompt"], tokens), "```", ""]
    STORYBOARD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Жазылды: {STORYBOARD.relative_to(ROOT)} ({len(shots)} кадр)")


def cmd_analyze(_):
    import librosa  # pip install librosa
    import numpy as np
    y, sr = librosa.load(str(SONG), sr=22050)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    times = [round(float(t), 3) for t in librosa.frames_to_time(beats, sr=sr)]
    BEATS.write_text(json.dumps({"tempo": float(np.atleast_1d(tempo)[0]), "beats": times}))
    print(f"Темп ≈ {float(np.atleast_1d(tempo)[0]):.0f} BPM, {len(times)} бит -> {BEATS.relative_to(ROOT)}")


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("ffmpeg қатесі:\n" + r.stderr[-2000:])


def cmd_render(args):
    shots = load_shots()
    if args.snap:
        shots = snap_to_beats(shots)
    w, h = (960, 540) if args.preview else (1920, 1080)
    preset = "veryfast" if args.preview else "slow"
    OUT.mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="lovestory_"))
    parts = []
    try:
        for i, s in enumerate(shots):
            frames = round(s["dur"] * FPS)
            seg = tmp / f"{i:03d}.mp4"
            vf = [f"scale={w}:{h}:force_original_aspect_ratio=increase", f"crop={w}:{h}",
                  f"fps={FPS}", "setsar=1", f"tpad=stop_mode=clone:stop_duration={s['dur']}"]
            if s["file"].exists():
                inp = ["-ss", str(s["clip_in"]), "-i", str(s["file"])]
                if args.grade and s["look"] in GRADES:
                    vf.append(GRADES[s["look"]])
            else:
                label = tmp / f"{i:03d}.txt"
                body = "\n".join(textwrap.wrap(s["scene_kk"], 48))
                label.write_text(f"{s['id']}  {s['section']}\n«{s.get('lyric', '')}»\n\n{body}",
                                 encoding="utf-8")
                inp = ["-f", "lavfi", "-i", f"color=c=0x1e1e24:s={w}x{h}:r={FPS}:d={s['dur'] + 1}"]
                vf.append(f"drawtext=fontfile={FONT}:textfile={label}:fontcolor=white:"
                          f"fontsize={h // 22}:x=(w-text_w)/2:y=(h-text_h)/2:line_spacing=10")
            if i == 0:
                vf.append("fade=t=in:st=0:d=1.5")
            if i == len(shots) - 1:
                vf.append(f"fade=t=out:st={max(0, s['dur'] - 3)}:d=3")
            run(["ffmpeg", "-y", "-v", "error", *inp, "-vf", ",".join(vf), "-an",
                 "-frames:v", str(frames), "-c:v", "libx264", "-preset", preset, "-crf", "18",
                 "-pix_fmt", "yuv420p", str(seg)])
            parts.append(seg)
            print(f"\r{i + 1}/{len(shots)} кадр", end="", flush=True)
        print()
        listfile = tmp / "list.txt"
        listfile.write_text("".join(f"file '{p}'\n" for p in parts))
        video = tmp / "video.mp4"
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(listfile),
             "-c", "copy", str(video)])
        out = OUT / ("lovestory_preview.mp4" if args.preview else "lovestory.mp4")
        if SONG.exists():
            run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-i", str(SONG),
                 "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
                 "-shortest", "-movflags", "+faststart", str(out)])
        else:
            print("! music/song.mp3 жоқ, дыбыссыз шығарамын")
            shutil.copy(video, out)
        print(f"Дайын: {out.relative_to(ROOT)} ({fmt(probe_duration(out))})")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check").set_defaults(fn=cmd_check)
    sub.add_parser("storyboard").set_defaults(fn=cmd_storyboard)
    sub.add_parser("analyze").set_defaults(fn=cmd_analyze)
    r = sub.add_parser("render")
    r.add_argument("--preview", action="store_true", help="960x540, жылдам")
    r.add_argument("--grade", action="store_true", help="warm/cold/dream түс түзету")
    r.add_argument("--snap", action="store_true", help="кесінділерді битке тарту")
    r.set_defaults(fn=cmd_render)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
