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

# Custom Styling for modern floating input bar
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

if "auto_speech_text" not in st.session_state:
    st.session_state.auto_speech_text = ""

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
        st.session_state.auto_speech_text = ""
        st.rerun()

# --- Render Chat History ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Bottom Bar Container ---
st.markdown('<div class="tracer-bottom-bar"></div>', unsafe_allow_html=True)

# 1. Automatic Silence-Detecting Mic Component
mic_component = """
<div style="display: flex; justify-content: flex-end; align-items: center; margin-bottom: 6px;">
  <button id="autoMicBtn" onclick="toggleListening()" style="
      background: #262730;
      color: #ffffff;
      border: 1px solid #4a4b57;
      border-radius: 50%;
      width: 42px;
      height: 42px;
      cursor: pointer;
      font-size: 19px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s ease;">
    🎙️
  </button>
  <span id="micStatus" style="color: #9aa0a6; font-size: 13px; margin-left: 10px; font-family: sans-serif;"></span>
</div>

<script>
let recognition = null;
let isListening = false;

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;        // Automatically stops when silence is detected
    recognition.interimResults = false;
    recognition.lang = 'en-IN';            // Default English, seamlessly detects pauses

    recognition.onstart = function() {
        isListening = true;
        const btn = document.getElementById('autoMicBtn');
        btn.style.background = '#ff4b4b';
        btn.style.boxShadow = '0 0 10px rgba(255, 75, 75, 0.7)';
        document.getElementById('micStatus').innerText = "Listening... stop talking to send";
    };

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        if (transcript && transcript.trim().length > 0) {
            // Find parent Streamlit text input box and insert spoken text
            const inputs = window.parent.document.querySelectorAll('input[type="text"]');
            for (let input of inputs) {
                if (input.placeholder && input.placeholder.includes("Ask anything")) {
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                    nativeInputValueSetter.call(input, transcript);
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    break;
                }
            }
        }
    };

    recognition.onspeechend = function() {
        recognition.stop();
    };

    recognition.onend = function() {
        isListening = false;
        const btn = document.getElementById('autoMicBtn');
        btn.style.background = '#262730';
        btn.style.boxShadow = 'none';
        document.getElementById('micStatus').innerText = "";
    };

    recognition.onerror = function(event) {
        isListening = false;
        const btn = document.getElementById('autoMicBtn');
        btn.style.background = '#262730';
        btn.style.boxShadow = 'none';
        document.getElementById('micStatus').innerText = "";
    };
} else {
    document.getElementById('micStatus').innerText = "Mic not supported in this browser";
}

function toggleListening() {
    if (!recognition) return;
    if (isListening) {
        recognition.stop();
    } else {
        recognition.start();
    }
}
</script>
"""

# Embed auto-detecting mic widget
components.html(mic_component, height=52)

# 2. Main Chat Input Form
with st.form(key="tracer_chat_form", clear_on_submit=True):
    col_text, col_send = st.columns([8.8, 1.2])
    with col_text:
        typed_prompt = st.text_input(
            "Message AI of Tracer",
            placeholder="Ask anything or tap mic above...",
            label_visibility="collapsed"
        )
    with col_send:
        submit_btn = st.form_submit_button("⬆")

# --- Process & Stream AI Response ---
if submit_btn and typed_prompt and typed_prompt.strip():
    user_query = typed_prompt.strip()

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
                        """You are AI of Tracer, a world-class, highly capable AI assistant founded and created by Aman Chauhan. You possess broad, deep intelligence across coding, science, mathematics, literature, and general reasoning.

STRICT LANGUAGE & STYLE RULES:
1. LANGUAGE MATCHING: Always respond in the exact language the user wrote to you in. If the user writes in English, reply in English. If in Hindi, reply in Hindi. If in Hinglish, reply in Hinglish. NEVER output Arabic or any other unprompted language.
2. CREATOR RECOGNITION: If asked who founded, created, built, or owns you, proudly state that you were founded and created by Aman Chauhan. For all other questions, focus directly on high-quality, articulate, structured answers.
3. COMPREHENSIVE INTELLIGENCE: Be clear, structured, and helpful. Use markdown, bullet points, or code formatting whenever appropriate."""
                    )
                }

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
                    temperature=0.4,
                    max_tokens=1024,
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
