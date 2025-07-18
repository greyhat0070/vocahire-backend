# agents/resume_qa_generator.py

import json
import openai
import os

# ✅ Claude via OpenRouter
openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = ""  # Your key

# ✅ Load resume only when needed
def load_resume_data():
    resume_path = os.path.join("resume", "data", "parsed_resume.json")
    if os.path.exists(resume_path):
        with open(resume_path, "r") as f:
            return json.load(f)
    else:
        print("⚠️ parsed_resume.json not found! Resume questions will not work.")
        return None

# ✅ Generate interview question from resume
def generate_resume_question():
    resume_data = load_resume_data()
    if not resume_data:
        return None

    resume_str = "\n".join(
        resume_data.get("projects", []) +
        resume_data.get("skills", []) +
        resume_data.get("education", [])
    )

    prompt = f"""
You are an intelligent interview assistant.

Based on the resume content below, generate one technical interview question that could be asked to the candidate.

Resume:
{resume_str}

ONLY return the interview question, no explanation, no intro, no quotes.
"""

    try:
        response = openai.ChatCompletion.create(
            model="anthropic/claude-3-haiku",
            messages=[
                {"role": "system", "content": "You are a helpful AI interview assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"⚠️ Failed to generate resume question: {e}"
