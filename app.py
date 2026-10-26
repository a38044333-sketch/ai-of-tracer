import streamlit as st
from groq import Groq

# 1. Custom Tab Name & Icon (Favicon)
st.set_page_config(
    page_title="AI of Tracer",
   page_icon="logo.png",
    layout="centered"
)

# 2. Hide Streamlit Branding (Hamburger menu, Footer, and Deploy button)
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_container__1QSob {display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 3. Your App Branding & Header
col1, col2 = st.columns([1, 5])
with col1:
    # If you upload a logo.png, replace the markdown below with: st.image("logo.png", width=70)
    st.image("logo.png", width=70), unsafe_allow_html=True)
with col2:
    st.title("AI of Tracer")
    st.caption("Official AI Assistant — Created & Founded by Aman Chauhan")

# Your Groq API key
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

# --- Sidebar: Visual Input & Profile ---
with st.sidebar:
    st.header("📸 Visual Input")
    captured_img = st.camera_input("Take a photo")
    if captured_img:
        st.success("Photo captured! (Tracer Vision)")
    st.divider()
    st.markdown("**App:** AI of Tracer")
    st.markdown("**Founder & Owner:** Aman Chauhan")
    st.info("💡 **Voice Tip:** Use the mic icon on your mobile Gboard keyboard to talk directly!")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User prompt input
if prompt := st.chat_input("Ask anything..."):
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
                            "You are AI of Tracer, an intelligent and fast AI assistant. "
                            "Your founder, creator, and owner is Aman Chauhan. "
                            "Whenever anyone asks who created you, who made you, who owns you, "
                            "or who your founder is, always proudly state that you were created "
                            "and founded by Aman Chauhan."
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
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})

        except Exception as e:
            st.error(f"Error: {e}")
