import os
from openai import OpenAI
from dotenv import load_dotenv

# .env dosyasındaki ortam değişkenlerini yükle
load_dotenv()

# OpenAI API anahtarını ortam değişkeninden al
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# API anahtarının mevcut olup olmadığını kontrol et
if not OPENAI_API_KEY:
    print("Hata: OPENAI_API_KEY ortam değişkeni ayarlanmamış.")
    print("Lütfen .env dosyanızı kontrol edin ve API anahtarınızı doğru girdiğinizden emin olun.")
    exit() # Programı sonlandır

# OpenAI istemcisini başlat
client = OpenAI(api_key=OPENAI_API_KEY)

# Sohbet geçmişini saklamak için bir liste
messages = [
    {"role": "system", "content": "Sen yardımcı bir yapay zeka asistanısın. Kısa ve net cevaplar vermeye çalış."},
]

print("Yapay zeka asistanınız aktif! Çıkmak için 'çık' yazın.")

while True:
    user_input = input("Siz: ")
    if user_input.lower() == 'çık':
        print("Görüşmek üzere!")
        break
    
    # Kullanıcının mesajını sohbet geçmişine ekle
    messages.append({"role": "user", "content": user_input})

    try:
        # Sohbet tamamlaması isteği gönder
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Kullanılacak model. Diğer modeller için OpenAI dökümanlarına bakılabilir.
            messages=messages
        )
        
        # Asistanın yanıtını al
        assistant_response = response.choices[0].message.content
        print("Asistan:", assistant_response)
        
        # Asistanın yanıtını sohbet geçmişine ekle
        messages.append({"role": "assistant", "content": assistant_response})

    except Exception as e:
        print(f"Bir hata oluştu: {e}")
        print("Lütfen daha sonra tekrar deneyin veya farklı bir soru sorun.")