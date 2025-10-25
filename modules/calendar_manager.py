from datetime import datetime
from modules.memory_manager import add_to_memory, query_long_term

def add_event(title, date_time):
    """
    Yeni etkinlik ekler.
    - title: Etkinlik adı
    - date_time: datetime objesi
    """
    event_data = {
        "title": title,
        "date_time": date_time.isoformat(),
        "created_at": datetime.now().isoformat()
    }
    add_to_memory("user", key="event", value=event_data, category="calendar")
    return f"Etkinlik eklendi: '{title}' ({date_time.strftime('%Y-%m-%d %H:%M')})"

def list_events(day=None):
    """
    Etkinlikleri listeler.
    - day: datetime objesi (opsiyonel, sadece o günün etkinlikleri)
    """
    events = query_long_term(category="calendar")
    result = []

    for e in events:
        e_val = e.get("value", {})
        event_time = datetime.fromisoformat(e_val.get("date_time"))
        if day and (event_time.date() != day.date()):
            continue
        result.append(f"{e_val.get('title')} — {event_time.strftime('%Y-%m-%d %H:%M')}")
    
    return result if result else ["Etkinlik bulunamadı."]

def get_upcoming_events():
    """
    Zamanı gelen veya gelecek 24 saatteki etkinlikleri döndürür.
    """
    now = datetime.now()
    events = query_long_term(category="calendar")
    upcoming = []

    for e in events:
        e_val = e.get("value", {})
        event_time = datetime.fromisoformat(e_val.get("date_time"))
        if 0 <= (event_time - now).total_seconds() <= 86400:  # 24 saat içinde
            upcoming.append(f"{e_val.get('title')} — {event_time.strftime('%Y-%m-%d %H:%M')}")

    return upcoming
