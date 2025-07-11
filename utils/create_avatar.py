# utils/create_avatar.py

from PIL import Image, ImageDraw
import io
import base64

def create_vuwall_avatar():
    """Erstellt ein rundes Avatar mit VuWall W auf weißem Hintergrund"""
    
    # Lade das VuWall W Logo
    w_logo = Image.open("utils/W_transparent.png")
    
    # Erstelle einen weißen runden Hintergrund
    size = 100
    avatar = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    
    # Zeichne weißen Kreis
    draw = ImageDraw.Draw(avatar)
    draw.ellipse([2, 2, size-2, size-2], fill='white', outline='#e0e0e0', width=2)
    
    # Resize das W Logo um in den Kreis zu passen
    logo_size = int(size * 0.6)  # 60% der Avatar-Größe
    w_logo = w_logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
    
    # Zentriere das W Logo
    x = (size - logo_size) // 2
    y = (size - logo_size) // 2
    
    # Füge das W Logo zum Avatar hinzu
    avatar.paste(w_logo, (x, y), w_logo)
    
    # Speichere das Avatar
    avatar.save("utils/vuwall_avatar.png")
    
    return "utils/vuwall_avatar.png"

if __name__ == "__main__":
    avatar_path = create_vuwall_avatar()
    print(f"Avatar erstellt: {avatar_path}")