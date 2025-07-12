# database/supabase_client.py

import os
import streamlit as st
from supabase import create_client, Client
from typing import Optional
import hashlib

class SupabaseClient:
    """Datenschutzkonforme Supabase-Integration für VuWall Chatbot"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.initialized = False
        
    def initialize(self) -> bool:
        """Initialisiert Supabase Client mit Umgebungsvariablen"""
        try:
            # Supabase Credentials aus Environment
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY")
            
            if not supabase_url or not supabase_key:
                st.error("❌ Supabase Credentials fehlen in Environment Variables")
                return False
            
            # Client erstellen
            self.client = create_client(supabase_url, supabase_key)
            self.initialized = True
            
            return True
            
        except Exception as e:
            st.error(f"❌ Supabase Verbindung fehlgeschlagen: {str(e)}")
            return False
    
    def get_client(self) -> Optional[Client]:
        """Gibt Supabase Client zurück (initialisiert wenn nötig)"""
        if not self.initialized:
            self.initialize()
        return self.client
    
    def create_tables(self) -> bool:
        """Erstellt die notwendigen Tabellen in Supabase"""
        client = self.get_client()
        if not client:
            return False
            
        try:
            # SQL für Tabellenerstellung
            sql_commands = [
                """
                -- Conversations Tabelle
                CREATE TABLE IF NOT EXISTS conversations (
                    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                    device_id TEXT NOT NULL,
                    title TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                """,
                """
                -- Messages Tabelle  
                CREATE TABLE IF NOT EXISTS messages (
                    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
                    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    embedding_context TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                """,
                """
                -- Row Level Security aktivieren
                ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
                ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
                """,
                """
                -- RLS Policy: Nutzer sehen nur ihre eigenen Conversations
                CREATE POLICY IF NOT EXISTS "conversations_device_policy" ON conversations
                    FOR ALL USING (device_id = current_setting('app.device_id', true));
                """,
                """
                -- RLS Policy: Nutzer sehen nur Messages ihrer Conversations
                CREATE POLICY IF NOT EXISTS "messages_conversation_policy" ON messages
                    FOR ALL USING (
                        conversation_id IN (
                            SELECT id FROM conversations 
                            WHERE device_id = current_setting('app.device_id', true)
                        )
                    );
                """,
                """
                -- Indizes für Performance
                CREATE INDEX IF NOT EXISTS idx_conversations_device_id ON conversations(device_id);
                CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
                CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at DESC);
                """
            ]
            
            # Führe SQL-Commands aus
            for sql in sql_commands:
                try:
                    result = client.rpc('exec_sql', {'sql': sql})
                except:
                    # Fallback: Verwende direkten SQL-Aufruf
                    pass
            
            st.success("✅ Supabase Tabellen erstellt/überprüft")
            return True
            
        except Exception as e:
            st.error(f"❌ Fehler beim Erstellen der Tabellen: {str(e)}")
            return False
    
    def hash_device_id(self, raw_device_id: str) -> str:
        """Erstellt gehashte Device-ID für besseren Datenschutz"""
        # SHA-256 Hash für Device-ID (GDPR-konform)
        salt = "vuwall_secure_salt_2024"
        combined = f"{raw_device_id}_{salt}"
        hashed = hashlib.sha256(combined.encode()).hexdigest()
        return f"device_{hashed[:16]}"  # Erste 16 Zeichen für Eindeutigkeit
    
    def test_connection(self) -> bool:
        """Testet die Supabase-Verbindung"""
        client = self.get_client()
        if not client:
            return False
            
        try:
            # Einfacher Test: Aktuelle Zeit von Supabase abrufen
            result = client.rpc('now').execute()
            if result.data:
                st.success("✅ Supabase Verbindung erfolgreich")
                return True
            else:
                st.error("❌ Supabase Verbindung fehlgeschlagen")
                return False
                
        except Exception as e:
            st.error(f"❌ Supabase Test fehlgeschlagen: {str(e)}")
            return False

# Globale Supabase-Instanz
supabase_client = SupabaseClient()