# browser_storage.py

import streamlit as st
import json
from datetime import datetime
from device_id import get_device_id

class BrowserChatStorage:
    """Browser LocalStorage Manager für Chat-Persistenz"""
    
    def __init__(self):
        self.device_id = get_device_id()
        self.storage_key = f"vuwall_chats_{self.device_id}"
    
    def save_to_browser(self, conversations):
        """Speichert Conversations im Browser LocalStorage"""
        
        # Konvertiere zu JSON-serialisierbarem Format
        storage_data = {
            "device_id": self.device_id,
            "last_updated": datetime.now().isoformat(),
            "conversations": conversations
        }
        
        # JavaScript für LocalStorage
        js_code = f"""
        <script>
        // Speichere Chat-Daten im LocalStorage
        const chatData = {json.dumps(storage_data)};
        localStorage.setItem('{self.storage_key}', JSON.stringify(chatData));
        console.log('✅ Chat-Daten gespeichert:', chatData);
        </script>
        """
        
        # Führe JavaScript aus
        st.components.v1.html(js_code, height=0)
    
    def load_from_browser(self):
        """Lädt Conversations aus Browser LocalStorage"""
        
        # JavaScript zum Laden der Daten
        js_code = f"""
        <script>
        // Lade Chat-Daten aus LocalStorage
        const savedData = localStorage.getItem('{self.storage_key}');
        if (savedData) {{
            const chatData = JSON.parse(savedData);
            console.log('📂 Chat-Daten geladen:', chatData);
            
            // Sende Daten an Streamlit (über Custom Event)
            const event = new CustomEvent('vuwall_chat_loaded', {{
                detail: chatData
            }});
            window.dispatchEvent(event);
        }} else {{
            console.log('ℹ️ Keine gespeicherten Chat-Daten gefunden');
        }}
        </script>
        """
        
        # Führe JavaScript aus
        st.components.v1.html(js_code, height=0)
    
    def clear_storage(self):
        """Löscht alle Chat-Daten für dieses Gerät"""
        
        js_code = f"""
        <script>
        localStorage.removeItem('{self.storage_key}');
        console.log('🗑️ Chat-Daten gelöscht');
        alert('Chat-Verlauf wurde gelöscht!');
        </script>
        """
        
        st.components.v1.html(js_code, height=0)
    
    def get_storage_info(self):
        """Zeigt Storage-Informationen"""
        
        js_code = f"""
        <script>
        const data = localStorage.getItem('{self.storage_key}');
        if (data) {{
            const size = new Blob([data]).size;
            console.log(`📊 Storage Info: ${{(size/1024).toFixed(2)}} KB verwendet`);
        }}
        </script>
        """
        
        st.components.v1.html(js_code, height=0)

# Globale Storage-Instanz
browser_storage = BrowserChatStorage()