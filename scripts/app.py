# scripts/app_chat.py

import streamlit as st
import uuid
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ask_bot import ask_bot_with_context
from database.service import chat_service
from dotenv import load_dotenv

load_dotenv()

# ─── Streamlit Konfiguration ────────────────────────────────────────────────────

st.set_page_config(
    page_title="🤖 VuWall KI-Chatbot",
    page_icon="🤖",
    layout="centered"
)

# ─── Session State Initialisierung ──────────────────────────────────────────────

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# ─── Helper Functions ────────────────────────────────────────────────────────────

def get_or_create_conversation():
    """Holt oder erstellt eine Konversation für die Session"""
    if not st.session_state.conversation_id:
        conversation = chat_service.get_or_create_conversation(
            user_id=st.session_state.user_id,
            title="Neue Unterhaltung"
        )
        st.session_state.conversation_id = conversation.id
    return st.session_state.conversation_id

def load_conversation_messages():
    """Lädt Nachrichten aus der Datenbank in Session State"""
    if st.session_state.conversation_id:
        messages = chat_service.get_conversation_messages(st.session_state.conversation_id)
        st.session_state.messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

def save_message(role: str, content: str, embedding_context: str = None):
    """Speichert eine Nachricht in der Datenbank"""
    conversation_id = get_or_create_conversation()
    chat_service.add_message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        embedding_used=embedding_context
    )

def start_new_conversation():
    """Startet eine neue Konversation"""
    conversation = chat_service.create_new_conversation(
        user_id=st.session_state.user_id,
        title=f"Chat {len(st.session_state.messages) + 1}"
    )
    st.session_state.conversation_id = conversation.id
    st.session_state.messages = []

def generate_conversation_title(first_question: str) -> str:
    """Generiert einen aussagekräftigen Titel basierend auf der ersten Frage"""
    # Einfache Titel-Generierung - kann später durch LLM erweitert werden
    if len(first_question) > 50:
        return first_question[:47] + "..."
    return first_question

# ─── UI Layout ───────────────────────────────────────────────────────────────────

st.title("🤖 VuWall KI-Chatbot")
st.markdown("Dein persönlicher Assistent für **VuWall**-Produkte und -Lösungen")

# Sidebar für Konversations-Management
with st.sidebar:
    st.header("💬 Unterhaltungen")
    
    if st.button("🆕 Neue Unterhaltung", use_container_width=True):
        start_new_conversation()
        st.rerun()
    
    # Zeige verfügbare Konversationen
    conversations = chat_service.get_user_conversations(st.session_state.user_id, limit=10)
    
    if conversations:
        st.subheader("Letzte Chats")
        for conv in conversations:
            # Zeige Konversation mit Button
            button_text = conv.title or f"Chat {conv.id}"
            if len(button_text) > 30:
                button_text = button_text[:27] + "..."
            
            is_current = conv.id == st.session_state.conversation_id
            if st.button(
                f"{'📍 ' if is_current else '💬 '}{button_text}",
                key=f"conv_{conv.id}",
                use_container_width=True,
                type="primary" if is_current else "secondary"
            ):
                st.session_state.conversation_id = conv.id
                load_conversation_messages()
                st.rerun()

# ─── Chat Interface ──────────────────────────────────────────────────────────────

# Ensure we have a conversation
conversation_id = get_or_create_conversation()

# Load messages if conversation was just selected
if not st.session_state.messages and st.session_state.conversation_id:
    load_conversation_messages()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Stelle deine Frage zu VuWall..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate bot response
    with st.chat_message("assistant"):
        with st.spinner("Antwort wird generiert..."):
            try:
                # Use enhanced bot function with conversation context
                answer, embedding_context = ask_bot_with_context(
                    question=prompt,
                    conversation_id=conversation_id
                )
                
                st.markdown(answer)
                
                # Add assistant message to chat history
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
                # Save both messages to database
                save_message("user", prompt)
                save_message("assistant", answer, embedding_context)
                
                # Update conversation title if this is the first message
                if len(st.session_state.messages) == 2:  # user + assistant
                    title = generate_conversation_title(prompt)
                    chat_service.update_conversation_title(conversation_id, title)
                
            except Exception as e:
                error_msg = f"Entschuldigung, es ist ein Fehler aufgetreten: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# ─── Footer ──────────────────────────────────────────────────────────────────────

# st.markdown("---")
# st.markdown(
#        "💡 **Tipp:** Du kannst mehrere Fragen in einer Unterhaltung stellen. "
#        "Der Bot erinnert sich an den Kontext eurer Unterhaltung!"
#    )