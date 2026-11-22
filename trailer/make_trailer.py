"""Типографический тизер «Тайна старого дома»: кадры (PIL+numpy), звук (синтез), сборка ffmpeg."""
import math, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]
W, H, FPS, DUR = 1280, 720, 24, 38.0
N = int(DUR * FPS)
SR = 44100
rng = np.random.default_rng(7)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

# ---------------------------------------------------------------- AUDIO
def env(n, a=0.01, r=0.3):
    t = np.arange(n) / SR
    e = np.minimum(1, t / a) * np.exp(-t / r)
    return e

def musicbox(freq, dur, amp=0.25):
    n = int(dur * SR); t = np.arange(n) / SR
    vib = 1 + 0.003 * np.sin(2 * math.pi * 5 * t)
    s = (np.sin(2*math.pi*freq*vib*t) + 0.35*np.sin(2*math.pi*2*freq*t)*np.exp(-t/0.25)
         + 0.12*np.sin(2*math.pi*3.01*freq*t)*np.exp(-t/0.12))
    return amp * s * env(n, 0.004, 0.9)

def hz(note):
    names = {'C':-9,'D':-7,'E':-5,'F':-4,'G':-2,'A':0,'B':2}
    n = names[note[0]]; i = 1
    if note[i] == '#': n += 1; i += 1
    octv = int(note[i:])
    return 440 * 2 ** ((n + (octv - 4) * 12) / 12)

audio = np.zeros(int(DUR * SR) + SR * 4)
def put(sig, at):
    i = int(at * SR); audio[i:i+len(sig)] += sig[:len(audio)-i]

MELODY = ["E5","C5","D5","B4", "C5","A4","B4","G#4", "A4","C5","E5","D5", "C5","B4","A4"]
def lullaby(start, beat, notes, amp=0.22):
    for k, nt in enumerate(notes):
        put(musicbox(hz(nt), beat * (3 if k == len(notes)-1 else 1.6), amp), start + k * beat)

# fragment (4 notes) at the very start, broken off
lullaby(0.6, 0.62, MELODY[:4], 0.2)
# full lullaby under the text sections, slower
lullaby(14.8, 0.72, MELODY, 0.17)
# title: lullaby an octave lower + harmony
lullaby(28.6, 0.6, MELODY[:8], 0.2)
for k, nt in enumerate(["A3","A3","E3","E3"]):
    put(musicbox(hz(nt), 2.6, 0.12), 28.6 + k*1.2)

# low drone with slow swell
t = np.arange(len(audio)) / SR
drone = (0.08*np.sin(2*math.pi*55*t) + 0.05*np.sin(2*math.pi*82.4*t + 1)
         + 0.03*np.sin(2*math.pi*110.6*t))
swell = 0.5 + 0.5*np.sin(2*math.pi*t/9 - 1.5)
fade = np.clip(t / 3, 0, 1) * np.clip((DUR + 1 - t) / 3, 0, 1)
audio += drone * swell * fade

# wind: lowpassed noise
noise = rng.standard_normal(len(audio))
k = np.ones(400) / 400
wind = np.convolve(noise, k, mode="same") * 0.6
wind *= (0.5 + 0.5*np.sin(2*math.pi*t/6.3)) * fade
audio += wind * 0.35

# clock ticks 8.5..15
for i, tt in enumerate(np.arange(8.6, 15.0, 0.5)):
    n = int(0.03 * SR)
    click = rng.standard_normal(n) * np.exp(-np.arange(n)/SR/0.004) * (0.25 if i % 2 else 0.18)
    put(click, tt)

# three knocks 25.6, 26.1, 26.6
KNOCKS = [25.6, 26.1, 26.6]
for tt in KNOCKS:
    n = int(0.25 * SR); tk = np.arange(n) / SR
    thump = 0.7*np.sin(2*math.pi*70*tk)*np.exp(-tk/0.06) + 0.2*rng.standard_normal(n)*np.exp(-tk/0.01)
    put(thump, tt)

