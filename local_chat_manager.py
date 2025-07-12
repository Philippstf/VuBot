# storage/local_chat_manager.py

import streamlit as st
import json
from datetime import datetime
from typing import List, Dict
from device_id import get_device_id

class LocalChatManager:
    """Verwaltet Chat-Daten im Browser LocalStorage (Ersatz für SQLite)"""
    
    def __init__(self):
        self.device_id = get_device_id()
        # Session State wird bereits in app.py initialisiert
    
    def create_conversation(self, title: str = "Neue Unterhaltung") -> Dict:
        """Erstellt eine neue Conversation"""
        
        conversation = {
            "id": len(st.session_state.local_conversations) + 1,
            "device_id": self.device_id,
            "title": title,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": []
        }
        
        st.session_state.local_conversations.append(conversation)
        st.session_state.current_conversation_id = conversation["id"]
        
        # Speichere im Browser
        self._save_to_browser()
        
        return conversation
    
    def get_current_conversation(self) -> Dict:
        """Holt die aktuelle Conversation oder erstellt eine neue"""
        
        if not st.session_state.current_conversation_id:
            return self.create_conversation()
        
        # Finde aktuelle Conversation
        for conv in st.session_state.local_conversations:
            if conv["id"] == st.session_state.current_conversation_id:
                return conv
        
        # Falls nicht gefunden, erstelle neue
        return self.create_conversation()
    
    def add_message(self, role: str, content: str, embedding_context: str = None):
        """Fügt eine Nachricht zur aktuellen Conversation hinzu"""
        
        conversation = self.get_current_conversation()
        
        message = {
            "id": len(conversation["messages"]) + 1,
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "embedding_used": embedding_context
        }
        
        conversation["messages"].append(message)
        conversation["updated_at"] = datetime.now().isoformat()
        
        # Speichere im Browser
        self._save_to_browser()
        
        return message
    
    def get_conversation_messages(self, conversation_id: int = None) -> List[Dict]:
        """Holt alle Nachrichten einer Conversation"""
        
        if not conversation_id:
            conversation = self.get_current_conversation()
        else:
            conversation = self._find_conversation(conversation_id)
            if not conversation:
                return []
        
        return conversation.get("messages", [])
    
    def get_recent_messages(self, conversation_id: int = None, limit: int = 10) -> List[Dict]:
        """Holt die letzten N Nachrichten für Kontext"""
        
        messages = self.get_conversation_messages(conversation_id)
        return messages[-limit:] if messages else []
    
    def get_all_conversations(self, limit: int = 20) -> List[Dict]:
        """Holt alle Conversations des Geräts"""
        
        # Sortiere nach letztem Update
        conversations = sorted(
            st.session_state.local_conversations,
            key=lambda x: x["updated_at"],
            reverse=True
        )
        
        return conversations[:limit]
    
    def update_conversation_title(self, conversation_id: int, title: str):
        """Aktualisiert den Titel einer Conversation"""
        
        conversation = self._find_conversation(conversation_id)
        if conversation:
            conversation["title"] = title
            conversation["updated_at"] = datetime.now().isoformat()
            self._save_to_browser()
    
    def delete_conversation(self, conversation_id: int):
        """Löscht eine Conversation"""
        
        st.session_state.local_conversations = [
            conv for conv in st.session_state.local_conversations 
            if conv["id"] != conversation_id
        ]
        
        # Wenn gelöschte Conversation die aktuelle war, setze zurück
        if st.session_state.current_conversation_id == conversation_id:
            st.session_state.current_conversation_id = None
        
        self._save_to_browser()
    
    def switch_conversation(self, conversation_id: int):
        """Wechselt zur angegebenen Conversation"""
        
        conversation = self._find_conversation(conversation_id)
        if conversation:
            st.session_state.current_conversation_id = conversation_id
            
            # Lade Nachrichten in Session State
            st.session_state.messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in conversation["messages"]
            ]
    
    def clear_all_data(self):
        """Löscht alle lokalen Chat-Daten"""
        
        st.session_state.local_conversations = []
        st.session_state.current_conversation_id = None
        st.session_state.messages = []
        
        # Lösche auch aus Browser Storage
        self._clear_browser_storage()
    
    def _find_conversation(self, conversation_id: int) -> Dict:
        """Findet eine Conversation anhand der ID"""
        
        for conv in st.session_state.local_conversations:
            if conv["id"] == conversation_id:
                return conv
        return None
    
    def _save_to_browser(self):
        """Speichert Daten mit robuster Browser-Persistenz"""
        
        storage_data = {
            "device_id": self.device_id,
            "last_updated": datetime.now().isoformat(),
            "conversations": st.session_state.local_conversations,
            "current_conversation_id": st.session_state.current_conversation_id
        }
        
        # Cache in Session State für Reload-Persistenz
        st.session_state.browser_storage_cache = storage_data
        
        # Verwende VuWall Persistence Manager
        js_code = f"""
        <script>
        try {{
            const chatData = {json.dumps(storage_data)};
            
            // Verwende VuWall Persistence wenn verfügbar
            if (window.vuwall_persistence) {{
                const success = window.vuwall_persistence.saveData(
                    chatData.conversations, 
                    chatData.current_conversation_id
                );
                if (success) {{
                    console.log('✅ VuWall: Chat-Daten gespeichert via Persistence Manager');
                }}
            }} else {{
                // Fallback: Direkter LocalStorage
                localStorage.setItem('vuwall_chats_{self.device_id}', JSON.stringify(chatData));
                console.log('✅ VuWall: Chat-Daten gespeichert via Fallback');
            }}
            
            // Update Window-Variable für sofortige Verfügbarkeit
            window.streamlit_chat_data = chatData;
            
        }} catch(e) {{
            console.error('❌ VuWall: Fehler beim Speichern:', e);
            
            // Notfall-Speicherung
            try {{
                localStorage.setItem('vuwall_chats_{self.device_id}', JSON.stringify({{
                    device_id: '{self.device_id}',
                    conversations: [],
                    current_conversation_id: null
                }}));
            }} catch(e2) {{
                console.error('❌ VuWall: Auch Notfall-Speicherung fehlgeschlagen:', e2);
            }}
        }}
        </script>
        """
        
        st.components.v1.html(js_code, height=0)
    
    def _clear_browser_storage(self):
        """Löscht alle Browser Storage Daten"""
        
        js_code = f"""
        <script>
        localStorage.removeItem('vuwall_chats_{self.device_id}');
        console.log('🗑️ Browser Storage gelöscht für Device: {self.device_id}');
        </script>
        """
        
        st.components.v1.html(js_code, height=0)
    
    def load_from_browser(self):
        """Lädt Daten aus Browser LocalStorage mit verbesserter Persistenz"""
        
        # Lade Chat Persistence Component
        with open("components/chat_persistence.html", "r", encoding="utf-8") as f:
            persistence_html = f.read()
        
        # Initialisiere mit Device-ID
        init_js = f"""
        <script>
        // Warte bis DOM geladen ist
        document.addEventListener('DOMContentLoaded', function() {{
            // Initialisiere VuWall Chat Persistence
            if (window.initVuWallChat) {{
                window.initVuWallChat('{self.device_id}');
                
                // Lade gespeicherte Daten
                if (window.vuwall_persistence) {{
                    const data = window.vuwall_persistence.loadData();
                    if (data && data.device_id === '{self.device_id}') {{
                        console.log('🔄 Streamlit: Lade Chat-Daten', data);
                        
                        // Sende an Streamlit via Window-Variable
                        window.streamlit_chat_data = data;
                        
                        // Trigger Streamlit Update
                        window.dispatchEvent(new CustomEvent('streamlit_update'));
                    }}
                }}
            }}
        }});
        
        // Immediate Check (falls DOM bereits geladen)
        if (document.readyState === 'complete' || document.readyState === 'interactive') {{
            setTimeout(() => {{
                if (window.initVuWallChat) {{
                    window.initVuWallChat('{self.device_id}');
                    
                    if (window.vuwall_persistence) {{
                        const data = window.vuwall_persistence.loadData();
                        if (data && data.device_id === '{self.device_id}') {{
                            window.streamlit_chat_data = data;
                        }}
                    }}
                }}
            }}, 100);
        }}
        </script>
        """
        
        # Kombiniere HTML + JavaScript
        full_html = persistence_html + init_js
        
        # Lade Persistence Component
        st.components.v1.html(full_html, height=0)
        
        # Prüfe ob Daten über Window-Variable verfügbar sind
        check_data_js = f"""
        <script>
        if (window.streamlit_chat_data) {{
            const data = window.streamlit_chat_data;
            console.log('✅ Streamlit: Chat-Daten gefunden', data);
            
            // Erstelle Hidden Input mit Daten
            const input = document.createElement('input');
            input.type = 'hidden';
            input.id = 'chat_data_loaded';
            input.value = JSON.stringify(data);
            document.body.appendChild(input);
            
            // Benachrichtige Streamlit
            const event = new Event('chat_loaded');
            document.dispatchEvent(event);
        }}
        </script>
        """
        
        st.components.v1.html(check_data_js, height=0)
        
        # Versuche Daten zu laden (synchron für bessere UX)
        try:
            # Simuliere LocalStorage Zugriff über Session State
            if hasattr(st.session_state, 'browser_storage_cache'):
                cached_data = st.session_state.browser_storage_cache
                if cached_data and cached_data.get("device_id") == self.device_id:
                    self._restore_from_data(cached_data)
        except:
            pass
    
    def _restore_from_data(self, data):
        """Stellt Chat-Daten aus gespeicherten Daten wieder her"""
        try:
            st.session_state.local_conversations = data.get("conversations", [])
            st.session_state.current_conversation_id = data.get("current_conversation_id")
            
            # Lade aktuelle Messages
            if st.session_state.current_conversation_id:
                current_conv = self._find_conversation(st.session_state.current_conversation_id)
                if current_conv and current_conv["messages"]:
                    st.session_state.messages = [
                        {"role": msg["role"], "content": msg["content"]}
                        for msg in current_conv["messages"]
                    ]
            
            # Cache für nächstes Mal
            st.session_state.browser_storage_cache = data
            
            return True
        except Exception as e:
            print(f"Fehler beim Wiederherstellen: {e}")
            return False

# Globale Chat-Manager Instanz
local_chat_manager = LocalChatManager()