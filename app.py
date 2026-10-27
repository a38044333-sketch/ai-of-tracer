import os
import streamlit as st
import streamlit.components.v1 as components
from groq import Groq

# --- Page Configuration ---
st.set_page_config(
    page_title="AI of Tracer",
    page_icon="⚡",
    layout="centered"
)

# Custom Styling for modern floating bottom dock
st.markdown(
    """
<style>
.main .block-container {
    padding-bottom: 150px;
}
div[data-testid="stVerticalBlock"] > div:has(div.tracer-bottom-bar) {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: #0e1117;
    padding: 0.8rem 1.2rem 1.2rem 1.2rem;
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
        st.rerun()

# --- Render Chat History ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Bottom Bar Container ---
st.markdown('<div class="tracer-bottom-bar"></div>', unsafe_allow_html=True)

# Mobile-Compatible Web Speech Mic Component
mic_component = """
<div style="display: flex; align-items: center; justify-content: flex-end; margin-bottom: 8px;">
  <button id="mobileMicBtn" type="button" style="
      background: #262730;
      color: #ffffff;
      border: 1px solid #4a4b57;
      border-radius: 50%;
      width: 44px;
      height: 44px;
      cursor: pointer;
      font-size: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      touch-action: manipulation;
      transition: all 0.2s ease;">
    🎙️
  </button>
  <span id="micStatus" style="color: #9aa0a6; font-size: 13px; margin-left: 10px; font-family: sans-serif;"></span>
</div>

<script>
let recognition = null;
let isRecording = false;

const SpeechAPI = window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechAPI) {
    recognition = new SpeechAPI();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    const btn = document.getElementById('mobileMicBtn');
    const status = document.getElementById('micStatus');

    recognition.onstart = function() {
        isRecording = true;
        btn.style.background = '#ff4b4b';
        btn.style.boxShadow = '0 0 12px rgba(255, 75, 75, 0.8)';
        status.innerText = "Listening... Speak now";
    };

    recognition.onresult = function(event) {
        const text = event.results[0][0].transcript;
        if (text && text.trim().length > 0) {
            status.innerText = "Transcribing...";
            try {
                // Find Streamlit parent input field and insert text
                const parentDoc = window.parent.document;
                const textInputs = parentDoc.querySelectorAll('input[type="text"]');
                for (let input of textInputs) {
                    if (input.placeholder && input.placeholder.includes("Ask anything")) {
                        const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                        setter.call(input, text);
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        
                        // Automatically submit form if submit button exists
                        setTimeout(() => {
                            const submitBtn = parentDoc.querySelector('button[kind="secondaryFormSubmit"]');
                            if (submitBtn) {
                                submitBtn.click();
                            }
                        }, 200);
                        break;
                    }
                }
            } catch(e) {
                status.innerText = "Tap input to paste";
            }
        }
    };

    recognition.onspeechend = function() {
        recognition.stop();
    };

    recognition.onend = function() {
        isRecording = false;
        btn.style.background = '#262730';
        btn.style.boxShadow = 'none';
        status.innerText = "";
    };

    recognition.onerror = function(event) {
        isRecording = false;
        btn.style.background = '#262730';
        btn.style.boxShadow = 'none';
        if (event.error === 'not-allowed') {
            status.innerText = "Allow Mic permission in browser settings";
        } else {
            status.innerText = "No speech heard. Try again.";
        }
    };

    btn.addEventListener('click', function(e) {
        e.preventDefault();
