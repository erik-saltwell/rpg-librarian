from __future__ import annotations

import imagehash
from PIL import ExifTags, Image


def get_image_width(image: Image.Image) -> int:
    return image.width


def get_image_height(image: Image.Image) -> int:
    return image.height


def get_hash(image: Image.Image) -> str:
    return str(imagehash.dhash(image))


def get_has_alpha(image: Image.Image) -> bool:
    if image.mode in ("RGBA", "RGBa", "LA", "La", "PA"):
        return True
    if image.mode == "P":
        return "transparency" in image.info
    return False


def get_exif_str(image: Image.Image, tag_name: str) -> str | None:
    exif = image.getexif()
    if not exif:
        return None
    tag_id = next((k for k, v in ExifTags.TAGS.items() if v == tag_name), None)
    if tag_id is None:
        return None
    val = exif.get(tag_id)
    if val is None:
        return None
    text = val.decode("utf-8", errors="replace") if isinstance(val, bytes) else str(val)
    return text.strip() or None
