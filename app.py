import os
import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text

st.set_page_config(page_title="AI of Tracer", page_icon="⚡", layout="centered")

st.title("⚡ AI of Tracer")
st.caption("Free Unlimited AI Assistant — Founded by Aman Chauhan")

# Retrieve Groq API Key securely from secrets or environment variables
api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")

if not api_key:
    st.warning("Please add your `GROQ_API_KEY` to Streamlit Secrets to enable chat.")
    client = None
else:
    client = Groq(api_key=api_key)

# Dynamic Model Selection
@st.cache_resource
def get_best_model(_client):
    if not _client:
        return "llama-3.3-70b-versatile"
    try:
        model_list = [m.id for m in _client.models.list().data]
        preferred = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
        ]
        for name in preferred:
            if name in model_list:
                return name
        for name in model_list:
            if "whisper" not in name and "guard" not in name:
                return name
    except Exception:
        pass
    return "llama-3.3-70b-versatile"

ACTIVE_MODEL = get_best_model(client)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_voice_prompt" not in st.session_state:
    st.session_state.last_voice_prompt = None

# Sidebar: Camera & Voice Tools
with st.sidebar:
    st.header("📸 Visual & Audio Input")

    captured_img = st.camera_input("Take a photo")
    if captured_img:
        st.success("Photo captured! (Tracer Vision)")

    st.write("🎙️ **Voice Input:**")
    voice_prompt = speech_to_text(
        language="en",
        start_prompt="Tap to Speak",
        stop_prompt="Stop Recording",
        just_once=True,
        key="voice_input",
    )

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Collect Input from Chat Bar or Microphone
text_input = st.chat_input("Ask anything...")
user_query = None

if text_input:
    user_query = text_input
elif voice_prompt and voice_prompt != st.session_state.last_voice_prompt:
    user_query = voice_prompt
    st.session_state.last_voice_prompt = voice_prompt

# Process and Stream AI Response
if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        if not client:
            st.error("GROQ_API_KEY is not configured.")
        else:
            try:
                system_instruction = {
                    "role": "system",
                    "content": (
                        "You are AI of Tracer, an intelligent and fast AI assistant. "
                        "Your founder, creator, and owner is Aman Chauhan. "
                        "Whenever anyone asks who created you, who made you, who owns you, "
                        "or who your founder is, always state clearly that you were created "
                        "and founded by Aman Chauhan."
                    ),
                }

                chat_payload = [system_instruction] + [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]

                stream = client.chat.completions.create(
                    messages=chat_payload,
                    model=ACTIVE_MODEL,
                    stream=True,
                )

                def generate_chunks():
                    for chunk in stream:
                        content = chunk.choices[0].delta.content
                        if content:
                            yield content

                bot_reply = st.write_stream(generate_chunks)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})

            except Exception as e:
                st.error(f"Error: {e}")
