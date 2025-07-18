from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

from agents import (
    resume_qa_generator,
    general_qa_generator,
    fallback_qa_generator,
    interview_agent,
    feedback_engine
)

from audio import (
    stt_whisper_local,
    tone_analysis,
    tts_speaker
)

# Initialize FastAPI app
app = FastAPI()

# CORS setup for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # update with your frontend domain if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Global interview state (can later move to DB per user)
question_queue = []
current_question_index = 0


# -------------------------
# Endpoint: Upload Resume
# -------------------------
@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    contents = await file.read()
    os.makedirs("temp", exist_ok=True)
    resume_path = f"temp/{file.filename}"

    with open(resume_path, "wb") as f:
        f.write(contents)

    # Generate initial interview questions using your custom logic
    intro_q = general_qa_generator.generate_general_question()
    resume_q = resume_qa_generator.generate_resume_question(resume_path)
    fallback_q = fallback_qa_generator.generate_fallback_question()

    global question_queue, current_question_index
    question_queue = [intro_q, resume_q, fallback_q]
    current_question_index = 0

    return {
        "message": "Resume uploaded and questions prepared.",
        "first_question": question_queue[0]
    }


# -------------------------
# Endpoint: Get Next Question
# -------------------------
@app.get("/next_question")
def get_next_question():
    global current_question_index
    if current_question_index >= len(question_queue):
        return {"done": True}
    
    question = question_queue[current_question_index]
    current_question_index += 1

    return {
        "done": False,
        "question": question
    }


# -------------------------
# Endpoint: Process Audio (Answer)
# -------------------------
@app.post("/process_audio")
async def process_audio(audio: UploadFile = File(...), username: str = Form(...)):
    os.makedirs("temp", exist_ok=True)
    audio_path = f"temp/{username}_response.wav"
    with open(audio_path, "wb") as f:
        f.write(await audio.read())

    # Step 1: Transcribe using Whisper
    transcript = stt_whisper_local.transcribe(audio_path)

    # Step 2: Analyze hesitation using tone model
    hesitation_score = tone_analysis.get_hesitation_score(audio_path)

    # Step 3: Get current question
    global current_question_index
    question_index = current_question_index - 1 if current_question_index > 0 else 0
    question = question_queue[question_index] if question_queue else "N/A"

    # Step 4: Generate feedback using Claude
    feedback = feedback_engine.generate_feedback(
        question=question,
        answer=transcript,
        hesitation_score=hesitation_score
    )

    # Step 5: Optional: Generate TTS (store or return URL)
    tts_path = f"temp/{username}_tts_response.wav"
    tts_speaker.generate_tts_audio(question, tts_path)
    # You can upload to Supabase or send to frontend if needed

    return {
        "transcript": transcript,
        "hesitation": hesitation_score,
        "feedback": feedback,
        "next_question": question_queue[current_question_index] if current_question_index < len(question_queue) else "No more questions."
    }


# -------------------------
# Optional: Health check
# -------------------------
@app.get("/")
def health():
    return {"status": "VocaHire backend is running 🚀"}
