#!/usr/bin/env python3
"""Prep a source photo for ASCII conversion.

Steps:
  1. Remove the background with rembg.
  2. Enhance local contrast with CLAHE (OpenCV).
  3. Composite onto a white background.

Usage: python scripts/prep_photo.py [source-photo.png]
Output: source-prepped.png
"""
import sys
import numpy as np
import cv2
from PIL import Image
from rembg import remove

INP = sys.argv[1] if len(sys.argv) > 1 else "source-photo.png"
OUT = "source-prepped.png"


def main():
    src = Image.open(INP).convert("RGBA")

    # 1. background removal
    cut = remove(src)  # RGBA with alpha

    # 2. CLAHE contrast on the luminance channel
    rgb = np.array(cut.convert("RGB"))
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    rgb = cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2RGB)

    enhanced = Image.fromarray(rgb).convert("RGBA")
    enhanced.putalpha(cut.split()[-1])  # keep cutout alpha

    # 3. composite on white
    white = Image.new("RGBA", enhanced.size, (255, 255, 255, 255))
    out = Image.alpha_composite(white, enhanced).convert("RGB")
    out.save(OUT)
    print(f"Saved {OUT} ({out.size[0]}x{out.size[1]})")


if __name__ == "__main__":
    main()
