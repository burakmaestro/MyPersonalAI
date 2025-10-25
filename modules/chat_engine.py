from openai import OpenAI
from modules.memory_manager import query_memory, add_to_memory

client = OpenAI()

def generate_response(user_input):
    """Kullanıcıdan gelen girdiye GPT yanıtı üretir."""
    try:
        # Hafızadan geçmiş bağlamı al
        memory_docs = query_memory(user_input)
        memory_context = "\n".join(memory_docs) if memory_docs else "Geçmiş bilgi bulunamadı."

        # GPT'ye mesajları hazırla
        messages = [
            {"role": "system", "content": f"""
Sen Echo adında bir yapay zekâ asistansın.
Kullanıcının geçmiş konuşmalarını hatırlarsın ve ona göre kişisel, doğal bir dilde konuşursun.
Geçmiş bağlam:
{memory_context}
"""}, 
            {"role": "user", "content": user_input}
        ]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        assistant_reply = response.choices[0].message.content

        # Hafızayı güncelle
        add_to_memory("user", user_input)
        add_to_memory("assistant", assistant_reply)

        return assistant_reply
    except Exception as e:
        return f"[HATA] Sohbet oluşturulamadı: {e}"
