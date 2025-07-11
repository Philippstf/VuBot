from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from pathlib import Path
import json
import re
import time

# INPUT
with open("data/sitemap_links.txt", "r") as f:
    urls = [line.strip() for line in f if line.strip()]

# OUTPUT
output_dir = Path("data/rag_chunks")
output_dir.mkdir(parents=True, exist_ok=True)

# Textreinigung
def clean_text(text: str) -> str:
    lines = text.splitlines()
    lines = [line.strip() for line in lines if line.strip()]
    lines = [line for line in lines if not re.match(r"\[.*?\]|\bClose\b|^×$", line)]
    return "\n".join(lines)

# Chunking-Funktion
def chunk_text(text: str, max_len=500, min_len=200):
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) <= max_len:
            current += " " + sentence
        else:
            if len(current.strip()) >= min_len:
                chunks.append(current.strip())
            current = sentence

    if len(current.strip()) >= min_len:
        chunks.append(current.strip())

    return chunks

# HTML -> sichtbarer Text extrahieren
def extract_text(html):
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main") or soup.body

    for tag in main(["script", "style", "nav", "footer", "header", "form", "aside"]):
        tag.decompose()

    return clean_text(main.get_text(separator="\n", strip=True))

# SCRAPE
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for url in urls:
        try:
            page.goto(url, timeout=20000)
            time.sleep(2)

            html = page.content()
            text = extract_text(html)
            chunks = chunk_text(text)

            title = url.rstrip("/").split("/")[-1] or "index"
            out_path = output_dir / f"{title}.json"

            data = []
            for i, chunk in enumerate(chunks):
                data.append({
                    "source_url": url,
                    "page_title": title,
                    "chunk_index": i,
                    "text": chunk
                })

            with open(out_path, "w", encoding="utf-8") as f_out:
                json.dump(data, f_out, ensure_ascii=False, indent=2)

            print(f"[✓] {title}.json – {len(chunks)} Chunks")

        except Exception as e:
            print(f"[!] Fehler bei {url}: {e}")

    browser.close()
