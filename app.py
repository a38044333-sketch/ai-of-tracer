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

# Custom CSS to float the input bar + mic button at the bottom
st.markdown("""
<style>
/* Add space at bottom so messages don't get covered */
.main .block-container {
    padding-bottom: 130px;
}

/* Floating bottom bar */
div[data-testid="stVerticalBlock"] > div:has(div.tracer-bottom-bar) {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: #0e1117;
    padding: 1rem 1.5rem 1.2rem 1.5rem;
    z-index: 999;
    box-shadow: 0 -10px 20px rgba(0, 0, 0, 0.4);
}

div.tracer-bottom-bar {
    max-width: 720px;
    margin: 0 auto;
}
</style>
""", unsafe_allow_html=True)

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

# --- Dynamic Model Selection (High Quota Only) ---
@st.cache_resource
def resolve_active_model(_client):
    if not _client:
        return "llama-3.3-70b-versatile"
    try:
        available_models = [m.id for m in _client.models.list().data]
        
        # Priority list avoids low-rate-limit models like qwen3.8-27b
        preferred_models = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "llama3-70b-8192",
            "llama3-8b-8192",
            "mixtral-8x7b-32768"
        ]
        
        for pref in preferred_models:
            if pref in available_models:
                return pref
                
        for m in available_models:
            # Skip whisper, guard, vision, and qwen models with restrictive OTPM
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

# --- Bottom Bar: Text Input + Mic Button ---
st.markdown('<div class="tracer-bottom-bar"></div>', unsafe_allow_html=True)
col_input, col_mic = st.columns([8.5, 1.5], vertical_alignment="bottom")

with col_input:
    with st.form(key="tracer_chat_form", clear_on_submit=True):
        f_col1, f_col2 = st.columns([9, 1])
        with f_col1:
            typed_prompt = st.text_input(
                "Message AI of Tracer",
                placeholder="Ask anything...",
                label_visibility="collapsed"
            )
        with f_col2:
            submit_btn = st.form_submit_button("⬆")

with col_mic:
    voice_prompt = speech_to_text(
        language="en",
