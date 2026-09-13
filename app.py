import streamlit as st
from groq import Groq
import uuid

# Sayfa Yapılandırması
j_icon_svg = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" fill="%232b2b2b"/><text x="50%" y="72%" font-family="sans-serif" font-weight="bold" font-size="70" fill="%23d0d0d0" text-anchor="middle">J</text></svg>'

st.set_page_config(
    page_title="Jarvis",
    page_icon=j_icon_svg,
    layout="centered"
)

# --- SOHBET GEÇMİŞİ VERİ YAPISI ---
if "chats" not in st.session_state:
    st.session_state.chats = {}  # Tüm sohbetler: {chat_id: {"title": str, "messages": list}}

if "current_chat_id" not in st.session_state or st.session_state.current_chat_id not in st.session_state.chats:
    # İlk sohbeti oluştur
    new_id = str(uuid.uuid4())
    st.session_state.chats[new_id] = {"title": "Yeni Sohbet", "messages": []}
    st.session_state.current_chat_id = new_id

# Aktif sohbetin mesajları
current_chat = st.session_state.chats[st.session_state.current_chat_id]
messages = current_chat["messages"]


# --- SOL MENÜ (SIDEBAR) ---
with st.sidebar:
    st.title("⚙️ Jarvis Ayarları")
    
    # Yeni Sohbet Başlat Butonu
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.chats[new_id] = {"title": "Yeni Sohbet", "messages": []}
        st.session_state.current_chat_id = new_id
        st.rerun()

    st.subheader("💬 Geçmiş Sohbetler")
    
    # Geçmiş sohbetleri listele
    for chat_id, chat_data in list(st.session_state.chats.items()):
        # Aktif sohbeti vurgulamak için stil
        button_label = f"💬 {chat_data['title']}"
        if chat_id == st.session_state.current_chat_id:
            button_label = f"▶️ {chat_data['title']}"
            
        if st.button(button_label, key=chat_id, use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.rerun()

    st.divider()
    if st.button("🗑️ Tüm Sohbetleri Temizle", use_container_width=True):
        st.session_state.chats = {}
        new_id = str(uuid.uuid4())
        st.session_state.chats[new_id] = {"title": "Yeni Sohbet", "messages": []}
        st.session_state.current_chat_id = new_id
        st.rerun()


# --- ANA EKRAN ---
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

# Aktif sohbetin mesajlarını ekrana yazdır
for message in messages:
    role_class = "user-bubble" if message["role"] == "user" else "assistant-bubble"
    st.markdown(f'<div class="chat-bubble {role_class}">{message["content"]}</div>', unsafe_allow_html=True)

# Kullanıcı Girişi
if prompt := st.chat_input("Mesajınızı yazın..."):
    # Eğer sohbet henüz isimlendirilmediyse (ilk mesajsa) başlığı güncelle
    if len(messages) == 0:
        current_chat["title"] = prompt[:20] + ("..." if len(prompt) > 20 else "")

    messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="chat-bubble user-bubble">{prompt}</div>', unsafe_allow_html=True)

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
                    for m in messages
                ],
            )
            bot_response = completion.choices[0].message.content
            break
        except Exception as e:
            last_error = e

    if bot_response:
        st.markdown(f'<div class="chat-bubble assistant-bubble">{bot_response}</div>', unsafe_allow_html=True)
        messages.append({"role": "assistant", "content": bot_response})
    else:
        st.error(f"Hata oluştu: {last_error}")
        
