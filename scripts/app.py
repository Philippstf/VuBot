# scripts/app_chat.py

import streamlit as st
import uuid
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ask_bot import ask_bot_with_context
from storage.local_chat_manager import local_chat_manager
from dotenv import load_dotenv

load_dotenv()

# ─── Custom Chat Display Function ──────────────────────────────────────────────

def display_chat_message(role, content, avatar_path=None):
    """Zeigt eine Chat-Nachricht mit custom HTML/CSS"""
    if role == "user":
        # User message - rechts ausgerichtet, blau
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-end; margin: 10px 0; align-items: flex-end;">
            <div style="background: linear-gradient(135deg, #007ACC, #0056b3); color: white; 
                        padding: 12px 16px; border-radius: 20px 20px 5px 20px; 
                        max-width: 70%; margin-right: 8px; box-shadow: 0 2px 8px rgba(0,122,204,0.3);
                        font-size: 14px; line-height: 1.4;">
                {content}
            </div>
            <div style="width: 40px; height: 40px; background-color: #ff6b6b; border-radius: 50%; 
                        display: flex; align-items: center; justify-content: center; 
                        font-size: 18px; color: white; flex-shrink: 0;">
                👤
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Assistant message - links ausgerichtet, grau
        avatar_img = ""
        if avatar_path:
            avatar_img = f'<img src="data:image/png;base64,{get_base64_image(avatar_path)}" style="width: 30px; height: 30px; object-fit: contain;">'
        else:
            avatar_img = "🤖"
            
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-start; margin: 10px 0; align-items: flex-end;">
            <div style="width: 40px; height: 40px; background-color: white; border-radius: 50%; 
                        display: flex; align-items: center; justify-content: center; 
                        border: 1px solid #ddd; flex-shrink: 0; margin-right: 8px;">
                {avatar_img}
            </div>
            <div style="background: #f8f9fa; color: #2c3e50; 
                        padding: 12px 16px; border-radius: 20px 20px 20px 5px; 
                        max-width: 70%; border: 1px solid #e9ecef; 
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        font-size: 14px; line-height: 1.4;">
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)

def get_base64_image(image_path):
    """Konvertiert Bild zu base64 für HTML einbettung"""
    try:
        import base64
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

# ─── Streamlit Konfiguration ────────────────────────────────────────────────────

st.set_page_config(
    page_title="🤖 VuWall KI-Chatbot",
    page_icon="🤖",
    layout="centered"
)

# ─── Session State Initialisierung ──────────────────────────────────────────────

# Browser-basierte Device-ID (ersetzt user_id)
if "device_id" not in st.session_state:
    from storage.device_id import get_device_id
    st.session_state.device_id = get_device_id()

# Initialisiere LocalStorage Session State
if "local_conversations" not in st.session_state:
    st.session_state.local_conversations = []

if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# Lade Chat-Daten aus Browser Storage beim ersten Start
if "storage_loaded" not in st.session_state:
    # Debug: Zeige Loading Status
    with st.spinner("Lade Chat-Verlauf..."):
        local_chat_manager.load_from_browser()
    st.session_state.storage_loaded = True
    
    # Debug Info zeigen
    if st.session_state.local_conversations:
        st.info(f"✅ {len(st.session_state.local_conversations)} Chat(s) wiederhergestellt!")

# ─── Helper Functions ────────────────────────────────────────────────────────────

def get_or_create_conversation():
    """Holt oder erstellt eine Konversation (LocalStorage)"""
    conversation = local_chat_manager.get_current_conversation()
    return conversation["id"]

def load_conversation_messages(conversation_id: int):
    """Lädt Nachrichten aus LocalStorage in Session State"""
    messages = local_chat_manager.get_conversation_messages(conversation_id)
    st.session_state.messages = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in messages
    ]

def save_message(role: str, content: str, embedding_context: str = None):
    """Speichert eine Nachricht im LocalStorage"""
    local_chat_manager.add_message(
        role=role,
        content=content,
        embedding_context=embedding_context
    )

def start_new_conversation():
    """Startet eine neue Konversation"""
    conversation = local_chat_manager.create_conversation(
        title=f"Chat {len(local_chat_manager.get_all_conversations()) + 1}"
    )
    st.session_state.messages = []
    # Session State wird automatisch durch local_chat_manager aktualisiert

def generate_conversation_title(first_question: str) -> str:
    """Generiert einen aussagekräftigen Titel basierend auf der ersten Frage"""
    # Einfache Titel-Generierung - kann später durch LLM erweitert werden
    if len(first_question) > 50:
        return first_question[:47] + "..."
    return first_question

# ─── UI Layout ───────────────────────────────────────────────────────────────────

