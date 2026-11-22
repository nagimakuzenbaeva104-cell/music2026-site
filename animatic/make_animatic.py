"""Аниматик «Тайна старого дома» по screenplay.md.

Силуэтная анимация: кадры рисуются PIL, звук синтезируется numpy/scipy, сборка ffmpeg.
Запуск:
    python3 make_animatic.py OUT_DIR            # полный рендер -> OUT_DIR/animatic.mp4
    python3 make_animatic.py OUT_DIR preview    # по одному кадру из каждого шота -> contact sheets
"""
import math, os, sys, subprocess, wave, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from multiprocessing import Pool
from scipy.signal import butter, lfilter

W, H, FPS = 1280, 720, 24
BW, BH = 1408, 792
SR = 44100


def _font(*cands):
    for c in cands:
        if os.path.exists(c):
            return c
    return cands[-1]


LIB = "/usr/share/fonts/truetype/liberation/"
DJ = "/usr/share/fonts/truetype/dejavu/"
F_SERIF = _font(LIB + "LiberationSerif-Regular.ttf")
F_ITAL = _font(LIB + "LiberationSerif-Italic.ttf")
F_BOLD = _font(LIB + "LiberationSerif-Bold.ttf", DJ + "DejaVuSerif-Bold.ttf")
F_SANS = _font(LIB + "LiberationSans-Regular.ttf", DJ + "DejaVuSans.ttf")
F_SANSB = _font(LIB + "LiberationSans-Bold.ttf", DJ + "DejaVuSans-Bold.ttf")
F_MONO = _font(LIB + "LiberationMono-Regular.ttf", DJ + "DejaVuSansMono.ttf")
F_HAND = _font("/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf", F_ITAL)

_FC = {}


def font(path, size):
    k = (path, int(size))
    if k not in _FC:
        _FC[k] = ImageFont.truetype(path, int(size))
    return _FC[k]


# =====================================================================
#  DRAWING HELPERS
# =====================================================================
def vgrad(top, bot, w=BW, h=BH):
    a = np.linspace(0, 1, h)[:, None, None]
    arr = (np.array(top, np.float32) * (1 - a) + np.array(bot, np.float32) * a) * np.ones((1, w, 1), np.float32)
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))


def mul(c, k):
    return tuple(int(max(0, min(255, v * k))) for v in c)


def glow(img, mask_draw_fn, color, strength, blur):
    """Additive light: mask_draw_fn(draw) paints a white mask."""
    m = Image.new("L", img.size, 0)
    mask_draw_fn(ImageDraw.Draw(m))
    if blur:
        sm = m.resize((img.size[0] // 4, img.size[1] // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(max(1, blur / 4)))
        m = sm.resize(img.size, Image.BILINEAR)
    a = np.asarray(m, np.float32)[..., None] / 255 * strength
    arr = np.asarray(img, np.float32) + a * np.array(color, np.float32)
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))


def blend_layer(img, layer_rgba, alpha=1.0):
    if alpha <= 0:
        return img
    base = img.convert("RGBA")
    if alpha < 1:
        a = layer_rgba.getchannel("A").point(lambda v: int(v * alpha))
        layer_rgba = layer_rgba.copy()
        layer_rgba.putalpha(a)
    return Image.alpha_composite(base, layer_rgba).convert("RGB")


def text_c(d, x, y, s, f, fill):
    w = d.textlength(s, font=f)
    d.text((x - w / 2, y), s, font=f, fill=fill)


# ----------------------------------------------------------- figures
def woman(d, x, y, h, c, face=1):
    r = h * 0.068
    hx, hy = x + face * h * 0.01, y - h + r
    d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=c)
    bx = hx - face * r * 0.95
    d.ellipse([bx - r * 0.55, hy - r * 0.95, bx + r * 0.55, hy + r * 0.15], fill=c)
    d.rectangle([x - r * 0.35, hy + r * 0.8, x + r * 0.35, hy + r * 1.6], fill=c)
    sy, wy = y - h + 2.3 * r, y - h * 0.48
    d.polygon([(x - h * 0.12, sy), (x + h * 0.12, sy), (x + h * 0.085, wy), (x - h * 0.085, wy)], fill=c)
    d.polygon([(x - h * 0.09, wy), (x - h * 0.005, wy), (x - h * 0.02, y), (x - h * 0.075, y)], fill=c)
    d.polygon([(x + h * 0.005, wy), (x + h * 0.09, wy), (x + h * 0.075, y), (x + h * 0.02, y)], fill=c)
    aw = max(2, int(h * 0.034))
    d.line([(x - h * 0.115, sy + 4), (x - h * 0.13, y - h * 0.42)], fill=c, width=aw)
    d.line([(x + h * 0.115, sy + 4), (x + h * 0.13, y - h * 0.42)], fill=c, width=aw)


def woman_sit(d, x, y, h, c, face=1, shin=0.32):
    """Sitting, hugging knees. y = level of the seat."""
    r = h * 0.075
    hx, hy = x + face * h * 0.06, y - h * 0.78
    d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=c)
    bx = hx - face * r * 0.95
    d.ellipse([bx - r * 0.55, hy - r * 0.95, bx + r * 0.55, hy + r * 0.15], fill=c)
    d.polygon([(hx - face * h * 0.13, hy + r * 1.2), (hx + face * h * 0.06, hy + r * 1.2),
               (x + face * h * 0.06, y), (x - face * h * 0.12, y)], fill=c)
    kx, ky = x + face * h * 0.28, y - h * 0.38
    d.polygon([(x - face * h * 0.05, y), (x + face * h * 0.06, y - h * 0.12), (kx, ky - h * 0.03), (kx + face * h * 0.03, ky + h * 0.05)], fill=c)
    d.polygon([(kx - face * h * 0.03, ky), (kx + face * h * 0.05, ky + h * 0.02), (kx + face * h * 0.06, y + h * shin), (kx - face * h * 0.03, y + h * shin)], fill=c)
    d.line([(hx, hy + r * 2), (kx, ky + h * 0.04)], fill=c, width=max(2, int(h * 0.04)))


def man(d, x, y, h, c, face=1, axe=None):
    r = h * 0.07
    hx, hy = x + face * h * 0.05, y - h + r * 1.2
    d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=c)
    d.rectangle([hx - r * 1.05, hy - r * 1.05, hx + r * 1.05, hy - r * 0.25], fill=c)
    d.polygon([(hx + face * r * 0.6, hy - r * 0.45), (hx + face * r * 1.9, hy - r * 0.2), (hx + face * r * 0.6, hy - r * 0.15)], fill=c)
    sy, wy = hy + r * 1.3, y - h * 0.47
    d.polygon([(x - h * 0.15 + face * h * 0.04, sy), (x + h * 0.15 + face * h * 0.04, sy), (x + h * 0.12, wy), (x - h * 0.12, wy)], fill=c)
    d.polygon([(x - h * 0.115, wy), (x - h * 0.01, wy), (x - h * 0.03, y), (x - h * 0.11, y)], fill=c)
    d.polygon([(x + h * 0.01, wy), (x + h * 0.115, wy), (x + h * 0.11, y), (x + h * 0.03, y)], fill=c)
    aw = max(2, int(h * 0.045))
    shx = x + face * h * 0.17
    if axe == "up":
        tx, ty = shx + face * h * 0.05, sy - h * 0.38
        d.line([(shx, sy + 6), (tx, ty)], fill=c, width=aw)
        d.line([(tx, ty), (tx - face * h * 0.06, ty - h * 0.25)], fill=(c[0] + 20, c[1] + 15, c[2] + 10), width=max(2, int(h * 0.02)))
        bx, by = tx - face * h * 0.06, ty - h * 0.25
        d.polygon([(bx, by), (bx + face * h * 0.1, by - h * 0.03), (bx + face * h * 0.09, by + h * 0.07)], fill=(90, 90, 95))
    elif axe == "down":
        tx, ty = shx + face * h * 0.06, y - h * 0.38
        d.line([(shx, sy + 6), (tx, ty)], fill=c, width=aw)
        d.line([(tx, ty), (tx + face * h * 0.12, y - h * 0.02)], fill=(c[0] + 20, c[1] + 15, c[2] + 10), width=max(2, int(h * 0.02)))
        bx, by = tx + face * h * 0.12, y - h * 0.02
        d.polygon([(bx, by), (bx + face * h * 0.1, by - h * 0.02), (bx + face * h * 0.04, by - h * 0.1)], fill=(90, 90, 95))
    else:
        d.line([(shx, sy + 6), (shx + face * h * 0.02, y - h * 0.42)], fill=c, width=aw)
    d.line([(x - face * h * 0.12, sy + 6), (x - face * h * 0.14, y - h * 0.42)], fill=c, width=aw)


def man_sit(d, x, y, h, c, face=-1):
    r = h * 0.075
    hx, hy = x + face * h * 0.08, y - h * 0.8
    d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=c)
    d.rectangle([hx - r * 1.05, hy - r * 1.05, hx + r * 1.05, hy - r * 0.25], fill=c)
    d.polygon([(hx + face * r * 0.6, hy - r * 0.45), (hx + face * r * 1.9, hy - r * 0.2), (hx + face * r * 0.6, hy - r * 0.15)], fill=c)
    d.polygon([(hx - face * h * 0.16, hy + r * 1.3), (hx + face * h * 0.1, hy + r * 1.3), (x + face * h * 0.08, y), (x - face * h * 0.14, y)], fill=c)
    d.polygon([(x - face * h * 0.1, y), (x + face * h * 0.3, y - h * 0.06), (x + face * h * 0.32, y + h * 0.04), (x - face * h * 0.1, y + h * 0.06)], fill=c)
    d.rectangle([min(x + face * h * 0.24, x + face * h * 0.32), y, max(x + face * h * 0.24, x + face * h * 0.32), y + h * 0.36], fill=c)


def dog(d, x, y, s, c, face=1, lying=False):
    if lying:
        d.ellipse([x - s * 0.6, y - s * 0.35, x + s * 0.5, y], fill=c)
        hx = x + face * s * 0.55
        d.ellipse([hx - s * 0.18, y - s * 0.38, hx + s * 0.18, y - s * 0.05], fill=c)
        d.polygon([(hx - s * 0.12, y - s * 0.3), (hx - s * 0.05, y - s * 0.52), (hx + s * 0.02, y - s * 0.32)], fill=c)
        d.polygon([(hx + s * 0.02, y - s * 0.32), (hx + s * 0.09, y - s * 0.52), (hx + s * 0.15, y - s * 0.28)], fill=c)
        return
    d.ellipse([x - s * 0.5, y - s * 0.62, x + s * 0.45, y - s * 0.3], fill=c)
    for lx in (-0.38, -0.22, 0.2, 0.33):
        d.rectangle([x + lx * s - s * 0.04, y - s * 0.4, x + lx * s + s * 0.04, y], fill=c)
    hx, hy = x + face * s * 0.52, y - s * 0.72
    d.ellipse([hx - s * 0.17, hy - s * 0.15, hx + s * 0.17, hy + s * 0.15], fill=c)
    d.polygon([(hx + face * s * 0.1, hy - s * 0.05), (hx + face * s * 0.32, hy + s * 0.03), (hx + face * s * 0.1, hy + s * 0.1)], fill=c)
    d.polygon([(hx - s * 0.12, hy - s * 0.08), (hx - s * 0.06, hy - s * 0.34), (hx + s * 0.0, hy - s * 0.1)], fill=c)
    d.polygon([(hx + s * 0.0, hy - s * 0.1), (hx + s * 0.07, hy - s * 0.34), (hx + s * 0.12, hy - s * 0.06)], fill=c)
    tx = x - face * s * 0.45
    d.arc([tx - s * 0.18, y - s * 0.9, tx + s * 0.18, y - s * 0.55], 0, 360, fill=c, width=max(2, int(s * 0.08)))


RED = (205, 45, 40)
BLUE = (70, 140, 215)


def girl(d, x, y, h, c, sandal, face=1, legs=0.0, wave=None):
    r = h * 0.1
    hx, hy = x, y - h + r
    d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=c)
    for sgn in (-1, 1):
        d.ellipse([hx + sgn * r * 1.05 - r * 0.35, hy - r * 0.1, hx + sgn * r * 1.05 + r * 0.35, hy + r * 0.6], fill=c)
    sy = hy + r * 1.15
    d.polygon([(x - h * 0.1, sy), (x + h * 0.1, sy), (x + h * 0.21, y - h * 0.3), (x - h * 0.21, y - h * 0.3)], fill=c)
    aw = max(2, int(h * 0.045))
    d.line([(x - h * 0.09, sy + 3), (x - h * 0.17, y - h * 0.48)], fill=c, width=aw)
    if wave is not None:
        ang = -0.9 + 0.35 * math.sin(wave)
        d.line([(x + h * 0.09, sy + 3), (x + h * 0.09 + h * 0.3 * math.sin(-ang), sy - h * 0.25 * math.cos(ang) + 10)], fill=c, width=aw)
    else:
        d.line([(x + h * 0.09, sy + 3), (x + h * 0.17, y - h * 0.48)], fill=c, width=aw)
    lw = max(2, int(h * 0.05))
    for sgn, ph in ((-1, 0), (1, math.pi)):
        lx0 = x + sgn * h * 0.06
        off = h * 0.12 * math.sin(legs + ph) if legs else 0
        fx, fy = lx0 + off, y - h * 0.03
        d.line([(lx0, y - h * 0.3), (fx, fy)], fill=c, width=lw)
        d.rectangle([fx - h * 0.04, fy - h * 0.02, fx + h * 0.05, fy + h * 0.03], fill=sandal)


def girl_sit(d, x, y, h, c, sandal, swing=0.0):
    """Sitting on bed edge, legs dangling. y = seat level."""
    r = h * 0.1
    hx, hy = x, y - h * 0.62
    d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=c)
    for sgn in (-1, 1):
        d.ellipse([hx + sgn * r * 1.05 - r * 0.35, hy - r * 0.1, hx + sgn * r * 1.05 + r * 0.35, hy + r * 0.6], fill=c)
    d.polygon([(x - h * 0.1, hy + r * 1.1), (x + h * 0.1, hy + r * 1.1), (x + h * 0.2, y), (x - h * 0.17, y)], fill=c)
    lw = max(2, int(h * 0.05))
    for k, sgn in enumerate((-1, 1)):
        kx = x + h * 0.12 + sgn * h * 0.04
        a = 0.5 * math.sin(swing + k * math.pi)
        fx, fy = kx + h * 0.28 * math.sin(a), y + h * 0.28 * math.cos(a)
        d.line([(x + sgn * h * 0.04, y - h * 0.02), (kx, y)], fill=c, width=lw)
        d.line([(kx, y), (fx, fy)], fill=c, width=lw)
        d.rectangle([fx - h * 0.03, fy - h * 0.01, fx + h * 0.06, fy + h * 0.035], fill=sandal)


def grandma_sit(d, x, y, h, c, face=1):
    r = h * 0.075
    hx, hy = x + face * h * 0.04, y - h * 0.82
    d.polygon([(hx - r * 1.3, hy + r * 1.1), (hx, hy - r * 1.4), (hx + r * 1.3, hy + r * 1.1)], fill=c)
    d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=c)
    d.polygon([(hx - h * 0.15, hy + r * 1.2), (hx + h * 0.12, hy + r * 1.2), (x + h * 0.18, y), (x - h * 0.18, y)], fill=c)
    d.line([(hx + face * h * 0.1, hy + r * 2), (hx + face * h * 0.3, hy + r * 1.2)], fill=c, width=max(2, int(h * 0.04)))


def swallow(d, x, y, s, c, face=1):
    d.polygon([(x - face * s, y), (x - face * s * 0.2, y - s * 0.25), (x + face * s * 0.6, y - s * 0.12),
               (x + face * s * 0.9, y - s * 0.02), (x + face * s * 0.55, y + s * 0.08), (x - face * s * 0.2, y + s * 0.18)], fill=c)
    d.polygon([(x - face * s * 0.2, y - s * 0.15), (x + face * s * 0.3, y - s * 0.9), (x + face * s * 0.35, y - s * 0.12)], fill=c)
    d.polygon([(x - face * s * 0.9, y + s * 0.02), (x - face * s * 1.6, y - s * 0.3), (x - face * s * 1.2, y + s * 0.05), (x - face * s * 1.6, y + s * 0.35)], fill=c)


def car(d, x, y, s, c=(235, 235, 230)):
    d.ellipse([x - s * 1.2, y - s * 0.15, x + s * 1.2, y + s * 0.35], fill=(60, 50, 35))
    d.rounded_rectangle([x - s, y - s * 0.45, x + s, y + s * 0.1], radius=int(s * 0.15), fill=c)
    d.rounded_rectangle([x - s * 0.55, y - s * 0.8, x + s * 0.45, y - s * 0.4], radius=int(s * 0.12), fill=mul(c, 0.85))