# reverb: convolve with decaying noise IR
ir_n = int(2.2 * SR)
ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n)/SR/0.55)
ir[0] = 1.0; ir /= np.abs(ir).sum() / 6
L = len(audio) + ir_n
F = 1 << (L - 1).bit_length()
wet = np.fft.irfft(np.fft.rfft(audio, F) * np.fft.rfft(ir, F), F)[:len(audio)]
mix = 0.65 * audio + 0.35 * wet
mix = mix[:int(DUR * SR)]
mix *= np.clip((DUR - np.arange(len(mix))/SR) / 2.5, 0, 1)
mix /= np.abs(mix).max() / 0.85
pcm = (mix * 32767).astype(np.int16)
with wave.open(OUT + ".wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

# ---------------------------------------------------------------- VISUALS
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
vign = 1 - 0.85 * (((xx - W/2) / (W*0.62))**2 + ((yy - H/2) / (H*0.62))**2)
vign = np.clip(vign, 0, 1)[..., None]
bg = np.zeros((H, W, 3), np.float32)
bg[..., 0], bg[..., 1], bg[..., 2] = 6, 14, 20   # cold blue-green night
grains = [np.asarray(Image.fromarray(rng.normal(128, 14, (H//2, W//2)).clip(0,255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32)[..., None] - 128 for _ in range(6)]

def window_layer():
    """Faint moonlit window frame (cross) as the background motif."""
    im = Image.new("L", (W, H), 0); d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = 760, 90, 1120, 560
    d.rectangle([x0, y0, x1, y1], fill=70)
    d.rectangle([x0, y0, x1, y1], outline=0, width=16)
    d.rectangle([(x0+x1)//2 - 7, y0, (x0+x1)//2 + 7, y1], fill=0)
    d.rectangle([x0, (y0+y1)//2 - 7, x1, (y0+y1)//2 + 7], fill=0)
    im = im.filter(ImageFilter.GaussianBlur(9))
    a = np.asarray(im, np.float32)[..., None] / 255
    return a * np.array([90, 140, 170], np.float32)
WINDOW = window_layer()

def girl_layer():
    im = Image.new("L", (W, H), 0); d = ImageDraw.Draw(im)
    cx, base = 1030, 545
    d.ellipse([cx-22, base-205, cx+22, base-160], fill=255)          # head
    d.polygon([(cx-16, base-158), (cx+16, base-158), (cx+46, base-60), (cx-46, base-60)], fill=255)  # dress
    d.rectangle([cx-20, base-60, cx-10, base-8], fill=255); d.rectangle([cx+10, base-60, cx+20, base-8], fill=255)
    im = im.filter(ImageFilter.GaussianBlur(3))
    return np.asarray(im, np.float32)[..., None] / 255
GIRL = girl_layer()

def text_layer(lines, font, size, color=(225, 220, 205), spacing=1.35, y_off=0):
    f = ImageFont.truetype(font, size)
    im = Image.new("L", (W, H), 0); d = ImageDraw.Draw(im)
    total = len(lines) * size * spacing
    y = (H - total) / 2 + y_off
    for ln in lines:
        w = d.textlength(ln, font=f)
        d.text(((W - w) / 2, y), ln, font=f, fill=255)
        y += size * spacing
    glow = np.asarray(im.filter(ImageFilter.GaussianBlur(6)), np.float32) / 255
    a = np.asarray(im, np.float32) / 255
    return a[..., None], glow[..., None], np.array(color, np.float32)

T = {
  "t1": text_layer(["Каждую ночь", "ровно в 3:17"], SERIF, 54),
  "t2": text_layer(["в старом доме", "поёт ребёнок"], SERIF, 54),
  "t3": text_layer(["Её видно", "только в отражениях"], SERIF, 54),
  "q":  text_layer(["«Девочка моя.", "Дом тебя позвал»"], SERIF_I, 50, (210, 195, 160)),
  "title": text_layer(["ТАЙНА", "СТАРОГО ДОМА"], SERIF_B, 82, (235, 228, 210), 1.25, -30),
  "sub": text_layer(["короткометражный фильм"], SERIF_I, 30, (170, 160, 140), 1, 120),
}

def fade(t, a, b, fin=0.8, fout=0.8):
    if t < a or t > b: return 0.0
    return min(1, (t - a) / fin, (b - t) / fout)

def clock_layer(t):
    im = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(im)
    cx, cy, R = W // 2, 200, 118
    d.rectangle([cx-160, cy-160, cx+160, cy+400], fill=(38, 24, 14), outline=(70, 46, 26), width=6)
    # pendulum (starts swinging at 11s)
    ang = 0.0 if t < 11 else 0.28 * math.sin(2*math.pi*(t-11)/1.0) * min(1, (t-11)/1.2)
    px, py = cx, cy + R + 10
    bx, by = px + 190*math.sin(ang), py + 190*math.cos(ang)
    d.line([px, py, bx, by], fill=(150, 120, 60), width=5)
    d.ellipse([bx-28, by-28, bx+28, by+28], fill=(170, 135, 60), outline=(110, 85, 40), width=3)
    d.ellipse([cx-R, cy-R, cx+R, cy+R], fill=(196, 186, 160), outline=(90, 70, 40), width=8)
    for i in range(60):
        a = math.radians(i * 6); l = 18 if i % 5 == 0 else 7
        d.line([cx + (R-12)*math.sin(a), cy - (R-12)*math.cos(a),
                cx + (R-12-l)*math.sin(a), cy - (R-12-l)*math.cos(a)],
               fill=(40, 30, 20), width=4 if i % 5 == 0 else 2)
    for a_deg, ln, wd in [((3+17/60)*30, 70, 9), (17*6, 112, 5)]:
        a = math.radians(a_deg)
        d.line([cx, cy, cx + ln*math.sin(a), cy - ln*math.cos(a)], fill=(20, 15, 10), width=wd)
    d.ellipse([cx-9, cy-9, cx+9, cy+9], fill=(20, 15, 10))
    f = ImageFont.truetype(SERIF, 34)
    s = "3:17"; d.text((cx + 200, cy - 20), s, font=f, fill=(160, 140, 110))
    return np.asarray(im, np.float32)

ff = subprocess.Popen(
    ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
     "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", OUT + ".wav",
     "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "24", "-preset", "medium",
     "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT],
    stdin=subprocess.PIPE)

SCHED = [("t1", 2.6, 7.4), ("t2", 15.2, 19.2), ("t3", 19.6, 23.6),
         ("q", 23.9, 25.4), ("title", 28.4, 37.2), ("sub", 30.0, 37.2)]

for i in range(N):
    t = i / FPS
    flick = 1 + 0.06*math.sin(t*23.1) * math.sin(t*7.3) + rng.normal(0, 0.02)
    frame = bg.copy()
    frame += WINDOW * (0.6 + 0.4*math.sin(t/3)) * fade(t, 0.5, 8.2, 2, 1) * 1.0
    frame += WINDOW * fade(t, 15, 27.2, 1.5, 0.6) * 0.8
    ca = fade(t, 7.8, 15.2, 1.0, 0.8)
    if ca > 0:
        frame = frame * (1 - ca*0.9) + clock_layer(t) * ca * 0.85
    for key, a, b in SCHED:
        al = fade(t, a, b, 1.0 if key != "title" else 2.0, 0.9)
        if al <= 0: continue
        m, g, c = T[key]
        if key == "title":  # slow push-in
            s = 1 + 0.03 * (t - a) / (b - a)
            im = Image.fromarray((m[..., 0]*255).astype(np.uint8)).resize((int(W*s), int(H*s)), Image.BICUBIC)
            ox, oy = (im.width - W)//2, (im.height - H)//2
            m = np.asarray(im.crop((ox, oy, ox+W, oy+H)), np.float32)[..., None] / 255
            g = np.asarray(Image.fromarray((m[..., 0]*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(8)), np.float32)[..., None]/255
        frame = frame * (1 - m*al) + c * m * al + c * g * al * 0.35
    # knock flashes
    for kt in KNOCKS:
        if kt <= t < kt + 0.12:
            frame += 120 * (1 - (t - kt) / 0.12)
    # child silhouette appears in the window pane for a moment (t3 section)
    sa = fade(t, 21.2, 22.6, 0.25, 0.5)
    if sa > 0:
        frame = frame * (1 - GIRL * sa * 0.85)
    frame = frame * flick
    frame = frame * vign + grains[i % 6]
    # global fade in/out
    frame *= min(1, t / 1.0, max(0, (DUR - t) / 1.5))
    ff.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())

ff.stdin.close(); ff.wait()
print("done", ff.returncode)
