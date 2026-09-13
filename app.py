import streamlit as st
from groq import Groq
import uuid
import json
import os

# Sayfa Yapılandırması
j_icon_svg = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" fill="%232b2b2b"/><text x="50%" y="72%" font-family="sans-serif" font-weight="bold" font-size="70" fill="%23d0d0d0" text-anchor="middle">J</text></svg>'

st.set_page_config(
    page_title="Jarvis",
    page_icon=j_icon_svg,
    layout="centered"
)

# --- KALICI VERİ SAKLAMA (JSON) ---
DB_FILE = "chats.json"

def load_chats():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_chats(chats):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(chats, f, ensure_ascii=False, indent=2)

if "chats" not in st.session_state:
    st.session_state.chats = load_chats()

if "current_chat_id" not in st.session_state or st.session_state.current_chat_id not in st.session_state.chats:
    if st.session_state.chats:
        st.session_state.current_chat_id = list(st.session_state.chats.keys())[-1]
    else:
        new_id = str(uuid.uuid4())
        st.session_state.chats[new_id] = {"title": "Yeni Sohbet", "messages": []}
        st.session_state.current_chat_id = new_id
        save_chats(st.session_state.chats)

current_chat = st.session_state.chats[st.session_state.current_chat_id]
messages = current_chat["messages"]

# --- SOL MENÜ (SIDEBAR) ---
with st.sidebar:
    st.title("⚙️ Jarvis Ayarları")
    
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.chats[new_id] = {"title": "Yeni Sohbet", "messages": []}
        st.session_state.current_chat_id = new_id
        save_chats(st.session_state.chats)
        st.rerun()

    st.subheader("💬 Geçmiş Sohbetler")
    
    for chat_id, chat_data in list(st.session_state.chats.items()):
        button_label = f"💬 {chat_data['title']}"
        if chat_id == st.session_state.current_chat_id:
            button_label = f"▶️ {chat_data['title']}"
            
        if st.button(button_label, key=chat_id, use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.rerun()

    st.divider()
    if st.button("🗑️ Tüm Sohbetleri Temizle", use_container_width=True):
        st.session_state.chats = {}
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        new_id = str(uuid.uuid4())
        st.session_state.chats[new_id] = {"title": "Yeni Sohbet", "messages": []}
        st.session_state.current_chat_id = new_id
        save_chats(st.session_state.chats)
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

for message in messages:
    role_class = "user-bubble" if message["role"] == "user" else "assistant-bubble"
    st.markdown(f'<div class="chat-bubble {role_class}">{message["content"]}</div>', unsafe_allow_html=True)

if prompt := st.chat_input("Mesajınızı yazın..."):
    if len(messages) == 0:
        current_chat["title"] = prompt[:20] + ("..." if len(prompt) > 20 else "")

    messages.append({"role": "user", "content": prompt})

    # Güncel ve Aktif Groq Modelleri
    candidate_models = [
        "llama-3.3-70b-versatile",
        "llama3-8b-8192",
        "llama3-70b-8192",
        "mixtral-8x7b-32768"
    ]
    
    system_prompt = {
        "role": "system",
        "content": "Your name is Jarvis. You are an AI assistant named Jarvis. NEVER claim to be ChatGPT or OpenAI. Always remember conversation details provided by the user in this chat session."
    }

    api_payload = [system_prompt] + [
        {"role": m["role"], "content": m["content"]} 
        for m in messages
    ]

    bot_response = None
    last_error = None

    with st.spinner("Jarvis düşünüyor..."):
        for model_name in candidate_models:
            try:
                completion = client.chat.completions.create(
                    model=model_name,
                    messages=api_payload,
                )
                bot_response = completion.choices[0].message.content
                break
            except Exception as e:
                last_error = e

    if bot_response:
        messages.append({"role": "assistant", "content": bot_response})
        save_chats(st.session_state.chats)
        st.rerun()
    else:
        st.error(f"Hata oluştu: {last_error}")
        
