#!/usr/bin/env python3
# ============================================================
# FastAPI backend for Inventory Chatbot (LLM + STT + TTS)
# ============================================================

import os
import sys
import tempfile
import re
import traceback
import io

# --- START OF CRITICAL PATH FIX ---
backend_dir = os.path.dirname(os.path.abspath(__file__))
ai_assistant_dir = os.path.join(backend_dir, "AIAssistant")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir) 
os.chdir(ai_assistant_dir)
# --- END OF CRITICAL PATH FIX ---

from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydub import AudioSegment
import uvicorn

from AIAssistant.inventory import is_inventory_query, answer_inventory_question
from AIAssistant.llm import llm_reply
from AIAssistant.stt import transcribe_audio
from AIAssistant.tts import piper_tts_to_wav

app = FastAPI(title="EDGE Inventory Chatbot")

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Language Detection ----------------
ARABIC_RE = re.compile(r'[\u0600-\u06FF]')
def detect_lang(text: str) -> str:
    if not text:
        return "en"
    return "ar" if ARABIC_RE.search(text) else "en"

# ---------------- Chat Endpoint ----------------
@app.post("/api/chat")
async def chat_endpoint(
    message: str = Form(...),
    speak: bool = Form(True),
):
    try:
        lang = detect_lang(message)
        out = llm_reply(message, history=[])
        reply_text, reply_lang = out if isinstance(out, tuple) else (str(out), lang)

        if is_inventory_query(message):
            reply_text = answer_inventory_question(message)
            reply_lang = lang

        audio_url = None
        if speak:
            text_to_speak = reply_text
            
            if reply_lang == 'ar':
                cleaned_text = re.sub(r'[^\u0621-\u064A\s]', '', reply_text)
                text_to_speak = cleaned_text
                print(f"[TTS] Final (Raw) Arabic String for TTS: '{text_to_speak}'")
            
            # --- START OF FIX ---
            elif reply_lang == 'en':
                # Clean English text: remove asterisks, newlines, quotes, etc.
                cleaned_text = re.sub(r'["\*_\n\(\)\[\]]', ' ', reply_text)
                # Replace multiple spaces with a single space
                cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
                text_to_speak = cleaned_text
                print(f"[TTS] Final (Cleaned) English String for TTS: '{text_to_speak}'")
            # --- END OF FIX ---

            err, wav_path = piper_tts_to_wav(text_to_speak, reply_lang)
            
            if err:
                print("[TTS] error:", err)
            elif wav_path:
                audio_url = f"/api/audio/{os.path.basename(wav_path)}"
        
        return {"reply": reply_text, "lang": reply_lang, "audio_url": audio_url}

    except Exception as e:
        print("[/api/chat] 500:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ---------------- Voice Input Endpoint ----------------
@app.post("/api/voice")
async def voice_endpoint(
    audio: UploadFile,
    speak: bool = Form(True),
    lang: str = Form("ar")
):
    transcription_wav_path = None
    try:
        audio_data = await audio.read()
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_data))
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
            transcription_wav_path = tmp_wav.name
            audio_segment.export(transcription_wav_path, format="wav")

        text = transcribe_audio(transcription_wav_path, lang_code=lang)
        reply_lang = detect_lang(text)

        if is_inventory_query(text):
            reply_text = answer_inventory_question(text)
        else:
            out = llm_reply(text, history=[])
            reply_text, reply_lang = out if isinstance(out, tuple) else (str(out), reply_lang)

        audio_url = None
        if speak:
            text_to_speak = reply_text
            
            if reply_lang == 'ar':
                cleaned_text = re.sub(r'[^\u0621-\u064A\s]', '', reply_text)
                text_to_speak = cleaned_text
                print(f"[TTS] Final (Raw) Arabic String for TTS: '{text_to_speak}'")

            # --- START OF FIX ---
            elif reply_lang == 'en':
                # Clean English text: remove asterisks, newlines, quotes, etc.
                cleaned_text = re.sub(r'["\*_\n\(\)\[\]]', ' ', reply_text)
                # Replace multiple spaces with a single space
                cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
                text_to_speak = cleaned_text
                print(f"[TTS] Final (Cleaned) English String for TTS: '{text_to_speak}'")
            # --- END OF FIX ---

            err, wav_path = piper_tts_to_wav(text_to_speak, reply_lang)
            
            if err:
                print("[TTS] error:", err)
            elif wav_path:
                audio_url = f"/api/audio/{os.path.basename(wav_path)}"

        return JSONResponse({
            "text": text,
            "reply": reply_text,
            "lang": reply_lang,
            "audio_url": audio_url
        })

    except Exception as e:
        print(f"[/api/voice] 500 Error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing audio: {e}")

    finally:
        if transcription_wav_path and os.path.exists(transcription_wav_path):
            os.remove(transcription_wav_path)

# ---------------- Serve Generated Audio ----------------
@app.get("/api/audio/{filename}")
async def serve_audio(filename: str):
    path = os.path.join(tempfile.gettempdir(), filename)
    if os.path.exists(path):
        return FileResponse(path, media_type="audio/wav")
    return JSONResponse({"error": "File not found"}, status_code=404)


# ---------------- Run ----------------
if __name__ == "__main__":
    print(f"--- AI Assistant Server ---")
    print(f"Current working directory: {os.getcwd()}")
    uvicorn.run("app_aiassistant:app", host="0.0.0.0", port=8000, reload=True)