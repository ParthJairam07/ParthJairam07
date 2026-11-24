"""Prep a photo for ASCII conversion.

Crops to head + chest, removes the background, boosts local contrast (CLAHE)
and writes a grayscale image on white plus the subject mask.

    python scripts/prep_photo.py source-photo.jpg [left top right bottom]

The optional crop box is in fractions of the image size (0..1).
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps
from rembg import remove

try:
    import pillow_heif

    pillow_heif.register_heif_opener()
except ImportError:
    pass

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CROP = (0.3, 0.29, 0.725, 0.625)
MAX_SIDE = 1400


def main() -> None:
    src = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "source-photo.jpg")
    crop = tuple(float(v) for v in sys.argv[2:6]) if len(sys.argv) >= 6 else DEFAULT_CROP

    img = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    w, h = img.size
    img = img.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h)))
    img.thumbnail((MAX_SIDE, MAX_SIDE))

    cut = remove(img)
    alpha = np.asarray(cut.split()[-1], dtype=np.float32) / 255.0

    gray = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray).astype(np.float32)

    out = gray * alpha + 255.0 * (1.0 - alpha)
    Image.fromarray(out.clip(0, 255).astype(np.uint8)).save(ROOT / "source-prepped.png")
    Image.fromarray((alpha * 255).astype(np.uint8)).save(ROOT / "source-mask.png")
    print("wrote source-prepped.png and source-mask.png", img.size)


if __name__ == "__main__":
    main()
