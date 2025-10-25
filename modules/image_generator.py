import os
from dotenv import load_dotenv
from openai import OpenAI

# .env dosyasını yükle
load_dotenv()

# API anahtarını al
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_image(prompt):
    """DALL·E 3 ile görsel oluşturur ve URL döndürür."""
    try:
        image = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        return image.data[0].url
    except Exception as e:
        return f"Görsel oluşturma başarısız: {e}"
