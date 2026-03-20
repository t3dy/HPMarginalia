"""Compress BL manuscript images for GitHub Pages deployment.

Strategy 1: Resize BL images (~4MB each) to match Siena quality (~500KB each).
Siena images are already small enough and are left untouched.

Output: site/images/bl/ and site/images/siena/ with web-ready JPEGs.
Original files are not modified.
"""

import os
import shutil
from pathlib import Path

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

BASE_DIR = Path(__file__).resolve().parent.parent
SITE_DIR = BASE_DIR / "site"

BL_SOURCE = BASE_DIR / "3 BL C.60.o.12 Photos-20260319T001113Z-3-001" / "3 BL C.60.o.12 Photos"
SIENA_SOURCE = BASE_DIR / "Siena O.III.38 Digital Facsimile-20260319T001110Z-3-001" / "Siena O.III.38 Digital Facsimile"

BL_DEST = SITE_DIR / "images" / "bl"
SIENA_DEST = SITE_DIR / "images" / "siena"

# Target: ~800px wide at 75% JPEG quality ≈ 300-500KB per image
TARGET_WIDTH = 800
JPEG_QUALITY = 75


def compress_with_pil(src, dst, target_width=TARGET_WIDTH, quality=JPEG_QUALITY):
    """Compress a JPEG using Pillow."""
    img = Image.open(src)
    # Calculate height to maintain aspect ratio
    w, h = img.size
    if w > target_width:
        ratio = target_width / w
        new_size = (target_width, int(h * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    img.save(dst, "JPEG", quality=quality, optimize=True)
    return dst.stat().st_size


def copy_if_small(src, dst, max_size=600_000):
    """Copy file if already under max_size, otherwise skip (needs PIL)."""
    if src.stat().st_size <= max_size:
        shutil.copy2(src, dst)
        return src.stat().st_size
    return None


def main():
    print("=== Compressing Images for GitHub Pages ===\n")

    if not HAS_PIL:
        print("Pillow not installed. Falling back to copy-only mode.")
        print("Install with: pip install Pillow")
        print("For now, copying Siena images (already small) and skipping BL (too large).\n")

    # Create output directories
    BL_DEST.mkdir(parents=True, exist_ok=True)
    SIENA_DEST.mkdir(parents=True, exist_ok=True)

    # Process BL images
    bl_files = sorted(BL_SOURCE.glob("*.jpg")) if BL_SOURCE.exists() else []
    print(f"BL source: {len(bl_files)} files")

    bl_processed = 0
    bl_total_size = 0
    for src in bl_files:
        dst = BL_DEST / src.name
        if dst.exists():
            bl_processed += 1
            bl_total_size += dst.stat().st_size
            continue

        if HAS_PIL:
            size = compress_with_pil(src, dst)
            bl_total_size += size
            bl_processed += 1
        else:
            # Without PIL, skip large BL files
            result = copy_if_small(src, dst)
            if result:
                bl_total_size += result
                bl_processed += 1

    print(f"  BL processed: {bl_processed}, total: {bl_total_size // 1024 // 1024} MB")

    # Process Siena images (already small, just copy)
    siena_files = sorted(SIENA_SOURCE.glob("*.jpg")) if SIENA_SOURCE.exists() else []
    print(f"Siena source: {len(siena_files)} files")

    siena_processed = 0
    siena_total_size = 0
    for src in siena_files:
        dst = SIENA_DEST / src.name
        if not dst.exists():
            shutil.copy2(src, dst)
        siena_processed += 1
        siena_total_size += dst.stat().st_size

    print(f"  Siena processed: {siena_processed}, total: {siena_total_size // 1024 // 1024} MB")

    total = (bl_total_size + siena_total_size) // 1024 // 1024
    print(f"\nTotal image output: {total} MB")
    print(f"Output directories: {BL_DEST}, {SIENA_DEST}")
    print("Done.")


if __name__ == "__main__":
    main()
