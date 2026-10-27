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
# Prioritizes Streamlit Secrets/Environment variables, with your key as fallback
RAW_KEY = "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"
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY") or RAW_KEY

try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error(f"Failed to initialize Groq client: {e}")
    client = None

# --- Dynamic Model Selection ---
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
    except
