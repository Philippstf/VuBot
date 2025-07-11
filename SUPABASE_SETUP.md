# 🗄️ Supabase Setup für VuWall Chatbot

## 1. Supabase-Projekt erstellen

1. **Gehe zu [supabase.com](https://supabase.com)**
2. **"Start your project" klicken**
3. **GitHub Account verbinden**
4. **"New Project" erstellen:**
   - Organization: Deine
   - Name: `vuwall-chatbot`
   - Database Password: **Sicheres Passwort generieren**
   - Region: **Europe (eu-central-1)** für GDPR

## 2. Datenbank-Tabellen erstellen

Im Supabase Dashboard → **SQL Editor** → **New Query**:

```sql
-- Conversations Tabelle
CREATE TABLE conversations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    device_id TEXT NOT NULL,
    title TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Messages Tabelle  
CREATE TABLE messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    embedding_context TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Row Level Security aktivieren
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Nutzer sehen nur ihre eigenen Conversations
CREATE POLICY "conversations_device_policy" ON conversations
    FOR ALL USING (device_id = current_setting('app.device_id', true));

-- RLS Policy: Nutzer sehen nur Messages ihrer Conversations
CREATE POLICY "messages_conversation_policy" ON messages
    FOR ALL USING (
        conversation_id IN (
            SELECT id FROM conversations 
            WHERE device_id = current_setting('app.device_id', true)
        )
    );

-- Indizes für Performance
CREATE INDEX idx_conversations_device_id ON conversations(device_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);

-- Helper-Funktion für RLS
CREATE OR REPLACE FUNCTION set_config(parameter text, value text)
RETURNS void AS $$
BEGIN
    PERFORM set_config(parameter, value, false);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

## 3. API-Keys abrufen

Im Supabase Dashboard → **Settings** → **API**:

- **Project URL**: `https://xyz.supabase.co`
- **Anon/Public Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

## 4. Environment Variables

### Lokal (.env):
```bash
SUPABASE_URL=https://deinprojekt.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
OPENAI_EMBED_API_KEY=sk-proj-...
OPENROUTER_API_KEY=sk-or-...
```

### Streamlit Cloud (Secrets):
```toml
SUPABASE_URL = "https://deinprojekt.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
OPENAI_EMBED_API_KEY = "sk-proj-..."
OPENROUTER_API_KEY = "sk-or-..."
```

## 5. GDPR & Datenschutz

### ✅ Was ist bereits implementiert:
- **Row Level Security** - User sehen nur ihre Daten
- **Device-ID Hashing** - SHA-256 für Anonymisierung
- **EU-Server** - GDPR-konforme Speicherung
- **Right to be Forgotten** - Komplette Datenlöschung möglich

### 🔒 Datenschutz-Features:
- **Keine IP-Speicherung**
- **Keine Cookies** für Tracking
- **Verschlüsselte Verbindung** (TLS)
- **Anonyme Device-IDs**

### 📋 GDPR-Compliance:
- **Lawful Basis**: Legitimate Interest (Chatbot-Funktionalität)
- **Data Minimization**: Nur notwendige Daten
- **Storage Limitation**: Automatische Löschung nach 12 Monaten möglich
- **Data Portability**: JSON-Export implementierbar

## 6. Testing

Nach Setup:

```bash
# Dependencies installieren
pip install -r requirements.txt

# App starten
streamlit run scripts/app.py
```

**Teste:**
1. ✅ **Chat schreiben** → Nachricht speichern
2. ✅ **F5 drücken** → Chat sollte persistiert sein
3. ✅ **Neuen Browser** → Neue Device-ID, isolierte Chats
4. ✅ **"Alle löschen"** → GDPR-konforme Löschung

## 7. Monitoring

Im Supabase Dashboard:
- **Database** → Tabellen anzeigen
- **Auth** → Keine User (nur Device-IDs)
- **Storage** → Aktuell nicht verwendet
- **Edge Functions** → Optional für erweiterte Features

## 8. Kosten

**Kostenlos bis:**
- 500MB Datenbank
- 2GB Bandwidth
- 50MB Dateispeicher
- 1 Million API-Requests

**Für VuWall Chatbot:**
- ~1KB pro Chat-Nachricht
- ~500.000 Nachrichten im Free Tier
- Perfekt für Demo/MVP

---

🎯 **Nach diesem Setup ist der VuWall Chatbot GDPR-konform und Enterprise-ready!**