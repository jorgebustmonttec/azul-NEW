import os
import subprocess
from pathlib import Path
from PIL import Image
from concurrent.futures import ProcessPoolExecutor

# --- CONFIGURATION ---
TARGET_DIR = "./"
SIZE_LIMIT_MB = 3
JPG_QUALITY = 80
PNG_COLORS = 256
# Gifsicle lossy level: 30 (light) to 200 (heavy). 80 is a good middle ground.
GIF_LOSSY = 80 

def compress_gif(file_path):
    """Uses Gifsicle to compress GIFs (keeps them animated)"""
    try:
        temp_path = file_path.with_suffix('.tmp.gif')
        # --optimize=3: heaviest optimization
        # --lossy: introduces slight noise to drastically drop size
        # --scale 0.8: optional, shrinks dimensions by 20% to save even more
        cmd = [
            "gifsicle", "--optimize=3", 
            f"--lossy={GIF_LOSSY}", 
            str(file_path), 
            "-o", str(temp_path)
        ]
        
        subprocess.run(cmd, check=True)
        
        orig_size = os.path.getsize(file_path)
        new_size = os.path.getsize(temp_path)
        
        # Only overwrite if it actually got smaller
        if new_size < orig_size:
            os.replace(temp_path, file_path)
            return f"✅ GIF: {file_path.name} ({orig_size/(1024*1024):.1f}MB -> {new_size/(1024*1024):.1f}MB)"
        else:
            os.remove(temp_path)
            return f"ℹ️ GIF: {file_path.name} was already optimized."
    except Exception as e:
        return f"❌ GIF Error {file_path.name}: {e}"

def compress_static(file_path):
    """Uses Pillow for PNG/JPG"""
    try:
        ext = file_path.suffix.lower()
        orig_size = os.path.getsize(file_path)
        
        with Image.open(file_path) as img:
            if ext in ['.jpg', '.jpeg']:
                img.save(file_path, "JPEG", quality=JPG_QUALITY, optimize=True)
            elif ext == '.png':
                img = img.convert("P", palette=Image.ADAPTIVE, colors=PNG_COLORS)
                img.save(file_path, "PNG", optimize=True)
        
        new_size = os.path.getsize(file_path)
        return f"✅ IMG: {file_path.name} ({orig_size/(1024*1024):.1f}MB -> {new_size/(1024*1024):.1f}MB)"
    except Exception as e:
        return f"❌ IMG Error {file_path.name}: {e}"

def worker(file_path):
    if file_path.suffix.lower() == '.gif':
        return compress_gif(file_path)
    else:
        return compress_static(file_path)

def main():
    files_to_process = []
    size_threshold = SIZE_LIMIT_MB * 1024 * 1024
    exts = {'.png', '.jpg', '.jpeg', '.gif'}

    for root, _, files in os.walk(TARGET_DIR):
        for name in files:
            fp = Path(root) / name
            if fp.suffix.lower() in exts and os.path.getsize(fp) > size_threshold:
                files_to_process.append(fp)

    print(f"Found {len(files_to_process)} files to crush. Let's go...")

    with ProcessPoolExecutor() as executor:
        results = list(executor.map(worker, files_to_process))

    for res in results:
        print(res)

if __name__ == "__main__":
    main()