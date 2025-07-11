# database/service.py

from typing import List, Optional
from sqlalchemy.orm import Session
from .models import Conversation, Message, SessionLocal, create_tables
from datetime import datetime

class ChatService:
    """Service-Klasse für Chat-Datenbank-Operationen"""
    
    def __init__(self):
        # Stelle sicher, dass Tabellen existieren
        create_tables()
    
    def get_or_create_conversation(self, user_id: str, title: str = None) -> Conversation:
        """Holt die aktuelle Konversation des Users oder erstellt eine neue"""
        db = SessionLocal()
        try:
            # Suche nach der neuesten Konversation des Users
            conversation = db.query(Conversation)\
                           .filter(Conversation.user_id == user_id)\
                           .order_by(Conversation.updated_at.desc())\
                           .first()
            
            # Erstelle neue Konversation wenn keine gefunden oder wenn gewünscht
            if not conversation:
                conversation = Conversation(
                    user_id=user_id,
                    title=title or "Neue Unterhaltung"
                )
                db.add(conversation)
                db.commit()
                db.refresh(conversation)
            
            return conversation
        finally:
            db.close()
    
    def create_new_conversation(self, user_id: str, title: str = None) -> Conversation:
        """Erstellt explizit eine neue Konversation"""
        db = SessionLocal()
        try:
            conversation = Conversation(
                user_id=user_id,
                title=title or f"Chat vom {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            return conversation
        finally:
            db.close()
    
    def add_message(self, conversation_id: int, role: str, content: str, embedding_used: str = None) -> Message:
        """Fügt eine neue Nachricht zur Konversation hinzu"""
        db = SessionLocal()
        try:
            message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                embedding_used=embedding_used
            )
            db.add(message)
            
            # Update conversation timestamp
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conversation:
                conversation.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(message)
            return message
        finally:
            db.close()
    
    def get_conversation_messages(self, conversation_id: int, limit: int = 50) -> List[Message]:
        """Holt alle Nachrichten einer Konversation"""
        db = SessionLocal()
        try:
            messages = db.query(Message)\
                        .filter(Message.conversation_id == conversation_id)\
                        .order_by(Message.timestamp.asc())\
                        .limit(limit)\
                        .all()
            return messages
        finally:
            db.close()
    
    def get_recent_messages(self, conversation_id: int, limit: int = 10) -> List[Message]:
        """Holt die letzten N Nachrichten für Kontext"""
        db = SessionLocal()
        try:
            messages = db.query(Message)\
                        .filter(Message.conversation_id == conversation_id)\
                        .order_by(Message.timestamp.desc())\
                        .limit(limit)\
                        .all()
            return list(reversed(messages))  # Chronologische Reihenfolge
        finally:
            db.close()
    
    def get_user_conversations(self, user_id: str, limit: int = 20) -> List[Conversation]:
        """Holt alle Konversationen eines Users"""
        db = SessionLocal()
        try:
            conversations = db.query(Conversation)\
                           .filter(Conversation.user_id == user_id)\
                           .order_by(Conversation.updated_at.desc())\
                           .limit(limit)\
                           .all()
            return conversations
        finally:
            db.close()
    
    def update_conversation_title(self, conversation_id: int, title: str):
        """Aktualisiert den Titel einer Konversation"""
        db = SessionLocal()
        try:
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conversation:
                conversation.title = title
                conversation.updated_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()
    
    def delete_conversation(self, conversation_id: int):
        """Löscht eine Konversation und alle zugehörigen Nachrichten"""
        db = SessionLocal()
        try:
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conversation:
                db.delete(conversation)
                db.commit()
        finally:
            db.close()

# Globale Service-Instanz
chat_service = ChatService()