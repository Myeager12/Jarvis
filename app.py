import streamlit as st
import google.generativeai as genai

st.title("Jarvis")

api_key = st.secrets.get("AQ.Ab8RN6IQSedMY3QC1yaoFWFmxPWdGbSqbBKMOhgYDAKk9K5Bqg", "")
genai.configure(api_key=api_key)

# En güncel model tanımlandı
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
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Hata: {e}")
        
