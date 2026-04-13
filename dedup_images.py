"""
Remove junk frames and near-duplicate images from the harp assembly sequence.
Uses average hash for perceptual similarity.
"""
import os
import struct
from pathlib import Path

IMG_DIR = Path("/home/clementsj/projects/clements47/images")

def read_image_bytes(path):
    """Read raw file bytes."""
    with open(path, 'rb') as f:
        return f.read()

def simple_hash(data):
    """Hash based on file size + sampled bytes."""
    # Sample bytes at regular intervals for a fingerprint
    step = max(1, len(data) // 64)
    samples = bytes(data[i] for i in range(0, len(data), step))[:64]
    return samples

# Try to use PIL for perceptual hashing
try:
    from PIL import Image
    import io
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("PIL not available, falling back to file-size based dedup")

def perceptual_hash(path, size=16):
    """Compute a simple average hash of the image."""
    if not HAS_PIL:
        data = read_image_bytes(path)
        return (os.path.getsize(path), simple_hash(data))
    
    img = Image.open(path).convert('L').resize((size, size), Image.LANCZOS)
    pixels = list(img.getdata())
    avg = sum(pixels) / len(pixels)
    return tuple(1 if p > avg else 0 for p in pixels)

def hamming_distance(h1, h2):
    """Hamming distance between two hashes."""
    if not HAS_PIL:
        return 0 if h1 == h2 else 100
    return sum(a != b for a, b in zip(h1, h2))

# Get all images sorted by name
files = sorted(IMG_DIR.iterdir())
print(f"Total files: {len(files)}")

# First pass: identify obviously junk frames (YouTube UI, black screens)
junk = []
keep_candidates = []

for f in files:
    if not f.suffix.lower() in ('.jpg', '.jpeg', '.png'):
        continue
    if HAS_PIL:
        try:
            img = Image.open(f)
            pixels = list(img.convert('L').resize((8,8)).getdata())
            avg = sum(pixels) / len(pixels)
            dark_pct = sum(1 for p in pixels if p < 30) / len(pixels)
            # Very dark frames are likely YouTube end screens
            if dark_pct > 0.7:
                junk.append(f)
                continue
        except:
            junk.append(f)
            continue
    keep_candidates.append(f)

print(f"Junk frames (dark/YouTube UI): {len(junk)}")

# Second pass: remove near-duplicates (keep first of each similar group)
# Threshold: hamming distance < 15% of hash bits
THRESHOLD = int(16 * 16 * 0.08)  # ~8% difference threshold for 16x16 hash
print(f"Similarity threshold: {THRESHOLD} bits")

hashes = []
keep = []
removed_dupes = []

for f in keep_candidates:
    try:
        h = perceptual_hash(f)
    except:
        keep.append(f)
        hashes.append(None)
        continue
    
    is_dupe = False
    # Only compare to recent frames (sequential video, dupes are adjacent)
    for i in range(max(0, len(hashes)-5), len(hashes)):
        if hashes[i] is not None and hamming_distance(h, hashes[i]) <= THRESHOLD:
            is_dupe = True
            removed_dupes.append(f)
            break
    
    if not is_dupe:
        keep.append(f)
        hashes.append(h)
    else:
        hashes.append(h)  # still track hash for chain comparison

print(f"Near-duplicates: {len(removed_dupes)}")
print(f"Keeping: {len(keep)}")

# Delete junk and duplicates
deleted = 0
for f in junk + removed_dupes:
    f.unlink()
    deleted += 1

print(f"Deleted {deleted} files")
print(f"Remaining: {len(list(IMG_DIR.iterdir()))} files")
