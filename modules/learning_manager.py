from datetime import datetime
from modules.memory_manager import add_to_memory, query_long_term

def add_learning(topic, notes=None):
    """
    Yeni öğrenme bilgisi ekler.
    - topic: Konu başlığı
    - notes: Opsiyonel açıklama / not
    """
    learning_data = {
        "topic": topic,
        "notes": notes if notes else "",
        "added_at": datetime.now().isoformat()
    }
    add_to_memory("user", key="learning", value=learning_data, category="learning")
    return f"Öğrenme bilgisi eklendi: {topic}"

def list_learnings():
    """
    Tüm öğrenilen bilgileri listeler.
    """
    learnings = query_long_term(category="learning")
    if not learnings:
        return ["Henüz öğrenilen bilgi yok."]
    return [f"{l['value']['topic']} — {l['value']['notes']}" for l in learnings]

def get_learning_summary():
    """
    Öğrenilen bilgilerin kısa bir özetini döndürür.
    """
    learnings = query_long_term(category="learning")
    if not learnings:
        return "Henüz öğrenilen bilgi yok."
    summary = [l['value']['topic'] for l in learnings]
    return "Öğrenilen konular: " + ", ".join(summary)
