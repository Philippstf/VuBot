# scripts/app.py

import streamlit as st
from ask_bot import ask_bot

st.set_page_config(
    page_title="🤖 VuWall KI-Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 VuWall KI-Chatbot")
st.markdown(
    "Stelle eine Frage zu **VuWall**-Produkten, -Lösungen oder -Funktionen."
)

with st.form(key="qa_form", clear_on_submit=True):
    user_question = st.text_input("Deine Frage hier …")
    submitted = st.form_submit_button("Frage stellen")

if submitted:
    if not user_question.strip():
        st.warning("Bitte zuerst eine Frage eingeben.")
    else:
        with st.spinner("Antwort wird generiert …"):
            try:
                answer = ask_bot(user_question)
                st.markdown("**Antwort:**")
                st.write(answer)
            except Exception as e:
                st.error(f"Fehler bei der Anfrage:\n{e}")
