import pyttsx3
import io
import threading
import os

tts_engine = pyttsx3.init()
tts_lock = threading.Lock()



def text_to_speech(text: str) -> bytes:
    """Convert text to speech using pyttsx3, returns WAV bytes."""
    try:
        with tts_lock:
            temp_file = "tts_output.wav"
            tts_engine.save_to_file(text, temp_file)
            tts_engine.runAndWait()

            with open(temp_file, "rb") as f:
                audio_bytes = f.read()
            os.remove(temp_file)
            return audio_bytes
    except Exception as e:
        print(f"pyttsx3 TTS Error: {e}")
        return b""
