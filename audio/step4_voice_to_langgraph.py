import sys
import os
import json
import time
import shutil
import getpass

# 📁 Ensure user database exists
user_db_path = "users/user_info.json"
os.makedirs("users", exist_ok=True)

if not os.path.exists(user_db_path):
    with open(user_db_path, "w") as f:
        json.dump({}, f)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.interview_agent import get_next_question, submit_answer
from agents.feedback_engine import generate_feedback
from audio.stt_whisper_local import transcribe_audio
from audio.tone_analysis import compute_hesitation_score
from audio.tts_speaker import speak
from resume.resume_parser import parse_resume

# ✅ Replaced deprecated VAD listener
from audio.tone_analysis import record_with_silero_vad as record_with_vad

# 🎙️ Login / Register
print("🎙️ Welcome to VOCAHIRE Interview Coach")

# 🔄 Load user database
with open(user_db_path, "r") as f:
    user_db = json.load(f)

action = input("🔐 Do you want to (1) Login or (2) Register? ").strip()
username = input("👤 Enter your username: ").strip()

user_base = os.path.join("users", username)
resume_dir = os.path.join(user_base, "resume")
logs_dir = os.path.join(user_base, "logs")

if action == "2":  # Register
    if username in user_db:
        print(f"⚠️ Username '{username}' already exists. Please login instead.")
        exit()
    password = getpass.getpass("🔐 Create your password: ").strip()
    user_db[username] = password
    with open(user_db_path, "w") as f:
        json.dump(user_db, f, indent=2)
    os.makedirs(resume_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)
    print(f"✅ New account created for {username}")
    print("👋 Please login again to continue.")
    exit()

elif action == "1":  # Login
    if username not in user_db:
        print(f"❌ Username '{username}' not found. Please register first.")
        exit()
    password = getpass.getpass("🔐 Enter your password: ").strip()
    if user_db[username] != password:
        print("❌ Incorrect password.")
        exit()
    print(f"✅ Welcome back, {username}!")

else:
    print("❌ Invalid input.")
    exit()

# 📄 Upload Resume
resume_path = os.path.join(resume_dir, "Resume.pdf")
parsed_resume_path = os.path.join(resume_dir, "parsed_resume.json")

if input("📄 Do you want to upload a new resume? (y/n): ").strip().lower() == "y":
    source_resume_path = input("📂 Enter full path to your Resume.pdf file: ").strip().strip('"')
    try:
        shutil.copy(source_resume_path, resume_path)
        print(f"✅ Resume copied to {resume_path}")
    except Exception as e:
        print(f"❌ Failed to copy resume: {e}")
        exit()
else:
    if not os.path.exists(resume_path):
        print("⚠️ No existing resume found. Please upload it.")
        exit()

# 📂 Auto Resume Parsing
if not os.path.exists(parsed_resume_path):
    if os.path.exists(resume_path):
        print("📄 Resume found! Parsing...")
        parsed_data = parse_resume(resume_path)
        with open(parsed_resume_path, "w") as f:
            json.dump(parsed_data, f, indent=2)
        print("✅ Resume parsed and saved.")
    else:
        print("⚠️ Resume not found. Skipping resume parsing.")
else:
    print("✅ parsed_resume.json found. Resume already parsed.")

# 🎙️ Interview Starts
print("\n🎙️ VOCAHIRE: Real-Time Voice Interview Coach")
print("✅ Starting VOCAHIRE Interview...\n")

interview_data = []

def voice_interview_loop():
    while True:
        question = get_next_question()
        print(f"⚙️ [Debug] Got question = {question}")
        if not question:
            print("⚠️ No more questions.")
            break

        print(f"\n🧠 AI: {question}")
        speak(question)
        print("🎙️ Speak now...")

        audio_path = record_with_vad()
        if not audio_path:
            continue

        answer = transcribe_audio(audio_path).strip()
        print(f"📝 Your Answer: {answer}")
        if not answer:
            print("⚠️ No valid answer received.")
            continue

        hesitation = compute_hesitation_score(audio_path)
        print(f"🎯 Hesitation Score: {hesitation}%")

        if hesitation > 35:
            print("🗣️ You seemed a bit hesitant.")
        else:
            print("🗣️ Great tone!")

        feedback = generate_feedback(question, answer, hesitation)
        speak(feedback)

        interview_data.append({
            "question": question,
            "answer": answer,
            "hesitation_score": hesitation,
            "feedback": feedback
        })

        submit_answer(answer)

    timestamp = int(time.time())
    log_path = os.path.join(logs_dir, f"interview_{timestamp}.json")
    with open(log_path, "w") as f:
        json.dump(interview_data, f, indent=2)

    print(f"\n📝 Full interview saved to: {log_path}")
    print("✅ Interview Completed. Thank you!")

# 🚀 Run
if __name__ == "__main__":
    voice_interview_loop()
