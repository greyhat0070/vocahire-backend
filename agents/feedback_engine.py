import openai

# ✅ Use OpenRouter endpoint
openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = ""  # 🔐 Paste your actual OpenRouter key here

# ✅ Claude-based feedback generator
def generate_feedback(question, answer, hesitation_score):
    system_prompt = "You are an AI interview coach. Analyze answers and give specific, kind, helpful feedback."

    user_prompt = f"""
You are evaluating an interview candidate.

Question: {question}
Answer: {answer}
Hesitation Score: {hesitation_score}%

Give a short 2-3 sentence feedback based on:
1. How well they answered
2. Whether they sounded confident
3. One improvement suggestion
"""

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
        return f"⚠️ Claude feedback failed: {e}"
