# modules/tts_engine.py

import os
import platform
import subprocess
import tempfile
import asyncio
from pathlib import Path
from openai import OpenAI
from queue import Queue

# OpenAI istemcisi
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# TTS Queue
speech_queue = Queue()

def enqueue_speech(text: str):
    """Metni TTS kuyruğuna ekler"""
    speech_queue.put(text)

async def run_speech_queue():
    """Queue'daki metinleri sırayla çalar"""
    while True:
        if not speech_queue.empty():
            text = speech_queue.get()
            await speak_async(text)
        else:
            await asyncio.sleep(0.1)

async def speak_async(text: str):
    """Asenkron TTS sesi oluşturur ve oynatır"""
    try:
        # Geçici ses dosyası oluştur
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            speech_response = client.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice="alloy",
                input=text
            )
            tmp_file.write(speech_response.read())
            tmp_file_path = tmp_file.name

        # FFmpeg ile sesi oynat (subprocess asenkron değil, ama sırayla çalacak)
        subprocess.run(["ffplay", "-nodisp", "-autoexit", tmp_file_path],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Dosyayı temizle
        os.remove(tmp_file_path)

    except Exception as e:
        print(f"⚠️ TTS hatası: {e}")
