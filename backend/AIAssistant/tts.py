#!/usr/bin/env python3
# ================== Piper Text-to-Speech Service (Library Version) ==================

import os
import tempfile
from .config import PIPER_VOICES
from piper.voice import PiperVoice
import soundfile as sf
import numpy as np

# Global cache to hold loaded voice models so we don't reload them
_PIPER_VOICES_CACHE = {}

def _piper_default_dirs():
    """Return possible Piper voice directories."""
    return [
        os.path.expandvars(r"%LOCALAPPDATA%\piper\voices"),  # Windows
        os.path.expanduser("~/.local/share/piper/voices"),   # Linux / RPi
        os.path.join(os.getcwd(), "voices"),                 # 'voices' folder in current dir
        os.getcwd(),                                         # current dir
    ]

def _guess_piper_paths(voice_tag):
    """Locate ONNX + JSON files for a given Piper voice tag."""
    onnx = voice_tag + ".onnx"
    jsn = voice_tag + ".onnx.json"

    for base in _piper_default_dirs():
        if not base or not os.path.isdir(base):
            continue
        mp = os.path.join(base, onnx)
        cp = os.path.join(base, jsn)
        if os.path.isfile(mp) and os.path.isfile(cp):
            return mp, cp
    return None, None

def _get_piper_voice(voice_tag: str):
    """Loads a Piper voice model once and caches it."""
    if voice_tag in _PIPER_VOICES_CACHE:
        return _PIPER_VOICES_CACHE[voice_tag]

    model_path, config_path = _guess_piper_paths(voice_tag)
    if not (model_path and config_path):
        print(f"Could not find model files for {voice_tag}")
        return None
    
    try:
        print(f"[TTS] Loading Piper voice: {voice_tag}")
        # The model will now load the MODIFIED .json file
        voice = PiperVoice.load(model_path, config_path=config_path)
        _PIPER_VOICES_CACHE[voice_tag] = voice
        return voice
    except Exception as e:
        print(f"Error loading Piper voice {voice_tag}: {e}")
        return None


def piper_tts_to_wav(text: str, lang_code: str = "en"):
    """
    Convert text → WAV audio file using the piper-python library directly.
    Returns (error_message or None, wav_path or None).
    """
    if not text.strip():
        return "Empty text provided.", None

    voice_tag = PIPER_VOICES.get(lang_code, PIPER_VOICES["en"])
    voice = _get_piper_voice(voice_tag)
    
    if not voice:
        return f"❌ Piper voice '{voice_tag}' not found or failed to load.", None

    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav_path = tmp.name
            
            with sf.SoundFile(wav_path, 'w', samplerate=voice.config.sample_rate, channels=1, subtype='PCM_16') as wav_file:
                
                # --- REVERTED TO THE SIMPLEST CALL ---
                # This will use the speed defined in the .json file
                for chunk in voice.synthesize(text):
                    audio_bytes = chunk.audio_int16_bytes 
                    int_array = np.frombuffer(audio_bytes, dtype=np.int16)
                    wav_file.write(int_array)
            
            return None, wav_path
            
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        return f"❌ Piper synthesis error::\n{err_msg}", None