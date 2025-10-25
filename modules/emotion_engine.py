from textblob import TextBlob

def detect_emotion(text):
    """
    Basit duygusal analiz.
    TextBlob polarity değerine göre:
    - Negatif: 'üzgün'
    - Nötr: 'nötr'
    - Pozitif: 'mutlu'
    """
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity > 0.2:
        emotion = "mutlu"
    elif polarity < -0.2:
        emotion = "üzgün"
    else:
        emotion = "nötr"

    return {"emotion": emotion, "polarity": polarity}

def empathic_response(user_text, detected_emotion):
    """
    Kullanıcının duygusuna göre empatik yanıt oluşturur.
    """
    responses = {
        "mutlu": [
            "Ne güzel! Bu enerji bana da geçti.",
            "Harika, seni böyle görmek sevindirici!"
        ],
        "üzgün": [
            "Üzgün olduğunu duydum, istersen biraz konuşabiliriz.",
            "Bu durumu aşmana yardımcı olabilirim."
        ],
        "nötr": [
            "Anladım, biraz daha detay verir misin?",
            "Hmm, devam edelim o zaman."
        ]
    }

    import random
    return random.choice(responses.get(detected_emotion, ["Anladım."]))
