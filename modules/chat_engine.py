from openai import OpenAI
import os

# API key .env dosyasından alınır
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_response(user_input):
    """OpenAI ile kullanıcıya cevap üretir."""
    try:
        if not user_input.strip():
            return "Lütfen bir mesaj yazın."

        # GPT'ye mesajları hazırla
        messages = [
            {"role": "system", "content": "Sen Echo adında bir yardımcı asistansın. Kullanıcıyla doğal bir dilde sohbet et."},
            {"role": "user", "content": user_input}
        ]

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"[HATA] Chat sorgusu başarısız: {e}"
