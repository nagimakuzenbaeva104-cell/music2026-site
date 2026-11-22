"""Озвучка через Piper (бесплатно, офлайн). Голоса скачиваются один раз в voices/."""
import subprocess

from .common import CACHE, VOICES, FactoryError, digest, run

HF = "https://huggingface.co/rhasspy/piper-voices/resolve/main"


def voice_path(model):
    """ru_RU-dmitri-medium -> voices/ru_RU-dmitri-medium.onnx (скачать при отсутствии)."""
    VOICES.mkdir(parents=True, exist_ok=True)
    onnx = VOICES / f"{model}.onnx"
    if onnx.exists() and (VOICES / f"{model}.onnx.json").exists():
        return onnx
    lang, name, quality = model.split("-")
    base = f"{HF}/{lang.split('_')[0]}/{lang}/{name}/{quality}/{model}"
    print(f"  скачиваю голос {model} ...")
    for suffix in (".onnx", ".onnx.json"):
        run(["curl", "-sfL", "--retry", "3", "-o", VOICES / f"{model}{suffix}", base + suffix])
    return onnx


def synth(text, voice_cfg):
    """Текст -> wav (кэшируется по тексту и настройкам голоса)."""
    if voice_cfg.get("engine", "piper") != "piper":
        raise FactoryError("Пока поддерживается только engine: piper")
    model = voice_path(voice_cfg["model"])
    key = digest(text, voice_cfg)
    out = CACHE / "tts" / f"{key}.wav"
    if out.exists():
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["python3", "-m", "piper", "-m", str(model), "-f", str(out),
           "--length-scale", str(voice_cfg.get("length_scale", 1.0)),
           "--sentence-silence", str(voice_cfg.get("sentence_silence", 0.2))]
    r = subprocess.run(cmd, input=text, text=True, capture_output=True)
    if r.returncode != 0 or not out.exists():
        raise FactoryError(f"Piper не смог озвучить: {text[:40]}...\n{r.stderr[-500:]}")
    return out
