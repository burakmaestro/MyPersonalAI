# modules/tts_engine.py

import os
import platform
import subprocess
import tempfile
from pathlib import Path
from openai import OpenAI

# OpenAI istemcisi (dotenv ile .env'den alıyor)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def speak(text: str):
    """
    OpenAI gpt-4o-mini-tts modelini kullanarak metni sese dönüştürür
    ve platforma uygun şekilde oynatır.
    """
    try:
        # 🧠 1. TTS sesi oluştur
        response = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=text
        )

        # 🗂️ 2. Geçici ses dosyasına kaydet (.wav)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(response.read())
            tmp_path = tmp_file.name

        # 🖥️ 3. İşletim sistemine göre sesi çal
        system = platform.system()

        if system == "Windows":
            # PowerShell kullanarak sesi çal
            subprocess.run([
                "powershell",
                "-c",
                f'(New-Object Media.SoundPlayer "{tmp_path}").PlaySync();'
            ])
        elif system == "Darwin":  # macOS
            subprocess.run(["afplay", tmp_path])
        else:  # Linux
            subprocess.run(["aplay", tmp_path])

        # 💨 4. Temizlik: dosyayı sil
        try:
            os.remove(tmp_path)
        except Exception:
            pass

    except Exception as e:
        print(f"⚠️ TTS hatası: {e}")