# ----------------------------------------------------------- objects
def clock(d, cx, cy, R, hh, mm, ang=0.0, ss=None, case=(55, 36, 22), face_c=(200, 190, 165), ink=(30, 22, 15), plen=2.1, show_case=True):
    if show_case:
        d.rectangle([cx - 1.35 * R, cy - 1.35 * R, cx + 1.35 * R, cy + R + plen * R + 0.55 * R], fill=case, outline=mul(case, 1.4), width=max(2, int(R * 0.05)))
    px, py = cx, cy + R + 4
    bx, by = px + plen * R * math.sin(ang), py + plen * R * math.cos(ang)
    d.line([px, py, bx, by], fill=(150, 120, 60), width=max(2, int(R * 0.05)))
    br = R * 0.27
    d.ellipse([bx - br, by - br, bx + br, by + br], fill=(170, 135, 60), outline=(110, 85, 40), width=2)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=face_c, outline=mul(case, 1.6), width=max(3, int(R * 0.07)))
    for i in range(60):
        a = math.radians(i * 6)
        l = R * (0.14 if i % 5 == 0 else 0.05)
        d.line([cx + (R * 0.88) * math.sin(a), cy - (R * 0.88) * math.cos(a), cx + (R * 0.88 - l) * math.sin(a), cy - (R * 0.88 - l) * math.cos(a)],
               fill=ink, width=max(1, int(R * (0.035 if i % 5 == 0 else 0.015))))
    for a_deg, ln, wd in [((hh % 12 + mm / 60) * 30, 0.5, 0.07), (mm * 6, 0.78, 0.04)]:
        a = math.radians(a_deg)
        d.line([cx, cy, cx + R * ln * math.sin(a), cy - R * ln * math.cos(a)], fill=ink, width=max(2, int(R * wd)))
    if ss is not None:
        a = math.radians(ss * 6)
        d.line([cx, cy, cx + R * 0.85 * math.sin(a), cy - R * 0.85 * math.cos(a)], fill=(150, 30, 25), width=max(1, int(R * 0.015)))
    d.ellipse([cx - R * 0.06, cy - R * 0.06, cx + R * 0.06, cy + R * 0.06], fill=ink)


def wallpaper(img, box, base, flower, step=46, rose=True, seed=1):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=base)
    rng = np.random.default_rng(seed)
    for j, y in enumerate(range(int(y0) - step, int(y1) + step, step)):
        for x in range(int(x0) - step + (j % 2) * step // 2, int(x1) + step, step):
            if rose:
                rr = step * 0.18
                d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=flower)
                d.ellipse([x - rr * 0.5, y - rr * 0.5, x + rr * 0.5, y + rr * 0.5], fill=mul(flower, 0.8))
                d.line([x, y + rr, x + rr * 0.6, y + rr * 2.2], fill=mul(base, 0.85), width=2)
            else:
                for k in range(5):
                    a = k * 2 * math.pi / 5 + rng.uniform(0, 0.3)
                    d.ellipse([x + 7 * math.cos(a) - 4, y + 7 * math.sin(a) - 4, x + 7 * math.cos(a) + 4, y + 7 * math.sin(a) + 4], fill=flower)
                d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(200, 170, 80))
    # clip outside box by redrawing borders not needed: pattern drawn only within area mostly


def logs(d, box, c, step=22):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=c)
    y = y0
    while y < y1:
        d.line([x0, y, x1, y], fill=mul(c, 0.72), width=3)
        d.line([x0, y + 3, x1, y + 3], fill=mul(c, 1.12), width=1)
        y += step


def window_carved(d, box, frame, glass, s=1.0, mullion=True):
    x0, y0, x1, y1 = box
    fw = max(4, int(10 * s))
    d.rectangle([x0 - fw * 2, y0 - fw * 2, x1 + fw * 2, y1 + fw * 2], fill=frame)
    cx = (x0 + x1) / 2
    d.polygon([(x0 - fw * 3, y0 - fw * 2), (cx, y0 - fw * 7), (x1 + fw * 3, y0 - fw * 2)], fill=frame)
    d.rectangle([x0 - fw * 3, y1 + fw * 2, x1 + fw * 3, y1 + fw * 3.5], fill=frame)
    for k in range(5):
        xx = x0 + (x1 - x0) * (k + 0.5) / 5
        d.ellipse([xx - fw * 0.6, y0 - fw * 4.2, xx + fw * 0.6, y0 - fw * 3.0], fill=mul(frame, 0.7))
    d.rectangle(box, fill=glass)
    if mullion:
        d.rectangle([cx - fw / 2, y0, cx + fw / 2, y1], fill=frame)
        my = y0 + (y1 - y0) * 0.4
        d.rectangle([x0, my - fw / 2, x1, my + fw / 2], fill=frame)


def apple_tree(d, x, y, s, leaves=(70, 95, 50), fruit=(185, 40, 35), trunk=(55, 40, 30)):
    d.polygon([(x - 12 * s, y), (x + 12 * s, y), (x + 6 * s, y - 150 * s), (x - 6 * s, y - 150 * s)], fill=trunk)
    rng = np.random.default_rng(int(x))
    for _ in range(14):
        cx, cy = x + rng.uniform(-110, 110) * s, y - 160 * s + rng.uniform(-80, 50) * s
        rr = rng.uniform(45, 75) * s
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=mul(leaves, rng.uniform(0.85, 1.1)))
    if fruit:
        for _ in range(22):
            fx, fy = x + rng.uniform(-150, 150) * s, y - 160 * s + rng.uniform(-90, 80) * s
            d.ellipse([fx - 6 * s, fy - 6 * s, fx + 6 * s, fy + 6 * s], fill=fruit)


def house(img, cx, base, s, wall=(78, 54, 34), frame=(110, 130, 150), roof=(52, 46, 44), glass=(30, 34, 40), porch_ok=False, plaque=False, lit=None):
    d = ImageDraw.Draw(img)
    w, h = 430 * s, 270 * s
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, base - h, base
    logs(d, (x0, y0, x1, y1), wall, int(17 * s))
    d.polygon([(x0 - 35 * s, y0 + 2), (cx, y0 - 175 * s), (x1 + 35 * s, y0 + 2)], fill=roof)
    d.polygon([(x0 + 15 * s, y0), (cx, y0 - 150 * s), (x1 - 15 * s, y0)], fill=mul(wall, 0.9))
    for k in range(1, 8):
        yy = y0 - k * 18 * s
        half = (150 * s - k * 18 * s) / (150 * s) * (w / 2 - 15 * s)
        if half > 0:
            d.line([cx - half, yy, cx + half, yy], fill=mul(wall, 0.65), width=2)
    gl = glass
    for gx in (cx - 55 * s, cx + 55 * s):
        window_carved(d, (gx - 26 * s, y0 - 95 * s, gx + 26 * s, y0 - 30 * s), frame, gl, s * 0.7)
    for i, gx in enumerate((x0 + 75 * s, cx, x1 - 75 * s)):
        g = lit if lit else gl
        window_carved(d, (gx - 38 * s, y0 + 70 * s, gx + 38 * s, y0 + 170 * s), frame, g, s)
    # porch (left)
    px0, px1 = x0 - 110 * s, x0
    d.rectangle([px0, y0 + 60 * s, px1, y1], fill=mul(wall, 0.85))
    d.polygon([(px0 - 15 * s, y0 + 62 * s), (px0 + 55 * s, y0 + 5 * s), (px1 + 5 * s, y0 + 62 * s)], fill=roof)
    d.rectangle([px0 + 25 * s, y0 + 100 * s, px1 - 25 * s, y1], fill=mul(wall, 0.45))
    tilt = 0 if porch_ok else 9 * s
    for k in range(3):
        sy = y1 + k * 14 * s
        d.polygon([(px0 - 15 * s - k * 10 * s, sy), (px1 + 5 * s + k * 10 * s, sy + tilt * (k + 1) / 3),
                   (px1 + 5 * s + k * 10 * s, sy + 14 * s + tilt * (k + 1) / 3), (px0 - 15 * s - k * 10 * s, sy + 14 * s)], fill=mul(wall, 1.15 - k * 0.12))
    if plaque:
        d.rectangle([px0 + 20 * s, y0 + 70 * s, px1 - 20 * s, y0 + 92 * s], fill=(190, 150, 95))
    return (px0, px1, y0, y1)


# =====================================================================
#  SHOT BACKGROUNDS
# =====================================================================
def road_points():
    pts = []
    P = [(180, 820), (560, 560), (820, 390), (1060, 250), (1130, 200)]
    for i in range(len(P) - 1):
        for k in range(20):
            u = k / 20
            pts.append((P[i][0] * (1 - u) + P[i + 1][0] * u, P[i][1] * (1 - u) + P[i + 1][1] * u))
    pts.append(P[-1])
    return pts


ROAD = road_points()


def d_field(autumn=False, with_house=False):
    img = vgrad((185, 195, 200), (215, 205, 175))
    d = ImageDraw.Draw(img)
    fc = (196, 170, 100) if not autumn else (175, 150, 95)
    d.rectangle([0, 190, BW, BH], fill=fc)
    rng = np.random.default_rng(3)
    for k in range(40):
        y = 190 + k * 16 + rng.integers(0, 8)
        d.line([0, y, BW, y - 60], fill=mul(fc, rng.uniform(0.9, 1.06)), width=8)
    jag = [(0, 200)] + [(x, 160 + rng.integers(-18, 10)) for x in range(0, BW + 30, 24)] + [(BW, 200)]
    d.polygon(jag, fill=(40, 58, 44))
    for x in (980, 1040, 1180):
        d.rectangle([x, 178, x + 30, 196], fill=(80, 60, 50))
        d.polygon([(x - 4, 178), (x + 15, 166), (x + 34, 178)], fill=(60, 45, 40))
    d.line(ROAD, fill=(218, 203, 165), width=24, joint="curve")
    if with_house:
        hx, hy = 1135, 205
        apple_tree(d, hx - 45, hy + 6, 0.12, leaves=(205, 170, 50) if autumn else (70, 95, 50), fruit=None)
        d.rectangle([hx - 22, hy - 16, hx + 22, hy + 6], fill=(78, 54, 34))
        d.polygon([(hx - 27, hy - 15), (hx, hy - 32), (hx + 27, hy - 15)], fill=(52, 46, 44))
        d.ellipse([hx + 30, hy + 2, hx + 62, hy + 14], fill=(110, 150, 170))
    return img


def d_car_int():
    img = vgrad((225, 222, 205), (200, 175, 110))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, BW, 235], fill=(222, 222, 212))
    d.polygon([(0, 235), (BW, 235), (BW, 400), (0, 400)], fill=(200, 175, 110))
    d.polygon([(640, 235), (700, 235), (900, 400), (420, 400)], fill=(215, 200, 160))
    d.polygon([(0, 380), (BW, 340), (BW, BH), (0, BH)], fill=(28, 25, 22))
    d.ellipse([90, 400, 650, 960], outline=(15, 14, 13), width=34)
    woman(d, 330, 1250, 1050, (18, 16, 15), face=1)
    d.rectangle([360, 290, 430, 312], fill=(60, 60, 62))
    d.rounded_rectangle([880, 440, 1380, BH + 40], radius=40, fill=(58, 50, 45))
    d.rectangle([940, 520, 1250, 760], fill=(185, 195, 200))
    f = font(F_SANS, 20)
    for i, ln in enumerate(["ДОГОВОР КУПЛИ-ПРОДАЖИ", "Продавец: Воронцова", "Алина Сергеевна", "———————", "———————"]):
        d.text((960, 540 + i * 30), ln, font=f, fill=(40, 40, 50))
    d.polygon([(1090, 470), (1270, 480), (1262, 620), (1082, 610)], fill=(240, 220, 90))
    fh = font(F_HAND, 24)
    for i, ln in enumerate(["Чт, 11:00 —", "нотариус.", "Покупатель", "снесёт дом"]):
        d.text((1100, 482 + i * 30), ln, font=fh, fill=(60, 50, 120))
    d.rounded_rectangle([690, 352, 830, 385], radius=8, fill=(10, 10, 12))
    return img


def d_mirror():
    img = vgrad((40, 36, 32), (20, 18, 16))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([280, 170, 1128, 540], radius=60, fill=(12, 12, 12))
    inner = vgrad((215, 210, 195), (120, 110, 95), 808, 330)
    di = ImageDraw.Draw(inner)
    di.rectangle([0, 230, 808, 330], fill=(70, 62, 55))
    di.rectangle([380, 30, 808, 150], fill=(230, 225, 205))
    woman(di, 230, 900, 900, (22, 20, 18), face=1)
    di.rectangle([250, 25, 330, 50], fill=(90, 90, 95))
    m = Image.new("L", inner.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, 807, 329], radius=50, fill=255)
    img.paste(inner, (300, 190), m)
    return img


def d_house_day():
    img = vgrad((150, 172, 192), (222, 212, 190))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 640, BW, BH], fill=(96, 110, 60))
    apple_tree(d, 190, 700, 1.25)
    house(img, 790, 650, 1.4)
    d = ImageDraw.Draw(img)
    man(d, 1215, 720, 290, (25, 24, 22), face=-1)
    dog(d, 1110, 735, 120, (30, 29, 27), face=-1)
    for x in range(1000, BW, 34):
        d.rectangle([x, 600, x + 22, BH], fill=(70, 58, 44))
        d.polygon([(x, 600), (x + 11, 585), (x + 22, 600)], fill=(70, 58, 44))
    d.rectangle([1000, 640, BW, 652], fill=(60, 50, 38))
    woman(d, 560, 790, 330, (20, 19, 18), face=1)
    return img


def d_window_up():
    img = Image.new("RGB", (BW, BH))
    d = ImageDraw.Draw(img)
    logs(d, (0, 0, BW, BH), (78, 54, 34), 34)
    window_carved(d, (494, 196, 914, 600), (110, 130, 150), (28, 32, 38), 2.2)
    return img


PAL = {
    "day":   dict(wall=(150, 120, 88), fl=(170, 115, 98), floor=(96, 66, 42), out=(232, 226, 200), wood=(72, 46, 30), face=(205, 195, 170)),
    "night": dict(wall=(34, 44, 68), fl=(44, 54, 84), floor=(24, 29, 46), out=(70, 92, 132), wood=(26, 26, 38), face=(120, 135, 160)),
    "cold":  dict(wall=(128, 124, 116), fl=(140, 122, 122), floor=(80, 70, 62), out=(215, 220, 225), wood=(60, 46, 36), face=(190, 188, 178)),
    "dawn":  dict(wall=(168, 128, 122), fl=(184, 140, 138), floor=(108, 78, 70), out=(245, 195, 180), wood=(80, 52, 44), face=(225, 200, 185)),
}


def d_dining(pal="day"):
    p = PAL[pal]
    img = Image.new("RGB", (BW, BH))
    wallpaper(img, (0, 0, BW, 600), p["wall"], p["fl"], 50, True)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 600, BW, BH], fill=p["floor"])
    for y in range(612, BH, 26):
        d.line([0, y, BW, y], fill=mul(p["floor"], 0.8), width=2)
    d.rectangle([0, 590, BW, 604], fill=mul(p["wood"], 1.1))
    d.rectangle([110, 150, 380, 470], fill=p["out"])
    d.rectangle([96, 136, 394, 484], outline=mul(p["wood"], 1.2), width=14)
    d.rectangle([238, 150, 252, 470], fill=mul(p["wood"], 1.2))
    for yy in range(160, 470, 18):
        for xx in range(118, 380, 18):
            d.ellipse([xx, yy, xx + 7, yy + 7], fill=mul(p["out"], 0.82))
    d.rectangle([640, 440, 1060, 610], fill=p["wood"])
    d.rectangle([670, 300, 1030, 440], fill=mul(p["wood"], 0.8))
    for k in range(4):
        xx = 700 + k * 85
        d.ellipse([xx, 320, xx + 60, 380], fill=mul(p["face"], 0.85), outline=mul(p["face"], 0.6), width=3)
    d.rectangle([660, 290, 1040, 302], fill=mul(p["wood"], 1.3))
    d.rectangle([650, 470, 1050, 480], fill=mul(p["wood"], 1.3))
    d.ellipse([340, 520, 640, 580], fill=mul(p["face"], 0.9))
    d.rectangle([380, 550, 600, 650], fill=mul(p["face"], 0.8))
    d.rectangle([420, 640, 440, 700], fill=p["wood"])
    d.rectangle([540, 640, 560, 700], fill=p["wood"])
    d.polygon([(150, BH), (620, 640), (900, 640), (1200, BH)], fill=mul((140, 60, 50), 0.55 if pal == "night" else 0.9))
    if pal == "day":
        img = glow(img, lambda m: m.polygon([(110, 150), (380, 150), (720, 760), (300, 790)], fill=255), (255, 220, 160), 0.28, 25)
    if pal == "night":
        def moon(m):
            m.polygon([(200, 640), (520, 640), (640, BH), (240, BH)], fill=180)
        img = glow(img, moon, (120, 150, 210), 0.35, 12)
        d = ImageDraw.Draw(img)
        for yy in range(650, BH, 22):
            for xx in range(220, 620, 22):
                d.ellipse([xx, yy, xx + 6, yy + 6], fill=(70, 90, 130))
    if pal == "dawn":
        img = glow(img, lambda m: m.polygon([(110, 150), (380, 150), (760, 760), (300, 790)], fill=255), (255, 170, 150), 0.25, 30)
    return img


