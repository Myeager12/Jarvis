import streamlit as st
import google.generativeai as genai

# Siyah arka planlı J harfi simgesi (Favicon) ve başlık ayarı
st.set_page_config(
    page_title="Jarvis",
    page_icon="https://img.icons8.com/ios-filled/100/333333/j.png",
    layout="centered"
)

st.title("Jarvis")

# Simgeleri tamamen kaldıran ve sade baloncuklar oluşturan CSS
st.markdown("""
    <style>
    .chat-bubble {
        padding: 12px 16px;
        border-radius: 12px;
        margin-bottom: 10px;
        max-width: 85%;
        word-wrap: break-word;
        font-family: sans-serif;
        line-height: 1.5;
    }
    .user-bubble {
        background-color: #f0f2f6;
        color: #111;
        margin-left: auto;
    }
    .assistant-bubble {
        background-color: #e8f0fe;
        color: #111;
        margin-right: auto;
    }
    </style>
""", unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY", "")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-3.6-flash")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesajları ekrana yaz
for message in st.session_state.messages:
    role_class = "user-bubble" if message["role"] == "user" else "assistant-bubble"
    st.markdown(f'<div class="chat-bubble {role_class}">{message["content"]}</div>', unsafe_allow_html=True)

if prompt := st.chat_input("Mesajınızı yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="chat-bubble user-bubble">{prompt}</div>', unsafe_allow_html=True)

    try:
        response = model.generate_content(prompt)
        bot_response = response.text
        
        st.markdown(f'<div class="chat-bubble assistant-bubble">{bot_response}</div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
    except Exception as e:
        st.error(f"Hata oluştu: {e}")
        
