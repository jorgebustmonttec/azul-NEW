import os
import math
from pathlib import Path
from PIL import Image
from concurrent.futures import ProcessPoolExecutor

# --- CONFIGURATION ---
TARGET_DIR = "./"        # Path to your site folder
SIZE_LIMIT_MB = 3        # Only touch files bigger than this
JPG_QUALITY = 80         # 80 is the "sweet spot" for web
PNG_COLORS = 256         # Reduces PNG size significantly (Quantization)
EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif'}

def compress_image(file_path):
    try:
        ext = file_path.suffix.lower()
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        
        with Image.open(file_path) as img:
            # --- JPG COMPRESSION ---
            if ext in ['.jpg', '.jpeg']:
                img.save(file_path, "JPEG", quality=JPG_QUALITY, optimize=True, progressive=True)
            
            # --- PNG COMPRESSION ---
            # If a PNG button is 5MB+, it's likely a 32-bit high-res file.
            # We convert to "P" mode (Palette) to slash size without losing transparency.
            elif ext == '.png':
                img = img.convert("P", palette=Image.ADAPTIVE, colors=PNG_COLORS)
                img.save(file_path, "PNG", optimize=True)
            
            # --- GIF COMPRESSION ---
            elif ext == '.gif':
                img.save(file_path, "GIF", save_all=True, optimize=True)

        new_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        return f"✅ {file_path.name}: {size_mb:.1f}MB -> {new_size_mb:.1f}MB"
    
    except Exception as e:
        return f"❌ Error processing {file_path.name}: {e}"

def main():
    files_to_process = []
    size_threshold = SIZE_LIMIT_MB * 1024 * 1024

    # 1. Walk through folders and find the heavy files
    print(f"Scanning {TARGET_DIR} for files > {SIZE_LIMIT_MB}MB...")
    for root, _, files in os.walk(TARGET_DIR):
        for name in files:
            file_path = Path(root) / name
            if file_path.suffix.lower() in EXTENSIONS:
                if os.path.getsize(file_path) > size_threshold:
                    files_to_process.append(file_path)

    if not files_to_process:
        print("No heavy files found! Your repo is safe.")
        return

    print(f"Found {len(files_to_process)} heavy images. Starting parallel compression...")

    # 2. Run in parallel using all available CPU cores
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(compress_image, files_to_process))

    for res in results:
        print(res)

if __name__ == "__main__":
    main()