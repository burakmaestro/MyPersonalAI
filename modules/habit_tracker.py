from datetime import datetime
from modules.memory_manager import add_to_memory, query_long_term

def add_habit(name, frequency="daily"):
    """
    Yeni alışkanlık ekler.
    - name: Alışkanlık adı
    - frequency: daily / weekly / monthly
    """
    habit_data = {
        "name": name,
        "frequency": frequency,
        "created_at": datetime.now().isoformat()
    }
    add_to_memory("user", key="habit", value=habit_data, category="habits")
    return f"Alışkanlık eklendi: '{name}' ({frequency})"

def mark_habit_done(name, date=None):
    """
    Alışkanlığı tamamlandı olarak işaretler.
    - date: tamamlandığı tarih (datetime objesi)
    """
    if date is None:
        date = datetime.now()
    done_data = {
        "name": name,
        "date": date.isoformat()
    }
    add_to_memory("user", key="habit_done", value=done_data, category="habits_done")
    return f"Alışkanlık tamamlandı olarak işaretlendi: {name}"

def get_habits(status=None):
    """
    Alışkanlık listesini döndürür.
    - status: "done", "pending", None
    """
    habits = query_long_term(category="habits")
    done_entries = query_long_term(category="habits_done")

    result = []
    for h in habits:
        name = h["value"]["name"]
        if status == "done" and not any(d["value"]["name"] == name for d in done_entries):
            continue
        if status == "pending" and any(d["value"]["name"] == name for d in done_entries):
            continue
        result.append(f"{name} ({h['value']['frequency']})")

    return result if result else ["Alışkanlık bulunamadı."]

def get_habit_streak(name):
    """
    Alışkanlık serisini döndürür (kaç gün arka arkaya yapıldı).
    """
    done_entries = query_long_term(category="habits_done")
    dates = sorted(
        [datetime.fromisoformat(d["value"]["date"]) for d in done_entries if d["value"]["name"] == name],
        reverse=True
    )
    if not dates:
        return f"{name} için tamamlanan alışkanlık yok."
    
    streak = 1
    for i in range(1, len(dates)):
        if (dates[i-1].date() - dates[i].date()).days == 1:
            streak += 1
        else:
            break
    return f"{name} alışkanlık serisi: {streak} gün"
