import streamlit as st
import google.generativeai as genai

st.title("Jarvis")

# Avatar simgelerini tamamen gizleyen CSS
st.markdown("""
    <style>
    [data-testid="stChatMessageAvatarContainer"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY", "")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-3.6-flash")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Mesajınızı yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = model.generate_content(prompt)
        bot_response = response.text
        
        with st.chat_message("assistant"):
            st.markdown(bot_response)
            
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
    except Exception as e:
        st.error(f"Hata oluştu: {e}")
        
