# main.py (F9 ile sesli modlu)

import os
import re
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import speech_recognition as sr
import keyboard  # F9 dinleme için

from modules.weather import get_weather
from modules.news import get_top_headlines
from modules.wikipedia_tools import get_wikipedia_summary
from modules.math_engine import calculate_expression
from modules.image_generator import generate_image
from modules.chat_engine import generate_response
from modules.calendar_manager import add_event, list_events, get_upcoming_events
from modules.habit_tracker import add_habit, mark_habit_done, get_habits, get_habit_streak
from modules.learning_manager import add_learning, list_learnings, get_learning_summary
from modules.advanced_chat import generate_advanced_response
from modules.tts_engine import enqueue_speech, run_speech_queue

# --- Load .env ---
load_dotenv()

# --- Mikrofon ve Recognizer ---
recognizer = sr.Recognizer()
mic = sr.Microphone()

# --- Async input ---
async def ainput(prompt: str = "") -> str:
    print(prompt, end="", flush=True)
    loop = asyncio.get_event_loop()
    return (await loop.run_in_executor(None, input)).strip()

# --- Sesli dinleme ---
async def listen():
    """Mikrofon ile sesli giriş alır"""
    with mic as source:
        print("🎤 Konuşun...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio, language="tr-TR")
        print(f"🧑 Siz (sesli): {text}")
        return text
    except sr.UnknownValueError:
        print("⚠️ Sizi anlayamadım.")
        return None
    except sr.RequestError as e:
        print(f"⚠️ Google Speech API hatası: {e}")
        return None

# --- F9 tuşu ile sesli mod ---
async def f9_listener():
    while True:
        if keyboard.is_pressed("f9"):
            spoken_text = await listen()
            if spoken_text:
                response = generate_advanced_response(spoken_text)
                print("Eleni:", response)
            await asyncio.sleep(0.5)  # tuş spam engeli
        await asyncio.sleep(0.1)

# --- Başlatma Mesajı ---
print("🤖 Eleni Başlatıldı. ('çık' yazarak çıkabilirsiniz')")
print("💬 Yazmak için yazın veya F9 tuşuna basarak sesli konuşun.")

# --- Ana Döngü ---
async def main_loop():
    # TTS kuyruğunu arka planda başlat
    asyncio.create_task(run_speech_queue())
    # F9 dinleyiciyi başlat
    asyncio.create_task(f9_listener())

    while True:
        user_input = await ainput("\n🧑 Siz: ")

        if user_input.lower() == "çık":
            print("👋 Görüşürüz! Yakında tekrar konuşuruz.")
            enqueue_speech("Görüşürüz! Yakında tekrar konuşuruz.")
            break

        # --- Görsel ---
        if user_input.lower().startswith(("görsel oluştur:", "resim çiz:")):
            prompt = user_input.split(":", 1)[1].strip()
            print("🎨 Görsel hazırlanıyor...")
            result = generate_image(prompt)
            print("Eleni:", result)
            enqueue_speech("Görsel oluşturuldu, kontrol edebilirsiniz.")
            continue

        # --- Hava durumu ---
        if "hava durumu" in user_input.lower() or "hava nasıl" in user_input.lower():
            match = re.search(r"(?:hava durumu|hava nasıl)\s+([a-zA-ZçÇğĞıİöÖşŞüÜ\s]+)", user_input.lower())
            city = match.group(1).strip().title() if match else None
            result = get_weather(city) if city else "Hangi şehrin hava durumunu öğrenmek istersiniz?"
            print("Eleni:", result)
            enqueue_speech(result)
            continue

        # --- Wikipedia ---
        if any(k in user_input.lower() for k in ["wikipedia", "nedir", "kimdir", "hakkında bilgi ver"]):
            query = re.sub(r"(wikipedia|nedir|kimdir|hakkında bilgi ver)", "", user_input, flags=re.IGNORECASE).strip()
            result = get_wikipedia_summary(query) if query else "Hangi konu hakkında bilgi almak istersiniz?"
            print("Eleni:", result)
            enqueue_speech(result)
            continue

        # --- Haberler ---
        if "haber" in user_input.lower():
            query = None
            if "haberler " in user_input.lower():
                query = user_input.lower().split("haberler ", 1)[1].strip()
            result = get_top_headlines(query=query)
            print("Eleni:", result)
            enqueue_speech("Haberler hazır, ekrandan kontrol edebilirsiniz.")
            continue

        # --- Matematik ---
        if any(op in user_input for op in ["+", "-", "*", "/", "kaç eder", "hesapla"]):
            expr = re.sub(r"[^0-9+\-*/().]", "", user_input)
            result = calculate_expression(expr)
            print("Eleni:", result)
            enqueue_speech(f"Sonuç: {result}")
            continue

        # --- Calendar ---
        if user_input.lower().startswith(("etkinlik ekle:", "event add:")):
            try:
                parts = user_input.split(":", 1)[1].strip().split("-", 1)
                if len(parts) == 2:
                    name = parts[0].strip()
                    dt_str = parts[1].strip()
                    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
                    result = add_event(name, dt)
                else:
                    result = "Lütfen etkinlik adı ve tarihi yazın: Etkinlik - YYYY-MM-DD HH:MM"
            except Exception as e:
                result = f"Hata: {e}"
            print("Eleni:", result)
            enqueue_speech(result)
            continue

        if user_input.lower() in ["etkinliklerimi göster", "list events"]:
            events = list_events()
            result = "\n".join(events)
            print("Eleni:", result)
            enqueue_speech("Etkinlikler listelendi.")
            continue

        if user_input.lower() in ["yaklaşan etkinlikler", "upcoming events"]:
            result = get_upcoming_events()
            print("Eleni:", result)
            enqueue_speech("Yaklaşan etkinlikler listelendi.")
            continue

        # --- Habit ---
        if user_input.lower().startswith(("alışkanlık ekle:", "habit add:")):
            habit_name = user_input.split(":", 1)[1].strip()
            result = add_habit(habit_name)
            print("Eleni:", result)
            enqueue_speech(result)
            continue

        if user_input.lower().startswith(("alışkanlığı yaptım:", "habit done:")):
            habit_name = user_input.split(":", 1)[1].strip()
            result = mark_habit_done(habit_name)
            print("Eleni:", result)
            enqueue_speech(result)
            continue

        if user_input.lower() in ["alışkanlıklarımı göster", "habit list"]:
            habits_list = get_habits()
            result = "\n".join(habits_list)
            print("Eleni:", result)
            enqueue_speech("Alışkanlıklar listelendi.")
            continue

        if user_input.lower().startswith(("alışkanlık serisi:", "habit streak:")):
            habit_name = user_input.split(":", 1)[1].strip()
            result = get_habit_streak(habit_name)
            print("Eleni:", result)
            enqueue_speech(f"{habit_name} serisi {result}")
            continue

        # --- Learning ---
        if user_input.lower().startswith(("öğreniyorum:", "learning add:")):
            topic = user_input.split(":", 1)[1].strip()
            result = add_learning(topic)
            print("Eleni:", result)
            enqueue_speech(result)
            continue

        if user_input.lower() in ["öğrendiklerimi göster", "learning list"]:
            learnings = list_learnings()
            result = "\n".join(learnings)
            print("Eleni:", result)
            enqueue_speech("Öğrendikleriniz listelendi.")
            continue

        if user_input.lower() in ["özet ver", "learning summary"]:
            summary = get_learning_summary()
            print("Eleni:", summary)
            enqueue_speech("Özet hazır, ekrandan kontrol edebilirsiniz.")
            continue

        # --- Genel Chat ---
        response = generate_advanced_response(user_input)
        print("Eleni:", response)

# --- Async Döngü Başlat ---
if __name__ == "__main__":
    asyncio.run(main_loop())
