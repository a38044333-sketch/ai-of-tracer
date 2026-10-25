import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text

st.set_page_config(page_title="AI of Tracer", page_icon="⚡", layout="centered")

st.title("⚡ AI of Tracer")
st.caption("Free Unlimited AI Assistant — Founded by Aman Chauhan")

# Replace with your actual Groq API key (starts with gsk_...)
GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

@st.cache_resource
def get_best_model():
    try:
        model_list = [m.id for m in client.models.list().data]
        preferred = [
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
    return "openai/gpt-oss-20b"

ACTIVE_MODEL = get_best_model()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar: Camera & Voice Tools ---
with st.sidebar:
    st.header("📸 Visual & Audio Input")
    
    # 1. Camera Input Feature
    captured_img = st.camera_input("Take a photo")
    if captured_img:
        st.success("Photo captured! (Tracer Vision)")
    
    # 2. Mic Input Feature (Speech to Text)
    st.write("🎙️ **Voice Input:**")
    voice_prompt = speech_to_text(language='en', start_prompt="Tap to Speak", stop_prompt="Stop Recording", key='voice_input')

# Display previous conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle Chat Input (either from keyboard or mic)
user_query = st.chat_input("Ask anything...") or voice_prompt

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

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
                    {"role": "user", "content": user_query},
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
