# scripts/ask_bot.py

import os
import pickle
import faiss
import numpy as np
import re
from openai import OpenAI
import openai

from dotenv import load_dotenv

load_dotenv()

# ─── Konfiguration ────────────────────────────────────────────────────────────

EMBED_API_KEY   = openai.api_key = os.getenv("OPENAI_EMBED_API_KEY")
EMBED_MODEL     = "text-embedding-3-small"

ROUTER_API_KEY  = os.getenv("OPENROUTER_API_KEY")
ROUTER_API_BASE = "https://openrouter.ai/api/v1"
LLM_MODEL       = "mistralai/mistral-small-3.2-24b-instruct:free"

INDEX_FILE      = "embeddings/faiss_index/index.faiss"
METADATA_FILE   = "embeddings/faiss_index/meta.pkl"

# ─── Clients initialisieren ─────────────────────────────────────────────────────

# Embeddings-Client
embed_client = OpenAI(api_key=EMBED_API_KEY)

# LLM-Client (OpenRouter)
router_client = OpenAI(
    api_key=ROUTER_API_KEY,
    base_url=ROUTER_API_BASE,
)

# ─── Index & Metadaten laden ────────────────────────────────────────────────────

index = faiss.read_index(INDEX_FILE)
with open(METADATA_FILE, "rb") as f:
    chunks = pickle.load(f)

# ─── Frage → Embedding ──────────────────────────────────────────────────────────

def get_question_embedding(question: str) -> np.ndarray:
    resp = embed_client.embeddings.create(
        model=EMBED_MODEL,
        input=question
    )
    vec = np.array(resp.data[0].embedding, dtype="float32")
    return vec.reshape(1, -1)

# ─── Ähnlichste Chunks abrufen mit Intent-Routing ──────────────────────────────

def retrieve_chunks(question: str, top_k: int = 5) -> list[dict]:
    # 1) Intent-Routing: bei Produkt-Listing-Fragen immer nur den Index-Chunk liefern
    if re.search(r"welche (produkte|lösungen|angebot(e)?|produkte hat)", question, re.I):
        return [c for c in chunks if c.get("page_title") == "products_index"]

    # 2) Standard-Vector-Retrieval
    qvec = get_question_embedding(question)
    _, I = index.search(qvec, top_k)
    return [chunks[i] for i in I[0]]

# ─── System-Prompt nach Kundenservice-Best Practices ───────────────────────────

SYSTEM_PROMPT = """Du bist der freundliche VuWall-Kundendienstassistent.
Deine Aufgabe:
• Antworte stets präzise, empathisch und serviceorientiert.
• Gib klare, knapp formulierte Antworten in Deutsch.
• Wenn Details fehlen, bitte proaktiv um genauere Angaben.
• Biete immer eine Eskalation an („Möchtest Du mehr Infos oder Kontakt zu einem Berater?“).
• Bewahre stets einen professionellen, aber sympathischen Ton.
• Berücksichtige den Gesprächsverlauf und beziehe dich auf vorherige Nachrichten wenn relevant.

Nutze nur die folgenden kontextuellen Informationen aus der VuWall-Wissensbasis. 
Wenn Du die Antwort nicht findest, entschuldige Dich kurz und schlage nachfolgende Aktionen vor:
1) Bitte um eine genauere Frage
2) Biete Live-Support (Telefon/E-Mail) an."""

# ─── Prompt bauen ───────────────────────────────────────────────────────────────

def build_system_prompt(context: list[dict], user_q: str, chat_history: list[dict] = None) -> list[dict]:
    ctx_text = "\n\n---\n\n".join(c["text"] for c in context)
    
    # Build messages array mit System-Prompt
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Füge Chat-Historie hinzu (letzte 8 Nachrichten)
    if chat_history:
        messages.extend(chat_history[-8:])
    
    # Aktueller RAG-Kontext wird als User-Message hinzugefügt
    user_content = (
        f"Frage:\n{user_q}\n\n"
        "Verfügbare Infos aus der VuWall-Wissensbasis:\n"
        f"{ctx_text}\n\n"
        "Antwort:"
    )
    messages.append({"role": "user", "content": user_content})
    
    return messages

# ─── Hauptfunktion: Frage → Antwort ─────────────────────────────────────────────

def ask_bot(question: str, chat_history: list[dict] = None) -> str:
    relevant = retrieve_chunks(question, top_k=5)
    messages = build_system_prompt(relevant, question, chat_history)
    resp = router_client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.2,
        max_tokens=512,
    )
    return resp.choices[0].message.content.strip()

def ask_bot_with_context(question: str, conversation_id: str = None) -> tuple[str, str]:
    """
    Erweiterte ask_bot Funktion mit Konversations-Kontext
    Returns: (answer, embedding_context)
    """
    # Hol Chat-Historie wenn conversation_id gegeben
    chat_history = []
    if conversation_id:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from supabase_service import supabase_chat_service
        recent_messages = supabase_chat_service.get_recent_messages(conversation_id, limit=8)
        chat_history = [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in recent_messages
        ]
    
    # RAG-Retrieval
    relevant = retrieve_chunks(question, top_k=5)
    embedding_context = "; ".join(c.get("page_title", "unknown") for c in relevant)
    
    # Build messages mit Chat-Historie
    messages = build_system_prompt(relevant, question, chat_history)
    
    # LLM-Call
    resp = router_client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.2,
        max_tokens=512,
    )
    
    answer = resp.choices[0].message.content.strip()
    return answer, embedding_context

# ─── Selbsttest ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    q = input("Frage an VuWall-Bot: ")
    print(ask_bot(q))