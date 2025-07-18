from agents.general_qa_generator import generate_general_question
from agents.resume_qa_generator import generate_resume_question
from agents.fallback_qa_generator import generate_fallback_question  # ✅ New import

MAX_RESUME_QUESTIONS = 1
MAX_FALLBACK_QUESTIONS = 1

resume_question_count = 0
fallback_question_count = 0
first_question_asked = False
first_general_question = ""

class InterviewState:
    def __init__(self):
        self.index = 0
        self.current_question = ""
        self.history = []
        self.finished = False

state = InterviewState()

def get_next_question():
    global state, resume_question_count, fallback_question_count, first_question_asked, first_general_question

    if state.finished:
        return None

    # 1️⃣ Generated intro question
    if not first_question_asked:
        first_general_question = generate_general_question()
        state.current_question = first_general_question
        first_question_asked = True
        return first_general_question

    # 2️⃣ Resume-based
    if resume_question_count < MAX_RESUME_QUESTIONS:
        question = generate_resume_question()
        if question:
            resume_question_count += 1
            state.current_question = question
            return question

    # 3️⃣ Generated fallback
    if fallback_question_count < MAX_FALLBACK_QUESTIONS:
        question = generate_fallback_question()
        fallback_question_count += 1
        state.current_question = question
        return question

    state.finished = True
    return None

def submit_answer(answer_text):
    global state

    if state.finished:
        return None

    if answer_text:
        state.history.append((state.current_question, answer_text))
        print(f"📝 Answer stored for: {state.current_question}")

    state.index += 1

    total = 1 + MAX_RESUME_QUESTIONS + MAX_FALLBACK_QUESTIONS
    if state.index >= total:
        state.finished = True

    return "ok"
