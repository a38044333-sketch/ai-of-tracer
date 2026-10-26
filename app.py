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

# 2. Universal CSS to eliminate ALL Streamlit logos, badges, footers, and headers
custom_css = """
    <style>
    /* Complete dark background */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #151b28 0%, #0b0f17 100%);
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* 1. Hide entire Streamlit top bar & deploy button */
    header, header[data-testid="stHeader"], div[data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }
    #MainMenu {
        display: none !important;
        visibility: hidden !important;
    }

    /* 2. Hide entire footer and "Made with Streamlit" */
    footer {
        display: none !important;
        visibility: hidden !important;
    }

    /* 3. Hide floating bottom badge ("Hosted with Streamlit", manage app, viewer badge) */
    [data-testid="stStatusWidget"],
    .viewerBadge_container__1QSob,
    .viewerBadge_link__1S137,
    div[class*="viewerBadge"],
    div[class*="stDeployButton"],
    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"],
    div[data-testid="manage-app-button"],
    button[title*="Streamlit"],
    a[href*="streamlit.io"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    /* 4. Hide any SVG or Image containing Streamlit logo */
    svg[data-testid="stLogo"] {
        display: none !important;
    }
    img[src*="streamlit"] {
        display: none !important;
    }

    /* 5. Custom App Header */
    .header-box {
        display: flex;
        align-items: center;
        gap: 15px;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.85));
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 18px;
        padding: 12px 18px;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    .header-title {
        font-size: 1.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.2;
    }
    .header-subtitle {
        color: #94a3b8;
        font-size: 0.8rem;
        margin-top: 2px;
    }

    /* 6. Chat Bubbles */
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

    /* 7. Bottom Input Box */
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

# 3. Clean Header with your Logo (Clean Title & Subtitle)
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
      '<div class="header-title">AI of Tracer</div>', unsafe_allow_html=True
  )
  st.markdown(
      '<div class="header-subtitle">Intelligent Assistant</div>',
      unsafe_allow_html=True,
  )

# 4. In-App Web Speech Recognition Mic Button
speech_js = """
<div style="display: flex; align-items: center; justify-content: flex-end; margin-bottom: 8px;">
    <button id="tracerMicBtn" onclick="toggleTracerVoice()" style="
        background: linear-gradient(135deg,
