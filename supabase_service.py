# database/supabase_service.py

import streamlit as st
from typing import List, Dict, Optional
from datetime import datetime
from supabase_client import supabase_client
import uuid

class SupabaseChatService:
    """GDPR-konforme Chat-Service mit Supabase Backend"""
    
    def __init__(self):
        self.client = supabase_client
        
    def ensure_connection(self) -> bool:
        """Stellt sicher, dass Supabase-Verbindung besteht"""
        if not self.client.initialized:
            if not self.client.initialize():
                return False
        return True
    
    def get_or_create_conversation(self, device_id: str, title: str = "Neue Unterhaltung") -> Optional[Dict]:
        """Holt aktuelle Konversation oder erstellt neue"""
        if not self.ensure_connection():
            return None
            
        try:
            client = self.client.get_client()
            hashed_device_id = self.client.hash_device_id(device_id)
            
            # Setze Device-ID für RLS (Row Level Security)
            client.rpc('set_config', {
                'parameter': 'app.device_id',
                'value': hashed_device_id
            }).execute()
            
            # Suche nach neuester Konversation
            result = client.table('conversations')\
                          .select('*')\
                          .eq('device_id', hashed_device_id)\
                          .order('updated_at', desc=True)\
                          .limit(1)\
                          .execute()
            
            if result.data:
                return result.data[0]
            else:
                # Erstelle neue Konversation
                return self.create_conversation(device_id, title)
                
        except Exception as e:
            st.error(f"❌ Fehler beim Laden der Konversation: {str(e)}")
            return None
    
    def create_conversation(self, device_id: str, title: str = "Neue Unterhaltung") -> Optional[Dict]:
        """Erstellt neue Konversation"""
        if not self.ensure_connection():
            return None
            
        try:
            client = self.client.get_client()
            hashed_device_id = self.client.hash_device_id(device_id)
            
            # Setze Device-ID für RLS
            client.rpc('set_config', {
                'parameter': 'app.device_id', 
                'value': hashed_device_id
            }).execute()
            
            # Erstelle Konversation
            conversation_data = {
                'device_id': hashed_device_id,
                'title': title,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            result = client.table('conversations')\
                          .insert(conversation_data)\
                          .execute()
            
            if result.data:
                return result.data[0]
            else:
                st.error("❌ Konversation konnte nicht erstellt werden")
                return None
                
        except Exception as e:
            st.error(f"❌ Fehler beim Erstellen der Konversation: {str(e)}")
            return None
    
    def add_message(self, conversation_id: str, role: str, content: str, embedding_context: str = None) -> Optional[Dict]:
        """Fügt Nachricht zu Konversation hinzu"""
        if not self.ensure_connection():
            return None
            
        try:
            client = self.client.get_client()
            
            # Erstelle Message
            message_data = {
                'conversation_id': conversation_id,
                'role': role,
                'content': content,
                'embedding_context': embedding_context,
                'created_at': datetime.now().isoformat()
            }
            
            result = client.table('messages')\
                          .insert(message_data)\
                          .execute()
            
            if result.data:
                # Update Konversation timestamp
                client.table('conversations')\
                      .update({'updated_at': datetime.now().isoformat()})\
                      .eq('id', conversation_id)\
                      .execute()
                
                return result.data[0]
            else:
                st.error("❌ Nachricht konnte nicht gespeichert werden")
                return None
                
        except Exception as e:
            st.error(f"❌ Fehler beim Speichern der Nachricht: {str(e)}")
            return None
    
    def get_conversation_messages(self, conversation_id: str) -> List[Dict]:
        """Holt alle Nachrichten einer Konversation"""
        if not self.ensure_connection():
            return []
            
        try:
            client = self.client.get_client()
            
            result = client.table('messages')\
                          .select('*')\
                          .eq('conversation_id', conversation_id)\
                          .order('created_at', desc=False)\
                          .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            st.error(f"❌ Fehler beim Laden der Nachrichten: {str(e)}")
            return []
    
    def get_recent_messages(self, conversation_id: str, limit: int = 10) -> List[Dict]:
        """Holt letzte N Nachrichten für Kontext"""
        messages = self.get_conversation_messages(conversation_id)
        return messages[-limit:] if messages else []
    
    def get_user_conversations(self, device_id: str, limit: int = 20) -> List[Dict]:
        """Holt alle Konversationen eines Geräts"""
        if not self.ensure_connection():
            return []
            
        try:
            client = self.client.get_client()
            hashed_device_id = self.client.hash_device_id(device_id)
            
            # Setze Device-ID für RLS
            client.rpc('set_config', {
                'parameter': 'app.device_id',
                'value': hashed_device_id
            }).execute()
            
            result = client.table('conversations')\
                          .select('*')\
                          .eq('device_id', hashed_device_id)\
                          .order('updated_at', desc=True)\
                          .limit(limit)\
                          .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            st.error(f"❌ Fehler beim Laden der Konversationen: {str(e)}")
            return []
    
    def update_conversation_title(self, conversation_id: str, title: str) -> bool:
        """Aktualisiert Konversations-Titel"""
        if not self.ensure_connection():
            return False
            
        try:
            client = self.client.get_client()
            
            result = client.table('conversations')\
                          .update({
                              'title': title,
                              'updated_at': datetime.now().isoformat()
                          })\
                          .eq('id', conversation_id)\
                          .execute()
            
            return bool(result.data)
            
        except Exception as e:
            st.error(f"❌ Fehler beim Aktualisieren des Titels: {str(e)}")
            return False
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Löscht Konversation und alle Nachrichten (CASCADE)"""
        if not self.ensure_connection():
            return False
            
        try:
            client = self.client.get_client()
            
            result = client.table('conversations')\
                          .delete()\
                          .eq('id', conversation_id)\
                          .execute()
            
            return bool(result.data)
            
        except Exception as e:
            st.error(f"❌ Fehler beim Löschen der Konversation: {str(e)}")
            return False
    
    def clear_all_conversations(self, device_id: str) -> bool:
        """Löscht alle Konversationen eines Geräts (GDPR Right to be forgotten)"""
        if not self.ensure_connection():
            return False
            
        try:
            client = self.client.get_client()
            hashed_device_id = self.client.hash_device_id(device_id)
            
            # Setze Device-ID für RLS
            client.rpc('set_config', {
                'parameter': 'app.device_id',
                'value': hashed_device_id
            }).execute()
            
            result = client.table('conversations')\
                          .delete()\
                          .eq('device_id', hashed_device_id)\
                          .execute()
            
            return True  # Auch wenn keine Daten gelöscht wurden, ist Operation erfolgreich
            
        except Exception as e:
            st.error(f"❌ Fehler beim Löschen aller Konversationen: {str(e)}")
            return False

# Globale Service-Instanz
supabase_chat_service = SupabaseChatService()