import streamlit as st
import streamlit.components.v1 as components
from groq import Groq

# 1. Page Configuration
st.set_page_config(
    page_title="AI of Tracer",
    page_icon="logo.png",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 2. Modern UI & Dark Mode Styling
custom_css = """
    <style>
    .stApp {
        background: radial-gradient(circle at 50% 0%, #151b28 0%, #0b0f17 100%);
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    header[data-testid="stHeader"] {display: none !important;}
    #MainMenu {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    div[class*="viewerBadge"] {display: none !important;}
    div[class*="stDeployButton"] {display: none !important;}
    div[data-testid="stToolbar"] {display: none !important;}

    /* Premium Header */
    .header-container {
        display: flex;
        align-items: center;
        gap: 16px;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.85));
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 20px;
        padding: 16px 20px;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 0 15px rgba(56, 189, 248, 0.15);
        backdrop-filter: blur(12px);
    }
    .header-title {
        font-size: 1.8rem;
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
        font-size: 0.75rem;
        font-weight: 600;
        margin-top: 4px;
    }

    /* Chat Messages Glassmorphism */
    div[data-testid="stChatMessage"] {
        background: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 14px 18px !important;
        margin-bottom: 12px !important;
        backdrop-filter: blur(8px);
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
        background: rgba(56, 189, 248, 0.08) !important;
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

# 3. Header Branding
header_html = """
<div class="header-container">
    <div>
        <div class="header-title">⚡ AI of Tracer</div>
        <div class="header-badge">ULTRA FAST INTELLIGENCE</div>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# 4. In-App Web Speech Recognition Mic Button (Audio Dictation)
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
        recognition.lang = 'hi-IN'; // Supports Hindi + Hinglish + English
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = function() {
            recognizing = true;
            btn.style.background = 'linear-gradient(135deg, #ef4
