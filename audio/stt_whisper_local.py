import requests

DEEPGRAM_API_KEY = "41300fb277755c217ebbe88bbd917ad25c7cfeca"  # 🔑 Paste actual key here

def transcribe_audio(audio_path):
    print(f"🧠 Transcribing: {audio_path} (via Deepgram API)")

    with open(audio_path, "rb") as f:
        audio_data = f.read()

    response = requests.post(
        "https://api.deepgram.com/v1/listen",
        headers={
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "audio/wav"
        },
        data=audio_data
    )

    result = response.json()
    try:
        transcript = result['results']['channels'][0]['alternatives'][0]['transcript']
        return transcript
    except Exception as e:
        print("⚠️ Transcription error:", e)
        return ""
