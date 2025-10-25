from datetime import datetime
from modules.memory_manager import add_to_memory, query_long_term

def add_task(task_text, due_time=None):
    """
    Yeni görev ekler.
    - task_text: görev açıklaması
    - due_time: datetime objesi (opsiyonel)
    """
    task_data = {
        "task": task_text,
        "due_time": due_time.isoformat() if due_time else None,
        "completed": False,
        "created_at": datetime.now().isoformat()
    }
    add_to_memory("user", key="task", value=task_data, category="tasks")
    return f"Görev eklendi: '{task_text}'"

def list_tasks(show_completed=False):
    """
    Tüm görevleri listeler.
    - show_completed: True ise tamamlanan görevler de gösterilir
    """
    tasks = query_long_term(category="tasks")
    result = []
    for t in tasks:
        t_val = t.get("value", {})
        if not show_completed and t_val.get("completed"):
            continue
        due = t_val.get("due_time") or "Tarih yok"
        status = "✔️" if t_val.get("completed") else "❌"
        result.append(f"{status} {t_val.get('task')} (Son tarih: {due})")
    return result

def complete_task(task_text):
    """
    Görevi tamamlandı olarak işaretler.
    """
    tasks = query_long_term(category="tasks")
    for t in tasks:
        t_val = t.get("value", {})
        if t_val.get("task").lower() == task_text.lower():
            t_val["completed"] = True
            add_to_memory("user", key="task", value=t_val, category="tasks")
            return f"Görev tamamlandı: '{task_text}'"
    return f"Görev bulunamadı: '{task_text}'"
