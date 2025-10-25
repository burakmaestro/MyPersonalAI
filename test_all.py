import time
from modules.weather import get_weather
from modules.news import get_top_headlines
from modules.wikipedia_tools import get_wikipedia_summary
from modules.math_engine import calculate_expression
from modules.image_generator import generate_image
from modules.chat_engine import generate_response

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
    print(f"Hava durumu {city}: {get_weather(city)}")
    time.sleep(1)

# 3️⃣ Wikipedia özet
print_header("WIKIPEDIA ÖZET")
queries = ["Einstein", "Python", "Bitcoin"]
for q in queries:
    print(f"{q}: {get_wikipedia_summary(q)}")
    time.sleep(1)

# 4️⃣ Haberler (RSS)
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

print("\n✅ Tüm testler tamamlandı!")
