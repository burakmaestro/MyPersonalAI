from openai import OpenAI
from modules.memory_manager import (
    query_memory, query_long_term, add_to_memory, query_personal_info
)
from modules.emotion_engine import detect_emotion, empathic_response
import re
import random

client = OpenAI()

def extract_personal_info(text):
    """Kullanıcıdan kişisel bilgi çıkarır."""
    info = {}
    # Ad
    match = re.search(r"\bbenim adım\s+(\w+)", text, re.I)
    if match:
        info["user_name"] = match.group(1).capitalize()
    # Çocuk sayısı
    match = re.search(r"(\d+)\s+(çocuğum|çocuklarım var)", text, re.I)
    if match:
        info["child_count"] = int(match.group(1))
    # İş
    match = re.search(r"(ben|çalışıyorum|işim)\s+(.*)", text, re.I)
    if match:
        info["job"] = match.group(2).strip().capitalize()
    return info

def generate_response(user_input):
    """Echo AI yanıt üretir, hafızayı ve duyguyu günceller."""
    try:
        # --- Kısa dönem hafıza
        short_memory = query_memory(limit=10)
        short_context = "\n".join([f"{m['role']}: {m['text']}" for m in short_memory]) \
            if short_memory else "Geçmiş bilgi bulunamadı."

        # --- Uzun dönem hafıza
        long_memory = query_long_term()
        long_context = "\n".join([
            f"{m.get('role')}: {m.get('text', m.get('value',''))}" 
            for m in long_memory
        ]) if long_memory else "Önemli geçmiş bilgi bulunamadı."

        # --- Kişisel bilgiler
        user_name = query_personal_info("user_name")
        name_greeting = f"Merhaba {user_name}, " if user_name else ""

        # --- Duygusal analiz
        emotion_info = detect_emotion(user_input)
        emo_reply = empathic_response(user_input, emotion_info["emotion"])

        # --- GPT mesajları
        messages = [
            {
                "role": "system",
                "content": f"""
Sen Echo AI'sın. Kullanıcının kişisel bilgilerini, geçmiş konuşmalarını ve duygusal bağlamını hatırlıyorsun.
Kullanıcı: {user_name if user_name else 'Bilinmiyor'}
Uzun hafıza:
{long_context}
Kısa hafıza:
{short_context}
Son kullanıcı duygusu: {emotion_info['emotion']}
"""
            },
            {"role": "user", "content": user_input}
        ]

        # --- GPT yanıt üret
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        assistant_reply = response.choices[0].message.content

        # --- Kişisel bilgileri otomatik kaydet
        personal_info = extract_personal_info(user_input)
        for key, value in personal_info.items():
            add_to_memory("user", key=key, value=value, category="personal_info")

        # --- Hafızayı güncelle
        add_to_memory("user", user_input)
        add_to_memory("assistant", assistant_reply)

        # --- Empatik ek yanıt
        full_reply = f"{assistant_reply}\n\n({emo_reply})"

        return full_reply

    except Exception as e:
        return f"[HATA] Sohbet oluşturulamadı: {e}"
