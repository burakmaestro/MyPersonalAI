from datetime import datetime, timedelta
from modules.memory_manager import add_to_memory, query_long_term

def add_reminder(text, remind_time=None):
    """
    Hatırlatıcı ekler.
    - text: hatırlatılacak mesaj
    - remind_time: datetime objesi, belirtilmezse 1 saat sonra varsayılan
    """
    if remind_time is None:
        remind_time = datetime.now() + timedelta(hours=1)
    
    reminder_data = {
        "text": text,
        "remind_time": remind_time.isoformat()
    }
    
    # Hatırlatıcıyı uzun hafızaya kaydet
    add_to_memory("user", key="reminder", value=reminder_data, category="reminders")
    
    return f"Hatırlatıcı kaydedildi: '{text}' → {remind_time.strftime('%Y-%m-%d %H:%M')}"

def get_due_reminders():
    """
    Zamanı gelen hatırlatıcıları döndürür.
    """
    reminders = query_long_term(category="reminders")
    due = []
    now = datetime.now()
    
    for r in reminders:
        r_time = datetime.fromisoformat(r.get("value", {}).get("remind_time"))
        if r_time <= now:
            due.append(r.get("value"))
    
    return due
