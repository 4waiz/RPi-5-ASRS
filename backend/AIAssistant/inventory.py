#!/usr/bin/env python3
# ==================== Inventory Logic ====================

import os
import sqlite3
import difflib
from .config import DB_PATH

# Known objects
INVENTORY_OBJECTS = [
    "red body", "blue body", "green body",
    "drilled chassis", "chassis", "wheels",
]

# Common synonyms
SYNONYMS = {
    "blue car": "blue body", "blue cars": "blue body",
    "red car": "red body", "red cars": "red body",
    "green car": "green body", "green cars": "green body",
    "body blue": "blue body", "body red": "red body", "body green": "green body",
    "drilled frame": "drilled chassis", "frame drilled": "drilled chassis",
    "frame": "chassis", "rims": "wheels", "tyres": "wheels", "tires": "wheels",
}


# ------------------ Helpers ------------------

def db_exists() -> bool:
    return os.path.exists(DB_PATH)


def db_connect():
    """Open a connection to the inventory DB."""
    return sqlite3.connect(DB_PATH)


def canonicalize(text_low: str):
    """Normalize a user query to a known object if possible."""
    for k, v in SYNONYMS.items():
        if k in text_low:
            return v
    for obj in INVENTORY_OBJECTS:
        if obj in text_low:
            return obj
    return None


def best_match_item(text: str):
    """Find the closest match to an inventory item."""
    t = text.lower().strip()
    cand = canonicalize(t)
    if cand:
        return cand

    # Try fuzzy matching
    cands = difflib.get_close_matches(t, INVENTORY_OBJECTS, n=1, cutoff=0.6)
    if cands:
        return cands[0]

    # Try sliding word windows (e.g. “how many red” → “red body”)
    words = [w for w in t.replace("?", " ").replace(",", " ").split() if w.strip()]
    for span_len in range(min(3, len(words)), 0, -1):
        for i in range(0, len(words) - span_len + 1):
            span = " ".join(words[i:i + span_len])
            c2 = difflib.get_close_matches(span, INVENTORY_OBJECTS, n=1, cutoff=0.75)
            if c2:
                return c2[0]

    return None


def is_inventory_query(text: str) -> bool:
    """Detect if user query refers to inventory/stock."""
    t = text.lower()
    triggers = [
        "how many", "quantity", "qty", "count", "stock", "inventory",
        "in stock", "do we have", "left"
    ]
    return any(k in t for k in triggers) or (best_match_item(t) is not None)


# ------------------ DB logic ------------------

def get_quantity_from_db(item: str):
    """Fetch quantity of a given item from SQLite DB."""
    if not db_exists():
        return None

    conn = db_connect()
    try:
        cur = conn.cursor()
        cur.execute("SELECT quantity FROM inventory WHERE LOWER(object)=LOWER(?)", (item,))
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        conn.close()


# ------------------ Main entry ------------------

def answer_inventory_question(user_text: str) -> str:
    """Main entry for chatbot inventory responses."""
    item = best_match_item(user_text)
    if not item:
        return (
            "I couldn’t identify the item. Try asking about: "
            "red body, blue body, green body, drilled chassis, chassis, or wheels."
        )

    if not db_exists():
        return (
            "I don’t have access to the inventory database yet. "
            "Please run `python db_init.py` in the app folder to create `factory_parts.db`."
        )

    qty = get_quantity_from_db(item)
    if qty is None:
        return f"I couldn’t find '{item}' in the database."
    return f"We have {qty} units of {item} in stock."


# ------------------ Quick test ------------------

if __name__ == "__main__":
    print("Testing inventory module...")
    print(answer_inventory_question("how many red bodies do we have"))
    print(answer_inventory_question("كم عدد الإطارات"))
