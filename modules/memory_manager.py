import os
import json
from pathlib import Path
from datetime import datetime

# Hafıza dosyaları
BASE_DIR = Path(__file__).parent / "../data/echo_memory_db"
BASE_DIR.mkdir(parents=True, exist_ok=True)

SHORT_TERM_FILE = BASE_DIR / "short_term.json"
MONTHLY_DIR = BASE_DIR / "monthly"
MONTHLY_DIR.mkdir(exist_ok=True)

# Short-term dosya yoksa oluştur
if not SHORT_TERM_FILE.exists():
    SHORT_TERM_FILE.write_text("[]", encoding="utf-8")

# --- Helper Fonksiyonlar ---
def load_memory(file_path):
    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except Exception:
        return []

def save_memory(file_path, data):
    file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def get_monthly_file():
    month_file = MONTHLY_DIR / f"{datetime.now().strftime('%Y-%m')}.json"
    if not month_file.exists():
        month_file.write_text("[]", encoding="utf-8")
    return month_file

def load_long_term_memory():
    """Uzun süreli hafızayı tüm aylık dosyalardan yükler"""
    memories = []
    for file in MONTHLY_DIR.glob("*.json"):
        memories.extend(load_memory(file))
    return memories

# --- Hafıza Fonksiyonları ---
def add_to_memory(role, text=None, category="conversation", key=None, value=None):
    """
    Mesaj veya kişisel bilgiyi hafızaya ekler.
    category: conversation, personal_info, preference, fact, reminders
    """
    if key:  # Kişisel bilgi ekleme / güncelleme
        month_file = get_monthly_file()
        memory = load_memory(month_file)
        exists = False
        for item in memory:
            if item.get("key") == key:
                item["value"] = value
                exists = True
                break
        if not exists:
            memory.append({"role": role, "key": key, "value": value, "category": category})
        save_memory(month_file, memory)
    else:  # Konuşma ekleme (short-term + long-term monthly)
        # Short-term
        short_term = load_memory(SHORT_TERM_FILE)
        short_term.append({"role": role, "text": text, "category": category})
        short_term = short_term[-20:]  # son 20 mesaj
        save_memory(SHORT_TERM_FILE, short_term)

        # Long-term monthly
        month_file = get_monthly_file()
        memory = load_memory(month_file)
        memory.append({"role": role, "text": text, "category": category})
        save_memory(month_file, memory)

def query_memory(limit=10):
    """Short-term hafızadan son konuşmaları döndürür"""
    short_term = load_memory(SHORT_TERM_FILE)
    return short_term[-limit:]

def query_long_term(category=None):
    """Uzun süreli hafızadan verileri getirir. Category ile filtrelenebilir."""
    results = load_long_term_memory()
    if category:
        results = [m for m in results if m.get("category") == category]
    return results

def query_personal_info(key):
    """Long-term hafızadan kişisel bilgiyi getirir"""
    memories = query_long_term(category="personal_info")
    for item in reversed(memories):
        if item.get("key") == key:
            return item.get("value")
    return None

def get_conversation_summary(last_n=20):
    """Long-term hafızadan son n konuşmayı özet olarak döndürür"""
    memories = query_long_term(category="conversation")
    if not memories:
        return "Önceki konuşma bulunamadı."
    summary = "\n".join([f"{m['role']}: {m['text']}" for m in memories[-last_n:]])
    return summary
