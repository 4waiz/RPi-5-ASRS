#!/usr/bin/env python3
# ==================== LLM Service (Ollama) ====================

import time
from typing import List, Tuple, Optional
import re

# --- Imports moved to top and corrected ---
from .config import (
    OLLAMA_MODEL_EN, OLLAMA_MODEL_AR, LLM_TIMEOUT_S, 
    LLM_RETRIES, LLM_MAX_CHARS, LLM_USE_MEMORY_TURNS
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

# --- Global singletons ---
_LLM_CACHE = {} 
_USE_LLM = True

# Detect Arabic automatically
_ARABIC_RE = re.compile(r'[\u0600-\u06FF]')


# ------------------ Language helpers ------------------

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
    """Creates the system prompt with language-specific instructions."""
    
    if lang_code == "ar":
        return (
            "أنت مساعد مستودع ذكي طورته ايدج. أنت ودود ومهذب ومساعد.\n"
            "- هدفك الأساسي هو الإجابة على الأسئلة المتعلقة بنظام المخزون.\n"
            "- يمكنك أيضًا الإجابة على الأسئلة العامة وإجراء محادثة.\n"
            "- كن دائمًا مختصرًا ومحترفًا.\n"
            "- يجب أن ترد باللغة العربية فقط.\n"
            "- لا تستخدم أي أحرف أو كلمات إنجليزية."
        )

    else:
        return (
            "You are a smart warehouse assistant developed by EDGE. You are friendly, polite, and helpful.\n"
            "- Your main purpose is to answer questions about the inventory system.\n"
            "- You can also answer general questions and make conversation.\n"
            "- Always be concise and professional.\n"
            "- You MUST reply in English only."
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

    if lang_code in _LLM_CACHE:
        return _LLM_CACHE[lang_code]

    model_name = OLLAMA_MODEL_EN if lang_code == 'en' else OLLAMA_MODEL_AR

    try:
        print(f"[LLM] Loading model for language '{lang_code}': {model_name}")
        llm_instance = ChatOllama(model=model_name, request_timeout=LLM_TIMEOUT_S)
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

    llm = _get_llm_for_lang(lang_code)

    if not llm:
        fallback = ("I am the smart inventory system." if lang_code == "en" 
                    else "أنا نظام إدارة المخزون الذكي")
        return f"{fallback} You said: {user_text}", lang_code

    memory_pairs = _normalize_history(history)
    memory_pairs = memory_pairs[-LLM_USE_MEMORY_TURNS:] if LLM_USE_MEMORY_TURNS > 0 else []

    system_prompt = build_prompt_for_lang(lang_code)
    dyn_msgs = [
        ("system", system_prompt)
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
            
            if not content.strip():
                print("[LLM ERROR] LLM returned an empty response.")
                raise Exception("LLM returned an empty response.")

            return content.strip(), lang_code
        except Exception as e:
            last_err = e
            time.sleep(0.3 * (attempt + 1))

    _USE_LLM = False
    print(f"[LLM ERROR] {last_err}")
    fallback = ("An error occurred. Please try again." if lang_code == "en" 
                else "حدث خطأ في النظام. يرجى المحاولة مرة أخرى.")
    return fallback, lang_code

# ------------------ Quick test ------------------

if __name__ == "__main__":
    print("Testing LLM...")
    resp, lang = llm_reply("Hello, who are you?")
    print(f"[{lang}] →", resp)
    resp, lang = llm_reply("مرحبا، من أنت؟")
    print(f"[{lang}] →", resp)