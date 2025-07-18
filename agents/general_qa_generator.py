# agents/general_qa_generator.py

import openai

# ✅ Set OpenRouter Key
openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = ""  # 🔐 Paste your actual OpenRouter key here

# 🔁 Generate general interview question
def generate_general_question():
    prompt = """
You are an AI HR assistant. Generate one professional introductory question that an interviewer might ask at the beginning of an interview. The question should be short and natural.

Only return the question. Do not include any explanation.
"""

    try:
        response = openai.ChatCompletion.create(
            model="anthropic/claude-3-haiku",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return "Tell me about yourself."  # Fallback
