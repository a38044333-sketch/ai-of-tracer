import streamlit as st
from groq import Groq

# 1. Page Configuration
st.set_page_config(
    page_title="AI of Tracer",
    page_icon="logo.png",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 2. Modern UI Styling (Dark Cyberpunk Theme)
custom_css = """
    <style>
    /* Global Background & Typography */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #151b28 0%, #0b0f17 100%);
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Hide Streamlit Default Chrome */
    header[data-testid="stHeader"] {display: none !important;}
    #MainMenu {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    div[class*="viewerBadge"] {display: none !important;}
    div[class*="stDeployButton"] {display: none !important;}
    div[data-testid="stToolbar"] {display: none !important;}

    /* Premium Header Card */
    .header-container {
        display: flex;
        align-items: center;
        gap: 16px;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.85));
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 20px;
        padding: 16px 20px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 0 15px rgba(56, 189, 248, 0.15);
        backdrop-filter: blur(12px);
    }
    .header-title {
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: -0.5px;
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
    .founder-tag {
        color: #94a3b8;
        font-size: 0.82rem;
        margin-top: 4px;
    }
    .founder-tag b {
        color: #38bdf8;
    }

    /* Chat Messages Glassmorphism */
    div[data-testid="stChatMessage"] {
        background: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 14px 18px !important;
        margin-bottom: 12px !important;
        backdrop-filter: blur(8px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    /* User chat bubble accent */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
        background: rgba(56, 189, 248, 0.08) !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
    }

    /* Fixed Bottom Input Styling */
    div[data-testid="stChatInput"] {
        border-radius: 24px !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        background: rgba(15, 23, 42, 0.95) !important;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.15) !important;
    }
    div[data-testid="stChatInput"]:focus-within {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.35) !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: #0f172a !important;
        border-right: 1px solid rgba(56, 189, 248, 0.15) !important;
    }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 3. Header Branding Component
header_html = """
<div class="header-container">
    <div>
        <div class="header-title">⚡ AI of Tracer</div>
        <div class="header-badge">ULTRA FAST INTELLIGENCE</div>
        <div class="founder-tag">Created & Founded by <b>Aman Chauhan</b></div>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# 4. Groq Client Setup
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

# 5. Sidebar: Tools & Profile
with st.sidebar:
  st.markdown("### 📸 Vision & Camera")
  captured_img = st.camera_input("Tracer Vision Lens")
  if captured_img:
    st.success("✨ Visual frame captured successfully!")

  st.markdown("---")
  st.markdown("### 👤 Founder Profile")
  st.markdown("**App:** AI of Tracer")
  st.markdown("**Founder & Creator:** Aman Chauhan")
  st.info(
      "💡 **Voice Prompting:** Tap the mic button on your phone keyboard to"
      " speak directly to Tracer!"
  )

# 6. Chat History & Logic
if "messages" not in st.session_state:
  st.session_state.messages = [{
      "role": "assistant",
      "content": (
          "Hello! I am **AI of Tracer**, built and founded by **Aman Chauhan**."
          " How can I help you today?"
      ),
  }]

for msg in st.session_state.messages:
  with st.chat_message(msg["role"]):
    st.markdown(msg["content"])

if prompt := st.chat_input("Ask Tracer anything..."):
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  with st.chat_message("assistant"):
    try:
      stream = client.chat.completions.create(
          messages=[
              {
                  "role": "system",
                  "content": (
                      "You are AI of Tracer, a futuristic, ultra-intelligent"
                      " and fast AI assistant. Your founder, creator, and owner"
                      " is Aman Chauhan. Whenever anyone asks who created you,"
                      " who made you, who owns you, or who your founder is,"
                      " always proudly state that you were created and founded"
                      " by Aman Chauhan. Be helpful, concise, and polite."
                  ),
              },
              {"role": "user", "content": prompt},
          ],
          model=ACTIVE_MODEL,
          stream=True,
      )

      def generate_chunks():
        for chunk in stream:
          content = chunk.choices[0].delta.content
          if content:
            yield content

      bot_reply = st.write_stream(generate_chunks)
      st.session_state.messages.append(
          {"role": "assistant", "content": bot_reply}
      )

    except Exception as e:
      st.error(f"Error: {e}")
