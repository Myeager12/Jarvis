import streamlit as st
from groq import Groq

# Sayfa Yapılandırması
j_icon_svg = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" fill="%232b2b2b"/><text x="50%" y="72%" font-family="sans-serif" font-weight="bold" font-size="70" fill="%23d0d0d0" text-anchor="middle">J</text></svg>'

st.set_page_config(
    page_title="Jarvis",
    page_icon=j_icon_svg,
    layout="centered"
)

st.title("Jarvis")

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

api_key = st.secrets.get("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    role_class = "user-bubble" if message["role"] == "user" else "assistant-bubble"
    st.markdown(f'<div class="chat-bubble {role_class}">{message["content"]}</div>', unsafe_allow_html=True)

if prompt := st.chat_input("Mesajınızı yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="chat-bubble user-bubble">{prompt}</div>', unsafe_allow_html=True)

    # Denediğimiz güncel modeller listesi
    candidate_models = [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "openai/gpt-oss-20b"
    ]
    
    bot_response = None
    last_error = None

    for model_name in candidate_models:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
            )
            bot_response = completion.choices[0].message.content
            break  # Başarılı olursa döngüden çık
        except Exception as e:
            last_error = e

    if bot_response:
        st.markdown(f'<div class="chat-bubble assistant-bubble">{bot_response}</div>', unsafe_allow_html=True)
    
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
    else:
        st.error(f"Hata oluştu: {last_error}")
        import streamlit as st
from groq import Groq

import streamlit as st
from groq import Groq

st.set_page_config(page_title="Jarvis", page_icon="🤖", layout="wide")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Sol Yan Menü (Sidebar)
with st.sidebar:
    st.title("⚙️ Jarvis Ayarları")
    selected_model = st.selectbox(
        "Model Seçin:",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"],
        index=0
    )
    if st.button("🗑️ Sohbeti Temizle", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Mesaj Geçmişi Başlatma
if "messages" not in st.session_state:
    st.session_state.messages = []

# 1. Önceki tüm mesajları ekrana bas
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

    # Model yanıtını al
    with st.chat_message("assistant"):
        try:
            # API'ye geçmişi temiz bir formatta gönderiyoruz
            api_messages = [
                {"role": m["role"], "content": m["content"]} 
                for m in st.session_state.messages
            ]
            
            response = client.chat.completions.create(
                model=selected_model,
                messages=api_messages
            )
            
            full_response = response.choices[0].message.content
            st.markdown(full_response)
            
            # Asistan yanıtını geçmişe kaydet
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
