# database/models.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False)  # Session-ID oder User-ID
    title = Column(String(500), nullable=True)     # Titel basierend auf erster Frage
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship zu Messages
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id='{self.user_id}', title='{self.title}')>"

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False)
    role = Column(String(50), nullable=False)       # 'user' oder 'assistant'
    content = Column(Text, nullable=False)          # Nachrichteninhalt
    timestamp = Column(DateTime, default=datetime.utcnow)
    embedding_used = Column(Text, nullable=True)    # RAG-Kontext falls vorhanden
    
    # Relationship zu Conversation
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}', conversation_id={self.conversation_id})>"

# Database Engine und Session Setup
DATABASE_URL = "sqlite:///./vuwall_chat.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Erstellt alle Tabellen in der Datenbank"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Gibt eine Datenbank-Session zurück"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()