def d_photo():
    img = vgrad((95, 64, 42), (70, 46, 30))
    d = ImageDraw.Draw(img)
    for y in range(0, BH, 14):
        d.line([0, y, BW, y + 6], fill=(85, 56, 36), width=2)
    ph = Image.new("RGB", (560, 420), (226, 216, 190))
    dp = ImageDraw.Draw(ph)
    inner = vgrad((180, 150, 110), (140, 112, 80), 500, 360)
    ph.paste(inner, (30, 30))
    grandma_sit(dp, 220, 360, 330, (60, 44, 32))
    girl(dp, 370, 385, 220, (60, 44, 32), (150, 120, 90))
    dp.polygon([(352, 168), (390, 166), (395, 198), (380, 205), (350, 200)], fill=(95, 64, 42))
    ph = ph.rotate(4, expand=True, fillcolor=(0, 0, 0))
    mask = ph.convert("L").point(lambda v: 255 if v > 2 else 0)
    img.paste(ph, (420, 170), mask)
    return img


def d_photo_back():
    img = vgrad((95, 64, 42), (70, 46, 30))
    d = ImageDraw.Draw(img)
    d.rectangle([420, 180, 980, 600], fill=(222, 210, 182))
    d.text((520, 330), "Лето 1996", font=font(F_HAND, 64), fill=(70, 60, 110))
    return img


def d_clock_wall(pal="day"):
    p = PAL[pal]
    img = Image.new("RGB", (BW, BH))
    wallpaper(img, (0, 0, BW, BH), p["wall"], p["fl"], 70, True)
    return img


def d_bedroom():
    img = vgrad((170, 98, 62), (120, 66, 44))
    d = ImageDraw.Draw(img)
    d.polygon([(0, 0), (620, 0), (0, 300)], fill=(90, 52, 36))
    d.rectangle([0, 640, BW, BH], fill=(80, 46, 30))
    sun = vgrad((250, 170, 95), (200, 92, 70), 250, 260)
    img.paste(sun, (900, 170))
    d.rectangle([888, 158, 1162, 442], outline=(60, 36, 24), width=14)
    d.rectangle([1018, 170, 1032, 430], fill=(60, 36, 24))
    img = glow(img, lambda m: m.polygon([(900, 170), (1150, 170), (1250, 790), (650, 790)], fill=255), (255, 170, 110), 0.25, 30)
    d = ImageDraw.Draw(img)
    d.rectangle([100, 470, 620, 640], fill=(40, 30, 26))
    cols = [(150, 70, 60), (90, 110, 80), (170, 140, 80), (80, 90, 130), (160, 110, 90)]
    for i in range(10):
        for j in range(3):
            d.rectangle([110 + i * 50, 480 + j * 50, 158 + i * 50, 528 + j * 50], fill=cols[(i + j * 2) % 5])
    for xx in (100, 610):
        d.rectangle([xx - 6, 380, xx + 6, 680], fill=(20, 18, 18))
        d.ellipse([xx - 14, 366, xx + 14, 394], fill=(20, 18, 18))
    d.line([100, 410, 610, 410], fill=(20, 18, 18), width=6)
    woman(d, 1030, 720, 430, (25, 15, 12), face=1)
    return img


def d_trellis():
    img = vgrad((120, 70, 48), (70, 40, 28))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 620, BW, BH], fill=(62, 38, 26))
    panels = [((190, 110), (510, 80), (510, 600), (190, 590)), ((540, 60), (870, 60), (870, 600), (540, 600)), ((900, 80), (1220, 110), (1220, 590), (900, 600))]
    for P in panels:
        d.polygon([(P[0][0] - 14, P[0][1] - 14), (P[1][0] + 14, P[1][1] - 14), (P[2][0] + 14, P[2][1] + 14), (P[3][0] - 14, P[3][1] + 14)], fill=(50, 30, 20))
        d.polygon(P, fill=(150, 96, 70))
    d.rectangle([910, 380, 1210, 470], fill=(40, 30, 26))
    cols = [(150, 70, 60), (90, 110, 80), (170, 140, 80), (80, 90, 130)]
    for i in range(6):
        d.rectangle([915 + i * 49, 385, 960 + i * 49, 465], fill=mul(cols[i % 4], 0.85))
    for xx in (350, 705):
        d.ellipse([xx - 48, 400, xx + 48, 500], fill=(28, 16, 12))
        d.polygon([(xx - 105, 600), (xx - 42, 492), (xx + 42, 492), (xx + 105, 600)], fill=(28, 16, 12))
    return img


TRELLIS_RIGHT = (900, 80, 1220, 600)


def d_wall_roses(pal="night"):
    p = PAL[pal]
    img = Image.new("RGB", (BW, BH))
    wallpaper(img, (0, 0, BW, BH), p["wall"], p["fl"], 110, True)
    return img


def d_yard():
    img = vgrad((185, 205, 218), (232, 226, 210))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 560, BW, BH], fill=(112, 100, 70))
    for x in range(0, BW, 30):
        d.rectangle([x, 430, x + 20, 560], fill=(120, 100, 80))
    d.rectangle([0, 470, BW, 480], fill=(105, 88, 70))
    for row in range(6):
        for k in range(11):
            cx, cy = 100 + k * 40 + (row % 2) * 20, 590 - row * 38
            d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=(140, 100, 60), outline=(95, 66, 40), width=3)
            d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], outline=(170, 130, 85), width=2)
    d.rectangle([1100, 430, 1225, 610], fill=(55, 45, 38))
    for yy in (460, 530, 590):
        d.rectangle([1095, yy, 1230, yy + 8], fill=(35, 32, 30))
    for cx in (820, 880, 1300):
        d.ellipse([cx - 22, 650, cx + 22, 685], fill=(220, 215, 205))
        d.ellipse([cx + 12, 635, cx + 32, 655], fill=(220, 215, 205))
        d.polygon([(cx + 18, 635), (cx + 24, 624), (cx + 28, 636)], fill=(190, 40, 40))
    d.rectangle([560, 640, 660, 700], fill=(90, 66, 44))
    return img


def d_wall_peel():
    img = Image.new("RGB", (BW, BH))
    wallpaper(img, (0, 0, BW, BH), PAL["cold"]["wall"], PAL["cold"]["fl"], 90, True)
    return img


def d_blue_door():
    img = Image.new("RGB", (BW, BH))
    wallpaper(img, (0, 0, BW, BH), PAL["cold"]["wall"], PAL["cold"]["fl"], 90, True)
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(5)
    pts = [(400 + rng.integers(-25, 25), y) for y in range(140, BH + 40, 40)]
    pts += [(1010 + rng.integers(-25, 25), y) for y in range(BH + 40, 140, -40)]
    d.polygon(pts, fill=(215, 205, 175))
    wallpaper_patch = Image.new("RGB", (BW, BH))
    wallpaper(wallpaper_patch, (0, 0, BW, BH), (215, 205, 175), (110, 140, 200), 40, False, 4)
    m = Image.new("L", (BW, BH), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    img.paste(wallpaper_patch, (0, 0), m)
    d = ImageDraw.Draw(img)
    d.rectangle([500, 230, 910, BH], fill=(60, 50, 40))
    d.rectangle([520, 250, 890, BH], fill=(72, 112, 152))
    d.rectangle([550, 280, 860, 470], outline=(58, 92, 128), width=8)
    d.rectangle([550, 510, 860, 760], outline=(58, 92, 128), width=8)
    swallow(d, 640, 420, 46, (30, 50, 90), 1)
    swallow(d, 770, 400, 46, (30, 50, 90), -1)
    hx, hy = 840, 560
    d.ellipse([hx - 16, hy - 16, hx + 16, hy + 16], fill=(150, 130, 90))
    d.polygon([(hx, hy), (hx - 42, hy - 22), (hx - 42, hy + 20)], fill=(175, 80, 75))
    d.polygon([(hx, hy), (hx + 42, hy - 22), (hx + 42, hy + 20)], fill=(175, 80, 75))
    d.line([(hx, hy), (hx - 14, hy + 50)], fill=(175, 80, 75), width=8)
    d.line([(hx, hy), (hx + 16, hy + 52)], fill=(175, 80, 75), width=8)
    return img


def d_phone(title, body, bg=(30, 40, 55), header_c=(150, 160, 180)):
    img = vgrad(bg, mul(bg, 0.5))
    img = img.filter(ImageFilter.GaussianBlur(4))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([474, 60, 934, 820], radius=50, fill=(12, 12, 14))
    d.rounded_rectangle([494, 110, 914, 800], radius=30, fill=(28, 30, 36))
    d.text((520, 140), "сообщения", font=font(F_SANS, 22), fill=(110, 115, 130))
    d.rounded_rectangle([515, 200, 893, 200 + 52 + 34 * len(body)], radius=22, fill=(52, 56, 66))
    d.text((535, 212), title, font=font(F_SANSB, 24), fill=header_c)
    for i, ln in enumerate(body):
        d.text((535, 248 + i * 34), ln, font=font(F_SANS, 26), fill=(225, 228, 235))
    d.ellipse([260, 600, 560, 900], fill=(40, 28, 22))
    return img


def d_secret(night=False):
    if not night:
        img = vgrad((128, 136, 140), (108, 114, 118))
    else:
        img = vgrad((30, 40, 62), (20, 26, 42))
    d = ImageDraw.Draw(img)
    k = 1 if not night else 0.4
    d.rectangle([0, 600, BW, BH], fill=mul((92, 82, 70), k))
    for y in range(0, 600, 32):
        d.line([0, y, BW, y], fill=mul((120, 128, 132), k), width=1)
    win_out = (210, 210, 200) if not night else (60, 80, 120)
    d.rectangle([1160, 150, 1360, 380], fill=win_out)
    d.rectangle([1148, 138, 1372, 392], outline=mul((90, 80, 70), k), width=12)
    d.rectangle([1140, 380, 1380, 398], fill=mul((110, 95, 80), k))
    for (sx, col) in ((1185, RED), (1285, BLUE)):
        cc = col if not night else mul(col, 0.55)
        d.rectangle([sx, 364, sx + 30, 380], fill=cc)
        d.rectangle([sx + 38, 364, sx + 68, 380], fill=cc)
    d.rectangle([620, 150, 720, 290], fill=mul((228, 224, 214), k))
    d.rectangle([620, 150, 720, 172], fill=mul((170, 50, 45), k))
    text_c(d, 670, 175, "17", font(F_BOLD, 52), mul((40, 40, 40), k))
    text_c(d, 670, 232, "июля", font(F_SERIF, 22), mul((60, 60, 60), k))
    text_c(d, 670, 258, "1996", font(F_SERIF, 20), mul((60, 60, 60), k))
    for bx in (170, 760):
        d.rectangle([bx, 440, bx + 380, 600], fill=mul((70, 58, 50), k))
        d.rectangle([bx + 6, 470, bx + 374, 590], fill=mul((186, 176, 156), k))
        d.rectangle([bx + 10, 450, bx + 110, 486], fill=mul((215, 210, 196), k))
        d.ellipse([bx + 40, 418, bx + 80, 458], fill=mul((150, 120, 110), k))
        d.polygon([(bx + 40, 455), (bx + 80, 455), (bx + 92, 505), (bx + 28, 505)], fill=mul((150, 100, 110), k))
        d.rectangle([bx - 8, 380, bx + 4, 620], fill=mul((60, 50, 44), k))
        d.rectangle([bx + 376, 420, bx + 388, 620], fill=mul((60, 50, 44), k))
    d.rectangle([600, 500, 720, 620], fill=mul((80, 62, 48), k))
    d.rectangle([620, 478, 700, 500], fill=mul((70, 100, 150), k))
    if not night:
        img = glow(img, lambda m: m.polygon([(1160, 150), (1360, 150), (1200, 790), (800, 790)], fill=255), (230, 225, 210), 0.12, 30)
        rng = np.random.default_rng(9)
        d = ImageDraw.Draw(img)
        for _ in range(140):
            x, y = rng.uniform(0, BW), rng.uniform(0, BH)
            d.ellipse([x, y, x + 2, y + 2], fill=(200, 200, 195))
    else:
        d = ImageDraw.Draw(img)
        d.rectangle([640, 450, 680, 500], fill=(70, 60, 40))
        d.ellipse([632, 410, 688, 460], fill=(240, 200, 120))
        img = glow(img, lambda m: m.ellipse([360, 160, 960, 760], fill=255), (255, 175, 90), 0.42, 70)
        d = ImageDraw.Draw(img)
        woman_sit(d, 640, 640, 330, (16, 14, 18), face=1, shin=0.0)
    return img


def d_notebook():
    img = vgrad((80, 62, 48), (60, 46, 34))
    d = ImageDraw.Draw(img)
    d.rectangle([330, 110, 1080, 700], fill=(72, 106, 150))
    d.rectangle([330, 110, 360, 700], fill=(55, 85, 120))
    d.rectangle([520, 250, 900, 400], fill=(230, 226, 212))
    f = font(F_SANSB, 96)
    rng = np.random.default_rng(2)
    x = 555
    for ch in "ЛИЗА":
        g = Image.new("L", (110, 130), 0)
        ImageDraw.Draw(g).text((8, 5), ch, font=f, fill=255)
        g = g.rotate(rng.uniform(-9, 9), expand=False)
        img.paste(Image.new("RGB", g.size, (60, 50, 140)), (x, 262), g)
        x += 82
    return img


def d_drawing():
    img = vgrad((80, 62, 48), (60, 46, 34))
    d = ImageDraw.Draw(img)
    d.rectangle([150, 80, 1260, 720], fill=(236, 232, 220))
    d.line([705, 80, 705, 720], fill=(200, 195, 185), width=4)
    for y in range(110, 720, 28):
        d.line([160, y, 1250, y], fill=(205, 215, 230), width=1)
    d.rectangle([220, 300, 420, 450], outline=(120, 80, 50), width=6)
    d.polygon([(200, 300), (320, 200), (440, 300)], outline=(150, 60, 50), width=6)
    d.ellipse([430, 470, 680, 560], outline=(60, 120, 200), width=8)
    gx = 870
    for k, sc in enumerate((RED, BLUE)):
        x = gx + k * 150
        d.ellipse([x - 28, 230, x + 28, 286], outline=(40, 40, 40), width=5)
        d.polygon([(x, 290), (x - 50, 440), (x + 50, 440)], outline=(40, 40, 40), width=5)
        d.line([x - 20, 440, x - 26, 520], fill=(40, 40, 40), width=5)
        d.line([x + 20, 440, x + 26, 520], fill=(40, 40, 40), width=5)
        d.rectangle([x - 44, 518, x - 10, 534], fill=sc)
        d.rectangle([x + 10, 518, x + 44, 534], fill=sc)
    d.line([gx + 30, 360, gx + 120, 360], fill=(40, 40, 40), width=5)
    d.text((780, 590), "Я и Аля.", font=font(F_HAND, 52), fill=(60, 50, 140))
    d.text((780, 645), "Мы всегда вместе.", font=font(F_HAND, 46), fill=(60, 50, 140))
    return img


def d_letter():
    img = vgrad((80, 62, 48), (60, 46, 34))
    d = ImageDraw.Draw(img)
    d.polygon([(360, 60), (1060, 80), (1040, 780), (340, 770)], fill=(232, 224, 200))
    f = font(F_HAND, 34)
    lines = ["Девочка моя.", "Дом тебя позвал —", "я знала, что позовёт.", "Прости меня.", "Вас было двое.", "Лиза и Алина."]
    for i, ln in enumerate(lines):
        d.text((420, 140 + i * 62), ln, font=f, fill=(55, 50, 100))
    return img


def sepia(img, warm=(1.0, 0.86, 0.66), fade=0.18):
    a = np.asarray(img, np.float32)
    lum = a @ np.array([0.3, 0.59, 0.11], np.float32)
    out = lum[..., None] * np.array(warm, np.float32)
    out = out * (1 - fade) + 255 * fade * np.array([1.0, 0.95, 0.85], np.float32)
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))


