import requests
from bs4 import BeautifulSoup
import os

def extract_vuwall_text(url="https://vuwall.com") -> str:
    """
    Ruft den Inhalt der angegebenen URL ab, filtert sichtbaren Text
    und gibt ihn als bereinigte Zeichenkette zurück.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Entferne irrelevante Teile wie Scripts, Styles, Footer
    for tag in soup(["script", "style", "footer", "nav", "header"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    clean_text = "\n".join(line for line in lines if line)

    return clean_text

def save_text_to_file(text: str, path="data/vuwall_knowledge.txt"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

if __name__ == "__main__":
    print("[INFO] Extrahiere Inhalte von vuwall.com ...")
    text = extract_vuwall_text()
    save_text_to_file(text)
    print("[INFO] Text gespeichert unter: data/vuwall_knowledge.txt")
