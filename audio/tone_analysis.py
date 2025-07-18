import wave
import contextlib
import webrtcvad

# 🎙️ Detect speaking vs silence chunks
def detect_speech_segments(wav_path):
    vad = webrtcvad.Vad(2)  # Aggressiveness level 2 (0–3)

    with contextlib.closing(wave.open(wav_path, 'rb')) as wf:
        sample_rate = wf.getframerate()
        channels = wf.getnchannels()
        width = wf.getsampwidth()
        n_frames = wf.getnframes()
        audio = wf.readframes(n_frames)

    if channels != 1 or width != 2 or sample_rate not in (8000, 16000, 32000, 48000):
        raise ValueError("Only mono 16-bit PCM at 8k/16k/32k/48k supported")

    frame_duration = 30  # ms
    frame_size = int(sample_rate * frame_duration / 1000) * 2
    segments = []

    for i in range(0, len(audio), frame_size):
        frame = audio[i:i + frame_size]
        if len(frame) < frame_size:
            break
        is_speech = vad.is_speech(frame, sample_rate)
        segments.append(is_speech)

    return segments

# 🔎 Compute % of silence (hesitation score)
def compute_hesitation_score(wav_path):
    segments = detect_speech_segments(wav_path)
    silence_chunks = segments.count(False)
    total_chunks = len(segments)
    
    if total_chunks == 0:
        return 0.0

    hesitation_score = round((silence_chunks / total_chunks) * 100, 2)
    return hesitation_score
