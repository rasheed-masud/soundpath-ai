# SoundPath AI – Music Career Architect
# Built with Gradio + GROQ
 

import gradio as gr
import os
import requests

# =========================
# 1. GROQ CONFIGURATION
# =========================

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3.1-8b-instant"   

# =========================
# 2. SYSTEM PROMPT (LOCKED)
# =========================

SYSTEM_PROMPT = """
You are SoundPath AI, an AI Music Career Architect.

Your role is to guide people from absolute zero to becoming skilled, disciplined, and industry-ready music professionals.

You mentor individuals across the entire music industry, including:
- Singers and vocalists
- Instrumentalists of any instrument
- Music producers
- Lyricists
- Composers
- Mixing and mastering learners
- Multi-skilled and independent artists
- Complete beginners who are unsure of their role

Your personality is balanced:
- Supportive and motivating
- Honest and realistic
- Disciplined, but never harsh
- Industry-aware, not theoretical

You do NOT promise instant fame or success.
You focus on:
- Skill development
- Daily and weekly routines
- Long-term career clarity
- Correct sequencing (skills → exposure → originals → growth)

When responding:
- First understand the user’s role, goal, time availability, and experience level
- Give structured guidance (step-by-step, routines, plans)
- Prefer actionable plans over generic advice
- Be clear about what the user should do now vs later
- Encourage consistency and patience

Industry rules you must follow:
- Beginners should focus on fundamentals before public releases
- Covers are usually recommended before originals for early growth
- Skill comes before branding
- Discipline beats motivation
- Long-term progress is more important than quick attention

If a user asks for something unrealistic, gently correct them and redirect them to a better path.

Your mission is to help users build real skills, real discipline, and a real music career path.
"""

# =========================
# 3. GROQ QUERY FUNCTION
# =========================

def query_groq(user_message, chat_history, role, goal, time_commitment, strictness, growth_speed):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    ui_context = f"""
User Profile:
- Music Role: {role}
- Primary Goal: {goal}
- Daily Time Commitment: {time_commitment} minutes
- Mentor Strictness Preference: {strictness}/5
- Growth Speed Preference: {growth_speed}/5
"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": ui_context}
    ]

    for user, bot in chat_history:
        messages.append({"role": "user", "content": user})
        messages.append({"role": "assistant", "content": bot})

    messages.append({"role": "user", "content": user_message})

    response = requests.post(
        GROQ_API_URL,
        headers=headers,
        json={
            "model": MODEL_NAME,
            "messages": messages,
            "temperature": 0.7
        }
    )

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"❌ Error {response.status_code}: {response.text}"

# =========================
# 4. CHAT RESPONSE HANDLER
# =========================

def respond(message, chat_history, role, goal, time_commitment, strictness, growth_speed):
    reply = query_groq(
        message,
        chat_history,
        role,
        goal,
        time_commitment,
        strictness,
        growth_speed
    )
    chat_history.append((message, reply))
    return "", chat_history

# =========================
# 5. GRADIO UI
# =========================

with gr.Blocks() as demo:
    gr.Markdown("## 🎶 SoundPath AI – Music Career Architect")
    gr.Markdown("From Zero to Industry-Ready Music Professional")

    with gr.Row():
        role = gr.Dropdown(
            label="Who are you in the music industry?",
            choices=[
                "Singer / Vocalist",
                "Instrumentalist",
                "Music Producer",
                "Lyricist",
                "Composer",
                "Multi-skilled Artist",
                "Absolute Beginner (Not sure yet)"
            ],
            value="Absolute Beginner (Not sure yet)"
        )

        goal = gr.Dropdown(
            label="What is your primary goal right now?",
            choices=[
                "Build daily practice routine",
                "Improve skills from zero",
                "Decide covers vs originals",
                "Grow audience & exposure",
                "Become industry-ready",
                "Long-term music career planning"
            ],
            value="Improve skills from zero"
        )

    with gr.Row():
        time_commitment = gr.Slider(15, 240, step=15, value=60, label="Daily time commitment (minutes)")
        strictness = gr.Slider(1, 5, step=1, value=3, label="Mentor strictness")
        growth_speed = gr.Slider(1, 5, step=1, value=3, label="Growth speed")

    chatbot = gr.Chatbot(label="SoundPath AI Chat")
    msg = gr.Textbox(label="Ask SoundPath AI")
    state = gr.State([])
    clear = gr.Button("Clear Chat")

    msg.submit(
        respond,
        [msg, state, role, goal, time_commitment, strictness, growth_speed],
        [msg, chatbot]
    )

    clear.click(lambda: ([], []), None, [chatbot, state])

# =========================
# 6. LAUNCH
# =========================

demo.launch()
