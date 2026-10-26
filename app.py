import os
import streamlit as st
import streamlit.components.v1 as components
from groq import Groq

# 1. Page Configuration
st.set_page_config(
    page_title="AI of Tracer",
    page_icon="logo.png" if os.path.exists("logo.png") else "⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 2. Aggressive CSS to destroy ALL Streamlit badges, footers, headers, and watermark logos
custom_css = """
    <style>
    .stApp {
        background: radial-gradient(circle at 50% 0%, #151b28 0%, #0b0f17 100%);
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* 1. COMPLETELY HIDE STREAMLIT TOP BAR & HAMBURGER */
    header, header[data-testid="stHeader"], div[data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }
    #MainMenu {
        display: none !important;
        visibility: hidden !important;
    }

    /* 2. COMPLETELY HIDE STREAMLIT FOOTER & HOSTED BADGE */
    footer {
        display: none !important;
        visibility: hidden !important;
    }
    [data-testid="stStatusWidget"],
    .viewerBadge_container__1QSob,
    .viewerBadge_link__1S137,
    div[class*="viewerBadge"],
    div[class*="stDeployButton"],
    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"],
    div[data-testid="manage-app-button"],
    button[title*="Streamlit"],
    a[href*="streamlit.io"],
    svg[data-testid="stLogo"],
    img[src*="streamlit"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    /* 3. Clean Header Styling */
    .app-header {
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.2;
    }
    .app-subtitle {
        color: #94a3b8;
        font-size: 0.85rem;
        margin-top: 2px;
        margin-bottom: 12px;
    }

    /* 4. Chat Bubbles */
    div[data-testid="stChatMessage"] {
        background: rgba(30, 41, 59, 0.55) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 12px 16px !important;
        margin-bottom: 12px !important;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
        background: rgba(56, 189, 248, 0.09) !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
    }

    /* 5. Bottom Input Box */
    div[data-testid="stChatInput"] {
        border-radius: 24px !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        background: rgba(15, 23, 42, 0.95) !important;
    }
    div[data-testid="stChatInput"]:focus-within {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.35) !important;
    }

    section[data-testid="stSidebar"] {
        background: #0f172a !important;
        border-right: 1px solid rgba(56, 189, 248, 0.15) !important;
    }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# JavaScript snippet that removes Streamlit's iframe wrapper badge in parent DOM
js_cleaner = """
<script>
function cleanBadges() {
    try {
        const doc = window.parent.document;
        const badges = doc.querySelectorAll('.viewerBadge_container__1QSob, [class*="viewerBadge"], [data-testid="manage-app-button"], footer, header');
        badges.forEach(b => b.style.setProperty('display', 'none', 'important'));
    } catch(e) {}
}
setInterval(cleanBadges, 500);
</script>
"""
components.html(js_cleaner, height=0)

# 3. Clean App Title (NO "created by" or "founded by" anywhere)
col_logo, col_info = st.columns([1, 5])
with col_logo:
  if os.path.exists("logo.png"):
    st.image("logo.png", width=60)
  else:
    st.markdown(
        "<h1 style='text-align: center; margin: 0;'>⚡</h1>",
        unsafe_allow_html=True,
    )
with col_info:
  st.markdown(
      '<div class="app-header">AI of Tracer</div>', unsafe_allow_html=True
  )
  st.markdown(
      '<div class="app-subtitle">Official AI Assistant</div>',
      unsafe_allow_html=True,
  )

# 4. In-App Web Speech Recognition Mic Button
speech_js = """
<div style="display: flex; align-items: center; justify-content: flex-end; margin-bottom: 8px;">
    <button id="tracerMicBtn" onclick="toggleTracerVoice()" style="
        background: linear-gradient(135deg, #0284c7, #6366f1);
        border: none;
        color: white;
        padding: 7px 14px;
        border-radius: 18px;
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
        alert("Voice dictation is supported in modern mobile browsers.");
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
            text.innerText = 'Listening...';
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
    preferred = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
        "qwen/qwen3.8-27b",
        "meta-llama/llama-4-scout-17b-16e-instruct",
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


ACTIVE_MODEL = get_best_model()

# 6. Sidebar Tools
