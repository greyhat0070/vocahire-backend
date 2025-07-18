# agents/fallback_qa_generator.py

import openai

openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = ""  # 🔐 Paste your actual OpenRouter key here

def generate_fallback_question():
    system_prompt = "You are a professional HR interviewer. Generate short, helpful technical or behavioral interview questions."

    user_prompt = """Give a short, clear HR-style interview question.
Don't include explanations or context—just the question itself."""

    try:
        response = openai.ChatCompletion.create(
            model="anthropic/claude-3-haiku",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return "⚠️ Could not generate question"
