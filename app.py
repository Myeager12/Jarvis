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
# conversation.py
import openai
from typing import List, Dict

class Conversation:
    def __init__(self, model="gpt-4o-mini", system_prompt="You are a helpful assistant."):
        self.model = model
        self.messages: List[Dict[str, str]] = []
        # System prompt is always first
        self.messages.append({"role": "system", "content": system_prompt})

    def add_user(self, text: str):
        self.messages.append({"role": "user", "content": text})

    def add_assistant(self, text: str):
        self.messages.append({"role": "assistant", "content": text})

    def last_response(self):
        # Returns the assistant's last reply
        for msg in reversed(self.messages):
            if msg["role"] == "assistant":
                return msg["content"]
        return None

    def to_file(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            for m in self.messages:
                f.write(f"{m['role']}: {m['content']}\n\n")

    def from_file(self, path: str):
        self.messages = []
        with open(path, "r", encoding="utf-8") as f:
            role = None
            content = ""
            for line in f:
                line = line.rstrip()
                if not line:
                    continue
                if line.endswith(":"):
                    if role and content:
                        self.messages.append({"role": role, "content": content.strip()})
                    role = line[:-1].lower()
                    content = ""
                else:
                    content += line + " "
            if role and content:
                self.messages.append({"role": role, "content": content.strip()})

    def ask(self, text: str):
        self.add_user(text)
        response = openai.chat.completions.create(
            model=self.model,
            messages=self.messages,
        )
        answer = response.choices[0].message.content
        self.add_assistant(answer)
        return answer

# Usage
if __name__ == "__main__":
    conv = Conversation()
    print(conv.ask("Hi! How can I help you today?"))
    print(conv.ask("I had a conversation earlier about saving history."))
    conv.to_file("chat_history.txt")
