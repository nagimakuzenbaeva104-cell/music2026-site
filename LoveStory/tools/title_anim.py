#!/usr/bin/env python3
"""«Бізді күткен таң» атау анимациясы.

Түнгі көк аспан біртіндеп алтын таңға ауысады, Тянь-Шань жоталарының артынан
күн шығады, ауада тозаң жылтырайды. Атау әріптері бірінен соң бірі пайда болады,
содан кейін сызық, орындаушы аты және «жақында».

Жеке іске қосу (LoveStory/ папкасынан):
  python3 tools/title_anim.py                       output/title_anim.mp4 1920x1080
  python3 tools/title_anim.py --vertical            output/title_anim_vertical.mp4
  python3 tools/title_anim.py --preview --dur 6     960x540, жылдам
  python3 tools/title_anim.py --png 4.5             бір кадрды PNG етіп сақтау

build.py мудфильмде `look=dawn` жолы үшін осы модульдің render() функциясын шақырады.
"""
import argparse
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FPS = 24

# Қазақ әріптері (ә, ғ, қ, ң, ө, ұ, ү, һ, і) бар қаріптер, бірінші табылғаны алынады
SERIF = ["/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"]
SANS = ["/usr/share/fonts/opentype/inter/Inter-Light.otf",
        "/usr/share/fonts/truetype/inter/Inter-Light.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]

DEFAULT_TEXT = "Бізді күткен таң|Нагима Кузенбаева||жақында"
CREAM = (242, 234, 216)
GOLD = (255, 206, 140)


def find_font(paths):
    for p in paths:
        if Path(p).exists():
            return p
    sys.exit("Қаріп табылмады: " + ", ".join(paths))


def smooth(a, b, t):
    """0..1 аралығындағы жұмсақ өту (smoothstep)."""
    x = min(1.0, max(0.0, (t - a) / (b - a)))
    return x * x * (3 - 2 * x)


def ease_out(a, b, t):
    x = min(1.0, max(0.0, (t - a) / (b - a)))
    return 1 - (1 - x) ** 3


def lerp(c0, c1, p):
    return np.asarray(c0, np.float32) * (1 - p) + np.asarray(c1, np.float32) * p


class Scene:
    def __init__(self, w, h, dur, text):
        self.w, self.h, self.dur = w, h, dur
        lines = [ln.strip() for ln in text.split("|")]
        filled = [ln for ln in lines if ln]
        self.title = filled[0] if filled else ""
        self.artist = filled[1] if len(filled) > 1 else ""
        self.tag = filled[-1] if len(filled) > 2 else ""
        self.portrait = h > w
        rng = np.random.default_rng(7)

        # Көкжиек: тік нұсқада төменірек, жазу үшін аспанға орын көп
        self.horizon = int(h * (0.74 if self.portrait else 0.70))
        yy = np.arange(h, dtype=np.float32)[:, None]
        xx = np.arange(w, dtype=np.float32)[None, :]
        self.yy, self.xx = yy, xx
        self.sky_t = np.clip(yy / self.horizon, 0, 1)

        # Жоталар: бірнеше синусоидадан, екі қабат
        x = np.arange(w, dtype=np.float32) / w
        def ridge(base, amp, seed):
            r = np.random.default_rng(seed)
            y = np.zeros_like(x)
            for k, a in zip((2, 5, 11, 23, 47), (1.0, 0.45, 0.22, 0.10, 0.05)):
                y += a * np.sin(2 * math.pi * (k * x + r.random()))
            y = (y - y.min()) / (y.max() - y.min())
            return self.horizon - base * h - amp * h * y
        self.ridge_back = ridge(0.02, 0.16 if not self.portrait else 0.10, 3)
        self.ridge_front = ridge(-0.03, 0.09 if not self.portrait else 0.06, 11)

        # Тозаң бөлшектері
        n = 140 if not self.portrait else 110
        self.px = rng.random(n) * w
        self.py = rng.random(n) * h
        self.pr = (rng.random(n) ** 2 * 2.2 + 0.6) * min(w, h) / 1080
        self.pv = (rng.random(n) * 0.5 + 0.3) * h / 1080 * 14   # px/с жоғары
        self.pphase = rng.random(n) * 2 * math.pi
        self.grain_seed = rng.integers(1 << 30)

        # Қаріптер мен әріптер
        unit = min(w, h)
        self.title_font = ImageFont.truetype(find_font(SERIF), 10)
        size = int(unit * (0.115 if not self.portrait else 0.135))
        # Ені 84%-дан аспасын
        while size > 10:
            self.title_font = ImageFont.truetype(find_font(SERIF), size)
            if self.title_font.getlength(self.title) <= w * 0.84:
                break
            size -= 2
        self.title_size = size
        self.small_font = ImageFont.truetype(find_font(SANS), int(size * 0.30))
        self.tag_font = ImageFont.truetype(find_font(SANS), int(size * 0.22))

        # Жазу орны: аспанның ортасы
        self.title_y = int(self.horizon * (0.42 if not self.portrait else 0.45))

    # ---------- фон ----------
    def background(self, t):
        w, h = self.w, self.h
        p = smooth(0.0, self.dur * 0.9, t)            # түн -> таң
        top = lerp((6, 9, 24), (28, 34, 72), p)
        mid = lerp((22, 30, 58), (120, 92, 120), p)
        hor = lerp((44, 56, 84), (252, 178, 112), p)
        s = self.sky_t[..., None]
        sky = np.where(s < 0.6, lerp(top, mid, s / 0.6), lerp(mid, hor, (s - 0.6) / 0.4))
        img = np.broadcast_to(sky, (h, w, 3)).astype(np.float32).copy()

        # Күн жарығы: көкжиектің артынан көтеріледі
        cx = w * 0.5
        rise = ease_out(0.3, self.dur, t)
        cy = self.horizon + h * 0.10 - h * 0.12 * rise
        d2 = ((self.xx - cx) / w) ** 2 * (1.6 if not self.portrait else 0.6) + ((self.yy - cy) / h) ** 2
        glow = np.exp(-d2 / 0.018) * (0.15 + 0.85 * p) + np.exp(-d2 / 0.0012) * p * 0.9
        img += glow[..., None] * np.asarray((255, 190, 120), np.float32) * 0.9

        # Жоталар (артқы қабатқа таң жарығы аздап түседі)
        back = lerp((18, 22, 40), (96, 70, 92), p)
        front = lerp((8, 10, 20), (38, 26, 40), p)
        img = np.where((self.yy >= self.ridge_back[None, :])[..., None], back, img)
        img = np.where((self.yy >= self.ridge_front[None, :])[..., None], front, img)

        # Тұман: көкжиек бойындағы жұмсақ жолақ, баяу жылжиды
        band = np.exp(-((self.yy - self.horizon) / (h * 0.05)) ** 2)
        wave = 0.75 + 0.25 * np.sin(self.xx / w * 6.0 + t * 0.35)
        mist = (band * wave)[..., None] * lerp((90, 104, 130), (255, 214, 180), p) * 0.35
        img += mist
        return img, p

    # ---------- бөлшектер ----------
    def particles(self, img, t, p):
        h, w = self.h, self.w
        y = (self.py - self.pv * t) % h
        x = self.px + np.sin(t * 0.6 + self.pphase) * w * 0.006
        tw = 0.55 + 0.45 * np.sin(t * 2.3 + self.pphase * 3)
        a = tw * (0.25 + 0.75 * p) * 0.55
        col = lerp((170, 190, 230), GOLD, p)
        for xi, yi, ri, ai in zip(x, y, self.pr, a):
            r = int(ri * 3) + 1
            x0, x1 = max(0, int(xi) - r), min(w, int(xi) + r + 1)
            y0, y1 = max(0, int(yi) - r), min(h, int(yi) + r + 1)
            if x0 >= x1 or y0 >= y1:
                continue
            gx = np.arange(x0, x1) - xi
            gy = np.arange(y0, y1)[:, None] - yi
            m = np.exp(-(gx ** 2 + gy ** 2) / (2 * ri * ri)) * ai
            img[y0:y1, x0:x1] += m[..., None] * col

    # ---------- жазу ----------
    def text_layer(self, t):
        w, h = self.w, self.h
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        f = self.title_font
        total = f.getlength(self.title)
        x0 = (w - total) / 2
        letters = [i for i, ch in enumerate(self.title) if not ch.isspace()]
        start, spread, each = 0.7, 1.5, 0.9
        for k, i in enumerate(letters):
            t0 = start + spread * k / max(1, len(letters) - 1)
            a = ease_out(t0, t0 + each, t)
            if a <= 0:
                continue
            dy = (1 - a) * self.title_size * 0.22
            x = x0 + f.getlength(self.title[:i])
            d.text((x, self.title_y + dy), self.title[i], font=f, fill=CREAM + (int(255 * a),),
                   anchor="ls")

        # Сызық ортадан екі жаққа ашылады
        lt = ease_out(2.5, 3.4, t)
        if lt > 0:
            half = w * (0.16 if not self.portrait else 0.26) * lt
            ly = self.title_y + self.title_size * 0.42
            d.line([(w / 2 - half, ly), (w / 2 + half, ly)], fill=GOLD + (int(200 * lt),),
                   width=max(1, self.title_size // 60))

        # Орындаушы: әріп аралығы кеңнен қалыпқа жиналады
        if self.artist:
            self._tracked(d, self.artist, self.small_font, self.title_y + self.title_size * 0.95,
                          ease_out(2.9, 4.0, t), spacing=0.18, color=CREAM)
        if self.tag:
            self._tracked(d, self.tag.upper(), self.tag_font,
                          self.title_y + self.title_size * 1.55,
                          ease_out(3.9, 4.9, t), spacing=0.55, color=GOLD)
        return layer

    def _tracked(self, d, text, font, y, a, spacing, color):
        if a <= 0:
            return
        sp = font.size * spacing * (1 + 1.2 * (1 - a))
        widths = [font.getlength(ch) for ch in text]
        total = sum(widths) + sp * (len(text) - 1)
        x = (self.w - total) / 2
        for ch, cw in zip(text, widths):
            d.text((x, y), ch, font=font, fill=color + (int(255 * a),), anchor="ls")
            x += cw + sp

    # ---------- толық кадр ----------
    def frame(self, t):
        img, p = self.background(t)
        self.particles(img, t, p)

        txt = self.text_layer(t)
        # Жазудың жылы жарқылы (кішірейтіп бұлыңғырлау: жылдам)
        small = txt.resize((self.w // 4, self.h // 4), Image.BILINEAR)
        glow = small.filter(ImageFilter.GaussianBlur(self.title_size / 18)).resize(
            (self.w, self.h), Image.BILINEAR)
        ga = np.asarray(glow, np.float32)[..., 3:4] / 255.0
        img += ga * np.asarray(GOLD, np.float32) * 0.55

        ta = np.asarray(txt, np.float32)
        alpha = ta[..., 3:4] / 255.0
        img = img * (1 - alpha) + ta[..., :3] * alpha

        # Виньетка мен түйір
        vx = (self.xx / self.w - 0.5) * 2
        vy = (self.yy / self.h - 0.5) * 2
        vig = 1 - 0.38 * np.clip(vx ** 2 * 0.6 + vy ** 2 * 0.8, 0, 1)
        img *= vig[..., None]
        rng = np.random.default_rng(self.grain_seed + int(t * FPS))
        img += rng.normal(0, 4.0, (self.h, self.w, 1)).astype(np.float32)
        return np.clip(img, 0, 255).astype(np.uint8)


def render(out, w=1920, h=1080, dur=6.0, text=DEFAULT_TEXT, preset="slow",
           fade_in=0.0, fade_out=0.0):
    """Анимацияны out файлына жазады (build.py кесінділерімен бірдей формат)."""
    scene = Scene(w, h, dur, text)
    frames = round(dur * FPS)
    vf = ["setsar=1"]
    if fade_in:
        vf.append(f"fade=t=in:st=0:d={fade_in}")
    if fade_out:
        vf.append(f"fade=t=out:st={max(0, dur - fade_out)}:d={fade_out}")
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-", "-vf", ",".join(vf), "-an",
           "-frames:v", str(frames), "-c:v", "libx264", "-preset", preset, "-crf", "18",
           "-pix_fmt", "yuv420p", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for i in range(frames):
            proc.stdin.write(scene.frame(i / FPS).tobytes())
    except BrokenPipeError:
        pass
    proc.stdin.close()
    err = proc.stderr.read().decode(errors="replace")
    if proc.wait() != 0:
        sys.exit("ffmpeg қатесі:\n" + err[-2000:])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vertical", action="store_true", help="1080x1920, Shorts/Reels")
    ap.add_argument("--preview", action="store_true", help="жартылай өлшем, жылдам")
    ap.add_argument("--dur", type=float, default=6.0, help="ұзақтығы, секунд")
    ap.add_argument("--text", default=DEFAULT_TEXT, help="«|» арқылы: атау|орындаушы||белгі")
    ap.add_argument("--png", type=float, metavar="SEC", help="тек осы секундтағы кадрды PNG етіп сақта")
    ap.add_argument("-o", "--out", help="шығатын файл")
    a = ap.parse_args()
    w, h = (1080, 1920) if a.vertical else (1920, 1080)
    if a.preview:
        w, h = w // 2, h // 2
    name = "title_anim" + ("_vertical" if a.vertical else "") + ("_preview" if a.preview else "")
    out_dir = ROOT / "output"
    out_dir.mkdir(exist_ok=True)
    if a.png is not None:
        out = Path(a.out) if a.out else out_dir / f"{name}_{a.png:.1f}s.png"
        Image.fromarray(Scene(w, h, a.dur, a.text).frame(a.png)).save(out)
    else:
        out = Path(a.out) if a.out else out_dir / f"{name}.mp4"
        render(out, w, h, a.dur, a.text, "veryfast" if a.preview else "slow",
               fade_in=0.6, fade_out=1.0)
    print(f"Дайын: {out}")


if __name__ == "__main__":
    main()
