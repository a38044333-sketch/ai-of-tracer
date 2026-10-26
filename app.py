import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
import os

# 1. Page Configuration with your Logo
st.set_page_config(
    page_title="AI of Tracer",
    page_icon="logo.png" if os.path.exists("logo.png") else "⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 2. Complete CSS Overrides to wipe ALL Streamlit logos, menus, and badges
custom_css = """
    <style>
    /* Dark Theme Canvas */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #151b28 0%, #0b0f17 100%);
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* 1. Remove Top Header & Streamlit Hamburger Menu */
    header[data-testid="stHeader"] {display: none !important; height: 0px !important;}
    #MainMenu {visibility: hidden !important; display: none !important;}
    
    /* 2. Remove "Hosted with Streamlit" bottom footer */
    footer {visibility: hidden !important; display: none !important;}
    
    /* 3. Remove Floating Streamlit badge / Toolbar on Mobile */
    [data-testid="stStatusWidget"] {display: none !important;}
    .viewerBadge_container__1QSob, .viewerBadge_link__1S137 {display: none !important;}
    div[class*="viewerBadge"] {display: none !important;}
    div[class*="stDeployButton"] {display: none !important;}
    div[data-testid="stToolbar"] {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}
    
    /* 4. Remove any Streamlit logo SVG elements */
    svg[data-testid="stLogo"] {display: none !important;}
    img[src*="streamlit"] {display: none !important;}

    /* Premium Cyber Header */
    .header-container {
        display: flex;
        align-items: center;
        gap: 14px;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.85));
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 20px;
        padding: 14px 18px;
        margin-bottom: 18px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 0 15px rgba(56, 189, 248, 0.15);
        backdrop-filter: blur(12px);
    }
    .header-title {
        font-size: 1.7rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.2;
    }
    .header-badge {
        display: inline-block;
        background: rgba(56, 189, 248, 0.12);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 2px 10px;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-top: 4px;
    }

    /* Glassmorphism Chat Bubble Styling */
    div[data-testid="stChatMessage"] {
        background: rgba(30, 41, 59, 0.55) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 12px 16px !important;
        margin-bottom: 12px !important;
        backdrop-filter: blur(8px);
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
        background: rgba(56, 189, 248, 0.09) !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
    }

    /* Fixed Bottom Input */
    div[data-testid="stChatInput"] {
        border-radius: 24px !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        background: rgba(15, 23, 42, 0.95) !important;
    }
    div[data-testid="stChatInput"]:focus-within {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.35) !important;
    }

    section[data-testid="stSidebar"] {
        background: #0f172a !important;
        border-right: 1px solid rgba(56, 189, 248, 0.15) !important;
    }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 3. Header with your robot logo
col_logo, col_info = st.columns([1, 5])
with col_logo:
  if os.path.exists("logo.png"):
    st.image("logo.png", width=65)
  else:
    st.markdown(
        "<h1 style='text-align: center; margin: 0;'>⚡</h1>",
        unsafe_allow_html=True,
    )
with col_info:
  st.markdown(
      '<div class="header-title">AI of Tracer</div>', unsafe_allow_html=True
  )
  st.markdown(
      '<div class="header-badge">ULTRA FAST INTELLIGENCE</div>',
      unsafe_allow_html=True,
  )

# 4. In-App Web Speech Recognition Mic Button
speech_js = """
<div style="display: flex; align-items: center; justify-content: flex-end; margin-bottom: 10px;">
    <button id="tracerMicBtn" onclick="toggleTracerVoice()" style="
        background: linear-gradient(135deg, #0284c7, #6366f1);
        border: none;
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
    ">
        <span id="micIcon">🎙️</span>
        <span id="micText">Tap to Speak</span>
    </button>
</div>

<script>
let recognition;
let recognizing = false;

function toggleTracerVoice() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        alert("Voice recognition is supported in Chrome, Edge, and Android WebViews.");
        return;
    }

    const btn = document.getElementById('tracerMicBtn');
    const icon = document.getElementById('micIcon');
    const text = document.getElementById('micText');

    if (!recognizing) {
        recognition = new SpeechRecognition();
        recognition.lang = 'hi-IN';
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = function() {
            recognizing = true;
            btn.style.background = 'linear-gradient(135deg, #ef4444, #f97316)';
            text.innerText = 'Listening... Bolen';
        };

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            const parentDoc = window.parent.document;
            const chatInput = parentDoc.querySelector('textarea[data-testid="stChatInputTextArea"]');
            if (chatInput) {
                chatInput.value = transcript;
                chatInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
        };

        recognition.onerror = function() {
            recognizing = false;
            btn.style.background = 'linear-gradient(135deg, #0284c7, #6366f1)';
            text.innerText = 'Tap to Speak';
        };

        recognition.onend = function() {
            recognizing = false;
            btn.style.background = 'linear-gradient(135deg, #0284c7, #6366f1)';
            text.innerText = 'Tap to Speak';
        };

        recognition.start();
    } else {
        recognition.stop();
    }
}
</script>
"""
components.html(speech_js, height=45)

# 5. Groq Setup
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)


@st.cache_resource
def get_best_model():
  try:
    model_list = [m.id for m in client.models.list().data]
