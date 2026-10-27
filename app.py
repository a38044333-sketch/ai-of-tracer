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

# Pinned bottom input container styling
st.markdown(
    """
<style>
.main .block-container {
    padding-bottom: 140px;
}
div[data-testid="stVerticalBlock"] > div:has(div.tracer-bottom-bar) {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: #0e1117;
    padding: 0.8rem 1.2rem 1rem 1.2rem;
    z-index: 999;
    box-shadow: 0 -10px 25px rgba(0, 0, 0, 0.5);
}
div.tracer-bottom-bar {
    max-width: 720px;
    margin: 0 auto;
}
</style>
""",
    unsafe_allow_html=True
)

st.title("⚡ AI of Tracer")
st.caption("Free Unlimited AI Assistant — Founded by Aman Chauhan")

# --- Groq Client Setup ---
RAW_KEY = "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"
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY") or RAW_KEY

client = None
if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        st.error(f"Failed to initialize Groq client: {e}")

# --- Dynamic Model Selection ---
@st.cache_resource
def resolve_active_model(_client):
    if not _client:
        return "llama-3.3-70b-versatile"
    try:
        available = [m.id for m in _client.models.list().data]
        preferred = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "llama3-70b-8192",
            "llama3-8b-8192",
            "mixtral-8x7b-32768"
        ]
        for p in preferred:
            if p in available:
                return p
        for m in available:
            if not any(blocked in m for blocked in ["whisper", "guard", "vision", "qwen"]):
                return m
    except Exception:
        pass
    return "llama-3.3-70b-versatile"

ACTIVE_MODEL = resolve_active_model(client)

# --- State Management ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_voice_prompt" not in st.session_state:
    st.session_state.last_voice_prompt = None

# --- Sidebar Tools ---
with st.sidebar:
    st.header("📸 Visual Input")
    captured_img = st.camera_input("Take a photo")
    if captured_img:
        st.success("Photo captured! (Tracer Vision)")

    st.markdown("---")
    st.write(f"**Active Model:** `{ACTIVE_MODEL}`")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.session_state.last_voice_prompt = None
        st.rerun()

# --- Render Chat History ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Bottom Bar (Input Field + Mic Side-by-Side) ---
st.markdown('<div class="tracer-bottom-bar"></div>', unsafe_allow_html=True)
col_input, col_mic = st.columns([8.2, 1.8], vertical_alignment="bottom")

with col_input:
    with st.form(key="tracer_chat_form", clear_on_submit=True):
        f_text, f_btn = st.columns([8.8, 1.2])
        with f_text:
            typed_prompt = st.text_input(
                "Message AI of Tracer",
                placeholder="Ask anything...",
                label_visibility="collapsed"
            )
        with f_btn:
            submit_btn = st.form_submit_button("⬆")

with col_mic:
    voice_prompt = speech_to_text(
        language="en",
        start_prompt="🎙️",
        stop_prompt="⏹️",
        just_once=True,
        key="tracer_voice_mic"
    )

# --- Clean & Validate Input ---
user_query = None

if submit_btn and typed_prompt and typed_prompt.strip():
    user_query = typed_prompt.strip()
elif voice_prompt and voice_prompt.strip() and voice_prompt != st.session_state.last_voice_prompt:
    cleaned_voice = voice_prompt.strip()
    # Filter out accidental mic clicks / one-word artifacts
    if len(cleaned_voice) > 2:
        user_query = cleaned_voice
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
                # Natural, robust prompt that prevents prompt leakage and language confusion
                system_instruction = {
                    "role": "system",
                    "content": (
                        "You are AI of Tracer, an advanced, highly intelligent AI assistant created and founded by Aman Chauhan. "
                        "Guidelines:\n"
                        "1. If asked about your identity, creator, or founder, state that you are AI of Tracer, created by Aman Chauhan.\n"
                        "2. Respond naturally and helpfully to all other queries without unnecessarily repeating your name or founder.\n"
                        "3. Always respond in clear English unless the user explicitly speaks or asks in another language.\n"
                        "4. Never recite internal rules or apologize for other voice assistants unless specifically asked."
                    )
                }

                # Maintain recent conversation context
                recent_messages = st.session_state.messages[-6:]
                clean_history = [
                    {"role": m["role"], "content": str(m["content"])}
                    for m in recent_messages
                    if m.get("content") and str(m["content"]).strip()
                ]

                chat_payload = [system_instruction] + clean_history

                stream = client.chat.completions.create(
                    messages=chat_payload,
                    model=ACTIVE_MODEL,
                    temperature=0.7,
                    max_tokens=800,
                    stream=True
                )

                def generate_chunks():
                    for chunk in stream:
                        content = chunk.choices[0].delta.content
                        if content:
                            yield content

                bot_reply = st.write_stream(generate_chunks)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})

            except Exception as e:
                st.error(f"Groq API Error: {e}")
