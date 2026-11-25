import sys, wave
import numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
w = wave.open(sys.argv[1]); sr = w.getframerate()
a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
for pair in sys.argv[2:]:
    t0, t1 = map(float, pair.split("-"))
    segs, _ = m.transcribe(a[int(t0*sr):int(t1*sr)], language="en", word_timestamps=True,
                           condition_on_previous_text=False, no_speech_threshold=None, log_prob_threshold=None)
    print("==", pair)
    for s in segs:
        print(f"[{s.start+t0:.2f}]", " ".join(f"{x.word.strip()}@{x.start+t0:.2f}" for x in s.words))
