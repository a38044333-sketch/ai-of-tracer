import os
import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text

# --- Page Configuration ---
st.set_page_config(
    page_title="AI of Tracer",
    page_icon="⚡",
    layout="centered"
)

st.title("⚡ AI of Tracer")
st.caption("Free Unlimited AI Assistant — Founded by Aman Chauhan")

# --- Groq Client Initialization ---
RAW_KEY = "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"
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY") or RAW_KEY

client = None
if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        st.error(f"Failed to initialize Groq client: {e}")

# Stable, actively supported Groq models
MODEL_CHOICE = "llama-3.1-8b-instant"

# --- State Management ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_voice_prompt" not in st.session_state:
    st.session_state.last_voice_prompt = None

# --- Sidebar: Visual & Voice Tools ---
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
        key="tracer_voice_mic"
    )

    st.markdown("---")
    st.write(f"**Model:** `{MODEL_CHOICE}`")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.session_state.last_voice_prompt = None
        st.rerun()

# --- Render Chat History ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Capture Input ---
text_input = st.chat_input("Ask anything...")
user_query = None

if text_input and text_input.strip():
    user_query = text_input.strip()
elif voice_prompt and voice_prompt.strip() and voice_prompt != st.session_state.last_voice_prompt:
    user_query = voice_prompt.strip()
    st.session_state.last_voice_prompt = voice_prompt

# --- Process & Stream AI Response ---
if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        if not client:
            st.error("Groq client is not initialized. Please verify your API key.")
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

                # Sanitize messages: ensure no empty strings or corrupt objects are sent
                clean_history = [
                    {"role": m["role"], "content": str(m["content"])}
                    for m in st.session_state.messages
                    if m.get("content") and str(m["content"]).strip()
                ]

                chat_payload = [system_instruction] + clean_history

                stream = client.chat.completions.create(
                    messages=chat_payload,
                    model=MODEL_CHOICE,
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
                # Displays the exact reason Groq rejected the payload
                st.error(f"Groq API Error: {e}")
