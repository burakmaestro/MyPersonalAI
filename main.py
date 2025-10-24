import os
import requests
from openai import OpenAI
from dotenv import load_dotenv
import wikipedia # Wikipedia için yeni kütüphane

# .env dosyasındaki ortam değişkenlerini yükle
load_dotenv()

# API anahtarlarını ortam değişkeninden al
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# API anahtarlarının mevcut olup olmadığını kontrol et
if not OPENAI_API_KEY:
    print("Hata: OPENAI_API_KEY ortam değişkeni ayarlanmamış.")
    print("Lütfen .env dosyanızı kontrol edin.")
    exit()
if not OPENWEATHER_API_KEY:
    print("Hata: OPENWEATHER_API_KEY ortam değişkeni ayarlanmamış.")
    print("Lütfen .env dosyanızı kontrol edin.")
    exit()

# OpenAI istemcisini başlat
client = OpenAI(api_key=OPENAI_API_KEY)

# Wikipedia için dili ayarla
wikipedia.set_lang("tr") # Türkçe Wikipedia kullanmak için

# Sohbet geçmişini saklamak için bir liste
messages = [
    {"role": "system", "content": "Sen yardımcı bir yapay zeka asistanısın. Görsel oluşturma, hava durumu bilgisi verme ve Wikipedia'dan bilgi çekme yeteneğin de var. Kullanıcı görsel istediğinde ona bir görsel oluşturabilirsin. Görsel oluşturma isteğini 'görsel oluştur:' veya 'resim çiz:' gibi ifadelerle anlamaya çalış. Hava durumu sorgularını 'hava durumu [şehir adı]' veya '[şehir adı] hava durumu' gibi ifadelerle anlamaya çalış. Wikipedia sorgularını ise 'wikipedia [konu]', '[konu] nedir/kimdir', '[konu] hakkında bilgi ver' gibi ifadelerle anlamaya çalış. Cevaplarını kısa ve net vermeye özen göster."},
]

print("Yapay zeka asistanınız aktif! Çıkmak için 'çık' yazın.")
print("Görsel oluşturmak için 'görsel oluştur: [açıklama]' yazabilirsiniz.")
print("Hava durumu öğrenmek için 'hava durumu [şehir adı]' yazabilirsiniz.")
print("Wikipedia'dan bilgi almak için 'wikipedia [konu]' veya '[konu] nedir?' yazabilirsiniz.")

# --- Hava Durumu Fonksiyonu (Öncekiyle aynı) ---
def get_weather(city_name):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city_name}&appid={OPENWEATHER_API_KEY}&units=metric&lang=tr"
    
    try:
        response = requests.get(complete_url)
        data = response.json()

        if data["cod"] == 200:
            main_data = data["main"]
            weather_data = data["weather"][0]
            
            temperature = main_data["temp"]
            feels_like = main_data["feels_like"]
            description = weather_data["description"]
            humidity = main_data["humidity"]
            wind_speed = data["wind"]["speed"]
            
            return (f"{city_name} şehrinde hava {description}, sıcaklık {temperature}°C (hissedilen "
                    f"{feels_like}°C). Nem oranı %{humidity}, rüzgar hızı {wind_speed} m/s.")
        elif data["cod"] == "404":
            return f"Üzgünüm, '{city_name}' şehrinin hava durumunu bulamadım. Yazımı kontrol edip tekrar dener misiniz?"
        else:
            return f"Hava durumu bilgisi alınırken bir hata oluştu: {data.get('message', 'Bilinmeyen hata')}"
    except requests.exceptions.RequestException as e:
        return f"Hava durumu servisine bağlanırken bir sorun oluştu: {e}"
    except Exception as e:
        return f"Hava durumu verileri işlenirken bir hata oluştu: {e}"

# --- Wikipedia Fonksiyonu (YENİ) ---
def get_wikipedia_summary(query, sentences=3):
    try:
        # En alakalı sayfayı bul
        page_title = wikipedia.search(query)
        if not page_title:
            return f"Üzgünüm, '{query}' hakkında Wikipedia'da bir sayfa bulamadım."
        
        # Sayfayı al ve özetini çek
        page = wikipedia.page(page_title[0], auto_suggest=False) # İlk bulunan sayfayı kullan
        summary = wikipedia.summary(page.title, sentences=sentences)
        return f"Wikipedia'dan alınan bilgi: {summary}"
    except wikipedia.exceptions.PageError:
        return f"Üzgünüm, '{query}' hakkında Wikipedia'da bir sayfa bulunamadı."
    except wikipedia.exceptions.DisambiguationError as e:
        return f"'{query}' için birden fazla sonuç var. Lütfen daha spesifik olun. Örneğin: {e.options[:3]}"
    except Exception as e:
        return f"Wikipedia bilgisi alınırken bir hata oluştu: {e}"


