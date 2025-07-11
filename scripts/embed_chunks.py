# scripts/embed_chunks.py

import os
import json
import glob
import pickle
import numpy as np
import faiss
from pathlib import Path
from time import sleep
from openai import OpenAI
import openai

from dotenv import load_dotenv

load_dotenv()

# ─── Konfiguration ─────────────────────────────────────────────────────────────
OPENAI_EMBED_API_KEY = openai.api_key = os.getenv("OPENAI_EMBED_API_KEY")
EMBED_MODEL         = "text-embedding-3-small"

client = OpenAI(api_key=OPENAI_EMBED_API_KEY)

CHUNK_DIR     = Path("data/rag_chunks")
INDEX_DIR     = Path("embeddings/faiss_index")
INDEX_FILE    = INDEX_DIR / "index.faiss"
METADATA_FILE = INDEX_DIR / "meta.pkl"

def get_embedding(text: str) -> list[float]:
    resp = client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )
    # hier greifen wir korrekt aufs Attribut zu
    return resp.data[0].embedding

def main():
    # 1) Chunks laden
    chunks = []; texts = []
    for fn in glob.glob(str(CHUNK_DIR / "*.json")):
        with open(fn, "r", encoding="utf-8") as f:
            for entry in json.load(f):
                chunks.append(entry)
                texts.append(entry["text"])
    print(f"ℹ️ {len(texts)} Chunks geladen")

    # 2) Embeddings abrufen
    embeddings = []
    for i, txt in enumerate(texts, 1):
        embeddings.append(get_embedding(txt))
        if i % 50 == 0:
            sleep(1)
            print(f"  – {i}/{len(texts)} Chunks ge-embedded")

    # 3) FAISS-Index bauen
    dim   = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings, dtype="float32"))
    print(f"✅ FAISS-Index mit {index.ntotal} Vektoren erstellt")

    # 4) Index & Metadaten speichern
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_FILE))
    with open(METADATA_FILE, "wb") as f:
        pickle.dump(chunks, f)
    print("✅ Index und Metadaten gespeichert.")

if __name__ == "__main__":
    main()
