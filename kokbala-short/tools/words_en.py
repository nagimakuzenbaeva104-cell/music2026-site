import sys, wave
import numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
w = wave.open(sys.argv[1]); sr = w.getframerate()
a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
segs, _ = m.transcribe(a, language="en", word_timestamps=True, condition_on_previous_text=False)
for s in segs:
    print(f"[{s.start:.2f}]", " ".join(f"{x.word.strip()}@{x.start:.2f}" for x in s.words))
