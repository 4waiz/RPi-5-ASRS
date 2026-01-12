#!/usr/bin/env python3
# ================== Vosk Speech-to-Text Service ==================

import os
import json
import wave
import soundfile as sf
import numpy as np
import math
from vosk import Model, KaldiRecognizer
from .config import VOSK_MODELS
import tempfile

_VOSK_MODEL = None
_VOSK_LANG = None


def _ensure_vosk(lang_code: str):
    """Load the requested Vosk model once."""
    global _VOSK_MODEL, _VOSK_LANG
    model_dir = VOSK_MODELS.get(lang_code, VOSK_MODELS["en"])
    if _VOSK_MODEL is None or _VOSK_LANG != lang_code:
        if not os.path.isdir(model_dir):
            raise FileNotFoundError(f"Vosk model not found: {model_dir}")
        _VOSK_MODEL = Model(model_dir)
        _VOSK_LANG = lang_code


def transcribe_audio(wav_path: str, lang_code: str = "en") -> str:
    """Transcribe WAV file → text using Vosk."""
    _ensure_vosk(lang_code)

    data, sr = sf.read(wav_path)
    if hasattr(data, "ndim") and data.ndim > 1:
        data = data.mean(axis=1)  # stereo → mono

    if sr != 16000:
        ratio = 16000 / sr
        idx = (np.arange(math.floor(len(data) * ratio)) / ratio).astype(np.float64)
        data = np.interp(idx, np.arange(len(data)), data).astype("float32")
        sr = 16000

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name
    sf.write(tmp_path, data, sr, format="WAV")

    try:
        rec = KaldiRecognizer(_VOSK_MODEL, 16000)
        rec.SetWords(True)
        with wave.open(tmp_path, "rb") as wf:
            while True:
                buf = wf.readframes(4000)
                if len(buf) == 0:
                    break
                rec.AcceptWaveform(buf)
        return json.loads(rec.FinalResult()).get("text", "").strip()
    finally:
        os.remove(tmp_path)


if __name__ == "__main__":
    print(transcribe_audio("test_audio.wav", "en"))
