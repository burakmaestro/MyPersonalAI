# modules/advanced_chat.py

import re
from modules.wikipedia_tools import get_wikipedia_summary
from modules.news import get_top_headlines
from modules.chat_engine import generate_response
from modules.tts_engine import enqueue_speech

# Kullanıcı profili
USER_PROFILE = {
    "interests": ["Python", "Yapay Zeka", "Kitap okuma"],
    "habits": ["Spor", "Meditasyon"]
}

last_emotion = "neutral"

def analyze_emotion(text: str) -> str:
    """Kullanıcı mesajındaki duyguyu tek kelime ile tahmin eder"""
    prompt = f"Bu mesajdaki duyguyu tek kelime ile etiketle: {text}"
    emotion = generate_response(prompt)
    return emotion.lower().strip()

def generate_advanced_response(user_text: str) -> str:
    """Kısa, samimi ve kişiselleştirilmiş yanıt üretir ve TTS kuyruğuna ekler"""
    global last_emotion

    # Duygu analizi
    emotion = analyze_emotion(user_text)
    last_emotion = emotion

    # RAG: Wikipedia ve Haber özetleri (kısa)
    wiki_summary = get_wikipedia_summary(user_text)
    news_summary = get_top_headlines(user_text)

    # Kullanıcı profili ve duygu özetlenmiş şekilde
    profile_info = f"İlgi alanlarınız: {', '.join(USER_PROFILE['interests'])}."
    emotion_info = f"Duygu: {emotion}." if emotion != "neutral" else ""

    # Model promptu: kısa ve doğal yanıt
    prompt = (
        f"Sen samimi, arkadaş canlısı ve akıcı bir yapay zeka asistanısın.\n"
        f"{profile_info} {emotion_info}\n"
        f"Wiki özet: {wiki_summary}\n"
        f"Haber özeti: {news_summary}\n"
        f"Kullanıcı mesajı: {user_text}\n"
        f"Yanıtını kısa, samimi ve doğrudan ver. Tekrar ve aşırı detaydan kaçın."
    )

    # Yanıt üret
    response = generate_response(prompt)

    # Gereksiz tekrarları temizle
    response = re.sub(r'(\b' + re.escape(user_text.strip()) + r'\b)', '', response, flags=re.IGNORECASE).strip()

    # Sesli yanıtı kuyruğa ekle
    enqueue_speech(response)

    return response
