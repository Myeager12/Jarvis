import streamlit as st
from groq import Groq

# Sayfa Yapılandırması
j_icon_svg = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" fill="%232b2b2b"/><text x="50%" y="72%" font-family="sans-serif" font-weight="bold" font-size="70" fill="%23d0d0d0" text-anchor="middle">J</text></svg>'

st.set_page_config(
    page_title="Jarvis",
    page_icon=j_icon_svg,
    layout="centered"
)

# Özel Stil Tanımlamaları
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

# Sol Menü (Sidebar / 3 Çizgi)
with st.sidebar:
    st.title("⚙️ Jarvis Ayarları")
    
    # Model seçimi menüsü
    selected_model = st.selectbox(
        "Öncelikli Model Seçin:",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"],
        index=0
    )
    
    st.divider()
    
    # Sohbeti temizleme butonu
    if st.button("🗑️ Sohbeti Temizle", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

# 1. Önceki Mesajları Göster
for message in st.session_state.messages:
    role_class = "user-bubble" if message["role"] == "user" else "assistant-bubble"
    st.markdown(f'<div class="chat-bubble {role_class}">{message["content"]}</div>', unsafe_allow_html=True)

# 2. Yeni Mesaj Alanı
if prompt := st.chat_input("Mesajınızı yazın..."):
    # Kullanıcı mesajını ekle
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Yedek model listesi (İlk sıraya sidebardaki seçimi koyuyoruz)
    candidate_models = [
        selected_model,
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant"
    ]
    # Tekrarlayan modelleri listeden temizle
    candidate_models = list(dict.fromkeys(candidate_models))
    
    bot_response = None
    last_error = None

    # Groq API Çağrısı
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
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
    else:
        st.error(f"Hata oluştu: {last_error}")

    # Sayfayı yenileyip tüm mesajların düzenli basılmasını sağla
    st.rerun()
