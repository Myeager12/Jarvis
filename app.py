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

#!/usr/bin/env python3
"""
Simple chatbot with persistent memory.

Requirements:
    pip install openai
"""

import json
import os
import openai
from typing import List, Dict

# --------------------------------------------------------------
# CONFIGURATION
# --------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Please set OPENAI_API_KEY environment variable")
openai.api_key = OPENAI_API_KEY

# Where we keep the user profile (very small, minimal personal data)
PROFILE_PATH = "chatbot_profile.json"
# How many turns we keep in short‑term context (you can increase if needed)
CONTEXT_WINDOW = 5

# --------------------------------------------------------------
# MEMORY HANDLER
# --------------------------------------------------------------
class Memory:
    """
    Handles both short‑term context and a tiny persistent profile.
    """
    def __init__(self, profile_path: str = PROFILE_PATH):
        self.profile_path = profile_path
        self.profile: Dict = self._load_profile()
        # Short‑term conversation history (list of {"role":..., "content":...})
        self.short_term: List[Dict] = []

    # ---- persistent profile ----
    def _load_profile(self) -> Dict:
        if os.path.exists(self.profile_path):
            try:
                with open(self.profile_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        # Default profile if file missing or corrupt
        return {"name": None, "preferences": {}, "last_topic": None}

    def save_profile(self) -> None:
        with open(self.profile_path, "w", encoding="utf-8") as f:
            json.dump(self.profile, f, indent=2, ensure_ascii=False)

    def set_user_info(self, name: str = None, preferences: Dict = None, last_topic: str = None) -> None:
        if name is not None:
            self.profile["name"] = name
        if preferences is not None:
            self.profile["preferences"].update(preferences)
        if last_topic is not None:
            self.profile["last_topic"] = last_topic

    def get_user_info(self) -> Dict:
        return self.profile

    # ---- short‑term context ----
    def add_to_context(self, role: str, content: str) -> None:
        """Add a new turn and keep only the most recent CONTEXT_WINDOW turns."""
        self.short_term.append({"role": role, "content": content})
        if len(self.short_term) > CONTEXT_WINDOW:
            self.short_term.pop(0)

    def get_context(self) -> List[Dict]:
        return self.short_term

# --------------------------------------------------------------
# CHATBOT LOGIC
# --------------------------------------------------------------
class ChatBot:
    def __init__(self, memory: Memory):
        self.memory = memory

    def ask(self, user_input: str) -> str:
        # Store user turn in context
        self.memory.add_to_context(role="user", content=user_input)

        # Build prompt: start with a system message that gives the bot its "persona"
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. "
                    "Use the short‑term context to keep the conversation flowing. "
                    "If the user mentions their name, greet them by name. "
                    "If the user mentions a preference (e.g., \"I like jazz\"), remember it in the profile."
                ),
            }
        ]

        # Insert short‑term context
        messages.extend(self.memory.get_context())

        # Send request to OpenAI
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # pick whatever model you have access to
            messages=messages,
            temperature=0.7,
            max_tokens=512,
        )
        assistant_reply = completion.choices[0].message["content"].strip()

        # Store assistant turn in context
        self.memory.add_to_context(role="assistant", content=assistant_reply)

        # (Optional) Detect user name or preferences in the reply
        # This is a very naive pattern matcher; replace with NLP if you need more accuracy.
        if self.memory.profile["name"] is None:
            if "hi" in assistant_reply.lower() or "hello" in assistant_reply.lower():
                # Guessing name from a phrase like "Hello, I'm Jane!"
                words = assistant_reply.split()
                for i, w in enumerate(words):
                    if w.lower() in {"i", "I'm"} and i + 1 < len(words):
                        self.memory.set_user_info(name=words[i + 1].rstrip("!.?"))
                        break

        # Persist profile after each turn
        self.memory.save_profile()
        return assistant_reply

# --------------------------------------------------------------
# RUN A SIMPLE CLI SESSION
# --------------------------------------------------------------
def main():
    mem = Memory()
    bot = ChatBot(mem)

    print("Hi! I'm Jarvis. Type 'quit' to exit.")
    while True:
        try:
            user_input = input("> ").strip()
        except EOFError:   # Ctrl-D
            break
        if user_input.lower() in {"quit", "exit"}:
            break

        # If user says something like "My name is Alice" we store it
        if "my name is" in user_input.lower():
            parts = user_input.split()
            # Very naive extraction; replace with better NLP if needed.
            try:
                idx = parts.index("is")
                name = parts[idx + 1].rstrip("!.?")
                mem.set_user_info(name=name)
                print(f"Got it! I'll call you {name}.")
                continue
            except ValueError:
                pass

        reply = bot.ask(user_input)
        print(reply)

    print("\nThanks for chatting! See you next time.")


if __name__ == "__main__":
    main()