while True:
    user_input = input("Siz: ")
    if user_input.lower() == 'çık':
        print("Görüşmek üzere!")
        break
    
    # --- Görsel Oluşturma Kontrolü ---
    if user_input.lower().startswith("görsel oluştur:") or user_input.lower().startswith("resim çiz:"):
        prompt_for_image = user_input.split(":", 1)[1].strip()
        print(f"Asistan: '{prompt_for_image}' için görsel oluşturuluyor...")
        
        try:
            image_response = client.images.generate(
                model="dall-e-3",
                prompt=prompt_for_for_image, # Hata düzeltme: 'prompt_for_for_image' -> 'prompt_for_image'
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            image_url = image_response.data[0].url
            print("Asistan: İşte görseliniz: ")
            print(image_url)
            
        except Exception as e:
            print(f"Bir görsel oluşturma hatası oluştu: {e}")
            print("Lütfen daha sonra tekrar deneyin veya görsel açıklamasını basitleştirin.")
        
        continue
    
    # --- Hava Durumu Kontrolü ---
    hava_durumu_kelimeleri = ["hava durumu", "hava nasıl", "sıcaklık ne"]
    is_weather_request = False
    city = None
    
    for keyword in hava_durumu_kelimeleri:
        if keyword in user_input.lower():
            is_weather_request = True
            parts = user_input.lower().split(keyword, 1)
            if len(parts) > 1 and parts[1].strip():
                city_raw = parts[1].strip()
            elif parts[0].strip():
                city_raw = parts[0].strip()
            else:
                city_raw = None # Şehir bulunamadı
            
            if city_raw:
                # En son kelimeyi alıp dene, daha sofistike şehir ayrıştırma için LLM kullanılabilir
                city = city_raw.split(' ')[-1].capitalize() 
                
                # Türkçe karakter sorunları için basit bir düzeltme:
                if city.lower() == "i̇stanbul": city = "Istanbul"
                if city.lower() == "i̇zmir": city = "Izmir"
                # Diğer Türkçe şehirler için de eklenebilir
                
                weather_info = get_weather(city)
                print("Asistan:", weather_info)
            else:
                print("Asistan: Hangi şehrin hava durumunu öğrenmek istersiniz?")
            break 
    
    if is_weather_request:
        continue

    # --- Wikipedia Kontrolü (YENİ) ---
    wikipedia_kelimeleri = ["wikipedia", "nedir", "kimdir", "hakkında bilgi ver"]
    is_wikipedia_request = False
    query = None

    for keyword in wikipedia_kelimeleri:
        if keyword in user_input.lower():
            is_wikipedia_request = True
            if user_input.lower().startswith("wikipedia "):
                query = user_input.lower().split("wikipedia ", 1)[1].strip()
            elif " hakkında bilgi ver" in user_input.lower():
                query = user_input.lower().split(" hakkında bilgi ver")[0].strip()
            elif " nedir" in user_input.lower():
                query = user_input.lower().split(" nedir")[0].strip()
            elif " kimdir" in user_input.lower():
                query = user_input.lower().split(" kimdir")[0].strip()
            
            if query:
                wiki_info = get_wikipedia_summary(query)
                print("Asistan:", wiki_info)
            else:
                print("Asistan: Hangi konu hakkında Wikipedia bilgisi almak istersiniz?")
            break
    
    if is_wikipedia_request:
        continue

    # --- Normal Sohbet İşlemi ---
    messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        
        assistant_response = response.choices[0].message.content
        print("Asistan:", assistant_response)
        
        messages.append({"role": "assistant", "content": assistant_response})

    except Exception as e:
        print(f"Bir sohbet hatası oluştu: {e}")
        print("Lütfen daha sonra tekrar deneyin veya farklı bir soru sorun.")