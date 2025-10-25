import os
import re
from datetime import datetime
from dotenv import load_dotenv

# Modüller
from modules.weather import get_weather
from modules.news import get_top_headlines
from modules.wikipedia_tools import get_wikipedia_summary
from modules.math_engine import calculate_expression
from modules.image_generator import generate_image
from modules.chat_engine import generate_response
from modules.reminder_manager import add_reminder, get_due_reminders
from modules.todo_manager import add_task, list_tasks, complete_task

# Ortam değişkenlerini yükle
load_dotenv()

print("🤖 Echo başlatıldı. ('çık' yazarak çıkabilirsiniz.)")

while True:
    # Zamanı gelen hatırlatıcıları kontrol et
    due_reminders = get_due_reminders()
    for r in due_reminders:
        print(f"⏰ Hatırlatma: {r['text']} ({r['remind_time']})")

    user_input = input("\n🧑 Siz: ")

    if user_input.lower() == "çık":
        print("👋 Görüşürüz Burak! Yakında tekrar konuşuruz.")
        break

    # --- Hatırlatıcı ekleme ---
    if user_input.lower().startswith(("hatırlat:", "hatırlatıcı ekle:")):
        parts = user_input.split(":", 1)
        text = parts[1].strip() if len(parts) > 1 else "Hatırlatılacak şey"

        # Opsiyonel: zamanı ayırma (örn. "15:30")
        time_match = re.search(r"(\d{1,2}:\d{2})", text)
        remind_time = None
        if time_match:
            hour, minute = map(int, time_match.group(1).split(":"))
            now = datetime.now()
            remind_time = datetime(now.year, now.month, now.day, hour, minute)

        result = add_reminder(text, remind_time)
        print("Echo:", result)
        continue

    # --- Görev ekleme ---
    if user_input.lower().startswith(("görev ekle:", "yapılacak ekle:")):
        task_text = user_input.split(":", 1)[1].strip()
        result = add_task(task_text)
        print("Echo:", result)
        continue

    # --- Görevleri listeleme ---
    if user_input.lower() in ["görevlerimi göster", "yapılacakları göster"]:
        tasks_list = list_tasks()
        result = "\n".join(tasks_list) if tasks_list else "Görev bulunamadı."
        print("Echo:", result)
        continue

    # --- Görevi tamamlama ---
    if user_input.lower().startswith("görevi tamamla:"):
        task_text = user_input.split(":", 1)[1].strip()
        result = complete_task(task_text)
        print("Echo:", result)
        continue

    # --- Görsel oluşturma ---
    if user_input.lower().startswith(("görsel oluştur:", "resim çiz:")):
        prompt = user_input.split(":", 1)[1].strip()
        print("🎨 Görsel hazırlanıyor...")
        result = generate_image(prompt)
        print("Echo:", result)
        continue

    # --- Hava durumu ---
    if "hava durumu" in user_input.lower() or "hava nasıl" in user_input.lower():
        match = re.search(r"(?:hava durumu|hava nasıl)\s+([a-zA-ZçÇğĞıİöÖşŞüÜ\s]+)", user_input.lower())
        city = match.group(1).strip().title() if match else None
        if city:
            result = get_weather(city)
        else:
            result = "Hangi şehrin hava durumunu öğrenmek istersiniz?"
        print("Echo:", result)
        continue

    # --- Wikipedia ---
    if any(keyword in user_input.lower() for keyword in ["wikipedia", "nedir", "kimdir", "hakkında bilgi ver"]):
        query = re.sub(r"(wikipedia|nedir|kimdir|hakkında bilgi ver)", "", user_input, flags=re.IGNORECASE).strip()
        if query:
            result = get_wikipedia_summary(query)
        else:
            result = "Hangi konu hakkında bilgi almak istersiniz?"
        print("Echo:", result)
        continue

    # --- Haberler ---
    if "haber" in user_input.lower():
        query = None
        if "haberler " in user_input.lower():
            query = user_input.lower().split("haberler ", 1)[1].strip()
        result = get_top_headlines(query=query)
        print("Echo:", result)
        continue

    # --- Matematik ---
    if any(op in user_input for op in ["+", "-", "*", "/", "kaç eder", "hesapla"]):
        expr = re.sub(r"[^0-9+\-*/().]", "", user_input)
        result = calculate_expression(expr)
        print("Echo:", result)
        continue

    # --- Genel sohbet ---
    result = generate_response(user_input)
    print("Echo:", result)
