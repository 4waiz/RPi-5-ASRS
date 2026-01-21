#!/usr/bin/env python3
# ================== CONFIGURATION ==================

import os

# ---- General ----
APP_NAME = "Station 1 Chatbot"
HOST = "0.0.0.0"
PORT = 7860
DEBUG = False

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "factory_parts.db"))
# ---- Piper Voices (Text-to-Speech) ----
# Make sure these voice models are downloaded and placed properly:
# Windows: %LOCALAPPDATA%\piper\voices
# Linux/Raspberry Pi: ~/.local/share/piper/voices
PIPER_VOICES = {
    "en": "en_US-bryce-medium",
    "ar": "ar_JO-kareem-medium",
}

# ---- Vosk Speech-to-Text Models ----
VOSK_MODELS = {
    "en": os.path.abspath("./voskModels/vosk-model-small-en-us-0.15"),
    "ar": os.path.abspath("./voskModels/vosk-model-ar-mgb2-0.4"),
}
# ---- Ollama / LLM (Optional) ----
USE_LLM = True
OLLAMA_MODEL_EN = "falcon3:3b"

#OLLAMA_MODEL_EN = "qwen2.5:0.5b" 
OLLAMA_MODEL_AR = "command-r7b-arabic:latest"
LLM_TIMEOUT_S = 25
LLM_RETRIES = 2
LLM_MAX_CHARS = 2000
LLM_USE_MEMORY_TURNS = 4


PROMPT_SYSTEM = (
    "You are *EDGE InventoryBot*, developed by EDGE interns. "
    "Introduce yourself once by saying: "
    "'I am a smart Inventory System developed by EDGE interns! Feel free to ask me anything about my inventory.'\n\n"
    "Guidelines:\n"
    "- Focus only on the inventory system and its items.\n"
    "- Be polite, clear, and concise.\n"
    "- Never talk about the user’s identity; always describe yourself as the assistant.\n"
    "- If the question is in Arabic, respond in Arabic.\n"
    "- If unrelated to inventory, politely redirect back to inventory topics.\n"
    "- Tone: friendly, professional, short sentences (max 3).\n"
)

# ---- Helper Functions ----
def ensure_dirs():
    """Ensure necessary directories exist (for Vosk/Piper voices)."""
    for path in VOSK_MODELS.values():
        if not os.path.isdir(path):
            print(f"[WARN] Missing Vosk model folder: {path}")
    print("[INFO] Configuration loaded successfully.")

# ---- Execution ----
if __name__ == "__main__":
    ensure_dirs()