def d_pond():
    img = vgrad((200, 220, 235), (240, 235, 210))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 330, BW, BH], fill=(120, 150, 80))
    for x in (120, 330, 1250):
        apple_tree(d, x, 380, 0.9, fruit=None)
    d.ellipse([560, 420, 1500, 900], fill=(70, 120, 150))
    d.ellipse([620, 450, 1440, 860], fill=(90, 140, 170))
    d.polygon([(560, 600), (900, 560), (905, 590), (565, 640)], fill=(150, 115, 75))
    for x in range(600, 900, 60):
        d.rectangle([x, 590, x + 8, 680], fill=(110, 85, 55))
    return sepia(img)


JETTY_END = (885, 573)


def d_under():
    img = vgrad((40, 90, 95), (8, 22, 28))
    for k in range(5):
        x = 200 + k * 260
        img = glow(img, lambda m, x=x: m.polygon([(x, 0), (x + 90, 0), (x + 260, BH), (x + 80, BH)], fill=255), (150, 210, 200), 0.18, 25)
    d = ImageDraw.Draw(img)
    hx, hy = 700, 520
    d.polygon([(hx - 40, BH), (hx + 40, BH), (hx + 30, hy + 60), (hx - 30, hy + 60)], fill=(10, 30, 34))
    d.ellipse([hx - 45, hy - 10, hx + 45, hy + 90], fill=(10, 30, 34))
    for k, a in enumerate((-0.5, -0.22, 0.05, 0.3)):
        d.line([(hx + k * 22 - 33, hy + 20), (hx + k * 22 - 33 + 70 * math.sin(a), hy + 20 - 90 * math.cos(a))], fill=(10, 30, 34), width=16)
    d.line([(hx + 40, hy + 50), (hx + 95, hy + 10)], fill=(10, 30, 34), width=16)
    return img


def d_garden():
    img = vgrad((205, 222, 232), (238, 232, 205))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 470, BW, BH], fill=(110, 140, 72))
    for x in (160, 520, 900, 1260):
        apple_tree(d, x, 500, 1.0, fruit=None)
    return sepia(img)


def d_face():
    img = vgrad((120, 128, 132), (95, 100, 104))
    d = ImageDraw.Draw(img)
    d.rectangle([140, 80, 560, 700], fill=(60, 50, 44))
    d.rectangle([165, 105, 535, 675], fill=(150, 156, 160))
    d.rectangle([165, 560, 535, 675], fill=(120, 112, 100))
    d.ellipse([820, 150, 1150, 520], fill=(18, 18, 20))
    d.ellipse([740, 160, 900, 340], fill=(18, 18, 20))
    d.polygon([(860, 480), (1100, 480), (1300, 792), (700, 792)], fill=(18, 18, 20))
    d.polygon([(1140, 330), (1170, 360), (1150, 370)], fill=(18, 18, 20))
    return img


def d_porch():
    img = vgrad((52, 48, 92), (196, 118, 92))
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(11)
    for _ in range(60):
        x, y = rng.uniform(0, BW), rng.uniform(0, 260)
        s = rng.uniform(1, 2.6)
        d.ellipse([x, y, x + s, y + s], fill=(235, 230, 210))
    logs(d, (0, 280, BW, 560), (52, 38, 30), 24)
    d.rectangle([600, 300, 820, 470], fill=(255, 200, 120))
    d.rectangle([590, 290, 830, 480], outline=(30, 40, 70), width=12)
    d.rectangle([705, 300, 715, 470], fill=(30, 40, 70))
    for k in range(4):
        y = 560 + k * 58
        d.rectangle([0, y, BW, y + 58], fill=mul((70, 52, 40), 1 - k * 0.12))
        d.line([0, y, BW, y], fill=(40, 30, 24), width=3)
    img = glow(img, lambda m: m.polygon([(600, 470), (820, 470), (860, 792), (640, 792)], fill=255), (255, 190, 110), 0.35, 20)
    d = ImageDraw.Draw(img)
    woman_sit(d, 520, 618, 360, (18, 14, 20), face=1)
    man_sit(d, 900, 618, 380, (18, 14, 20), face=-1)
    dog(d, 1110, 676, 170, (20, 16, 22), face=-1, lying=True)
    return img


def d_kitchen():
    img = vgrad((214, 204, 184), (196, 186, 166))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 640, BW, BH], fill=(130, 100, 70))
    d.rectangle([90, 150, 640, 700], fill=(232, 228, 218))
    d.rectangle([90, 150, 640, 170], fill=(210, 206, 196))
    d.rounded_rectangle([250, 420, 470, 560], radius=60, fill=(25, 18, 14))
    d.ellipse([260, 110, 360, 160], fill=(40, 36, 34))
    d.rectangle([1040, 120, 1320, 380], fill=(250, 248, 230))
    d.rectangle([1028, 108, 1332, 392], outline=(110, 130, 150), width=12)
    img = glow(img, lambda m: m.polygon([(1040, 120), (1320, 120), (1100, 790), (700, 790)], fill=255), (255, 240, 190), 0.25, 25)
    d = ImageDraw.Draw(img)
    d.rectangle([760, 520, 1330, 545], fill=(110, 80, 55))
    d.rectangle([790, 545, 810, 700], fill=(90, 66, 46))
    d.rectangle([1280, 545, 1300, 700], fill=(90, 66, 46))
    d.rectangle([820, 420, 1040, 520], fill=(160, 120, 80))
    d.ellipse([850, 395, 890, 435], fill=(150, 120, 110))
    d.ellipse([910, 395, 950, 435], fill=(150, 120, 110))
    for sx, c in ((980, RED), (1000, BLUE)):
        d.rectangle([sx, 406 + (sx - 980), sx + 28, 420 + (sx - 980)], fill=c)
    d.rectangle([1080, 490, 1290, 520], fill=(190, 200, 205))
    woman(d, 700, 700, 420, (30, 26, 24), face=-1)
    return img


CONTRACT_NAME_Y = 430


def d_contract():
    img = vgrad((214, 204, 184), (180, 170, 150))
    d = ImageDraw.Draw(img)
    d.rectangle([200, 40, 1210, 790], fill=(240, 238, 230))
    text_c(d, 705, 90, "ДОГОВОР КУПЛИ-ПРОДАЖИ", font(F_BOLD, 40), (30, 30, 35))
    text_c(d, 705, 140, "жилого дома и земельного участка", font(F_SERIF, 26), (60, 60, 65))
    f = font(F_MONO, 22)
    for i in range(6):
        d.line([260, 220 + i * 30, 1150 - (i % 3) * 120, 220 + i * 30], fill=(160, 160, 165), width=3)
    d.text((260, CONTRACT_NAME_Y), "Продавец: Воронцова Алина Сергеевна", font=font(F_SERIF, 38), fill=(20, 20, 25))
    for i in range(7):
        d.line([260, 520 + i * 30, 1150 - (i % 4) * 90, 520 + i * 30], fill=(160, 160, 165), width=3)
    return img


def d_kitchen_ext():
    img = Image.new("RGB", (BW, BH))
    d = ImageDraw.Draw(img)
    logs(d, (0, 0, BW, BH), (96, 68, 44), 30)
    inner = vgrad((60, 40, 30), (30, 20, 16), 520, 420)
    di = ImageDraw.Draw(inner)
    woman(di, 300, 560, 460, (14, 10, 8), face=-1)
    img.paste(inner, (444, 190))
    img = glow(img, lambda m: m.ellipse([380, 220, 760, 640], fill=255), (255, 140, 60), 0.5, 60)
    d = ImageDraw.Draw(img)
    d.rectangle([424, 170, 984, 190], fill=(110, 130, 150))
    d.rectangle([424, 610, 984, 640], fill=(110, 130, 150))
    d.rectangle([424, 170, 444, 640], fill=(110, 130, 150))
    d.rectangle([964, 170, 984, 640], fill=(110, 130, 150))
    d.rectangle([696, 190, 712, 610], fill=(110, 130, 150))
    d.polygon([(404, 170), (704, 90), (1004, 170)], fill=(110, 130, 150))
    return img


def d_refl():
    img = vgrad((14, 20, 34), (8, 12, 22))
    refl = vgrad((120, 80, 40), (70, 45, 22), BW, BH)
    dr = ImageDraw.Draw(refl)
    dr.rectangle([780, 470, 1240, 610], fill=(150, 110, 70))
    dr.rectangle([790, 440, 900, 480], fill=(170, 130, 90))
    woman_sit(dr, 420, 640, 360, (40, 26, 16), face=1, shin=0.0)
    refl = glow(refl, lambda m: m.ellipse([450, 250, 850, 650], fill=255), (255, 190, 100), 0.5, 60)
    arr = np.asarray(img, np.float32) * 0.45 + np.asarray(refl, np.float32) * 0.55
    img = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, BW, 40], fill=(20, 18, 26))
    d.rectangle([0, BH - 40, BW, BH], fill=(20, 18, 26))
    d.rectangle([0, 0, 40, BH], fill=(20, 18, 26))
    d.rectangle([BW - 40, 0, BW, BH], fill=(20, 18, 26))
    d.rectangle([BW // 2 - 14, 0, BW // 2 + 14, BH], fill=(20, 18, 26))
    d.rectangle([0, 300, BW, 324], fill=(20, 18, 26))
    return img


def d_dawn_window():
    img = vgrad((230, 196, 190), (200, 196, 190))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 470, BW, BH], fill=(150, 150, 130))
    apple_tree(d, 300, 520, 1.0, leaves=(140, 150, 120), fruit=(190, 120, 110))
    d.ellipse([900, 600, 1360, 720], fill=(170, 185, 195))
    mist = Image.new("L", (BW, BH), 0)
    ImageDraw.Draw(mist).rectangle([0, 420, BW, BH], fill=150)
    mist = mist.filter(ImageFilter.GaussianBlur(60))
    a = np.asarray(mist, np.float32)[..., None] / 255
    arr = np.asarray(img, np.float32) * (1 - a * 0.6) + np.array([235, 220, 215], np.float32) * a * 0.6
    img = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
    lay = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    woman(ImageDraw.Draw(lay), 620, 900, 760, (60, 50, 50, 110), face=1)
    img = blend_layer(img, lay)
    d = ImageDraw.Draw(img)
    fr = (70, 52, 46)
    d.rectangle([0, 0, BW, 46], fill=fr)
    d.rectangle([0, BH - 46, BW, BH], fill=fr)
    d.rectangle([0, 0, 46, BH], fill=fr)
    d.rectangle([BW - 46, 0, BW, BH], fill=fr)
    d.rectangle([BW // 2 - 14, 0, BW // 2 + 14, BH], fill=fr)
    d.rectangle([0, 330, BW, 352], fill=fr)
    return img


def d_epilogue():
    img = vgrad((150, 182, 215), (228, 222, 200))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 640, BW, BH], fill=(130, 125, 70))
    d.ellipse([1080, 640, 1500, 760], fill=(110, 160, 205))
    apple_tree(d, 150, 700, 1.15, leaves=(210, 170, 50), fruit=(200, 60, 40))
    px0, px1, y0, y1 = house(img, 840, 650, 1.35, frame=(40, 95, 180), porch_ok=True, plaque=True)
    d = ImageDraw.Draw(img)
    lx = px0 + 40
    d.line([(lx - 60, 760), (lx + 20, 300)], fill=(150, 120, 80), width=10)
    d.line([(lx + 20, 760), (lx + 100, 300)], fill=(150, 120, 80), width=10)
    for k in range(8):
        yy = 740 - k * 56
        u = (760 - yy) / 460
        d.line([(lx - 60 + 80 * u, yy), (lx + 20 + 80 * u, yy)], fill=(150, 120, 80), width=7)
    woman(d, lx + 60, 520, 300, (25, 24, 22), face=1)
    man(d, lx - 110, 780, 300, (25, 24, 22), face=1)
    dog(d, 1100, 780, 130, (30, 29, 27), face=1)
    return img


def d_plaque():
    img = Image.new("RGB", (BW, BH))
    d = ImageDraw.Draw(img)
    logs(d, (0, 0, BW, BH), (90, 64, 42), 46)
    d.rounded_rectangle([210, 230, 1200, 560], radius=20, fill=(196, 156, 100), outline=(120, 90, 55), width=10)
    swallow(d, 560, 510, 26, (95, 65, 40), 1)
    swallow(d, 850, 510, 26, (95, 65, 40), -1)
    text_c(d, 705, 270, "ДОМ СЕСТЁР ВОРОНЦОВЫХ", font(F_BOLD, 58), (90, 60, 36))
    text_c(d, 705, 370, "АЛИНЫ И ЛИЗЫ", font(F_BOLD, 64), (90, 60, 36))
    return img


def d_black():
    return Image.new("RGB", (BW, BH), (0, 0, 0))


