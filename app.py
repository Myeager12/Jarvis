import streamlit as st
from groq import Groq

# Sayfa Yapılandırması ve Favicon (Siyah J SVG)
j_icon_svg = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" fill="%232b2b2b"/><text x="50%" y="72%" font-family="sans-serif" font-weight="bold" font-size="70" fill="%23d0d0d0" text-anchor="middle">J</text></svg>'

st.set_page_config(
    page_title="Jarvis",
    page_icon=j_icon_svg,
    layout="centered"
)

st.title("Jarvis")

# Baloncuk stilleri
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

# Groq İstemcisi
api_key = st.secrets.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski mesajları ekrana yaz
for message in st.session_state.messages:
    role_class = "user-bubble" if message["role"] == "user" else "assistant-bubble"
    st.markdown(f'<div class="chat-bubble {role_class}">{message["content"]}</div>', unsafe_allow_html=True)

if prompt := st.chat_input("Mesajınızı yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="chat-bubble user-bubble">{prompt}</div>', unsafe_allow_html=True)

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
        )
        bot_response = completion.choices[0].message.content
        
        st.markdown(f'<div class="chat-bubble assistant-bubble">{bot_response}</div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
    except Exception as e:
        st.error(f"Hata oluştu: {e}")
        
