from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from pathlib import Path
import time

# Input: Liste der URLs
with open("data/sitemap_links.txt", "r") as f:
    urls = [line.strip() for line in f if line.strip()]

output_dir = Path("data/html_pages")
output_dir.mkdir(parents=True, exist_ok=True)

def extract_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for url in urls:
        try:
            page.goto(url, timeout=20000)
            time.sleep(2)  # optional: warten bis Seite ganz geladen ist
            html = page.content()
            text = extract_text(html)

            title = url.rstrip("/").split("/")[-1] or "index"
            filename = output_dir / f"{title}.txt"

            with open(filename, "w", encoding="utf-8") as f_out:
                f_out.write(text)

            print(f"[✓] Gespeichert: {filename.name}")

        except Exception as e:
            print(f"[!] Fehler bei {url}: {e}")

    browser.close()
