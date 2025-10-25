import os
import re
from dotenv import load_dotenv

# Modülleri içe aktar
from modules.weather import get_weather
from modules.news import get_top_headlines
from modules.wikipedia_tools import get_wikipedia_summary
from modules.math_engine import calculate_expression
from modules.image_generator import generate_image
from modules.chat_engine import generate_response

# Ortam değişkenlerini yükle
load_dotenv()

print("🤖 Echo AI Başlatıldı! ('çık' yazarak çıkabilirsiniz.)")

def extract_city(user_input):
    match = re.search(r"(?:hava durumu|hava nasıl)\s+([a-zA-ZçÇğĞıİöÖşŞüÜ\s]+)", user_input, re.IGNORECASE)
    return match.group(1).strip().title() if match else None

def extract_wiki_query(user_input):
    query = re.sub(r"(wikipedia|nedir|kimdir|hakkında bilgi ver)", "", user_input, flags=re.IGNORECASE).strip()
    return query if query else None

def extract_math_expression(user_input):
    expr = re.sub(r"[^0-9+\-*/().]", "", user_input)
    return expr if expr else None

while True:
    user_input = input("\n🧑 Siz: ").strip()
    if user_input.lower() == "çık":
        print("👋 Görüşürüz Burak! Yakında tekrar konuşuruz.")
        break

    lower_input = user_input.lower()

    # --- Görsel oluşturma ---
    if lower_input.startswith(("görsel oluştur:", "resim çiz:")):
        prompt = user_input.split(":", 1)[1].strip()
        result = generate_image(prompt) if prompt else "Lütfen görsel için bir açıklama girin."
        print("Echo:", result)
        continue

    # --- Hava durumu ---
    if "hava durumu" in lower_input or "hava nasıl" in lower_input:
        city = extract_city(user_input)
        result = get_weather(city) if city else "Hangi şehrin hava durumunu öğrenmek istersiniz?"
        print("Echo:", result)
        continue

    # --- Wikipedia ---
    if any(k in lower_input for k in ["wikipedia", "nedir", "kimdir", "hakkında bilgi ver"]):
        query = extract_wiki_query(user_input)
        result = get_wikipedia_summary(query) if query else "Hangi konu hakkında bilgi almak istersiniz?"
        print("Echo:", result)
        continue

    # --- Haberler ---
    if "haber" in lower_input:
        query = lower_input.split("haberler", 1)[1].strip() if "haberler" in lower_input else None
        result = get_top_headlines(query=query)
        print("Echo:", result)
        continue

    # --- Matematik ---
    if any(op in user_input for op in ["+", "-", "*", "/", "kaç eder", "hesapla"]):
        expr = extract_math_expression(user_input)
        result = calculate_expression(expr) if expr else "Lütfen geçerli bir matematik işlemi girin."
        print("Echo:", result)
        continue

    # --- Genel sohbet ---
    result = generate_response(user_input)
    print("Echo:", result)
