# 🚀 VuWall Chatbot Deployment Guide

## Streamlit Cloud Deployment

### 1. Repository Setup ✅
- Repository: `https://github.com/Philippstf/VuBot`
- Branch: `master`
- Main file: `scripts/app.py`

### 2. Streamlit Cloud Steps

1. **Gehe zu [share.streamlit.io](https://share.streamlit.io)**
2. **Verbinde GitHub Account** (falls noch nicht verbunden)
3. **Create new app:**
   - Repository: `Philippstf/VuBot`
   - Branch: `master`
   - Main file path: `scripts/app.py`
4. **Deploy klicken**

### 3. Environment Variables (Secrets)

In Streamlit Cloud App Settings → Secrets:

```toml
# Required API Keys
OPENAI_EMBED_API_KEY = "sk-your-openai-key-here"
OPENROUTER_API_KEY = "sk-or-your-openrouter-key-here"
```

### 4. Features nach Deployment

✅ **Browser-basierte Chat-Persistenz**
- Jedes Gerät hat eigenen Chat-Verlauf
- Persistenz über Browser-Sessions
- Keine Server-Datenbank erforderlich

✅ **VuWall Branding**
- Responsive Logo-Header
- Custom Chat-Bubbles
- Mobile-optimiert

✅ **RAG-powered Responses**
- OpenAI Embeddings für Suche
- OpenRouter für kostenloses LLM
- VuWall Wissensbasis integration

### 5. URL Structure

Nach Deployment verfügbar unter:
- `https://[app-name].streamlit.app`
- Automatische HTTPS
- Global CDN

### 6. Monitoring & Updates

- **Auto-Deploy:** Bei Git-Push automatisch
- **Logs:** In Streamlit Cloud Dashboard
- **Resources:** Kostenlos bis 1GB RAM

### 7. Troubleshooting

**Persistence nicht funktioniert?**
1. Browser-Console öffnen (F12)
2. Nach "VuWall:" Logs suchen
3. LocalStorage prüfen: `localStorage.getItem('vuwall_chats_...')`

**API-Fehler?**
1. Secrets korrekt gesetzt?
2. API-Keys aktiv?
3. Rate-Limits erreicht?

### 8. Produktions-Optimierungen

Für höhere Nutzung später:
- PostgreSQL für echte Persistenz
- User-Authentication
- Analytics Dashboard
- Performance Monitoring

---

🎯 **Ready to deploy!** Folge den Schritten oben für Live-Deployment.