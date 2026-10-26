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

# 2. Clean Dark Theme & UI Styling
custom_css = """
    <style>
    .stApp {
        background: radial-gradient(circle at 50% 0%, #151b28 0%, #0b0f17 100%);
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Hide Streamlit Default Chrome */
    header, header[data-testid="stHeader"], div[data-testid="stHeader"] {display: none !important;}
    #MainMenu {display: none !important;}
    footer {display: none !important;}
    [data-testid="stStatusWidget"], div[class*="viewerBadge"], div[class*="stDeployButton"], div[data-testid="stToolbar"] {
        display: none !important;
    }

    /* Clean Cyber Header */
    .app-header {
        font-size: 1.7rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.2;
    }
    .app-subtitle {
        color: #94a3b8;
        font-size: 0.8rem;
        margin-top: 2px;
        margin-bottom: 8px;
    }

    /* Chat Messages Glassmorphism */
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

    /* Input Box */
    div[data-testid="stChatInput"] {
        border-radius: 24px !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        background: rgba(15, 23, 42, 0.95) !important;
    }

    /* Sliding Sidebar (Drawer) Styling */
    section[data-testid="stSidebar"] {
        background: #0d131f !important;
        border-right: 1px solid rgba(56, 189, 248, 0.2) !important;
    }
    .history-title {
        color: #38bdf8;
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 3. Session State Management (Chats & History)
if "chat_sessions" not in st.session_state:
  st.session_state.chat_sessions = {
      "Chat 1": [{
          "role": "assistant",
          "content": (
              "Hello! How can I help you today? Aap Hindi ya English me puch"
              " sakte hain."
          ),
      }]
  }

if "current_chat_id" not in st.session_state:
  st.session_state.current_chat_id = "Chat 1"

# 4. Sliding Sidebar: Past Searches & Chat History (Swipe/Slide open)
with st.sidebar:
  st.markdown(
      '<div class="history-title">🕒 Past Searches & History</div>',
      unsafe_allow_html=True,
  )

  # New Chat Button
  if st.button("➕ New Chat", use_container_width=True):
    new_id = f"Chat {len(st.session_state.chat_sessions) + 1}"
    st.session_state.chat_sessions[new_id] = [
        {"role": "assistant", "content": "Hello! How can I help you today?"}
    ]
    st.session_state.current_chat_id = new_id
    st.rerun()

  st.markdown("---")

  # List all past searches/sessions
  for chat_id in reversed(list(st.session_state.chat_sessions.keys())):
    first_user_msg = next(
        (
            m["content"]
            for m in st.session_state.chat_sessions[chat_id]
            if m["role"] == "user"
        ),
        None,
    )
    button_label = (
        f"💬 {first_user_msg[:24]}..." if first_user_msg else f"💬 {chat_id}"
    )

    is_active = chat_id == st.session_state.current_chat_id
    if st.button(
        button_label,
        key=f"btn_{chat_id}",
        use_container_width=True,
        type="primary" if is_active else "secondary",
    ):
      st.session_state.current_chat_id = chat_id
      st.rerun()

  st.markdown("---")
  st.markdown("### 📸 Vision Lens")
  captured_img = st.camera_input("Take a Photo")
  if captured_img:
    st.success("Frame captured!")

# 5. Header Component
col_logo, col_info = st.columns([1, 5])
with col_logo:
  if os.path.exists("logo.png"):
    st.image("logo.png", width=55)
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
      f'<div class="app-subtitle">Active: <b>{st.session_state.current_chat_id}</b> • Slide sidebar for past searches</div>',
      unsafe_allow_html=True,
  )

# 6. In-App Web Speech Recognition Mic Button
speech_js = """
<div style="display: flex; align-items: center; justify-content: flex-end; margin-bottom: 6px;">
    <button id="tracerMicBtn" onclick="toggleTracerVoice()" style="
        background: linear-gradient(135deg, #0284c7, #6366f1);
        border: none;
        color: white;
        padding: 6px 14px;
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

# 7. Groq Client
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

SYSTEM_PROMPT = """You are AI of Tracer, an advanced, highly intelligent AI assistant.

CRITICAL RULES:
1. Speak completely naturally, exactly like ChatGPT.
2. NEVER mention who created you, who made you, or Aman Chauhan on your own.
3. ONLY if the user specifically and directly asks "Who made you?", "Who created you?", "Who is your founder?", or "Tumhe kisne banaya?", answer that you were created and founded by Aman Chauhan.
4. Language: Fully fluent in Hindi (हिन्दी), Hinglish, and English.
5. Provide clear, accurate, and concise answers.
"""

ASSISTANT_AVATAR = "logo.png" if os.path.exists("logo.png") else "⚡"
current_messages = st.session_state.chat_sessions[
    st.session_state.current_chat_id
]

# 8. Render Current Active Conversation
for msg in current_messages:
  avatar_choice = ASSISTANT_AVATAR if msg["role"] == "assistant" else None
  with st.chat_message(msg["role"], avatar=avatar_choice):
    if msg.get("type") == "image":
      st.image(msg["content"], caption=msg.get("caption", "Generated Image"))
    else:
      st.markdown(msg["content"])

# 9. Handle User Prompt
if prompt := st.chat_input("Ask anything... (Hindi / English)"):
  current_messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  # Image generation detection
  image_keywords = [
      "generate image",
      "create image",
      "draw",
      "photo of",
      "image of",
      "tasveer",
      "chitra",
      "photo banao",
      "picture of",
  ]
  is_image_req = any(kw in prompt.lower() for kw in image_keywords)

  with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
    if is_image_req:
      with st.spinner("Generating image... 🎨"):
        cleaned_query = prompt.lower()
        for kw in image_keywords:
          cleaned_query = cleaned_query.replace(kw, "")
        cleaned_query = cleaned_query.strip() or "cyberpunk robot"

        image_url = f"https://image.pollinations.ai/prompt/{cleaned_query.replace(' ', '%20')}?width=1024&height=1024&nologo=true"
        st.image(image_url, caption=f"Generated: {prompt}")
        current_messages.append({
            "role": "assistant",
            "type": "image",
            "content": image_url,
            "caption": prompt,
        })
    else:
      try:
        stream = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *[
                    {"role": m["role"], "content": m["content"]}
                    for m in current_messages
                    if m.get("type") != "image"
                ],
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
        current_messages.append({"role": "assistant", "content": bot_reply})

      except Exception as e:
        st.error(f"Error: {e}")
