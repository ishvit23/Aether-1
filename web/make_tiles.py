import os
from PIL import Image, ImageDraw

def main():
    os.makedirs("public", exist_ok=True)
    img = Image.new("RGBA", (64, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Tile 0: Grass (x: 0 to 15)
    d.rectangle([0, 0, 15, 15], fill="#2d4c1e")
    d.line([2, 10, 2, 6], fill="#447a2c", width=1)
    d.line([8, 12, 8, 5], fill="#447a2c", width=1)
    d.line([13, 8, 13, 4], fill="#447a2c", width=1)

    # Tile 1: Wall (x: 16 to 31)
    d.rectangle([16, 0, 31, 15], fill="#555555")
    d.line([16, 4, 31, 4], fill="#333333", width=1)
    d.line([16, 10, 31, 10], fill="#333333", width=1)
    d.line([22, 0, 22, 4], fill="#333333", width=1)
    d.line([26, 4, 26, 10], fill="#333333", width=1)

    # Tile 2: Nest (x: 32 to 47)
    d.rectangle([32, 0, 47, 15], fill="#2d4c1e") # grass bg
    d.ellipse([34, 4, 45, 12], fill="#5c4033", outline="#3b2b20") # nest
    d.ellipse([37, 6, 42, 10], fill="#3b2b20") # inner hole

    # Tile 3: Humanoid Base Sprite (x: 48 to 63)
    d.rectangle([48, 0, 63, 15], fill=(0,0,0,0)) # clear bg
    # Head
    d.rectangle([53, 2, 58, 6], fill="#FFFFFF", outline="#000000")
    # Body
    d.rectangle([52, 7, 59, 11], fill="#FFFFFF", outline="#000000")
    # Legs
    d.rectangle([53, 12, 54, 15], fill="#FFFFFF", outline="#000000")
    d.rectangle([57, 12, 58, 15], fill="#FFFFFF", outline="#000000")

    img.save("public/tiles.png")
    print("Generated public/tiles.png successfully.")

if __name__ == "__main__":
    main()