# =====================================================================
#  OVERLAYS  (img, t_shot, dur, shot) -> img
# =====================================================================
def smooth(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def lab(sh, name, default=0.0):
    return sh["labels"].get(name, default)


def ov_car(img, t, dur, sh):
    d = ImageDraw.Draw(img)
    u = 0.12 + 0.5 * smooth(t / dur)
    i = min(len(ROAD) - 2, int(u * (len(ROAD) - 1)))
    x, y = ROAD[i]
    s = 16 * (1 - u * 0.6)
    for k in range(1, 6):
        px, py = ROAD[max(0, i - k * 2)]
        rr = s * (0.6 + k * 0.25)
        d.ellipse([px - rr, py - rr * 0.5, px + rr, py + rr * 0.5], fill=(225, 212, 180))
    car(d, x, y, s)
    return img


def ov_notif(img, t, dur, sh):
    t0 = lab(sh, "notif")
    lt = t - t0
    if lt < 0:
        return img
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([690, 352, 830, 385], radius=8, fill=(90, 110, 150))
    slide = 0 if lt < 3.0 else (lt - 3.0) * 900
    if slide > 700:
        return img
    x0 = 520 + slide
    d.rounded_rectangle([x0, 250, x0 + 520, 330], radius=16, fill=(236, 238, 242))
    d.text((x0 + 20, 260), "Нотариус Гусева", font=font(F_SANSB, 22), fill=(30, 30, 40))
    d.text((x0 + 20, 292), "Напоминаю о сделке в четверг", font=font(F_SANS, 22), fill=(60, 60, 70))
    return img


def ov_redflash(img, t, dur, sh):
    t0 = lab(sh, "flash", dur * 0.6)
    if t0 <= t < t0 + 0.22:
        d = ImageDraw.Draw(img)
        d.ellipse([930, 400, 990, 470], fill=(190, 30, 30))
        d.rectangle([945, 460, 980, 500], fill=(170, 25, 25))
    return img


def ov_tulle(img, t, dur, sh):
    lay = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    pts = [(494, 196)]
    for k in range(0, 41):
        y = 196 + k * 10.1
        x = 640 + 30 * math.sin(t * 0.9 + k * 0.25) * (k / 40) + 20 * math.sin(t * 0.5)
        pts.append((x, y))
    pts.append((494, 600))
    d.polygon(pts, fill=(220, 225, 230, 110))
    return blend_layer(img, lay)


def ov_dining_clock(img, t, dur, sh):
    hh, mm, mode = sh["clock"]
    pal = sh.get("pal", "day")
    p = PAL[pal]
    ang = 0.0
    if mode == "swing":
        ang = 0.22 * math.sin(2 * math.pi * t / 1.2)
    elif mode == "one":
        t0 = lab(sh, "swing", 1e9)
        if t >= t0:
            ang = 0.25 * math.sin(2 * math.pi * (t - t0) / 1.4) * math.exp(-(t - t0) * 1.6)
    elif mode == "stop_at":
        t0 = lab(sh, "stop", 1e9)
        if t < t0:
            ang = 0.22 * math.sin(2 * math.pi * t / 1.2)
        else:
            mm = mm + 1
    d = ImageDraw.Draw(img)
    clock(d, 850, 110, 50, hh, mm, ang, case=mul(p["wood"], 1.1), face_c=p["face"])
    return img


def ov_dust(img, t, dur, sh):
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(1)
    for k in range(70):
        bx, by = rng.uniform(150, 700), rng.uniform(150, 700)
        x = bx + 25 * math.sin(t * 0.3 + k)
        y = by - (t * 8 + k * 13) % 120
        d.ellipse([x, y, x + 3, y + 3], fill=(250, 235, 200))
    return img


def ov_clock_close(img, t, dur, sh):
    hh, mm, mode = sh["clock"]
    pal = sh.get("pal", "day")
    p = PAL[pal]
    d = ImageDraw.Draw(img)
    ang, ss = 0.0, None
    if mode == "one":
        t0 = lab(sh, "swing", 1.0)
        if t >= t0:
            ang = 0.3 * math.sin(2 * math.pi * (t - t0) / 1.5) * math.exp(-(t - t0) * 1.4)
    elif mode == "seconds":
        t0 = lab(sh, "jump", 1e9)
        ss = (48 + t * 1.0) % 60 if t < t0 else 0
        if t >= t0:
            mm += 1
    elif mode == "swing":
        ang = 0.22 * math.sin(2 * math.pi * t / 1.2)
    elif mode == "stop_close":
        t0 = lab(sh, "stop", 1e9)
        if t < t0:
            ang = 0.22 * math.sin(2 * math.pi * t / 1.2)
        else:
            ang = 0.22 * math.sin(2 * math.pi * t0 / 1.2) * math.exp(-(t - t0) * 3)
            mm += 1
    clock(d, 704, 300, 200, hh, mm, ang, ss=ss, case=mul(p["wood"], 1.1), face_c=p["face"], plen=1.3)
    return img


def ov_girl_mirror(img, t, dur, sh):
    t0, t1 = lab(sh, "girl", 1e9), lab(sh, "turn", 1e9)
    if t0 <= t < t1:
        d = ImageDraw.Draw(img)
        girl_sit(d, 1000, 395, 200, (30, 18, 14), RED, swing=t * 4)
    return img


def ov_flashlight(img, t, dur, sh):
    t0 = lab(sh, "enter", 0)
    x = 1300 - 520 * smooth((t - 0.0) / max(0.1, t0 + 2.0))
    d = ImageDraw.Draw(img)
    woman(d, x, 740, 360, (12, 14, 22), face=-1)
    return glow(img, lambda m: m.polygon([(x - 50, 520), (x - 600, 300), (x - 600, 760)], fill=255), (230, 230, 200), 0.22, 20)


def ov_ghosts_window(img, t, dur, sh):
    t0 = lab(sh, "ghosts", 1e9)
    a = smooth((t - t0) / 0.8) * (1 - smooth((t - t0 - 5.0) / 0.8))
    if a <= 0:
        return img
    lay = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rectangle([110, 150, 380, 470], fill=(150, 105, 60, 210))
    d.ellipse([170, 380, 330, 420], fill=(200, 170, 120, 230))
    grandma_sit(d, 175, 440, 210, (60, 36, 20, 255), face=1)
    girl_sit(d, 300, 430, 120, (60, 36, 20, 255), RED)
    return blend_layer(img, lay, a)


def ov_hand(img, t, dur, sh):
    t0, t1 = lab(sh, "hand", 0), lab(sh, "pull", 1e9)
    if t0 <= t < t1:
        d = ImageDraw.Draw(img)
        d.ellipse([600, 330, 800, 560], fill=(14, 16, 24))
        for k in range(4):
            x = 610 + k * 50
            d.rounded_rectangle([x, 180 + abs(k - 1.5) * 25, x + 40, 400], radius=20, fill=(14, 16, 24))
        d.rounded_rectangle([780, 380, 900, 430], radius=20, fill=(14, 16, 24))
        d.rectangle([640, 540, 780, BH], fill=(14, 16, 24))
    return img


def ov_stepan(img, t, dur, sh):
    d = ImageDraw.Draw(img)
    t_up, t_down = lab(sh, "axe_up", 1e9), lab(sh, "axe_down", 1e9)
    t_up2 = lab(sh, "axe_up2", 1e9)
    pose = "down"
    if t_up <= t < t_down or t >= t_up2:
        pose = "up"
    man(d, 520, 700, 400, (28, 26, 24), face=1, axe=pose)
    t_dog = lab(sh, "dog", 1e9)
    dx = 300 + 520 * smooth((t - t_dog) / 2.0)
    dog(d, dx, 735, 140, (34, 32, 30), face=1)
    wx = 1010 if t < lab(sh, "leave", 1e9) else 1010 + 300 * smooth((t - lab(sh, "leave")) / 2.0)
    woman(d, wx, 720, 380, (22, 21, 20), face=-1)
    return img


def ov_peel(img, t, dur, sh):
    u = smooth(t / dur)
    w = 1300 * u
    if w <= 1:
        return img
    patch = Image.new("RGB", (BW, BH))
    wallpaper(patch, (0, 0, BW, BH), (215, 205, 175), (110, 140, 200), 40, False, 4)
    d = ImageDraw.Draw(patch)
    if u > 0.45:
        pw = (u - 0.45) / 0.55 * 900
        d.rectangle([700 - pw / 2, 120, 700 + pw / 2, BH], fill=(150, 120, 80))
        for k in range(int(pw / 60)):
            x = 700 - pw / 2 + 30 + k * 60
            d.line([x, 120, x, BH], fill=(130, 100, 65), width=2)
            d.ellipse([x - 5, 150, x + 5, 160], fill=(60, 60, 60))
    m = Image.new("L", (BW, BH), 0)
    dm = ImageDraw.Draw(m)
    pts = [(54, 0)] + [(54 + w + 25 * math.sin(y * 0.03), y) for y in range(0, BH + 20, 20)] + [(54, BH)]
    dm.polygon(pts, fill=255)
    img.paste(patch, (0, 0), m)
    d = ImageDraw.Draw(img)
    ex = 54 + w
    d.polygon([(ex, 350), (ex + 160, 330), (ex + 160, 350), (ex, 370)], fill=(170, 170, 175))
    d.rectangle([ex + 150, 325, ex + 300, 355], fill=(60, 40, 30))
    return img


def ov_plank(img, t, dur, sh):
    if t > 1.2:
        return img
    d = ImageDraw.Draw(img)
    u = smooth(t / 1.2)
    dy = u * 900
    d.rectangle([470, 200 + dy, 940, BH + 60 + dy], fill=(150, 120, 80))
    return img


def ov_typed(img, t, dur, sh):
    t0 = lab(sh, "type", 1e9)
    if t < t0:
        return img
    msg = "Сделки не будет"
    n = min(len(msg), int((t - t0) * 9))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([600, 560, 893, 620], radius=22, fill=(60, 110, 200))
    d.text((620, 572), msg[:n], font=font(F_SANS, 28), fill=(240, 244, 250))
    return img


def ov_finger(img, t, dur, sh):
    d = ImageDraw.Draw(img)
    u = smooth((t - 1.0) / max(1.0, dur - 2.0))
    x = 560 + 90 * u
    d.rounded_rectangle([x - 22, CONTRACT_NAME_Y + 40, x + 22, CONTRACT_NAME_Y + 300], radius=22, fill=(60, 42, 34))
    d.ellipse([x - 18, CONTRACT_NAME_Y + 38, x + 18, CONTRACT_NAME_Y + 64], fill=(190, 150, 140))
    return img


_BURN = {}


def ov_burn(img, t, dur, sh):
    u = smooth((t - 0.5) / (dur - 1.5))
    if "d" not in _BURN:
        yy, xx = np.mgrid[0:BH, 0:BW].astype(np.float32)
        dist = np.abs(yy - (CONTRACT_NAME_Y + 22)) * 1.0 + np.abs(xx - 705) * 0.35
        rng = np.random.default_rng(3)
        noise = np.asarray(Image.fromarray(rng.uniform(0, 255, (BH // 16, BW // 16)).astype(np.uint8)).resize((BW, BH), Image.BICUBIC), np.float32)
        _BURN["d"] = dist + noise * 0.25
    dist = _BURN["d"]
    thr = (1 - u) * (dist.max() + 20) - 10
    arr = np.asarray(img, np.float32).copy()
    burned = dist > thr
    edge = (dist > thr - 18) & ~burned
    arr[burned] = arr[burned] * 0.0 + np.array([22, 16, 12], np.float32)
    arr[edge] = np.array([255, 140, 40], np.float32) * (0.8 + 0.2 * math.sin(t * 20))
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))


def ov_fire(img, t, dur, sh):
    fl = 0.75 + 0.25 * math.sin(t * 13) * math.sin(t * 5.3)
    d = ImageDraw.Draw(img)
    for k in range(5):
        x = 290 + k * 34
        hgt = 60 + 30 * math.sin(t * 9 + k * 1.7)
        d.polygon([(x - 18, 555), (x + 18, 555), (x + 3 * math.sin(t * 7 + k), 555 - hgt)], fill=(255, 150 + k * 15, 50))
    return glow(img, lambda m: m.ellipse([150, 330, 580, 700], fill=255), (255, 130, 50), 0.35 * fl, 50)


def ov_bubbles(img, t, dur, sh):
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(4)
    for k in range(40):
        x0 = rng.uniform(560, 860)
        sp = rng.uniform(40, 120)
        y = BH - ((t * sp + k * 37) % (BH + 50))
        r = rng.uniform(3, 10)
        x = x0 + 8 * math.sin(t * 2 + k)
        d.ellipse([x - r, y - r, x + r, y + r], outline=(180, 230, 230), width=2)
    return img


def ov_pond_story(img, t, dur, sh):
    d = ImageDraw.Draw(img)
    c = (70, 55, 40)
    tj = lab(sh, "jump", dur * 0.5)
    ex, ey = JETTY_END
    run_end = max(1.0, tj - 1.2)
    u = smooth(t / run_end)
    xb = 120 + (ex - 40 - 120) * u
    xr = 60 + (ex - 110 - 60) * u
    yb = 640 + (ey - 640) * u
    yr = 660 + (ey + 15 - 660) * u
    legs = t * 12 if u < 1 else 0
    if u >= 1:
        for sx, col in ((640, BLUE), (700, RED)):
            d.rectangle([sx, 585, sx + 18, 595], fill=col)
            d.rectangle([sx + 22, 585, sx + 40, 595], fill=col)
    if t < tj:
        girl(d, xb, yb, 150, c, BLUE, legs=legs)
    elif t < tj + 0.7:
        v = (t - tj) / 0.7
        girl(d, ex - 40 + 140 * v, ey - 140 * math.sin(v * math.pi) + 60 * v, 150, c, BLUE)
    else:
        for k in range(3):
            rr = 20 + ((t - tj - 0.7) * 60 + k * 30) % 120
            d.ellipse([ex + 100 - rr, ey + 70 - rr * 0.3, ex + 100 + rr, ey + 70 + rr * 0.3], outline=(220, 210, 190), width=3)
    girl(d, xr, yr, 150, c, RED, legs=legs)
    return img


def ov_run(img, t, dur, sh):
    d = ImageDraw.Draw(img)
    x = BW + 100 - (BW + 250) * (t / dur)
    girl(d, x, 680, 200, (70, 55, 40), RED, face=-1, legs=t * 14)
    return img


def ov_wardrobe(img, t, dur, sh):
    t0 = lab(sh, "girl", 1e9)
    a = smooth((t - t0) / 1.5)
    if a <= 0:
        return img
    lay = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    girl(ImageDraw.Draw(lay), 350, 640, 300, (40, 44, 50, 255), BLUE)
    img = blend_layer(img, lay, a)
    tt = lab(sh, "tear", 1e9)
    if t >= tt:
        d = ImageDraw.Draw(img)
        y = 400 + min(120, (t - tt) * 30)
        d.ellipse([1128, y, 1136, y + 12], fill=(210, 220, 235))
    return img


def ov_refl(img, t, dur, sh):
    ta, tb = lab(sh, "girl", 1e9), lab(sh, "name", 1e9)
    a = smooth((t - ta) / 1.2)
    if a <= 0:
        return img
    lay = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    u = smooth((t - tb - 1.5) / 3.0)
    x = 1000 + (560 - 1000) * u
    if u <= 0:
        girl_sit(d, x, 480, 170, (50, 30, 18, 255), BLUE, swing=0)
    elif u < 1:
        girl(d, x, 640, 200, (50, 30, 18, 255), BLUE, legs=t * 6)
    else:
        girl_sit(d, 560, 640, 220, (50, 30, 18, 255), BLUE)
    return blend_layer(img, lay, a * 0.9)


def ov_wave(img, t, dur, sh):
    t0 = lab(sh, "wave", 1e9)
    a = smooth((t - t0) / 1.0) * (1 - smooth((t - t0 - 4.0) / 1.5))
    if a > 0:
        lay = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
        girl(ImageDraw.Draw(lay), 1180, 640, 90, (90, 80, 85, 255), BLUE, wave=t * 6)
        img = blend_layer(img, lay, a * 0.8)
    tp = lab(sh, "palm", 1e9)
    if t >= tp:
        lay = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.ellipse([560, 420, 700, 560], fill=(240, 235, 235, 70))
        for k in range(4):
            d.rounded_rectangle([565 + k * 34, 300 + abs(k - 1.5) * 18, 595 + k * 34, 440], radius=15, fill=(240, 235, 235, 70))
        img = blend_layer(img, lay, smooth((t - tp) / 1.0))
    return img


OVL = {k[3:]: v for k, v in globals().items() if k.startswith("ov_")}


# =====================================================================
#  SCRIPT  (shots + cues)
# =====================================================================
def A(text, **kw):
    return dict(kind="act", text=text, **kw)


def D(who, text, **kw):
    return dict(kind="dlg", who=who, text=text, **kw)


def P(sec, **kw):
    return dict(kind="pause", sec=sec, **kw)


def CARD(lines, sub=None, dur=3.4, aud=None, big=False):
    return dict(card=True, lines=lines, sub=sub, dur=dur, aud=aud or [], big=big, cues=[], amb=[])


def S(draw, cues, cam=None, ov=(), amb=(), aud=(), **kw):
    sh = dict(draw=draw, cues=cues, cam=cam or (1.0, 1.06, None, None), ov=list(ov), amb=list(amb), aud=list(aud))
    sh.update(kw)
    return sh


V = "ВАРВАРА (голос)"
AL, ST = "АЛИНА", "СТЕПАН ИЛЬИЧ"

SHOTS = [
    CARD(["ТАЙНА СТАРОГО ДОМА"], "аниматик по сценарию короткометражного фильма", 7.0, [("lullaby", 0.8, dict(inst="box", beat=0.62, n=4, amp=0.2))], big=True),
    # ---------------- 1
    CARD(["СЦЕНА 1"], "НАТ. ПРОСЁЛОЧНАЯ ДОРОГА — ДЕНЬ"),
    S(lambda: d_field(), [A("Конец августа. Поле выгоревшей травы, вдали — ельник и несколько крыш."), P(1.0, label="hum"),
                          A("По бесконечной пыльной дороге ползёт одинокая белая машина.")],
      cam=(1.0, 1.25, (704, 396), (900, 330)), ov=["car"], amb=["wind", "grass"], aud=[("hum", 3.5, dict(n=4))]),
    S(d_car_int, [A("За рулём — АЛИНА, в солнцезащитных очках. На сиденье — договор купли-продажи и стикер её почерком."),
                  A("Телефон вспыхивает уведомлением.", label="notif"),
                  A("Алина, не глядя, смахивает его.")],
      cam=(1.05, 1.12, (760, 450), (800, 420)), ov=["notif"], amb=["car"]),
    S(d_mirror, [A("Её отражение в зеркале заднего вида. Глаза за очками не видны."), P(0.6, label="flash"),
                 A("На долю секунды на заднем сиденье мелькает что-то красное. Алина не замечает.")],
      cam=(1.1, 1.3, (704, 360), (760, 380)), ov=["redflash"], amb=["car"]),
    # ---------------- 2
    CARD(["СЦЕНА 2"], "НАТ. ДОМ ВОРОНЦОВЫХ — ДВОР — ДЕНЬ"),
    S(d_house_day, [A("Бревенчатый дом начала века. Наличники когда-то были синими. Окна второго этажа похожи на глаза."),
                    D(AL, "Ну здравствуй.", note="тихо, себе"),
                    A("Скрип калитки. Через забор смотрит СТЕПАН ИЛЬИЧ. Рядом лайка Буран рычит — на дом, не на Алину."),
                    D(ST, "Алька? Ты, что ли?"),
                    D(AL, "Здравствуйте. Простите, я…"),
                    D(ST, "Не помнишь. Ну да. Ты маленькая была. Степан Ильич я. Варвара твоя у меня молоко брала сорок лет."),
                    D(AL, "Спасибо, что похоронили её. Я не успела."),
                    D(ST, "Продавать приехала?", note="после паузы"),
                    D(AL, "Да."),
                    D(ST, "Ты вот что. Ночью в столовую не ходи. После трёх."),
                    D(AL, "Домовой?", note="с усмешкой"),
                    D(ST, "Не знаю я, кто. Варвара тридцать лет ночами там сидела. Не ходи, и всё.")],
      cam=(1.0, 1.12, (704, 396), (760, 360)), amb=["wind", "birds"], aud=[("dog_growl", 9.0, {})]),
    S(d_window_up, [A("Он уходит, прихрамывая. Буран смотрит на окно второго этажа."), A("Тюль качается, хотя ветра нет.")],
      cam=(1.0, 1.25, (704, 520), (704, 396)), ov=["tulle"], amb=["wind"], aud=[("cello", 1.0, dict(note="A2", dur=8.0, amp=0.16))]),
    # ---------------- 3
    CARD(["СЦЕНА 3"], "ИНТ. ДОМ — ПРИХОЖАЯ И СТОЛОВАЯ — ДЕНЬ"),
    S(lambda: d_dining("day"), [A("Пыльный полумрак. В солнечных лучах плавают пылинки. Над буфетом — часы. Стрелки стоят на 3:17."),
                                A("Алина проводит пальцем по буфету. Открывает ящик: старые фотографии.")],
      cam=(1.0, 1.15, (600, 396), (800, 330)), ov=["dining_clock", "dust"], clock=(3, 17, "stop"), pal="day", amb=["room"]),
    S(d_photo, [A("Бабушка Варвара в молодости, рядом — девочка лет семи. Лицо девочки аккуратно вырезано ножницами."),
                D(AL, "Это я?", note="хмурится")],
      cam=(1.0, 1.2, (704, 396), (760, 360)), amb=["room"]),
    S(d_photo_back, [A("На обороте почерком бабушки: «Лето 1996»."), P(1.0)], cam=(1.0, 1.08, None, None), amb=["room"]),
    S(lambda: d_clock_wall("day"), [A("Она пробует качнуть маятник.", label="swing"), A("Маятник делает один ход и замирает. 3:17.")],
      cam=(1.0, 1.1, (704, 380), (704, 330)), ov=["clock_close"], clock=(3, 17, "one"), pal="day", amb=["room"], aud=[("tick1", 0, {})]),
    # ---------------- 4
    CARD(["СЦЕНА 4"], "ИНТ. ДОМ — СПАЛЬНЯ НА ВТОРОМ ЭТАЖЕ — ВЕЧЕР"),
    S(d_bedroom, [A("Закат окрашивает всё в медь. Алина складывает вещи в коробки и останавливается у окна."),
                  A("Внизу — стена дома с тремя окнами первого этажа. Она считает на пальцах."),
                  D(AL, "Прихожая, столовая, кухня… Три окна. А комнат внутри — две.", note="себе, профессионально")],
      cam=(1.0, 1.12, (704, 396), (900, 380)), amb=["room"]),
    S(d_trellis, [A("Она садится к трюмо. Три створки зеркала — три отражения."), P(0.5, label="girl"),
                  A("В правой створке, за её плечом, на кровати сидит ДЕВОЧКА в красных сандалиях и болтает ногами."),
                  P(0.8, label="turn"),
                  A("Алина резко оборачивается. Кровать пуста. В зеркале — никого."),
                  D(AL, "Отлично. Тридцать четыре года — и вот.", note="нервно смеётся")],
      cam=(1.0, 1.0, (704, 360), (704, 360)), cam_keys=[(0, 1.0, (704, 380)), ("girl", 1.0, (704, 380)), ("turn", 1.6, (1060, 340)), ("end", 1.0, (704, 380))],
      ov=["girl_mirror"], amb=["room"], aud=[("cluster", "girl", dict(until="turn"))]),
    # ---------------- 5
    CARD(["СЦЕНА 5"], "ИНТ. ДОМ — СТОЛОВАЯ — НОЧЬ (3:17)"),
    S(lambda: d_dining("night"), [A("Лунный свет сквозь кружевные занавески. Часы, которые стояли, идут."),
                                  A("Из столовой доносится детский голос: кто-то напевает колыбельную."),
                                  A("АЛИНА спускается с телефоном-фонариком. Босая.", label="enter"),
                                  D(AL, "Эй? Кто здесь?", note="шёпотом", label="hush"),
                                  A("Пение прекращается. Часы показывают 3:17, маятник качается."),
                                  A("В тёмном стекле окна: за столом сидят двое — бабушка Варвара и ДЕВОЧКА.", label="ghosts"),
                                  A("Бабушка гладит девочку по голове и плачет."),
                                  A("Алина оборачивается к столу. Там пусто.")],
      cam=(1.0, 1.05, (704, 396), (600, 400)), ov=["dining_clock", "flashlight", "ghosts_window"], clock=(3, 17, "swing"), pal="night",
      amb=["night", "tick"], aud=[("hum", 2.0, dict(n=15, until="hush"))]),
    S(lambda: d_wall_roses("night"), [A("Она подходит к стене между столовой и кухней. Прикладывает ладонь к обоям.", label="hand"),
                                      A("С той стороны — тихий детский стук. Три удара. Пауза. Ещё три.", label="knock"),
                                      P(3.6),
                                      A("Алина отдёргивает руку.", label="pull"),
                                      D(AL, "Что тебе нужно?", note="дрожащим голосом")],
      cam=(1.0, 1.1, (704, 396), (704, 396)), ov=["hand"], amb=["night", "tick"], aud=[("knocks6", "knock", {})], flash=[("knock", [1.0, 1.45, 1.9, 3.1, 3.55, 4.0])]),
    S(lambda: d_clock_wall("night"), [A("Часы бьют один раз.", label="stop"), A("Маятник замирает. 3:18. Тишина.")],
      cam=(1.0, 1.15, (704, 330), (704, 300)), ov=["clock_close"], clock=(3, 17, "stop_close"), pal="night",
      aud=[("bong", "stop", {}), ("piano_note", 5.0, {})], amb=["night"]),
    # ---------------- 6
    CARD(["СЦЕНА 6"], "НАТ. ДВОР СТЕПАНА ИЛЬИЧА — УТРО"),
    S(d_yard, [A("Поленница, бочка с дождевой водой, куры. Степан Ильич колет дрова.", label="axe_up"),
               P(0.6, label="axe_down"),
               D(AL, "Что было в той комнате? Рядом со столовой."),
               D(ST, "Иди домой, Алька."),
               D(AL, "Вы сказали не ходить ночью в столовую. Я пошла. Там поют. Там стучат из стены."),
               D(AL, "Я видела в зеркале девочку. Либо я схожу с ума, либо вы мне сейчас всё расскажете."),
               A("Долгая пауза. Буран подходит и тычется носом Алине в ладонь.", label="dog"),
               D(ST, "Варвара велела не рассказывать. Взяла с меня слово. На иконе."),
               D(AL, "Варвара умерла."),
               D(ST, "Вот потому и держу.", note="глухо", label="axe_up2"),
               A("Алина уходит. Он опускает топор и, не оборачиваясь, говорит ей в спину:", label="leave"),
               D(ST, "Не ты её боишься. Она тебя ждёт.")],
      cam=(1.05, 1.12, (704, 420), (760, 420)), ov=["stepan"], amb=["birds", "hens"], aud=[("chop", 0.4, {}), ("chop", 2.0, {})], shake=2.0),
    # ---------------- 7
    CARD(["СЦЕНА 7"], "ИНТ. ДОМ — СТОЛОВАЯ — ДЕНЬ"),
    S(d_wall_peel, [A("Дневной свет теперь кажется холодным. Алина срезает обои со стены."),
                    A("Под розами — ещё один слой, с голубыми васильками."),
                    A("Под васильками — фанера, прибитая поверх дверного проёма.")],
      cam=(1.05, 1.2, (704, 396), (800, 396)), ov=["peel"], amb=["room"], aud=[("heartbeat", 0.0, dict(until="end"))]),
    S(d_blue_door, [P(1.4, label="crack"), A("Фанера падает. За ней — низкая голубая дверь. На уровне детских глаз нарисованы две ласточки."),
                    A("На ручке — бантик из выцветшей красной ленты.")],
      cam=(1.0, 1.15, (704, 450), (704, 470)), ov=["plank"], amb=["room"], aud=[("crack", 0.1, {})]),
    S(lambda: d_phone("Нотариус Гусева", ["Покупатель просит перенести", "сделку на среду. Техника", "для сноса заказана на субботу."]),
      [P(0.3, label="buzz"), A("Телефон вибрирует. Алина вздрагивает всем телом."), A("Она убирает телефон, не ответив. Смотрит на голубую дверь.")],
      cam=(1.0, 1.1, (704, 380), (704, 360)), amb=["room"], aud=[("buzz", 0.2, {})], shake_at=[(0.2, 0.6, 6)]),
    # ---------------- 8
    CARD(["СЦЕНА 8"], "ИНТ. ПОТАЙНАЯ КОМНАТА — ДЕНЬ"),
    S(lambda: d_secret(False), [A("Детская, законсервированная, как капсула времени. Всё покрыто пылью, но ничего не тронуто."),
                                A("Две одинаковые кроватки. Две одинаковые куклы. Календарь остановился на 17 июля 1996."),
                                A("На подоконнике — две пары детских сандалий: голубые и красные."),
                                A("Алина садится на край кровати. На тумбочке — школьная тетрадь.")],
      cam=(1.0, 1.25, (704, 420), (690, 420)), amb=["room"], aud=[("lullaby", 1.0, dict(inst="piano", beat=1.05, n=15, amp=0.2))]),
    S(d_notebook, [D(AL, "Лиза?.. Кто ты такая?", note="почти беззвучно"), P(1.0)], cam=(1.0, 1.1, None, None), amb=["room"]),
    S(d_drawing, [A("Детские рисунки: дом, пруд, две девочки держатся за руки."),
                  A("Подпись: «Я и Аля. Мы всегда вместе»."),
                  A("Из тетради выпадает конверт: «Моей девочке. Когда вернётся»."),
                  A("Дрожащие пальцы разрывают конверт.")],
      cam=(1.0, 1.15, (704, 400), (900, 420)), amb=["room"]),
    # ---------------- 9
    CARD(["СЦЕНА 9"], "ИНТ. ПОТАЙНАЯ КОМНАТА — ДЕНЬ / ФЛЕШБЭК"),
    S(d_letter, [D(V, "«Девочка моя. Дом тебя позвал — я знала, что позовёт. Прости меня. Вас было двое. Лиза и Алина».")],
      cam=(1.0, 1.15, (704, 300), (704, 420)), amb=["room"]),
    S(d_pond, [A("ФЛЕШБЭК. 1996. Две одинаковые девочки бегут к пруду, смеясь."),
               D(V, "«Семнадцатого июля вы убежали к пруду. Я не углядела. Это моя вина»."),
               A("Девочка в голубом прыгает с мостков. Девочка в красном стоит у края и боится.", label="jump"),
               P(2.0)],
      cam=(1.0, 1.08, (704, 420), (760, 430)), ov=["pond_story"], amb=["summer"], grade="flash", aud=[("splash", "jump+0.7", {})]),
    S(d_under, [A("Под водой. Тишина. Солнечные лучи. Пузырьки. Детская ладонь тянется вверх."), P(1.5)],
      cam=(1.0, 1.1, (704, 396), (704, 360)), ov=["bubbles"], amb=["under"], grade="flash"),
    S(d_garden, [A("Девочка в красном бежит по саду с криком, которого мы не слышим."), P(0.5)],
      cam=(1.0, 1.05, None, None), ov=["run"], grade="flash", mute=True),
    S(d_face, [D(V, "«Утонула Алина. А ты, Лизонька, стояла на мостках и смотрела»."),
               A("Алина роняет письмо. Лицо неподвижно, как маска."),
               D(AL, "Лиза…"),
               D(V, "«Ты полгода молчала, а потом сказала: „Я Аля“. Мама сказала: „Пусть, так ей легче“."),
               D(V, "Мы заклеили комнату и стали звать тебя её именем. Думали — спасаем. А отняли у тебя и сестру, и тебя саму».", label="tear"),
               A("В зеркале шкафа за её спиной стоит ДЕВОЧКА — впервые в голубых сандалиях. Мокрые волосы. Смотрит спокойно.", label="girl"),
               P(1.0)],
      cam=(1.0, 1.2, (704, 396), (900, 380)), ov=["wardrobe"], amb=["room"], aud=[("lullaby", "tear", dict(inst="cello", beat=1.1, n=15, amp=0.2, octave=-1))]),
    # ---------------- 10
    CARD(["СЦЕНА 10"], "НАТ. КРЫЛЬЦО ДОМА — ВЕЧЕР"),
    S(d_porch, [A("Сумерки, первые звёзды. Алина сидит на ступеньках. Подходит Степан Ильич, садится рядом. Буран ложится у ног."),
                D(ST, "Нашла, значит.", note="после долгой паузы"),
                D(AL, "Почему никто не сказал?"),
                D(ST, "Варвара боялась. Ты как заговорила тогда — так в ту комнату и не входила. Обходила стену. Она и заклеила."),
                D(ST, "А потом мать тебя в город увезла, и ты всё забыла. Начисто."),
                D(AL, "Мама никогда о ней не говорила. Ни разу."),
                D(ST, "Не могла она, Алька. Ты ж одно лицо с ней. Наташа на тебя глянет — а видит ту, что в пруду.", note="тяжело"),
                D(ST, "Она после похорон и не прожила тут ни дня. Собрала тебя и уехала."),
                D(ST, "Варваре звонить запретила: «Будешь про Алю напоминать — внучку больше не увидишь»."),
                D(ST, "Вот Варвара и молчала. Чтоб хоть по телефону тебя слышать."),
                D(AL, "Я думала, она меня просто не любила.", note="почти шёпотом"),
                D(ST, "Любила. Боялась только."),
                D(AL, "А девочка в доме?"),
                D(ST, "Варвара говорила: каждую ночь, в три семнадцать, Алинка стучит. Чтобы её позвали. По имени."),
                D(ST, "А звать-то было некого — ты носила её имя. Как же её позовёшь, если имя занято?"),
                P(1.2),
                D(AL, "Она ждёт, чтобы я вернула ей имя."),
                D(ST, "Может, и так. А может, чтобы ты своё забрала."),
                P(1.5)],
      cam=(1.0, 1.15, (704, 430), (704, 470)), amb=["crickets"]),
    # ---------------- 11
    CARD(["СЦЕНА 11"], "ИНТ. ДОМ — КУХНЯ — ДЕНЬ"),
    S(d_kitchen, [A("Яркое солнце, почти неуместное. На столе — коробка: две куклы, две пары сандалий, тетрадь «Лиза»."),
                  A("Рядом — папка с договором.")],
      cam=(1.0, 1.1, (704, 420), (800, 420)), ov=["fire"], amb=["fire"]),
    S(d_contract, [A("Алина долго смотрит на строку с именем. Ноготь медленно ведёт по буквам."), P(1.0)],
      cam=(1.1, 1.5, (705, 440), (640, 450)), ov=["finger"], amb=["fire"]),
    S(lambda: d_phone("Нотариус Гусева", ["Входящий вызов…"], bg=(60, 50, 40)),
      [A("Звонит нотариус. Алина сбрасывает. Пишет коротко:", label="type"), P(2.5)],
      cam=(1.0, 1.06, None, None), ov=["typed"], amb=["fire"], aud=[("buzz", 0.2, {})]),
    S(d_contract, [A("Она кладёт договор в огонь. Бумага чернеет с краёв; последней сгорает строка с именем."), P(4.0)],
      cam=(1.0, 1.15, (705, 420), (705, 440)), ov=["burn"], amb=["fire"]),
    S(d_kitchen_ext, [A("Снаружи, через окно: Алина у печи, свет огня на лице."), A("Дом больше не кажется зловещим: просто старый, уставший дом.")],
      cam=(1.0, 1.12, (704, 396), (704, 400)), amb=["wind", "birds"], aud=[("cello", 0.5, dict(note="D3", dur=9.0, amp=0.15))]),
    # ---------------- 12
    CARD(["СЦЕНА 12"], "ИНТ. ДОМ — СТОЛОВАЯ И ПОТАЙНАЯ КОМНАТА — НОЧЬ (3:16)"),
    S(lambda: d_secret(True), [A("Голубая дверь распахнута. В детской горит керосиновая лампа — единственное тёплое пятно в синей ночи."),
                               A("Алина сидит на полу между кроватками. На коленях — фотография с вырезанным лицом.")],
      cam=(1.0, 1.15, (704, 420), (680, 470)), amb=["night", "tick"]),
    S(lambda: d_clock_wall("night"), [A("Часы в столовой. 3:16. Секундная стрелка движется."), A("Тиканье становится громче, громче…"), P(1.0, label="jump"), P(2.2)],
      cam=(1.0, 1.25, (704, 300), (704, 300)), ov=["clock_close"], clock=(3, 16, "seconds"), pal="night", amb=["night"], aud=[("tick_cresc", 0.0, dict(until="jump"))]),
    S(lambda: d_secret(True), [A("Тишина. Потом — три тихих удара. Не из стены. Изнутри комнаты.", label="knock"), P(2.5), A("Алина не вздрагивает. Она поднимает глаза на тёмное окно.")],
      cam=(1.1, 1.2, (690, 450), (690, 430)), amb=["night"], aud=[("knocks3", "knock+0.8", {})], flash=[("knock", [0.8, 1.25, 1.7])]),
    S(d_refl, [A("В стекле отражается комната — тёплая, золотая. На кровати напротив сидит ДЕВОЧКА в голубых сандалиях.", label="girl"),
               D(AL, "Аля.", note="тихо, мягко, как ребёнку"),
               A("Девочка в отражении замирает."),
               D(AL, "Алечка. Ты прости меня. Я тогда стояла и смотрела. Я испугалась."),
               D(AL, "Мне было семь лет, и я испугалась воды."),
               A("Девочка медленно качает головой — не надо, мол."),
               D(AL, "Я столько лет носила твоё имя. Думала, так ты со мной.", note="слёзы, но голос твёрдый"),
               D(AL, "А ты была тут, одна, за стенкой. Тебе даже позвать никого было нельзя."),
               P(1.0),
               D(AL, "Тебя зовут Алина Воронцова. А меня — Лиза. Лиза Воронцова.", label="name"),
               A("Девочка улыбается — впервые. Встаёт, подходит к отражению Лизы и садится рядом. Кладёт голову ей на плечо."),
               P(1.5),
               D("ЛИЗА", "Спи, моя ласточка, спи…", note="напевает"),
               P(5.0)],
      cam=(1.0, 1.1, (704, 420), (760, 450)), ov=["refl"], amb=["night"],
      aud=[("duet", "name+3.0", {}), ("pad", "name+2.0", dict(dur=22.0))]),
    # ---------------- 13
    CARD(["СЦЕНА 13"], "ИНТ. ДОМ — СТОЛОВАЯ — РАССВЕТ"),
    S(lambda: d_dining("dawn"), [A("Первые розовые лучи. Лиза просыпается на полу детской, укрытая лоскутным одеялом. Кто укрыл — непонятно."),
                                 A("Она выходит в столовую. Часы идут. 5:42. Маятник качается ровно и спокойно.")],
      cam=(1.0, 1.15, (704, 396), (850, 300)), ov=["dining_clock"], clock=(5, 42, "swing"), pal="dawn", amb=["tick", "birds"]),
    S(d_dawn_window, [A("Лиза подходит к окну. В стекле — только её отражение. Одно."), P(1.5, label="wave"),
                      A("У пруда, в утреннем тумане, мелькает детская фигурка, машущая рукой."), P(2.5, label="palm"),
                      A("Лиза прикладывает ладонь к стеклу."),
                      D("ЛИЗА", "Пока, Аля.", note="одними губами"), P(3.0)],
      cam=(1.0, 1.1, (704, 396), (800, 420)), ov=["wave"], amb=["birds"], aud=[("lullaby", 0.5, dict(inst="major", beat=0.8, n=15, amp=0.2))]),
    # ---------------- 14
    CARD(["СЦЕНА 14"], "НАТ. ДОМ ВОРОНЦОВЫХ — ДЕНЬ. ЭПИЛОГ, ЧЕРЕЗ МЕСЯЦ"),
    S(d_epilogue, [A("Ранняя осень. Наличники выкрашены в синий. Крыльцо починено. Пруд вычищен."),
                   A("Лиза на стремянке прибивает табличку над крыльцом. Степан Ильич держит лестницу."),
                   D(ST, "Криво."),
                   D("ЛИЗА", "Не криво, а живописно."),
                   D(ST, "Вся в Варвару.", note="ворчливо, но улыбаясь"), P(1.0)],
      cam=(1.0, 1.1, (704, 420), (560, 420)), amb=["birds", "wind"], aud=[("hammer", 3.0, {}), ("dog_bark", 6.5, {})]),
    S(d_plaque, [A("На табличке — две ласточки и надпись."), P(3.0)], cam=(1.0, 1.15, None, None), amb=["birds"]),
    S(lambda: d_field(autumn=True, with_house=True), [A("Камера поднимается: крыша, яблоня, поле, полоса ельника. Мы улетаем."), P(4.0)],
      cam=(4.0, 1.0, (1135, 200), (704, 396)), amb=["wind", "tick_faint"], aud=[("lullaby", 0.5, dict(inst="cello", beat=1.0, n=8, amp=0.22, octave=-1))]),
    CARD(["«Тех, кого мы потеряли, нельзя забыть.", "Их можно только назвать по имени»."], None, 8.0),
    CARD(["КОНЕЦ"], "аниматик · силуэтная раскадровка по сценарию", 5.0),
]


# =====================================================================
#  VOICES (Piper TTS, offline)
# =====================================================================
VOICE_DIR = os.environ.get("PIPER_VOICES", os.path.join(os.path.dirname(os.path.abspath(__file__)), "voices"))
CAST = {  # speaker prefix -> (model, length_scale, pitch_factor, gain)
    "АЛИНА": ("ru_RU-irina-medium", 1.0, 1.0, 1.0),
    "ЛИЗА": ("ru_RU-irina-medium", 1.0, 1.0, 1.0),
    "СТЕПАН": ("ru_RU-dmitri-medium", 1.12, 0.96, 1.0),
    "ВАРВАРА": ("ru_RU-irina-medium", 1.0, 0.88, 0.95),
}


def tts_clean(s):
    for ch in "«»„“\"":
        s = s.replace(ch, "")
    return s.replace("—", ",").replace("…", ".").strip()


def synth_voices(cache):
    import hashlib
    from piper import PiperVoice, SynthesisConfig
    os.makedirs(cache, exist_ok=True)
    loaded = {}
    for sh in SHOTS:
        for c in sh.get("cues", []):
            if c["kind"] != "dlg":
                continue
            key = next(k for k in CAST if c["who"].startswith(k))
            model, ls, pitch, gain = CAST[key]
            note = c.get("note", "")
            if "губами" in note or "шёпот" in note or "беззвучно" in note:
                gain *= 0.55
            txt = tts_clean(c["text"])
            h = hashlib.md5(f"{model}|{ls}|{txt}".encode()).hexdigest()[:12]
            path = os.path.join(cache, h + ".wav")
            if not os.path.exists(path):
                if model not in loaded:
                    loaded[model] = PiperVoice.load(os.path.join(VOICE_DIR, model + ".onnx"))
                with wave.open(path, "wb") as w:
                    loaded[model].synthesize_wav(txt, w, syn_config=SynthesisConfig(length_scale=ls))
            with wave.open(path) as w:
                sr0 = w.getframerate()
                x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
            # pitch factor < 1: play slower (lower + longer), then resample to SR
            src_sr = sr0 * pitch
            n_out = int(len(x) / src_sr * SR)
            y = np.interp(np.linspace(0, len(x) - 1, n_out), np.arange(len(x)), x)
            y = y / (np.abs(y).max() + 1e-9) * 0.55 * gain
            c["voice"] = y
            c["vdur"] = len(y) / SR


# =====================================================================
#  TIMING
# =====================================================================
def cue_len(c):
    if c["kind"] == "pause":
        return c["sec"]
    n = len(c["text"])
    if c["kind"] == "dlg":
        if "vdur" in c:
            return max(1.8, c["vdur"] + 0.8, 0.8 + n / 22.0)
        return max(2.4, 1.0 + n / 13.0)
    return max(2.8, 1.2 + n / 15.0)


def layout():
    t = 0.0
    for sh in SHOTS:
        sh["start"] = t
        if sh.get("card"):
            sh["labels"] = {"end": sh["dur"]}
            t += sh["dur"]
            continue
        lt = 0.7
        timed = []
        labels = {}
        for c in sh["cues"]:
            ln = cue_len(c)
            if "label" in c:
                labels[c["label"]] = lt
            if c["kind"] != "pause":
                timed.append((lt, lt + ln, c))
            lt += ln + (0.25 if c["kind"] != "pause" else 0)
        sh["dur"] = lt + 0.6
        labels["end"] = sh["dur"]
        sh["labels"] = labels
        sh["timed"] = timed
        t += sh["dur"]
    return t


def resolve(sh, ref):
    if isinstance(ref, (int, float)):
        return float(ref)
    if "+" in ref:
        a, b = ref.split("+")
        return sh["labels"].get(a, 0.0) + float(b)
    return sh["labels"].get(ref, 0.0)


# =====================================================================
#  TEXT LAYERS (screen space)
# =====================================================================
def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if d.textlength(test, font=f) <= maxw:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def sub_layer(c):
    """Returns (y0, rgb[h,w,3], alpha[h,w,1]) band."""
    im = Image.new("RGBA", (W, 260), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if c["kind"] == "dlg":
        f = font(F_SERIF, 34)
        lines = wrap(d, c["text"], f, 1040)
        who = c["who"] + (f"  ({c['note']})" if c.get("note") else "")
        hgt = 34 + len(lines) * 42 + 18
        y0 = H - hgt - 26
        d.rounded_rectangle([110, 0, W - 110, hgt], radius=14, fill=(0, 0, 0, 150))
        fw = font(F_SANSB, 20)
        d.text((W / 2 - d.textlength(who, font=fw) / 2, 10), who, font=fw, fill=(230, 190, 120, 255))
        for i, ln in enumerate(lines):
            d.text((W / 2 - d.textlength(ln, font=f) / 2, 38 + i * 42), ln, font=f, fill=(245, 242, 235, 255))
    else:
        f = font(F_ITAL, 30)
        lines = wrap(d, c["text"], f, 1080)
        hgt = len(lines) * 38 + 22
        y0 = 26
        d.rounded_rectangle([80, 0, W - 80, hgt], radius=12, fill=(0, 0, 0, 120))
        for i, ln in enumerate(lines):
            d.text((W / 2 - d.textlength(ln, font=f) / 2, 10 + i * 38), ln, font=f, fill=(225, 222, 210, 255))
    arr = np.asarray(im, np.float32)[:hgt]
    return y0, arr[..., :3], arr[..., 3:4] / 255


def card_image(sh):
    im = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(im)
    if sh.get("big"):
        f = font(F_BOLD, 84)
    elif len(sh["lines"][0]) > 20:
        f = font(F_ITAL, 44)
    else:
        f = font(F_BOLD, 60)
    total = len(sh["lines"]) * f.size * 1.3
    y = H / 2 - total / 2 - (20 if sh["sub"] else 0)
    for ln in sh["lines"]:
        text_c(d, W / 2, y, ln, f, (232, 226, 210))
        y += f.size * 1.3
    if sh["sub"]:
        text_c(d, W / 2, y + 16, sh["sub"], font(F_SANS, 26), (170, 165, 150))
    return np.asarray(im, np.float32)


# =====================================================================
#  RENDER
# =====================================================================
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIGN = np.clip(1 - 0.75 * (((xx - W / 2) / (W * 0.65)) ** 2 + ((yy - H / 2) / (H * 0.65)) ** 2), 0, 1)[..., None]
del yy, xx


def make_grains(amp, seed):
    rng = np.random.default_rng(seed)
    return [np.asarray(Image.fromarray(rng.normal(128, amp, (H // 2, W // 2)).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32)[..., None] - 128
            for _ in range(6)]


def cam_at(sh, t):
    dur = sh["dur"]
    keys = sh.get("cam_keys")
    if keys:
        pts = [(resolve(sh, k[0]) if not isinstance(k[0], (int, float)) else k[0], k[1], k[2]) for k in keys]
        pts.sort(key=lambda p: p[0])
        for i in range(len(pts) - 1):
            if pts[i][0] <= t <= pts[i + 1][0]:
                u = smooth((t - pts[i][0]) / max(1e-3, pts[i + 1][0] - pts[i][0]))
                z = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * u
                c = (pts[i][2][0] + (pts[i + 1][2][0] - pts[i][2][0]) * u, pts[i][2][1] + (pts[i + 1][2][1] - pts[i][2][1]) * u)
                return z, c
        return pts[-1][1], pts[-1][2]
    z0, z1, c0, c1 = sh["cam"]
    c0 = c0 or (BW / 2, BH / 2)
    c1 = c1 or c0
    u = smooth(t / dur) if z0 < 2 else 1 - (1 - t / dur) ** 2.2
    z = z0 + (z1 - z0) * u
    return z, (c0[0] + (c1[0] - c0[0]) * u, c0[1] + (c1[1] - c0[1]) * u)


def render_shot(args):
    idx, outdir, only_t = args
    sh = SHOTS[idx]
    dur = sh["dur"]
    n = int(round(dur * FPS))
    path = os.path.join(outdir, f"seg_{idx:03d}.mp4")
    rng = np.random.default_rng(idx)
    flashback = sh.get("grade") == "flash"
    grains = make_grains(22 if flashback else 9, idx)
    if sh.get("card"):
        base_card = card_image(sh)
        base = None
    else:
        base = sh["draw"]()
        subs = [(a, b, sub_layer(c)) for a, b, c in sh["timed"]]
        flashes = []
        for lbl, offs in sh.get("flash", []):
            t0 = sh["labels"].get(lbl, 0)
            flashes += [t0 + o for o in offs]
    frames = [int(only_t * FPS)] if only_t is not None else range(n)
    if only_t is None:
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                               "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    out = None
    for i in frames:
        t = i / FPS
        if sh.get("card"):
            fr = base_card.copy()
            fade = min(1.0, t / 0.8, (dur - t) / 0.8)
            fr = fr * max(0.0, fade)
        else:
            img = base
            if sh["ov"]:
                img = base.copy()
                for name in sh["ov"]:
                    img = OVL[name](img, t, dur, sh)
            z, (cx, cy) = cam_at(sh, t)
            cw, chh = BW / z, BH / z
            if sh.get("shake"):
                cx += sh["shake"] * math.sin(t * 7.1) + sh["shake"] * 0.6 * math.sin(t * 13.3)
                cy += sh["shake"] * math.cos(t * 6.3)
            for (s0, sd, amp) in sh.get("shake_at", []):
                if s0 <= t < s0 + sd:
                    cx += rng.uniform(-amp, amp)
                    cy += rng.uniform(-amp, amp)
            if flashback:
                cx += rng.uniform(-3, 3)
                cy += rng.uniform(-3, 3)
            cx = min(max(cx, cw / 2), BW - cw / 2)
            cy = min(max(cy, chh / 2), BH - chh / 2)
            fr = img.crop((int(cx - cw / 2), int(cy - chh / 2), int(cx + cw / 2), int(cy + chh / 2))).resize((W, H), Image.BILINEAR)
            fr = np.asarray(fr, np.float32)
            flick = 1 + (0.05 if flashback else 0.015) * math.sin(t * 23.1) * math.sin(t * 7.3)
            fr = fr * flick
            for ft in flashes:
                if ft <= t < ft + 0.12:
                    fr = fr + 70 * (1 - (t - ft) / 0.12)
            fr = fr * VIGN
            for a, b, (y0, rgb, al) in subs:
                f_ = min(1.0, (t - a) / 0.25, (b - t) / 0.25)
                if f_ <= 0:
                    continue
                hgt = rgb.shape[0]
                band = fr[y0:y0 + hgt]
                fr[y0:y0 + hgt] = band * (1 - al * f_) + rgb * al * f_
            fr = fr + grains[i % 6]
            fade = 1.0
            if sh.get("fade_in", False) or True:
                fade = min(1.0, t / 0.25, (dur - t) / 0.25)
            fr = fr * max(0.0, fade)
        frame = fr.clip(0, 255).astype(np.uint8)
        if only_t is not None:
            out = frame
        else:
            ff.stdin.write(frame.tobytes())
    if only_t is None:
        ff.stdin.close()
        ff.wait()
        return path
    return out


# =====================================================================
#  AUDIO
# =====================================================================
def hz(note):
    names = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}
    n, i = names[note[0]], 1
    if note[i] == "#":
        n += 1
        i += 1
    elif note[i] == "b":
        n -= 1
        i += 1
    return 440 * 2 ** ((n + (int(note[i:]) - 4) * 12) / 12)


MEL = ["E5", "C5", "D5", "B4", "C5", "A4", "B4", "G#4", "A4", "C5", "E5", "D5", "C5", "B4", "A4"]
MEL_MAJ = ["E5", "C#5", "D5", "B4", "C#5", "A4", "B4", "G#4", "A4", "C#5", "E5", "D5", "C#5", "B4", "A4"]
SCALE = ["A", "B", "C", "D", "E", "F", "G#"]


def third_below(note):
    order = ["C", "D", "E", "F", "G#", "A", "B"]
    nm, o = note[:-1], int(note[-1])
    di = o * 7 + order.index(nm) - 2
    o2, p2 = divmod(di, 7)
    return f"{order[p2]}{o2}"


def shift_oct(note, k):
    return note[:-1] + str(int(note[-1]) + k)


def env_ad(n, a, r):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / r)


def i_box(f, dur, amp):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.25) + 0.12 * np.sin(2 * np.pi * 3.01 * f * t) * np.exp(-t / 0.12)
    return amp * s * env_ad(n, 0.004, 0.9)


def i_piano(f, dur, amp, detune=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for k, a in enumerate((1, 0.5, 0.3, 0.18, 0.1, 0.06), start=1):
        s += a * np.sin(2 * np.pi * f * k * (1 + detune) * t) * np.exp(-t * (1.2 + k * 0.6))
        if detune:
            s += a * 0.7 * np.sin(2 * np.pi * f * k * (1 - detune) * t) * np.exp(-t * (1.2 + k * 0.6))
    return amp * s * np.minimum(1, t / 0.005)


def i_bowed(f, dur, amp, attack=0.25, nh=10, vib=5.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    ph = 2 * np.pi * f * t + (f * 0.004) * np.sin(2 * np.pi * vib * t) * 2 * np.pi / vib
    s = np.zeros(n)
    for k in range(1, nh + 1):
        s += np.sin(k * ph) / k * (0.85 ** k)
    e = np.minimum(1, t / attack) * np.minimum(1, np.maximum(0, (dur - t)) / 0.4)
    return amp * s * e


def i_voice(f, dur, amp):
    n = int(dur * SR)
    t = np.arange(n) / SR
    ph = 2 * np.pi * f * t + 0.6 * np.sin(2 * np.pi * 5.2 * t)
    s = np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.08 * np.sin(3 * ph)
    e = np.minimum(1, t / 0.09) * np.minimum(1, np.maximum(0, (dur - t)) / 0.25)
    return amp * s * e


class Mix:
    def __init__(self, dur):
        self.a = np.zeros(int((dur + 6) * SR))

    def put(self, sig, at):
        i = int(at * SR)
        if i < 0:
            sig = sig[-i:]
            i = 0
        j = min(len(self.a), i + len(sig))
        if j > i:
            self.a[i:j] += sig[: j - i]


def lp(x, fc):
    b, a = butter(2, fc / (SR / 2), "low")
    return lfilter(b, a, x)


def bp(x, f1, f2):
    b, a = butter(2, [f1 / (SR / 2), f2 / (SR / 2)], "band")
    return lfilter(b, a, x)


RNG = np.random.default_rng(42)


def noise(n):
    return RNG.standard_normal(n)


def amb_sig(kind, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    if kind == "wind":
        return lp(noise(n), 400) * 0.5 * (0.6 + 0.4 * np.sin(2 * np.pi * t / 6.1))
    if kind == "grass":
        x = bp(noise(n), 5500, 7500) * 0.06
        return x * (0.5 + 0.5 * (np.sin(2 * np.pi * 9 * t) > 0.3))
    if kind == "car":
        return lp(noise(n), 160) * 0.9 + 0.05 * np.sin(2 * np.pi * 48 * t)
    if kind == "room":
        return lp(noise(n), 200) * 0.12
    if kind == "night":
        return lp(noise(n), 150) * 0.12 + bp(noise(n), 3800, 4400) * 0.015 * (np.sin(2 * np.pi * 0.7 * t) > 0.6)
    if kind == "crickets":
        c = np.sin(2 * np.pi * 4300 * t) * (np.sin(2 * np.pi * 28 * t) > 0) * (np.sin(2 * np.pi * 1.6 * t) > 0.2)
        c2 = np.sin(2 * np.pi * 3900 * t) * (np.sin(2 * np.pi * 31 * t) > 0) * (np.sin(2 * np.pi * 1.1 * t + 1) > 0.3)
        return 0.04 * (c + c2) + lp(noise(n), 150) * 0.08
    if kind == "birds":
        s = np.zeros(n)
        for _ in range(int(dur * 1.2)):
            at = RNG.uniform(0, max(0.1, dur - 0.5))
            ln = int(RNG.uniform(0.08, 0.22) * SR)
            tt = np.arange(ln) / SR
            f0 = RNG.uniform(2500, 4200)
            sig = np.sin(2 * np.pi * (f0 * tt + RNG.uniform(-4000, 4000) * tt * tt)) * np.sin(np.pi * tt / tt[-1]) * 0.05
            i = int(at * SR)
            s[i:i + ln] += sig[: n - i]
        return s + lp(noise(n), 300) * 0.15
    if kind == "hens":
        s = np.zeros(n)
        for _ in range(int(dur / 3)):
            at = RNG.uniform(0, max(0.1, dur - 0.5))
            ln = int(0.18 * SR)
            tt = np.arange(ln) / SR
            sig = bp(noise(ln), 600, 1400) * np.sin(np.pi * tt / tt[-1]) * 0.25
            i = int(at * SR)
            s[i:i + ln] += sig[: n - i]
        return s
    if kind == "tick" or kind == "tick_faint":
        s = np.zeros(n)
        k = 0
        for at in np.arange(0.2, dur, 0.5):
            ln = int(0.03 * SR)
            sig = noise(ln) * np.exp(-np.arange(ln) / SR / 0.004) * (0.22 if k % 2 else 0.15)
            i = int(at * SR)
            s[i:i + ln] += sig[: n - i]
            k += 1
        return s * (0.35 if kind == "tick_faint" else 1.0)
    if kind == "fire":
        s = lp(noise(n), 300) * 0.25
        for _ in range(int(dur * 9)):
            i = int(RNG.uniform(0, dur - 0.05) * SR)
            ln = int(0.01 * SR)
            s[i:i + ln] += noise(ln) * RNG.uniform(0.05, 0.25)
        return s
    if kind == "summer":
        return bp(noise(n), 6000, 8000) * 0.05 + lp(noise(n), 300) * 0.1 + 0.02 * np.sin(2 * np.pi * 220 * t) * (np.sin(2 * np.pi * 0.3 * t) > 0.8)
    if kind == "under":
        return lp(noise(n), 120) * 0.9 + 0.08 * np.sin(2 * np.pi * 40 * t)
    return np.zeros(n)


def sfx(name, kw):
    if name == "knock":
        n = int(0.25 * SR)
        t = np.arange(n) / SR
        return 0.7 * np.sin(2 * np.pi * 75 * t) * np.exp(-t / 0.05) + 0.25 * noise(n) * np.exp(-t / 0.01)
    if name == "bong":
        n = int(4 * SR)
        t = np.arange(n) / SR
        return sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / d) for f, a, d in ((220, 0.5, 1.6), (440 * 1.19, 0.25, 0.9), (660 * 1.33, 0.15, 0.5), (110, 0.3, 2.0)))
    if name == "crack":
        n = int(0.9 * SR)
        t = np.arange(n) / SR
        return noise(n) * np.exp(-t / 0.08) * 0.6 + 0.8 * np.sin(2 * np.pi * 60 * t) * np.exp(-((t - 0.45) / 0.05) ** 2 * 0.5) * (t > 0.4)
    if name == "chop":
        n = int(0.4 * SR)
        t = np.arange(n) / SR
        return 0.6 * np.sin(2 * np.pi * 120 * t) * np.exp(-t / 0.04) + bp(noise(n), 800, 3000) * np.exp(-t / 0.02) * 0.8
    if name == "buzz":
        n = int(1.2 * SR)
        t = np.arange(n) / SR
        return 0.3 * np.sign(np.sin(2 * np.pi * 170 * t)) * ((t % 0.6) < 0.35) * 0.5
    if name == "splash":
        n = int(1.5 * SR)
        t = np.arange(n) / SR
        return bp(noise(n), 400, 4000) * np.exp(-t / 0.3) * 0.7
    if name == "dog_growl":
        n = int(1.6 * SR)
        t = np.arange(n) / SR
        return lp(noise(n), 300) * (0.5 + 0.5 * np.sin(2 * np.pi * 22 * t)) * np.sin(np.pi * t / t[-1]) * 0.8
    if name == "dog_bark":
        out = np.zeros(int(1.2 * SR))
        for at in (0.0, 0.4):
            ln = int(0.15 * SR)
            tt = np.arange(ln) / SR
            sig = bp(noise(ln), 500, 1800) * np.exp(-tt / 0.05) * 1.2 + 0.4 * np.sin(2 * np.pi * 330 * tt) * np.exp(-tt / 0.05)
            i = int(at * SR)
            out[i:i + ln] += sig
        return out
    if name == "hammer":
        out = np.zeros(int(3 * SR))
        for at in (0.0, 0.5, 1.0, 1.9):
            ln = int(0.2 * SR)
            tt = np.arange(ln) / SR
            sig = 0.5 * np.sin(2 * np.pi * 900 * tt) * np.exp(-tt / 0.02) + 0.4 * np.sin(2 * np.pi * 140 * tt) * np.exp(-tt / 0.05)
            i = int(at * SR)
            out[i:i + ln] += sig
        return out
    if name == "piano_note":
        return i_piano(hz("D#5"), 4.0, 0.35, detune=0.012)
    return np.zeros(10)


def build_audio(total, outwav):
    M = Mix(total)
    muted, muffled = [], []
    for sh in SHOTS:
        s0, dur = sh["start"], sh["dur"]
        if sh.get("mute"):
            muted.append((s0, s0 + dur))
        for a in sh.get("amb", []):
            sig = amb_sig(a, dur + 0.6)
            n = len(sig)
            e = np.minimum(1, np.arange(n) / (0.3 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.3 * SR))
            M.put(sig * e * (0.8 if a != "under" else 1.0), s0)
            if a == "under":
                muffled.append((s0, s0 + dur))
        for name, at, kw in sh.get("aud", []):
            t0 = s0 + resolve(sh, at)
            until = s0 + resolve(sh, kw["until"]) if "until" in kw else None
            if name == "lullaby":
                inst = kw.get("inst", "box")
                beat, amp, n_ = kw["beat"], kw["amp"], kw["n"]
                mel = MEL_MAJ if inst == "major" else MEL
                for k, nt in enumerate(mel[:n_]):
                    nt = shift_oct(nt, kw.get("octave", 0))
                    L = beat * (3 if k == n_ - 1 else 1.6)
                    f = hz(nt)
                    if inst == "box":
                        sig = i_box(f, L, amp)
                    elif inst == "piano":
                        sig = i_piano(f, L * 1.5, amp)
                    elif inst == "cello":
                        sig = i_bowed(f, beat * (3 if k == n_ - 1 else 1.05), amp)
                    else:  # major: full ensemble
                        sig = i_box(f, L, amp * 0.8)
                        sig = sig + np.pad(i_bowed(f / 2, beat * 1.05, amp * 0.5), (0, max(0, len(sig) - int(beat * 1.05 * SR))))[: len(sig)]
                        sig = sig + np.pad(i_bowed(f / 4, beat * 1.05, amp * 0.4), (0, max(0, len(sig) - int(beat * 1.05 * SR))))[: len(sig)]
                    M.put(sig, t0 + k * beat)
                if inst == "major":
                    for k, nt in enumerate(["A2", "D3", "E3", "A2"]):
                        M.put(i_bowed(hz(nt), beat * 3.6, 0.1, attack=0.8), t0 + k * beat * 3.6)
            elif name == "hum":
                n_ = kw.get("n", 4)
                for k, nt in enumerate(MEL[:n_]):
                    at_k = t0 + k * 0.75
                    if until and at_k >= until:
                        break
                    L = 0.7 if k < n_ - 1 else 1.4
                    if until:
                        L = min(L, until - at_k)
                    M.put(i_voice(hz(nt), max(0.05, L), 0.09), at_k)
            elif name == "duet":
                beat = 0.85
                for k, nt in enumerate(MEL):
                    L = beat * (3 if k == 14 else 0.95)
                    M.put(i_voice(hz(nt), L, 0.08), t0 + k * beat)
                    M.put(i_voice(hz(third_below(nt)), L, 0.06), t0 + k * beat)
            elif name == "pad":
                for nt in ("A3", "C4", "E4"):
                    M.put(i_bowed(hz(nt), kw["dur"], 0.045, attack=2.5, nh=6), t0)
            elif name == "cello":
                M.put(i_bowed(hz(kw["note"]), kw["dur"], kw["amp"], attack=1.2), t0)
            elif name == "cluster":
                L = (until or t0 + 4) - t0
                for f in (220, 233, 247, 262, 277):
                    sig = i_bowed(f, L + 0.05, 0.03, attack=L * 0.9, nh=6)
                    sig[-int(0.03 * SR):] *= np.linspace(1, 0, int(0.03 * SR))
                    M.put(sig, t0)
            elif name == "heartbeat":
                end = until or t0 + 10
                for at_ in np.arange(t0, end, 0.9):
                    for o, a in ((0, 0.7), (0.22, 0.45)):
                        ln = int(0.25 * SR)
                        tt = np.arange(ln) / SR
                        M.put(a * np.sin(2 * np.pi * 50 * tt) * np.exp(-tt / 0.08), at_ + o)
            elif name == "tick_cresc":
                end = until
                ts = np.arange(t0 + 0.2, end, 0.5)
                for k, at_ in enumerate(ts):
                    ln = int(0.03 * SR)
                    g = 0.12 + 0.55 * (k / max(1, len(ts) - 1)) ** 2
                    M.put(noise(ln) * np.exp(-np.arange(ln) / SR / 0.004) * g, at_)
            elif name == "tick1":
                for k, at_ in enumerate((1.2, 1.9)):
                    ln = int(0.03 * SR)
                    M.put(noise(ln) * np.exp(-np.arange(ln) / SR / 0.004) * 0.25, t0 + sh["labels"].get("swing", 0) + at_ - 1.0)
            elif name == "knocks6":
                for o in (1.0, 1.45, 1.9, 3.1, 3.55, 4.0):
                    M.put(sfx("knock", {}) * 0.8, t0 + o)
            elif name == "knocks3":
                for o in (0.0, 0.45, 0.9):
                    M.put(sfx("knock", {}) * 0.6, t0 + o)
            else:
                M.put(sfx(name, kw), t0)
    vt = np.zeros_like(M.a)
    for sh in SHOTS:
        for a0, b0, c in sh.get("timed", []):
            if "voice" in c:
                i = int((sh["start"] + a0 + 0.2) * SR)
                v = c["voice"]
                j = min(len(vt), i + len(v))
                vt[i:j] += v[: j - i]
    act = lp(np.abs(vt), 4.0)
    act = np.clip(act / 0.05, 0, 1)
    duck = 1 - 0.6 * act
    a = M.a * duck
    for s, e in muffled:
        i, j = int(s * SR), int(e * SR)
        a[i:j] = lp(a[i:j], 300)
    # reverb
    ir_n = int(2.0 * SR)
    ir = RNG.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / SR / 0.5)
    ir[0] = 1.0
    ir /= np.abs(ir).sum() / 5
    L = len(a) + ir_n
    F = 1 << (L - 1).bit_length()
    wet = np.fft.irfft(np.fft.rfft(a, F) * np.fft.rfft(ir, F), F)[: len(a)]
    out = 0.7 * a + 0.3 * wet
    out = out / (np.percentile(np.abs(out), 99.95) + 1e-9) * 0.5
    out = out + vt * 0.95
    for s, e in muted:
        i, j = int(s * SR), int(e * SR)
        r = int(0.15 * SR)
        out[i:j] = 0
        out[max(0, i - r):i] *= np.linspace(1, 0, i - max(0, i - r))
        out[j:j + r] *= np.linspace(0, 1, len(out[j:j + r]))
    out = out[: int(total * SR)]
    out = np.tanh(out * 1.1) * 0.9
    pcm = (out * 32767).astype(np.int16)
    with wave.open(outwav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


# =====================================================================
def main():
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    synth_voices(os.path.join(outdir, "tts"))
    total = layout()
    print(f"shots: {len(SHOTS)}  total: {total / 60:.1f} min", flush=True)
    if len(sys.argv) > 2 and sys.argv[2] == "preview":
        tiles = []
        for i, sh in enumerate(SHOTS):
            if sh.get("card") and i > 1:
                continue
            fr = render_shot((i, outdir, sh["dur"] * 0.62))
            tiles.append(Image.fromarray(fr).resize((480, 270)))
        for k in range(0, len(tiles), 12):
            sheet = Image.new("RGB", (480 * 4, 270 * 3))
            for j, tl in enumerate(tiles[k:k + 12]):
                sheet.paste(tl, ((j % 4) * 480, (j // 4) * 270))
            sheet.save(os.path.join(outdir, f"preview_{k // 12}.png"))
        return
    wav = os.path.join(outdir, "audio.wav")
    build_audio(total, wav)
    print("audio done", flush=True)
    with Pool(4) as pool:
        paths = []
        for k, p in enumerate(pool.imap(render_shot, [(i, outdir, None) for i in range(len(SHOTS))])):
            paths.append(p)
            print(f"shot {k + 1}/{len(SHOTS)}", flush=True)
    lst = os.path.join(outdir, "list.txt")
    with open(lst, "w") as f:
        for p in paths:
            f.write(f"file '{os.path.abspath(p)}'\n")
    final = os.path.join(outdir, "animatic.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", final], check=True)
    print("final:", final, flush=True)


if __name__ == "__main__":
    main()
