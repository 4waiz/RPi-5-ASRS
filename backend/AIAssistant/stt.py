#!/usr/bin/env python3

#!/usr/bin/env python3
# ================== Whisper (Local) Speech-to-Text Service ==================

import os

# Try to import whisper, but handle gracefully if it fails on Windows
try:
    import whisper  # <-- The main import for local Whisper
    WHISPER_AVAILABLE = True
except Exception as e:
    print(f"Warning: Could not import whisper library: {e}")
    print("AI Assistant speech-to-text will be disabled.")
    WHISPER_AVAILABLE = False
    whisper = None

# We will cache the loaded model in memory
_WHISPER_MODEL = None
_WHISPER_MODEL_NAME = None

def _ensure_whisper_model(model_name: str):
    """Load the requested Whisper model once."""
    global _WHISPER_MODEL, _WHISPER_MODEL_NAME

    if not WHISPER_AVAILABLE:
        return

    # If the model is not loaded or the requested model name has changed
    if _WHISPER_MODEL is None or _WHISPER_MODEL_NAME != model_name:
        print(f"Loading Whisper model: {model_name}...")
        try:
            _WHISPER_MODEL = whisper.load_model(model_name)
            _WHISPER_MODEL_NAME = model_name
            print(f"Whisper model '{model_name}' loaded successfully.")
        except Exception as e:
            print(f"Error loading Whisper model {model_name}: {e}")
            print("Please ensure you have the model or that the name is correct.")
            print("Common models: 'tiny', 'base', 'small', 'medium', 'large'")
            _WHISPER_MODEL = None
            _WHISPER_MODEL_NAME = None
            
def transcribe_audio(wav_path: str, lang_code: str = "en", model_name: str = "base") -> str:
    """Transcribe WAV file -> text using local Whisper."""

    if not WHISPER_AVAILABLE:
        return "Error: Whisper library is not available on this system."

    # Step 1: Load the model (e.g., "base", "small", "medium")
    _ensure_whisper_model(model_name)

    if _WHISPER_MODEL is None:
        return "Error: Whisper model is not loaded."

    # Step 2: Set transcription options
    # We pass the language code to the transcribe function
    transcribe_options = {}
    if lang_code and lang_code != "multilingual":
        transcribe_options["language"] = lang_code

    # Step 3: Transcribe the file
    # Whisper handles resampling, mono conversion, etc., automatically.
    try:
        # The transcribe function takes the file path directly
        result = _WHISPER_MODEL.transcribe(audio=wav_path, **transcribe_options)
        
        # Step 4: Return the text
        return result.get("text", "").strip()
    
    except Exception as e:
        print(f"Error during Whisper transcription: {e}")
        return ""


if __name__ == "__main__":
    # --- IMPORTANT ---
    # Make sure you have a file named 'test_audio.wav' in the same directory.
    to_transcribe = "test_audio.wav"

    if os.path.exists(to_transcribe):
        print(f"Transcribing '{to_transcribe}' (lang='en', model='base')...")
        
        # --- You can change the model name here to test ---
        # Options: "tiny", "base", "small", "medium", "large"
        # "base" is a good first test. "small" is a good balance.
        text = transcribe_audio(to_transcribe, "en", model_name="base")
        
        print("\n--- Result ---")
        print(text)
    else:
        print(f"Error: Test file '{to_transcribe}' not found.")




'''
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
'''