# Header mit VuWall Logo - Mobile Responsive
st.markdown("""
<style>
@media (max-width: 768px) {{
    .header-container {{
        flex-direction: column !important;
        align-items: center !important;
        text-align: center !important;
    }}
    .header-container img {{
        margin-right: 0 !important;
        margin-bottom: 10px !important;
        height: 50px !important;
    }}
    .header-container h1 {{
        font-size: 2.2rem !important;
    }}
}}
</style>
<div class="header-container" style="display: flex; align-items: center; margin-bottom: 20px;">
    <img src="data:image/webp;base64,{}" style="height: 60px; margin-right: 15px;">
    <h1 style="margin: 0; color: white; font-size: 3.2rem; font-weight: bold;">KI-Chatbot</h1>
</div>
""".format(get_base64_image("utils/VuWall_transparent.webp")), unsafe_allow_html=True)

st.markdown("Dein persönlicher Assistent für **VuWall**-Produkte und -Lösungen")

# Sidebar für Konversations-Management
with st.sidebar:
    # VuWall Logo in der Sidebar
    st.image("utils/VuWall_transparent.webp", width=200)
    st.markdown("---")
    st.header("💬 Unterhaltungen")
    
    if st.button("🆕 Neue Unterhaltung", use_container_width=True):
        start_new_conversation()
        st.rerun()
    
    # Zeige verfügbare Konversationen (LocalStorage)
    conversations = local_chat_manager.get_all_conversations(limit=10)
    
    if conversations:
        st.subheader("Letzte Chats")
        for conv in conversations:
            # Zeige Konversation mit Button
            button_text = conv["title"] or f"Chat {conv['id']}"
            if len(button_text) > 30:
                button_text = button_text[:27] + "..."
            
            current_conv = local_chat_manager.get_current_conversation()
            is_current = conv["id"] == current_conv["id"]
            
            if st.button(
                f"{'📍 ' if is_current else '💬 '}{button_text}",
                key=f"conv_{conv['id']}",
                use_container_width=True,
                type="primary" if is_current else "secondary"
            ):
                local_chat_manager.switch_conversation(conv["id"])
                st.rerun()
    
    # Storage-Info und Clear-Button
    st.markdown("---")
    st.caption(f"💾 Device: {st.session_state.device_id[:8]}...")
    
    # Storage Status
    total_chats = len(st.session_state.local_conversations)
    total_messages = sum(len(conv.get("messages", [])) for conv in st.session_state.local_conversations)
    st.caption(f"📊 {total_chats} Chat(s), {total_messages} Nachrichten")
    
    # URL-Persistenz Status
    query_params = st.query_params
    if "chat_data" in query_params:
        st.caption("🔗 URL-Backup aktiv")
    
    if st.button("🗑️ Alle Chats löschen", use_container_width=True, type="secondary"):
        local_chat_manager.clear_all_data()
        st.rerun()

# ─── Chat Interface ──────────────────────────────────────────────────────────────

# Ensure we have a conversation
conversation_id = get_or_create_conversation()

# Load messages for current conversation  
current_conv = local_chat_manager.get_current_conversation()
if not st.session_state.messages and current_conv["messages"]:
    load_conversation_messages(current_conv["id"])

# Display chat messages mit custom Styling
for message in st.session_state.messages:
    avatar_path = "utils/W_transparent.png" if message["role"] == "assistant" else None
    display_chat_message(message["role"], message["content"], avatar_path)

# Chat input
if prompt := st.chat_input("Stelle deine Frage zu VuWall..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    display_chat_message("user", prompt)

    # Generate bot response
    with st.spinner("Antwort wird generiert..."):
        try:
            # Use enhanced bot function with conversation context
            answer, embedding_context = ask_bot_with_context(
                question=prompt,
                conversation_id=conversation_id
            )
            
            # Add assistant message to chat history
            st.session_state.messages.append({"role": "assistant", "content": answer})
            display_chat_message("assistant", answer, "utils/W_transparent.png")
            
            # Save both messages to database
            save_message("user", prompt)
            save_message("assistant", answer, embedding_context)
            
            # Update conversation title if this is the first message
            if len(st.session_state.messages) == 2:  # user + assistant
                title = generate_conversation_title(prompt)
                local_chat_manager.update_conversation_title(conversation_id, title)
            
        except Exception as e:
            error_msg = f"Entschuldigung, es ist ein Fehler aufgetreten: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            display_chat_message("assistant", error_msg, "utils/W_transparent.png")

# ─── Footer ──────────────────────────────────────────────────────────────────────

# st.markdown("---")
# st.markdown(
#        "💡 **Tipp:** Du kannst mehrere Fragen in einer Unterhaltung stellen. "
#        "Der Bot erinnert sich an den Kontext eurer Unterhaltung!"
#    )