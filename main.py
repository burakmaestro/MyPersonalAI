import os
import re
import time
from datetime import datetime
from dotenv import load_dotenv
import speech_recognition as sr
from modules.weather import get_weather
from modules.news import get_top_headlines
from modules.wikipedia_tools import get_wikipedia_summary
from modules.math_engine import calculate_expression
from modules.image_generator import generate_image
from modules.chat_engine import generate_response
from modules.calendar_manager import add_event, list_events, get_upcoming_events
from modules.habit_tracker import add_habit, mark_habit_done, get_habits, get_habit_streak
from modules.learning_manager import add_learning, list_learnings, get_learning_summary

# OpenAI TTS
from openai import OpenAI

# --- Load .env ---
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# --- Sesli okuma ---
def speak(text: str):
    """OpenAI TTS (gpt-4o-mini-tts) ile sesi oluşturur ve FFmpeg ile çalar."""
    try:
        # Geçici ses dosyası oluştur
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            speech_response = client.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice="alloy",  # istersen "verse", "soft" veya "calm" gibi ses tonlarını da deneyebiliriz
                input=text
            )
            tmp_file.write(speech_response.read())
            tmp_file_path = tmp_file.name

        # FFmpeg ile sesi oynat
        subprocess.run(["ffplay", "-nodisp", "-autoexit", tmp_file_path],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Dosyayı temizle
        os.remove(tmp_file_path)

    except Exception as e:
        print(f"⚠️ TTS hatası: {e}")

# --- Mikrofon ile giriş ---
recognizer = sr.Recognizer()
mic = sr.Microphone()

def listen():
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

# --- Başlık ---
def print_header(title):
    print("\n" + "="*10 + f" {title} " + "="*10)

print("🤖 Echo AI Başlatıldı. ('çık' yazarak çıkabilirsiniz.)")
print("💬 Yazmak için yazın, sesli konuşmak için 'sesli' yazın.")

while True:
    user_input = input("\n🧑 Siz: ")

    if user_input.lower() == "çık":
        print("👋 Görüşürüz! Yakında tekrar konuşuruz.")
        speak("Görüşürüz! Yakında tekrar konuşuruz.")
        break

    if user_input.lower() == "sesli":
        spoken_text = listen()
        if spoken_text:
            user_input = spoken_text
        else:
            continue

    # --- Görsel ---
    if user_input.lower().startswith(("görsel oluştur:", "resim çiz:")):
        prompt = user_input.split(":", 1)[1].strip()
        print("🎨 Görsel hazırlanıyor...")
        result = generate_image(prompt)
        print("Echo:", result)
        speak("Görsel oluşturuldu, kontrol edebilirsiniz.")
        continue

    # --- Hava ---
    if "hava durumu" in user_input.lower() or "hava nasıl" in user_input.lower():
        match = re.search(r"(?:hava durumu|hava nasıl)\s+([a-zA-ZçÇğĞıİöÖşŞüÜ\s]+)", user_input.lower())
        city = match.group(1).strip().title() if match else None
        result = get_weather(city) if city else "Hangi şehrin hava durumunu öğrenmek istersiniz?"
        print("Echo:", result)
        speak(result)
        continue

    # --- Wikipedia ---
    if any(k in user_input.lower() for k in ["wikipedia", "nedir", "kimdir", "hakkında bilgi ver"]):
        query = re.sub(r"(wikipedia|nedir|kimdir|hakkında bilgi ver)", "", user_input, flags=re.IGNORECASE).strip()
        result = get_wikipedia_summary(query) if query else "Hangi konu hakkında bilgi almak istersiniz?"
        print("Echo:", result)
        speak(result)
        continue

    # --- Haberler ---
    if "haber" in user_input.lower():
        query = None
        if "haberler " in user_input.lower():
            query = user_input.lower().split("haberler ", 1)[1].strip()
        result = get_top_headlines(query=query)
        print("Echo:", result)
        speak("Haberler hazır, ekrandan kontrol edebilirsiniz.")
        continue

    # --- Matematik ---
    if any(op in user_input for op in ["+", "-", "*", "/", "kaç eder", "hesapla"]):
        expr = re.sub(r"[^0-9+\-*/().]", "", user_input)
        result = calculate_expression(expr)
        print("Echo:", result)
        speak(f"Sonuç: {result}")
        continue

    # --- Calendar ---
    if user_input.lower().startswith(("etkinlik ekle:", "event add:")):
        parts = user_input.split(":", 1)[1].strip().split("-", 1)
        if len(parts) == 2:
            name = parts[0].strip()
            dt_str = parts[1].strip()
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
            result = add_event(name, dt)
        else:
            result = "Lütfen etkinlik adı ve tarihi yazın: Etkinlik - YYYY-MM-DD HH:MM"
        print("Echo:", result)
        speak(result)
        continue

    if user_input.lower() in ["etkinliklerimi göster", "list events"]:
        events = list_events()
        result = "\n".join(events)
        print("Echo:", result)
        speak("Etkinlikler listelendi.")
        continue

    if user_input.lower() in ["yaklaşan etkinlikler", "upcoming events"]:
        result = get_upcoming_events()
        print("Echo:", result)
        speak("Yaklaşan etkinlikler listelendi.")
        continue

    # --- Habit ---
    if user_input.lower().startswith(("alışkanlık ekle:", "habit add:")):
        habit_name = user_input.split(":", 1)[1].strip()
        result = add_habit(habit_name)
        print("Echo:", result)
        speak(result)
        continue

    if user_input.lower().startswith(("alışkanlığı yaptım:", "habit done:")):
        habit_name = user_input.split(":", 1)[1].strip()
        result = mark_habit_done(habit_name)
        print("Echo:", result)
        speak(result)
        continue

    if user_input.lower() in ["alışkanlıklarımı göster", "habit list"]:
        habits_list = get_habits()
        result = "\n".join(habits_list)
        print("Echo:", result)
        speak("Alışkanlıklar listelendi.")
        continue

    if user_input.lower().startswith(("alışkanlık serisi:", "habit streak:")):
        habit_name = user_input.split(":", 1)[1].strip()
        result = get_habit_streak(habit_name)
        print("Echo:", result)
        speak(f"{habit_name} serisi {result}")
        continue

    # --- Learning ---
    if user_input.lower().startswith(("öğreniyorum:", "learning add:")):
        topic = user_input.split(":", 1)[1].strip()
        result = add_learning(topic)
        print("Echo:", result)
        speak(result)
        continue

    if user_input.lower() in ["öğrendiklerimi göster", "learning list"]:
        learnings = list_learnings()
        result = "\n".join(learnings)
        print("Echo:", result)
        speak("Öğrendikleriniz listelendi.")
        continue

    if user_input.lower() in ["özet ver", "learning summary"]:
        summary = get_learning_summary()
        print("Echo:", summary)
        speak("Özet hazır, ekrandan kontrol edebilirsiniz.")
        continue

    # --- Genel Chat ---
    result = generate_response(user_input)
    print("Echo:", result)
    speak(result)
