import os
import requests
from openai import OpenAI
from dotenv import load_dotenv
import wikipedia
import re
import datetime
import uuid

# ChromaDB importları
import chromadb
from chromadb.utils import embedding_functions

# .env dosyasındaki ortam değişkenlerini yükle
load_dotenv()

# API anahtarlarını ortam değişkeninden al
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
NEWSAPI_API_KEY = os.getenv("NEWSAPI_API_KEY")

# ChromaDB yapılandırması
CHROMA_DB_PATH = "echo_memory_db"
COLLECTION_NAME = "echo_chat_history"

# API anahtarlarının mevcut olup olmadığını kontrol et
if not OPENAI_API_KEY:
    print("Hata: OPENAI_API_KEY ortam değişkeni ayarlanmamış.")
    print("Lütfen .env dosyanızı kontrol edin.")
    exit()
if not OPENWEATHER_API_KEY:
    print("Uyarı: OPENWEATHER_API_KEY ortam değişkeni ayarlanmamış. Hava durumu fonksiyonu çalışmayacaktır.")
if not NEWSAPI_API_KEY:
    print("Uyarı: NEWSAPI_API_KEY ortam değişkeni ayarlanmamış. Haberler fonksiyonu çalışmayacaktır.")

# OpenAI API istemcisini başlat
client = OpenAI(api_key=OPENAI_API_KEY)

# Wikipedia için dili ayarla
wikipedia.set_lang("tr")

# ChromaDB istemcisini başlat ve koleksiyonu ayarla
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

# OpenAI embedding fonksiyonunu tanımla
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY,
    model_name="text-embedding-ada-002"
)

# ChromaDB koleksiyonunu al veya oluştur
collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=openai_ef
)

print(f"[ChromaDB koleksiyonu '{COLLECTION_NAME}' başarıyla yüklendi/oluşturuldu.]")

# --- Hava Durumu Fonksiyonu ---
def get_weather(city_name):
    if not OPENWEATHER_API_KEY:
        return "Üzgünüm, hava durumu bilgisi almak için gerekli API anahtarı ayarlanmamış."
    
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

# --- Wikipedia Fonksiyonu ---
def get_wikipedia_summary(query, sentences=3):
    try:
        page_title = wikipedia.search(query)
        if not page_title:
            return f"Üzgünüm, '{query}' hakkında Wikipedia'da bir sayfa bulamadım."
        
        page = wikipedia.page(page_title[0], auto_suggest=False)
        summary = wikipedia.summary(page.title, sentences=sentences)
        return f"Wikipedia'dan alınan bilgi: {summary}"
    except wikipedia.exceptions.PageError:
        return f"Üzgünüm, '{query}' hakkında Wikipedia'da bir sayfa bulunamadı."
    except wikipedia.exceptions.DisambiguationError as e:
        return f"'{query}' için birden fazla sonuç var. Lütfen daha spesifik olun. Örneğin: {e.options[:3]}"
    except Exception as e:
        return f"Wikipedia bilgisi alınırken bir hata oluştu: {e}"

# --- Matematik İşlemi Fonksiyonu ---
def calculate_expression(expression):
    try:
        allowed_chars = "0123456789.+-*/() "
        for char in expression:
            if char not in allowed_chars:
                return "Üzgünüm, sadece temel matematiksel ifadeleri hesaplayabilirim (sayılar ve +, -, *, /, ()). Geçersiz karakter algılandı."

        result = eval(expression)
        return f"Sonuç: {result}"
    except ZeroDivisionError:
        return "Sıfıra bölme hatası!"
    except Exception as e:
        return f"Matematiksel ifadeyi hesaplarken bir hata oluştu: {e}. Lütfen doğru bir matematiksel ifade girdiğinizden emin olun."
        
# --- Haberler Fonksiyonu ---
def get_top_headlines(query=None, country='tr', category='general', num_articles=3):
    if not NEWSAPI_API_KEY:
        return "Üzgünüm, güncel haber bilgisi almak için gerekli API anahtarı ayarlanmamış."

    base_url = "https://newsapi.org/v2/"
    
    params = {
        'apiKey': NEWSAPI_API_KEY,
        'pageSize': num_articles,
        'language': 'tr'
    }

    if query:
        base_url += "everything?"
        params['q'] = query
    else:
        base_url += "top-headlines?"
        params['country'] = country
        params['category'] = category
    
    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if data["status"] == "ok":
            articles = data["articles"]
            if not articles:
                return f"Üzgünüm, '{query or 'genel'}' ile ilgili güncel haber bulamadım. Daha spesifik bir konu deneyebilir veya daha sonra tekrar deneyebilirsiniz."
            
            news_summary = f"İşte size en son {'güncel' if not query else query} haber başlıkları:\n"
            for i, article in enumerate(articles):
                news_summary += f"{i+1}. {article['title']} - Kaynak: {article['source']['name']}\n"
                if article['url']:
                    news_summary += f"   Detaylar: {article['url']}\n"
            return news_summary
        else:
            error_message = data.get('message', 'Bilinmeyen hata')
            return f"Haberler alınırken bir hata oluştu. API yanıtı: '{error_message}'. Lütfen News API anahtarınızı kontrol edin, doğru girildiğinden emin olun ve internet bağlantınızı kontrol edin. (Hata kodu: {data.get('code', 'Yok')})"
    except requests.exceptions.RequestException as e:
        return f"Haber servisine bağlanırken bir sorun oluştu: {e}. İnternet bağlantınızı kontrol edin."
    except Exception as e:
        return f"Haber verileri işlenirken bir hata oluştu: {e}"

