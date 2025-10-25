import time
from datetime import datetime
from modules.weather import get_weather
from modules.news import get_top_headlines
from modules.wikipedia_tools import get_wikipedia_summary
from modules.math_engine import calculate_expression
from modules.image_generator import generate_image
from modules.chat_engine import generate_response
from modules.calendar_manager import add_event, list_events, get_upcoming_events
from modules.habit_tracker import add_habit, mark_habit_done, get_habits, get_habit_streak
from modules.learning_manager import add_learning, list_learnings, get_learning_summary

def print_header(title):
    print("\n" + "="*10 + f" {title} " + "="*10)

# 1️⃣ Görsel oluşturma
print_header("GÖRSEL OLUŞTURMA")
prompts = ["güzel bir gün batımı", "uzayda bir şehir"]
for p in prompts:
    print(f"Prompt: {p}")
    print("Sonuç:", generate_image(p))
    time.sleep(1)

# 2️⃣ Hava durumu
print_header("HAVA DURUMU")
cities = ["İstanbul", "Ankara"]
for city in cities:
    print(f"{city}: {get_weather(city)}")
    time.sleep(1)

# 3️⃣ Wikipedia özet
print_header("WIKIPEDIA ÖZET")
queries = ["Einstein", "Python", "Bitcoin"]
for q in queries:
    print(f"{q}: {get_wikipedia_summary(q)}")
    time.sleep(1)

# 4️⃣ Haberler
print_header("HABERLER")
queries = [None, "teknoloji", "spor"]
for q in queries:
    label = "Tüm Haberler" if not q else q
    print(f"{label}: {get_top_headlines(query=q)}")
    time.sleep(1)

# 5️⃣ Matematik
print_header("MATEMATİK HESAPLAMA")
expressions = ["10 / 2", "2 + 5 * 3", "45 - 12"]
for expr in expressions:
    print(f"{expr} = {calculate_expression(expr)}")
    time.sleep(1)

# 6️⃣ Chat / Genel Sohbet
print_header("CHAT / GENEL SOHBET")
messages = ["Merhaba, nasılsın?", "Bugün nasılsın?", "Bana bir fıkra anlat"]
for msg in messages:
    print(f"Mesaj: {msg}")
    print("Cevap:", generate_response(msg))
    time.sleep(1)

# 7️⃣ Calendar / Etkinlikler
print_header("CALENDAR / ETKİNLİKLER")
events = [("Toplantı", "2025-10-25 15:00"), ("Alışveriş", "2025-10-25 18:00")]
for name, dt_str in events:
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")  # string → datetime
    print(f"Etkinlik ekle: {name} - {dt}")
    print(add_event(name, dt))
    time.sleep(1)

print("Tüm etkinlikler:", list_events())
print("Yaklaşan etkinlikler:", get_upcoming_events())

print("Tüm etkinlikler:", list_events())
print("Yaklaşan etkinlikler:", get_upcoming_events())

# 8️⃣ Habit tracker
print_header("HABIT TRACKER")
habits = ["Su iç", "Meditasyon yap"]
for habit in habits:
    print(f"Alışkanlık ekle: {habit}")
    print(add_habit(habit))
    time.sleep(1)

for habit in habits:
    print(f"Alışkanlık yaptım: {habit}")
    print(mark_habit_done(habit))
    time.sleep(1)

print("Alışkanlıklar:", get_habits())
for habit in habits:
    print(f"{habit} serisi:", get_habit_streak(habit))

# 9️⃣ Learning manager
print_header("LEARNING MANAGER")
topics = ["Python öğreniyorum", "AI araştırması"]
for topic in topics:
    print(f"Öğreniyorum: {topic}")
    print(add_learning(topic))
    time.sleep(1)

print("Öğrendiklerim:", list_learnings())
print("Özet:", get_learning_summary())

print("\n✅ Tüm testler tamamlandı!")
