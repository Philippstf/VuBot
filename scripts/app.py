# app.py

import streamlit as st
import uuid
import sys
import os
# (Optional, falls du noch andere Imports aus scripts brauchst)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ask_bot import ask_bot_with_context
from database.supabase_service import supabase_chat_service
from storage.device_id import get_device_id
from dotenv import load_dotenv

load_dotenv()

# ─── Globales Dark-Mode-CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>



[data-testid="stChatInput"],
[data-testid="stChatInput"] *,
[data-testid="stChatInput"] *:focus,
[data-testid="stChatInput"] *:focus-visible,
[data-testid="stChatInput"] *:focus-within {
  outline: none !important;
  box-shadow: none !important;
}
/* ─── Roter BaseWeb-Fokus weg ─── */
/* 1. Unterdrücke alle standardmäßigen Outlines/Box-Shadows im inneren BaseWeb-Container */
[data-testid="stChatInput"] [data-baseweb="textarea"],
[data-testid="stChatInput"] [data-baseweb="textarea"] * {
  outline: none !important;
  box-shadow: none !important;
}

/* 2. Deaktiviere zusätzlich den BaseWeb-Fokusring auf dem inneren Wrapper */
[data-testid="stChatInput"] > div:first-child {
  outline: none !important;
}

/* ChatInput: Keine roten Outlines, Schatten oder Border beim Fokus/Active */
textarea[data-testid="stChatInputTextArea"]:focus,
textarea[data-testid="stChatInputTextArea"]:active {
  outline: none !important;
  box-shadow: none !important;
  border-color: #ffffff !important; /* bleibt weiß */
}

/* Submit-Button: Keine roten Effekte bei Hover, Fokus, Active */
button[data-testid="stChatInputSubmitButton"]:hover,
button[data-testid="stChatInputSubmitButton"]:focus,
button[data-testid="stChatInputSubmitButton"]:active,
button[data-testid="stChatInputSubmitButton"]:visited {
  background-color: #ffffff !important;
  color: #000000 !important;
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
}


/* App-Hintergrund & Text */
[data-testid="stAppViewContainer"] {
    background-color: #0e1117;
    color: #e1e1e1;
}
/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #171924;
    color: #e1e1e1;
}
/* Header (oben) */
[data-testid="stHeader"] {
    background-color: #0e1117;
}
/* Chat-Input-Feld */
div[role="textbox"] {
    background-color: #1e1f26 !important;
    color: #e1e1e1 !important;
    border: 1px solid #333 !important;
}
/* Buttons und Controls */
.stButton>button, .stCheckbox>label, .stSelectbox>div, .stRadio>label {
    color: #e1e1e1;
    background-color: #1e1f26;
    border: 1px solid #333;
}
/* Scrollbar (optional) */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-thumb {
    background-color: #333;
    border-radius: 4px;
}

  [data-testid="stBottom"] *,
  [data-testid="stChatInput"] * {
    background-color: transparent !important;
  }

[data-testid="stChatInput"] > div:first-child {
    box-shadow: inset 0 0 0 1px #ffffff !important;
    border-radius: 24px !important;
}

  /* Weißer Input-Text */
  textarea[data-testid="stChatInputTextArea"] {
      color: #ffffff !important;
  }
  /* Weißer Placeholder (etwas gedämpft) */
  textarea[data-testid="stChatInputTextArea"]::placeholder {
      color: #aaaaaa !important;
  }

  /* Wrapper: entferne jeglichen Standard-Focus und setze nur deinen weiße Outline */
  [data-testid="stChatInput"] > div:first-child {
    outline: none !important;
  }

    /* Textarea: kein roter oder blauer Outline/Shadow beim Fokussieren */
  textarea[data-testid="stChatInputTextArea"]:focus {
    outline: none !important;
    box-shadow: none !important;
  }

  /* 2) Beim Fokussieren ausschließlich deinen weißen Inset-Rahmen anzeigen */
[data-testid="stChatInput"] > div:first-child:focus-within {
  box-shadow: inset 0 0 0 1px #ffffff !important;
}


