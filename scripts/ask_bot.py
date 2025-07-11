# scripts/ask_bot.py

import os
import pickle
import faiss
import numpy as np
import re
from openai import OpenAI
import openai

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

# ─── Prompt bauen ───────────────────────────────────────────────────────────────

def build_system_prompt(context: list[dict], user_q: str) -> list[dict]:
    ctx_text = "\n\n---\n\n".join([c["text"] for c in context])
    user_content = (
        "Beantworte die Frage **präzise** und **sachlich** auf Deutsch.\n\n"
        f"Frage:\n{user_q}\n\n"
        "Verfügbare Informationen aus der VuWall-Wissensbasis:\n"
        f"{ctx_text}\n\n"
        "Antwort:"
    )
    return [
        {"role": "system", "content": "Du bist ein hilfreicher VuWall-Assistent."},
        {"role": "user",   "content": user_content}
    ]

# ─── Hauptfunktion: Frage → Antwort ─────────────────────────────────────────────

def ask_bot(question: str) -> str:
    relevant = retrieve_chunks(question, top_k=5)
    messages = build_system_prompt(relevant, question)
    resp = router_client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.2,
        max_tokens=512,
    )
    return resp.choices[0].message.content.strip()

# ─── Selbsttest ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    q = input("Frage an VuWall-Bot: ")
    print(ask_bot(q))
