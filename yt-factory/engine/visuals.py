"""Фон сцены: ваш клип / фото (с медленным наездом) или фирменный градиент канала.

Случайные стоковые кадры движок не подставляет: фон берётся только из
assets/ проекта (то, что вы одобрили) либо генерируется в стиле бренда.
"""
from .common import run

GRADE = "eq=contrast=1.06:saturation=0.92:gamma=0.97"


def grain(fps):
    return f"noise=alls=7:allf=t,vignette=angle=PI/4.2,fps={fps},format=yuv420p"


def scene_clip(scene, idx, length, w, h, fps, brand, assets_dir, out, fast=False):
    asset = scene.get("asset")
    preset = ["-preset", "ultrafast" if fast else "medium",
              "-crf", "26" if fast else "16"]
    move = scene.get("move", "in")  # in | out | left | right
    if asset:
        src = assets_dir / asset
        fit = (scene.get("shot") or {}).get("fit", "cover")
        if src.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp") and fit == "contain":
            # архивное/малое фото: в рамке поверх размытой копии, медленный наезд.
            # Рамка — в полосе 12–55% высоты, НАД субтитрами (57–72%): текст не ложится на лицо.
            frames = int(length * fps) + 1
            bw, bh = int(w * 0.82) // 2 * 2, int(h * 0.43) // 2 * 2
            vf = (f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
                  f"boxblur=24:2,eq=brightness=-0.18:saturation=0.7[bg];"
                  f"[0:v]scale={bw}:{bh}:force_original_aspect_ratio=decrease,"
                  f"pad=iw+12:ih+12:6:6:color=0xF2E6C8[fg];"
                  f"[bg][fg]overlay=(W-w)/2:{int(h * 0.12)}+({bh}-h)/2,"
                  f"zoompan=z='1+0.05*on/{frames}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':"
                  f"d={frames}:s={w}x{h}:fps={fps},{GRADE},{grain(fps)}")
            cmd = ["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", src,
                   "-t", f"{length:.3f}", "-filter_complex", vf]
        elif src.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
            frames = int(length * fps) + 1
            z = {"in": f"1+0.10*on/{frames}", "out": f"1.10-0.10*on/{frames}"}.get(move, "1.08")
            x = {"left": f"(iw-iw/zoom)*(1-on/{frames})",
                 "right": f"(iw-iw/zoom)*on/{frames}"}.get(move, "(iw-iw/zoom)/2")
            vf = (f"scale={w*2}:{h*2}:force_original_aspect_ratio=increase,"
                  f"crop={w*2}:{h*2},zoompan=z='{z}':x='{x}':y='(ih-ih/zoom)/2':"
                  f"d={frames}:s={w}x{h}:fps={fps},{GRADE},{grain(fps)}")
            cmd = ["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", src,
                   "-t", f"{length:.3f}", "-vf", vf]
        else:
            vf = (f"scale={int(w*1.08)}:{int(h*1.08)}:force_original_aspect_ratio=increase,"
                  f"crop={w}:{h}:x='(iw-ow)*t/{length:.3f}':y='(ih-oh)/2',"
                  f"{GRADE},{grain(fps)}")
            cmd = ["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", src,
                   "-t", f"{length:.3f}", "-an", "-vf", vf]
    else:
        c = brand["colors"]["bg"]
        # каждая сцена — свой ракурс градиента (seed/позиции), палитра одна
        x0, y0 = [(0, 0), (w, 0), (w // 2, h), (0, h)][idx % 4]
        x1, y1 = w - x0, h - y0
        src = (f"gradients=s={w}x{h}:r={fps}:d={length:.3f}:"
               f"c0=0x{c[0][1:]}:c1=0x{c[1][1:]}:c2=0x{c[2][1:]}:c3=0x{c[3][1:]}:"
               f"nb_colors=4:x0={x0}:y0={y0}:x1={x1}:y1={y1}:speed=0.012:seed={idx * 7 + 3}")
        cmd = ["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", src,
               "-vf", f"{GRADE},{grain(fps)}"]
    run(cmd + ["-r", str(fps), "-pix_fmt", "yuv420p", "-c:v", "libx264", *preset, out])
    return out
