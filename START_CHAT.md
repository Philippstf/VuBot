# 🚀 VuWall Chatbot mit Chat-Interface

## ✨ Was ist neu?

Der VuWall Chatbot wurde komplett überarbeitet und bietet jetzt:

- **🗨️ Echtes Chat-Interface** mit scrollbarer Nachrichten-Historie
- **💾 Persistente Speicherung** aller Unterhaltungen in einer SQLite-Datenbank
- **🧠 Kontext-Bewusste Gespräche** - der Bot erinnert sich an vorherige Nachrichten
- **📂 Mehrere Unterhaltungen** können parallel geführt und verwaltet werden
- **🔄 Session-Management** für nahtlose Benutzererfahrung

## 🛠️ Setup

### 1. Dependencies installieren
```bash
pip install -r requirements.txt
```

### 2. Environment-Variablen (.env)
Stelle sicher, dass deine `.env`-Datei diese Keys enthält:
```
OPENAI_EMBED_API_KEY=sk-...
OPENROUTER_API_KEY=sk-...
```

### 3. Embeddings prüfen
Stelle sicher, dass die FAISS-Embeddings existieren:
```
embeddings/faiss_index/index.faiss
embeddings/faiss_index/meta.pkl
```

## 🎯 Starten

### Option 1: Neue Chat-App (empfohlen)
```bash
streamlit run scripts/app_chat.py
```

### Option 2: Alte einfache App
```bash
streamlit run scripts/app.py
```

### Option 3: Test der Funktionalität
```bash
python test_chat.py
```

## 🏗️ Architektur

```
VuBot/
├── database/
│   ├── models.py          # SQLAlchemy Datenbank-Modelle
│   ├── service.py         # Chat-Service für DB-Operationen
│   └── __init__.py
├── scripts/
│   ├── app_chat.py        # 🆕 Neue Chat-App
│   ├── app.py             # Alte einfache App
│   └── ask_bot.py         # 🔄 Erweitert um Chat-Kontext
├── vuwall_chat.db         # 🆕 SQLite-Datenbank (wird automatisch erstellt)
└── test_chat.py           # Test-Script
```

## 🗃️ Datenbank-Schema

### Conversations
- `id` - Eindeutige Konversations-ID
- `user_id` - Session-basierte User-ID
- `title` - Titel der Unterhaltung
- `created_at` / `updated_at` - Zeitstempel

### Messages  
- `id` - Eindeutige Nachrichten-ID
- `conversation_id` - Verknüpfung zur Konversation
- `role` - 'user' oder 'assistant'
- `content` - Nachrichteninhalt
- `timestamp` - Zeitstempel
- `embedding_used` - RAG-Kontext (optional)

## 🎨 Features

### Chat-Interface
- **Nachrichtenhistorie** mit User/Assistant-Bubbles
- **Typing-Indicator** während der Antwort-Generierung
- **Scrollbare Historie** für längere Gespräche

### Sidebar-Navigation
- **Neue Unterhaltung** starten
- **Konversationsliste** mit den letzten 10 Chats
- **Aktuelle Unterhaltung** hervorgehoben

### Intelligente Titel-Generierung
- Automatische Titel basierend auf der ersten Frage
- Kürzung langer Titel für bessere Darstellung

## 🔧 Technische Details

### RAG-Integration
- Beibehaltung des FAISS-basierten Retrieval-Systems
- OpenAI Embeddings für Vektorsuche
- OpenRouter für LLM (kostenlos: Mistral Small)

### Chat-Kontext
- Letzte 8 Nachrichten werden als Kontext weitergegeben
- System-Prompt erweitert um Chat-Verhalten
- Preservation des VuWall-spezifischen Kundenservice-Tons

### Skalierbarkeit
- SQLite für Development
- Migration zu PostgreSQL möglich (SQLAlchemy ORM)
- Session-basierte User-IDs (Auth-ready)

## 🚦 Nächste Schritte

1. **User-Authentifizierung** - Echte User-Accounts statt Session-IDs
2. **Enhanced UI** - Streamlit-Chat-Components für bessere UX  
3. **Export-Funktionen** - Chat-Historie als PDF/Word exportieren
4. **Admin-Panel** - Konversationen verwalten und analysieren
5. **Performance** - Caching und Optimierungen für große Datenmengen

Viel Spaß mit dem neuen Chat-Interface! 🎉