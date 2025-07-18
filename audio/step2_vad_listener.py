import webrtcvad
import pyaudio
import numpy as np
import soundfile as sf
import time
from collections import deque
import os

def record_with_vad():
    vad = webrtcvad.Vad(1)
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    FRAME_DURATION = 30
    FRAME_SIZE = int(RATE * FRAME_DURATION / 1000)
    SILENCE_LIMIT = 1.5

    p = pyaudio.PyAudio()

    try:
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                        input=True, frames_per_buffer=FRAME_SIZE)
    except Exception as e:
        print(f"❌ Could not open audio stream: {e}")
        return None

    print("🎙️ Speak now...")

    recording = False
    frames = []
    silence_counter = 0
    pre_speech_buffer = deque(maxlen=10)

    try:
        while True:
            try:
                audio_chunk = stream.read(FRAME_SIZE, exception_on_overflow=False)
            except Exception as e:
                print(f"❌ Mic read error: {e}")
                break

            is_speech = vad.is_speech(audio_chunk, RATE)
            pre_speech_buffer.append(audio_chunk)

            if is_speech:
                if not recording:
                    print("🟢 Start Recording")
                    frames.extend(pre_speech_buffer)
                    recording = True
                frames.append(audio_chunk)
                silence_counter = 0
            elif recording:
                silence_counter += FRAME_DURATION / 1000.0
                frames.append(audio_chunk)
                if silence_counter > SILENCE_LIMIT:
                    print("🔴 Stop Recording")
                    break

    finally:
        try:
            stream.stop_stream()
            stream.close()
        except Exception:
            pass
        p.terminate()

    if frames:
        audio_np = np.frombuffer(b''.join(frames), dtype=np.int16)
        timestamp = int(time.time())
        save_dir = os.path.join("data", "recordings")
        os.makedirs(save_dir, exist_ok=True)
        filename = os.path.join(save_dir, f"recording_{timestamp}.wav")
        sf.write(filename, audio_np, RATE)
        print(f"💾 Saved: {filename}")
        return filename
    else:
        print("⚠️ No audio recorded.")
        return None