/* ─── Responsive Header für Mobile ─── */
@media (max-width: 600px) {
  .vuwall-header-flex {
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 14px !important;
    margin-bottom: 16px !important;
    text-align: center !important;
  }
  .vuwall-header-flex img {
    margin: 0 auto 2px auto !important;
    height: 56px !important;
    display: block !important;
    max-width: 80vw !important;
  }
  .vuwall-header-flex h1 {
    font-size: 2.5rem !important;
    text-align: center !important;
    margin: 0 !important;
    font-weight: 800 !important;
    letter-spacing: 0.01em !important;
    line-height: 1.1 !important;
  }
}
</style>
""", unsafe_allow_html=True)

# ─── Custom Chat Display Function ──────────────────────────────────────────────

def get_base64_image(image_path):
    """Konvertiert Bild zu base64 für HTML-Einbettung"""
    try:
        import base64
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

def display_chat_message(role, content, avatar_path=None):
    """Zeigt eine Chat-Nachricht mit custom HTML/CSS im Dark Mode"""
    if role == "user":
        st.markdown(f"""
        <div style="
            display: flex; 
            justify-content: flex-end; 
            margin: 10px 0; 
            align-items: flex-end;
        ">
            <div style="
                background: linear-gradient(135deg, #1f3a93, #34495e);
                color: white;
                padding: 12px 16px;
                border-radius: 20px 20px 5px 20px;
                max-width: 70%;
                margin-right: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.5);
                font-size: 14px;
                line-height: 1.4;
            ">
                {content}
            </div>
            <div style="
                width: 40px; 
                height: 40px; 
                background-color: #e67e22; 
                border-radius: 50%; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                font-size: 18px; 
                color: white; 
                flex-shrink: 0;
            ">
                👤
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        avatar_img = ""
        if avatar_path:
            avatar_img = f'<img src="data:image/png;base64,{get_base64_image(avatar_path)}" style="width: 30px; height: 30px; object-fit: contain;">'
        else:
            avatar_img = "🤖"

        st.markdown(f"""
        <div style="
            display: flex; 
            justify-content: flex-start; 
            margin: 10px 0; 
            align-items: flex-end;
        ">
            <div style="
                width: 40px; 
                height: 40px; 
                background-color: #1e1f26; 
                border-radius: 50%; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                border: 1px solid #333; 
                flex-shrink: 0; 
                margin-right: 8px;
            ">
                {avatar_img}
            </div>
            <div style="
                background: #2e303e; 
                color: #e1e1e1; 
                padding: 12px 16px; 
                border-radius: 20px 20px 20px 5px; 
                max-width: 70%; 
                border: 1px solid #333; 
                box-shadow: 0 2px 4px rgba(0,0,0,0.5);
                font-size: 14px; 
                line-height: 1.4;
            ">
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─── Streamlit Konfiguration ────────────────────────────────────────────────────

st.set_page_config(
    page_title="🤖 VuWall KI-Chatbot",
    page_icon="🤖",
    layout="centered"
)

# ─── Session State Initialisierung ──────────────────────────────────────────────

if "device_id" not in st.session_state:
    st.session_state.device_id = get_device_id()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_conversation" not in st.session_state:
    st.session_state.current_conversation = None

if "supabase_initialized" not in st.session_state:
    with st.spinner("Verbindung zur Datenbank..."):
        if supabase_chat_service.ensure_connection():
            st.session_state.supabase_initialized = True
            conversation = supabase_chat_service.get_or_create_conversation(
                device_id=st.session_state.device_id,
                title="Neue Unterhaltung"
            )
            if conversation:
                st.session_state.current_conversation = conversation
                messages = supabase_chat_service.get_conversation_messages(conversation['id'])
                st.session_state.messages = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in messages
                ]
                if messages:
                    st.success(f"✅ Chat mit {len(messages)} Nachrichten geladen!")
        else:
            st.error("❌ Datenbankverbindung fehlgeschlagen")
            st.session_state.supabase_initialized = False

# ─── Helper Functions ────────────────────────────────────────────────────────────

def get_or_create_conversation():
    if st.session_state.current_conversation:
        return st.session_state.current_conversation["id"]
    conversation = supabase_chat_service.get_or_create_conversation(
        device_id=st.session_state.device_id,
        title="Neue Unterhaltung"
    )
    if conversation:
        st.session_state.current_conversation = conversation
        return conversation["id"]
    return None

def load_conversation_messages(conversation_id: str):
    messages = supabase_chat_service.get_conversation_messages(conversation_id)
    st.session_state.messages = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in messages
    ]

def save_message(role: str, content: str, embedding_context: str = None):
    if st.session_state.current_conversation:
        supabase_chat_service.add_message(
            conversation_id=st.session_state.current_conversation["id"],
            role=role,
            content=content,
            embedding_context=embedding_context
        )


def start_new_conversation():
    conversation = supabase_chat_service.create_conversation(
        device_id=st.session_state.device_id,
        title="Neue Unterhaltung"
    )
    if conversation:
        st.session_state.current_conversation = conversation
        st.session_state.messages = []

def generate_conversation_title(first_question: str) -> str:
    if len(first_question) > 50:
        return first_question[:47] + "..."
    return first_question

# ─── UI Layout ───────────────────────────────────────────────────────────────────

# Header mit VuWall Logo
st.markdown(f"""
<div class="vuwall-header-flex" style="
    display: flex; 
    align-items: center; 
    margin-bottom: 20px;
">
    <img src="data:image/webp;base64,{get_base64_image('utils/VuWall_transparent.webp')}" 
         style="height: 60px; margin-right: 15px;">
    <h1 style="
        margin: 0; 
        color: #e1e1e1; 
        font-size: 3.2rem; 
        font-weight: bold;
    ">
        KI-Chatbot
    </h1>
</div>
""", unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown('<div class="vuwall-subtitle">Dein persönlicher Assistent für <b>VuWall</b>-Produkte und -Lösungen</div>', unsafe_allow_html=True)

# Sidebar für Konversations-Management
with st.sidebar:
    st.markdown(
        f'''
        <img src="data:image/webp;base64,{get_base64_image('utils/VuWall_transparent.webp')}"
             style="width: 200px; max-width: 100%; image-rendering: auto; display: block; margin: 0 auto;"/>
        ''',
        unsafe_allow_html=True
    )
    st.markdown("---")
    st.header("💬 Unterhaltungen")
    
    if st.button("🆕 Neue Unterhaltung", use_container_width=True):
        start_new_conversation()
        st.rerun()
    
    conversations = supabase_chat_service.get_user_conversations(
        st.session_state.device_id, limit=10
    )
    if conversations:
        st.subheader("Letzte Chats")
        for conv in conversations:
            title = conv["title"] or f"Chat {conv['id'][:8]}..."
            if len(title) > 30:
                title = title[:27] + "..."
            is_current = (st.session_state.current_conversation and 
                          conv["id"] == st.session_state.current_conversation["id"])
            if st.button(
                f"{'📍 ' if is_current else '💬 '}{title}",
                key=f"conv_{conv['id']}",
                use_container_width=True,
                type="primary" if is_current else "secondary"
            ):
                st.session_state.current_conversation = conv
                load_conversation_messages(conv["id"])
                st.rerun()
    
    st.markdown("---")
    total_chats = len(conversations)
    total_messages = len(st.session_state.messages)
    if st.button("🗑️ Alle Chats löschen", use_container_width=True, type="secondary"):
        if supabase_chat_service.clear_all_conversations(st.session_state.device_id):
            st.session_state.current_conversation = None
            st.session_state.messages = []
            st.success("✅ Alle Chats gelöscht (GDPR-konform)")
        st.rerun()

# ─── Chat Interface ──────────────────────────────────────────────────────────────

conversation_id = get_or_create_conversation()
if not st.session_state.messages and st.session_state.current_conversation:
    load_conversation_messages(st.session_state.current_conversation["id"])

for msg in st.session_state.messages:
    avatar = "utils/W_transparent.png" if msg["role"] == "assistant" else None
    display_chat_message(msg["role"], msg["content"], avatar)

if user_input := st.chat_input("Stelle deine Frage zu VuWall..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    display_chat_message("user", user_input)
    with st.spinner("Antwort wird generiert..."):
        try:
            answer, ctx = ask_bot_with_context(
                question=user_input, conversation_id=conversation_id
            )
            st.session_state.messages.append({"role": "assistant", "content": answer})
            display_chat_message("assistant", answer, "utils/W_transparent.png")
            save_message("user", user_input)
            save_message("assistant", answer, ctx)
            if len(st.session_state.messages) == 2:
                new_title = generate_conversation_title(user_input)
                supabase_chat_service.update_conversation_title(conversation_id, new_title)
        except Exception as e:
            err = f"Entschuldigung, ein Fehler ist aufgetreten: {e}"
            st.error(err)
            st.session_state.messages.append({"role": "assistant", "content": err})
            display_chat_message("assistant", err, "utils/W_transparent.png")
