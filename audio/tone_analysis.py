# tone_analysis.py

import torchaudio
import torch
import numpy as np
import os
import time
from scipy.io import wavfile

# Load silero VAD model
model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=True)
(get_speech_timestamps, _, read_audio, _, _) = utils


def record_with_silero_vad():
    import sounddevice as sd
    import soundfile as sf

    RATE = 16000
    DURATION = 10  # seconds
    THRESHOLD = 0.7

    print("🎙️ Recording with Silero VAD... Speak now.")

    audio = sd.rec(int(RATE * DURATION), samplerate=RATE, channels=1, dtype='int16')
    sd.wait()

    temp_wav = "temp/audio.wav"
    sf.write(temp_wav, audio, RATE)

    wav = read_audio(temp_wav, sampling_rate=RATE)
    speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=RATE)

    if not speech_timestamps:
        print("⚠️ No speech detected.")
        return None

    print("✅ Speech detected.")
    return temp_wav


def compute_hesitation_score(audio_path):
    wav, sr = torchaudio.load(audio_path)
    speech_timestamps = get_speech_timestamps(wav[0], model, sampling_rate=sr)

    total = wav.shape[1] / sr
    if not speech_timestamps:
        return 100

    speech_duration = sum([(t['end'] - t['start']) / sr for t in speech_timestamps])
    hesitation = 100 - int((speech_duration / total) * 100)
    return hesitation  
