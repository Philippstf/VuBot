# storage/device_id.py

import hashlib
import streamlit as st

def generate_device_id():
    """Generiert eine einzigartige Device-ID basierend auf Browser-Eigenschaften"""
    
    # Verwende Session-Informationen für Device-Fingerprinting
    device_info = []
    
    # User Agent aus Request Headers (falls verfügbar)
    if hasattr(st, '_get_session'):
        try:
            session = st._get_session()
            if session and hasattr(session, 'request'):
                user_agent = session.request.headers.get('User-Agent', '')
                device_info.append(user_agent)
        except:
            pass
    
    # Fallback: Verwende Session-ID als Basis
    if 'device_id' not in st.session_state:
        # Erstelle eine semi-persistente ID basierend auf Session
        import uuid
        import time
        
        # Kombiniere verschiedene Faktoren
        factors = [
            str(uuid.getnode()),  # MAC-Adresse (wenn verfügbar)
            str(hash(str(st.session_state))),  # Session-Hash
            str(int(time.time() / 3600))  # Stunden-basierte Komponente für Stabilität
        ]
        
        device_info.extend(factors)
        
        # Generiere eindeutige ID
        device_string = '|'.join(device_info)
        device_hash = hashlib.sha256(device_string.encode()).hexdigest()[:16]
        
        st.session_state.device_id = f"vuwall_device_{device_hash}"
    
    return st.session_state.device_id

def get_device_id():
    """Holt die aktuelle Device-ID"""
    if 'device_id' not in st.session_state:
        return generate_device_id()
    return st.session_state.device_id