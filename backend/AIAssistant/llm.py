#!/usr/bin/env python3
# ==================== LLM Service (Ollama + Gemma 3) ====================

import time
from typing import List, Tuple, Optional
import re
from .config import OLLAMA_MODEL_EN, OLLAMA_MODEL_AR

# Global singletons
_LLM_CACHE = {} 
_PROMPT_TMPL = None
_USE_LLM = True

# Limits and behavior
LLM_TIMEOUT_S = 25
LLM_RETRIES = 2
LLM_MAX_CHARS = 2000
LLM_USE_MEMORY_TURNS = 4  # number of (user,bot) pairs to keep

# Detect Arabic automatically
_ARABIC_RE = re.compile(r'[\u0600-\u06FF]')


# ------------------ Language helpers ------------------

# --- add this helper near the top of llm.py ---
def _normalize_history(history):
    """Return a list of (user, bot) strings; drop malformed items."""
    norm = []
    if not history:
        return norm
    for item in history:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            u, a = item[0], item[1]
            norm.append((str(u), str(a)))
    return norm


def detect_lang(text: str) -> str:
    """Return 'ar' if the message has Arabic letters, else 'en'."""
    if not text:
        return "en"
    return "ar" if _ARABIC_RE.search(text) else "en"


def build_prompt_for_lang(lang_code: str) -> str:
    """Language-specific style instructions."""
    if lang_code == "ar":
        return (
            "أنت مساعد افتراضي. يجب أن ترد باللغة العربية فقط. "
            "يجب أن تكون إجابتك بأكملها باللغة العربية. "
            "لا تستخدم أي أحرف أو كلمات أو أرقام إنجليزية. "
            "كن ودوداً ومختصراً."
        )

    else:
        return (
            "Reply only in English. "
            "Start your very first response with the exact greeting: 'I am a smart digital warehouse developed by EDGE. How can I help you' "
        )


# ------------------ Initialization ------------------

def _get_llm_for_lang(lang_code: str):
    """
    Loads and caches the correct Ollama model for the given language.
    Returns the ChatOllama instance.
    """
    global _LLM_CACHE, _USE_LLM
    if not _USE_LLM:
        return None

    # If model is already loaded, return it from the cache
    if lang_code in _LLM_CACHE:
        return _LLM_CACHE[lang_code]

    # Select the correct model name
    model_name = OLLAMA_MODEL_EN if lang_code == 'en' else OLLAMA_MODEL_AR

    try:
        from langchain_ollama import ChatOllama
        print(f"[LLM] Loading model for language '{lang_code}': {model_name}")
        llm_instance = ChatOllama(model=model_name, request_timeout=LLM_TIMEOUT_S)

        # Save the new model instance to the cache
        _LLM_CACHE[lang_code] = llm_instance
        return llm_instance
    except Exception as e:
        print(f"[LLM INIT ERROR] Failed to load model {model_name}: {e}")
        _USE_LLM = False
        return None

# ------------------ Core function ------------------

def _truncate(s: str, limit: int) -> str:
    s = (s or "").strip()
    if len(s) <= limit:
        return s
    return s[:limit] + "…"

def llm_reply(user_text: str,
              history: Optional[List[Tuple[str, str]]] = None) -> Tuple[str, str]:
    """
    Generate a reply using the correct language-specific Ollama model.
    Returns (response_text, lang_code).
    """
    global _USE_LLM
    lang_code = detect_lang(user_text)
    user_text = _truncate(user_text, LLM_MAX_CHARS)

    # Get the correct LLM for the detected language
    llm = _get_llm_for_lang(lang_code)

    # Fallback if LLM is unavailable
    if not llm:
        fallback = ("I am the smart inventory system." if lang_code == "en" 
                    else "أنا نظام إدارة المخزون الذكي")
        return f"{fallback} You said: {user_text}", lang_code

    # --- The rest of the logic remains the same ---
    from langchain.prompts import ChatPromptTemplate

    memory_pairs = _normalize_history(history)
    memory_pairs = memory_pairs[-LLM_USE_MEMORY_TURNS:] if LLM_USE_MEMORY_TURNS > 0 else []

    # Build prompt
    control_msg = build_prompt_for_lang(lang_code)
    dyn_msgs = [
        ("system", "You are a smart warehouse developed by EDGE. You are a friendly and concise assistant."),
        ("system", control_msg),
    ]
    for u, a in memory_pairs:
        dyn_msgs.append(("human", _truncate(u, 300)))
        dyn_msgs.append(("ai", _truncate(a, 300)))
    dyn_msgs.append(("human", "{input}"))

    prompt = ChatPromptTemplate.from_messages(dyn_msgs)
    msgs = prompt.format_messages(input=user_text)

    # Generate reply with retries
    last_err = None
    for attempt in range(LLM_RETRIES + 1):
        try:
            out = llm.invoke(msgs)
            content = getattr(out, "content", "") or ""
            return content.strip(), lang_code
        except Exception as e:
            last_err = e
            time.sleep(0.3 * (attempt + 1))

    _USE_LLM = False
    print(f"[LLM ERROR] {last_err}")
    fallback = ("An error occurred." if lang_code == "ar" 
                else "حدث خطأ في النظام.")
    return fallback, lang_code

# ------------------ Quick test ------------------

if __name__ == "__main__":
    print("Testing LLM...")
    resp, lang = llm_reply("Hello, who are you?")
    print(f"[{lang}] →", resp)
    resp, lang = llm_reply("مرحبا، من أنت؟")
    print(f"[{lang}] →", resp)
