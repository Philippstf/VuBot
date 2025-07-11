# test_chat.py - Einfacher Test der Chat-Funktionalität

import os
import sys
sys.path.append('.')

from database.service import chat_service
from scripts.ask_bot import ask_bot_with_context

def test_database():
    """Testet die Datenbank-Funktionalität"""
    print("🔧 Teste Datenbank-Setup...")
    
    # Erstelle Test-Konversation
    conversation = chat_service.create_new_conversation(
        user_id="test_user",
        title="Test Chat"
    )
    print(f"✅ Konversation erstellt: ID {conversation.id}")
    
    # Füge Test-Nachrichten hinzu
    msg1 = chat_service.add_message(
        conversation_id=conversation.id,
        role="user",
        content="Was ist VuWall?"
    )
    print(f"✅ User-Message gespeichert: ID {msg1.id}")
    
    msg2 = chat_service.add_message(
        conversation_id=conversation.id,
        role="assistant",
        content="VuWall ist ein Unternehmen für Video-Wall-Lösungen.",
        embedding_used="products; about"
    )
    print(f"✅ Assistant-Message gespeichert: ID {msg2.id}")
    
    # Teste Nachrichtenabruf
    messages = chat_service.get_conversation_messages(conversation.id)
    print(f"✅ {len(messages)} Nachrichten abgerufen")
    
    # Teste Konversations-Abruf
    conversations = chat_service.get_user_conversations("test_user")
    print(f"✅ {len(conversations)} Konversationen gefunden")
    
    return conversation.id

def test_bot_with_context():
    """Testet die Bot-Funktionalität mit Kontext"""
    print("\n🤖 Teste Bot mit Konversations-Kontext...")
    
    # Erstelle Konversation
    conversation_id = test_database()
    
    # Teste Bot-Antwort mit Kontext
    question = "Erzähle mir mehr über die Produkte"
    answer, context = ask_bot_with_context(question, conversation_id)
    
    print(f"❓ Frage: {question}")
    print(f"🤖 Antwort: {answer}")
    print(f"📊 RAG-Kontext: {context}")
    
    # Speichere in DB
    chat_service.add_message(conversation_id, "user", question)
    chat_service.add_message(conversation_id, "assistant", answer, context)
    
    print("✅ Konversation erfolgreich erweitert!")

if __name__ == "__main__":
    print("🚀 Starte VuWall Chatbot Tests...\n")
    
    try:
        test_bot_with_context()
        print("\n✅ Alle Tests erfolgreich!")
        print("\n📝 Du kannst jetzt die Chat-App starten mit:")
        print("   streamlit run scripts/app_chat.py")
        
    except Exception as e:
        print(f"\n❌ Test fehlgeschlagen: {e}")
        print("🔍 Stelle sicher, dass:")
        print("  - Die .env Datei korrekt konfiguriert ist")
        print("  - OPENAI_EMBED_API_KEY gesetzt ist")
        print("  - OPENROUTER_API_KEY gesetzt ist")
        print("  - Die FAISS-Embeddings existieren")