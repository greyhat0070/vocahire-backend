import pyttsx3

# 🗣️ Initialize TTS engine once
engine = pyttsx3.init()
engine.setProperty('rate', 160)  # Speed
engine.setProperty('volume', 1.0)  # Max volume

def speak(text):
    print(f"🔊 Speaking: {text}")
    engine.say(text)
    engine.runAndWait()