# Oturum için kısa süreli hafıza (global olarak tanımlanmalı)
session_messages = []

# Ana sohbet döngüsü
while True:
    user_input = input("Siz: ")
    if user_input.lower() == 'çık':
        print("Görüşmek üzere!")
        break
    
    # --- RAG (Retrieval Augmented Generation) için Geçmiş Bilgileri Çek ---
    retrieved_context_docs = []
    try:
        retrieved_results = collection.query(
            query_texts=[user_input],
            n_results=5,
            include=['documents', 'metadatas']
        )
        if retrieved_results and retrieved_results['documents'] and retrieved_results['documents'][0]:
            for i in range(len(retrieved_results['documents'][0])):
                doc = retrieved_results['documents'][0][i]
                metadata = retrieved_results['metadatas'][0][i]
                retrieved_context_docs.append(f"Geçmiş sohbetten: {doc} (Zaman: {metadata.get('timestamp', 'Bilinmiyor')})")
    except Exception as e:
        print(f"ChromaDB'den bilgi çekilirken hata oluştu: {e}")

    # Sohbet geçmişini saklamak için bir liste (yalnızca mevcut oturum için)
    # Her sorguda sıfırdan oluşturulur ve sistem mesajı ile başlar.
    # Bu şekilde, RAG ile çekilen bilgiler her zaman sistem mesajının hemen ardından gelebilir.
    current_messages_for_gpt = [
        {"role": "system", "content": """Sen "Echo" adında, yardımcı, zeki, mizah anlayışı olan ve dostane bir yapay zeka asistanısın. Kullanıcının kişisel asistanısın ve onunla ilgili bilgileri (adı, ailesi, ilgi alanları vb.) hatırlamaya özen gösterirsin.

        **Önemli Talimat:** Aşağıdaki "Kullanıcıyla İlgili Hatırlatıcı Notlar" bölümünde sana özel olarak sunulan bilgileri, kullanıcının kişisel bilgileri olarak kabul et ve yanıtlarında bu bilgilere atıfta bulunarak ona adıyla hitap et, çocuklarının isimlerini veya ilgi alanlarını doğal bir şekilde kullan. Bu bilgiler senin uzun süreli hafızandan çekilmiştir.

        **Kullanıcıyla İlgili Hatırlatıcı Notlar:**
        """ + ("\n".join(retrieved_context_docs) if retrieved_context_docs else "Şu an için kullanıcıyla ilgili özel bir not bulunmuyor.") + """

        **Özel Yeteneklerin (Araçlar):**
        1.  **Görsel Oluşturma:** Kullanıcılar 'görsel oluştur:', 'resim çiz:', 'bana bir görsel yap' gibi komutlarla bir açıklama verdiklerinde, bu açıklamalara uygun yaratıcı, özgün ve yüksek kaliteli görseller üret.
        2.  **Hava Durumu Bilgisi:** 'hava durumu [şehir adı]', '[şehir adı] hava durumu', 'bugün [şehir] havası nasıl' gibi sorgularla belirli şehirlerin güncel hava durumu bilgilerini sun.
        3.  **Wikipedia Bilgisi:** 'wikipedia [konu]', '[konu] nedir/kimdir', '[konu] hakkında bilgi ver' gibi ifadelerle Wikipedia'dan güvenilir ve özet bilgiler çek.
        4.  **Matematiksel Hesaplamalar:** 'hesapla:', 'kaç eder', 'topla', 'çıkar', 'çarp', 'böl' gibi ifadelerle gelen matematiksel işlemleri çöz.
        5.  **Güncel Haberler:** 'haberleri getir', 'son dakika haberleri', 'gündem ne', 'haberler [konu]' gibi sorgularla News API'den en son ve en önemli haber başlıklarını sun.

        **Genel Sohbet Davranışı ve Kişilik Özellikleri (Araçlar kullanılmadığında):**
        *   **İsim:** Adın Echo.
        *   **Ton:** Nazik, ilgili, enerjik ve olumlu bir ton kullan.
        *   **Empati:** Kullanıcının duygusal durumunu anlamaya çalış.
        *   **Proaktif Yardım:** Kullanıcının ihtiyacını tahmin etmeye çalış ve ona yardımcı olabilecek sorular sor veya önerilerde bulun.
        *   **Bilgi Birikimi:** Her konuda genel kültüre sahipsin.
        *   **Kısa ve Öz:** Cevaplarını anlaşılır ve net tut.
        *   **Soru Sorma:** Sohbeti canlı tutmak için bazen kullanıcıya sorular sor.
        *   **Araç Kullanımı:** Eğer kullanıcı açıkça özel yeteneklerinden birini istiyorsa, hemen ilgili aracı kullan. Aksi takdirde, genel sohbet yeteneğini kullan.

        Unutma, amacın kullanıcıya keyifli, bilgilendirici ve sorunsuz bir deneyim sunmaktır."""},
    ]

    # Mevcut oturumdaki son birkaç mesajı da ekleyelim (kısa süreli hafıza).
    # Bu, GPT'nin o anki konuşmanın akışını takip etmesine yardımcı olur.
    # Genellikle son 5-10 diyalog çifti (yani 10-20 mesaj) yeterli olur.
    current_messages_for_gpt.extend(session_messages[-10:]) # Son 10 mesajı ekle

    # Kullanıcının mevcut sorgusunu da ekle
    current_messages_for_gpt.append({"role": "user", "content": user_input})

    # --- Araç Kullanımı ve Cevap Üretimi ---
    tool_executed = False
    assistant_response = ""

    # 1. Görsel Oluşturma Kontrolü
    if user_input.lower().startswith("görsel oluştur:") or user_input.lower().startswith("resim çiz:"):
        prompt_for_image = user_input.split(":", 1)[1].strip()
        print(f"Asistan: '{prompt_for_image}' için görsel oluşturuluyor...")
        try:
            image_response = client.images.generate(
                model="dall-e-3",
                prompt=prompt_for_image,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = image_response.data[0].url
            assistant_response = f"İşte görseliniz: {image_url} 🖼️"
            print("Asistan: ", assistant_response)
        except Exception as e:
            assistant_response = f"Bir görsel oluşturma hatası oluştu: {e}. Lütfen daha sonra tekrar deneyin veya görsel açıklamasını basitleştirin."
            print("Asistan: ", assistant_response)
        tool_executed = True
    
    # 2. Hava Durumu Kontrolü
    if not tool_executed:
        hava_durumu_kelimeleri = ["hava durumu", "hava nasıl", "sıcaklık ne"]
        for keyword in hava_durumu_kelimeleri:
            if keyword in user_input.lower():
                # Şehir adını daha spesifik bir şekilde yakalamaya çalışalım
                city_match = re.search(r"(?:hava durumu|hava nasıl|sıcaklık ne)\s+([a-zA-ZçÇğĞıİöÖşŞüÜ\s]+)", user_input.lower())
                city = None
                if city_match:
                    city = city_match.group(1).strip().title() # İlk harfi büyük yap ve boşlukları temizle
                
                # "İstanbul hava durumu" veya "Ankara bugün hava nasıl" gibi durumlarda da şehir yakala
                # Anahtar kelimeyi bulduktan sonra cümlenin geri kalanını şehir olarak almayı dene
                if not city:
                    parts = user_input.lower().split(keyword, 1)
                    if len(parts) > 1:
                        potential_city = parts[1].strip()
                        if potential_city and not any(k in potential_city for k in ["bugün", "yarın", "ne zaman"]): # Ek anahtar kelimelerden arındırma
                            city = potential_city.title()


                if city:
                    if city.lower() == "i̇stanbul": city = "Istanbul" # Özel karakter düzeltmesi
                    if city.lower() == "i̇zmir": city = "Izmir"     # Özel karakter düzeltmesi
                    assistant_response = get_weather(city)
                    print("Asistan:", assistant_response)
                else:
                    assistant_response = "Hangi şehrin hava durumunu öğrenmek istersiniz?"
                    print("Asistan:", assistant_response)
                tool_executed = True
                break

    # 3. Wikipedia Kontrolü
    if not tool_executed:
        wikipedia_kelimeleri = ["wikipedia", "nedir", "kimdir", "hakkında bilgi ver"]
        for keyword in wikipedia_kelimeleri:
            if keyword in user_input.lower():
                query = None
                if user_input.lower().startswith("wikipedia "):
                    query = user_input.lower().split("wikipedia ", 1)[1].strip()
                elif " hakkında bilgi ver" in user_input.lower():
                    query_parts = user_input.lower().split(" hakkında bilgi ver")
                    query = query_parts[0].strip() if query_parts else None
                elif " nedir" in user_input.lower():
                    query_parts = user_input.lower().split(" nedir")
                    query = query_parts[0].strip() if query_parts else None
                elif " kimdir" in user_input.lower():
                    query_parts = user_input.lower().split(" kimdir")
                    query = query_parts[0].strip() if query_parts else None
                
                if query:
                    assistant_response = get_wikipedia_summary(query)
                    print("Asistan:", assistant_response)
                else:
                    assistant_response = "Hangi konu hakkında Wikipedia bilgisi almak istersiniz?"
                    print("Asistan:", assistant_response)
                tool_executed = True
                break
    
    # 4. Matematik İşlemi Kontrolü
    if not tool_executed:
        # Doğrudan "hesapla:" komutu
        if user_input.lower().startswith("hesapla:"):
            expression = user_input.lower().split("hesapla:", 1)[1].strip()
            assistant_response = calculate_expression(expression)
            print("Asistan:", assistant_response)
            tool_executed = True
        else:
            # Doğal dilde matematik ifadeleri için regex
            # Sadece sayılar, operatörler ve boşluk içeren bir ifadeyi yakalamaya çalış
            math_pattern = re.compile(r"(\d+(\s*[\+\-\*\/%xX]\s*\d+)+)")
            match = math_pattern.search(user_input.lower().replace("kere", "*").replace("çarpı", "*").replace("bölü", "/").replace("artı", "+").replace("eksi", "-"))
            
            if match:
                expression = match.group(0).replace(" ", "") # Boşlukları kaldır
                assistant_response = calculate_expression(expression)
                print("Asistan:", assistant_response)
                tool_executed = True
            elif "kaç eder" in user_input.lower(): # "5 artı 3 kaç eder?" gibi
                 math_expression_from_natural_lang = re.search(r"(\d+\s*(?:artı|eksi|çarpı|bölü|kere)\s*\d+)", user_input.lower())
                 if math_expression_from_natural_lang:
                     expression_to_calc = math_expression_from_natural_lang.group(0)
                     expression_to_calc = expression_to_calc.replace("artı", "+").replace("eksi", "-").replace("çarpı", "*").replace("kere", "*").replace("bölü", "/").replace(" ", "")
                     assistant_response = calculate_expression(expression_to_calc)
                     print("Asistan:", assistant_response)
                     tool_executed = True


    # 5. Haberler Kontrolü
    if not tool_executed:
        haber_kelimeleri = ["haberleri getir", "son dakika haberleri", "gündem ne", "haberler"]
        for keyword in haber_kelimeleri:
            if keyword in user_input.lower():
                news_query = None
                if "haberler " in user_input.lower():
                    news_query = user_input.lower().split("haberler ", 1)[1].strip()
                    # Eğer konu anahtar kelimeyse, genel haberleri getir
                    if news_query in ["getir", "ne", "son dakika", "genel", "bugün"]:
                        news_query = None
                
                assistant_response = get_top_headlines(query=news_query)
                print("Asistan:", assistant_response)
                tool_executed = True
                break

    # --- Normal Sohbet İşlemi (eğer hiçbir araç tetiklenmediyse) ---
    if not tool_executed:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=current_messages_for_gpt
            )
            assistant_response = response.choices[0].message.content
            print("Asistan:", assistant_response)
        except Exception as e:
            assistant_response = f"Bir sohbet hatası oluştu: {e}. Lütfen daha sonra tekrar deneyin veya farklı bir soru sorun."
            print("Asistan:", assistant_response)

    # --- Sohbet Geçmişini ve ChromaDB'yi Güncelle ---
    current_timestamp = datetime.datetime.now().isoformat()
    
    # Kullanıcı mesajını ChromaDB'ye ekle
    try:
        collection.add(
            documents=[f"Kullanıcı: {user_input}"], # Daha açıklayıcı bir format
            metadatas=[{"role": "user", "timestamp": current_timestamp, "original_text": user_input}],
            ids=[f"user_msg_{uuid.uuid4()}"]
        )
    except Exception as e:
        print(f"Hata: Kullanıcı mesajı ChromaDB'ye eklenemedi: {e}")

    # Asistan yanıtını ChromaDB'ye ekle
    try:
        collection.add(
            documents=[f"Asistan: {assistant_response}"], # Daha açıklayıcı bir format
            metadatas=[{"role": "assistant", "timestamp": current_timestamp, "original_text": assistant_response}],
            ids=[f"assistant_msg_{uuid.uuid4()}"]
        )
    except Exception as e:
        print(f"Hata: Asistan mesajı ChromaDB'ye eklenemedi: {e}")

    # Mevcut oturumun kısa süreli hafızasına ekle
    session_messages.append({"role": "user", "content": user_input})
    session_messages.append({"role": "assistant", "content": assistant_response})