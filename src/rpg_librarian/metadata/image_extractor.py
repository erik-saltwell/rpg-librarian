from __future__ import annotations

from pathlib import Path

from PIL import ExifTags, Image

from ..catalog.model.image_metadata import ImageMetadata
from ..catalog.model.media_type_metadata import MediaTypeMetadata
from .metadata_extractor import MetadataExtractor

# This catalog indexes a trusted local library, so Pillow's decompression-bomb
# guard (which raises for images above ~179M pixels as a possible DOS attack) only
# rejects legitimately huge maps and posters. Disable the limit so they extract.
Image.MAX_IMAGE_PIXELS = None


def get_image_width(image: Image.Image) -> int:
    return image.width


def get_image_height(image: Image.Image) -> int:
    return image.height


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


class ImageMetadataExtractor(MetadataExtractor):
    def __init__(self, file_path: Path):
        self._image = Image.open(file_path)
        self._image.load()

    def extract_value(self, candidate: str) -> str | None:
        key = candidate.lower()
        exif = self._image.getexif()
        if not exif:
            return None
        for tag_id, tag_name in ExifTags.TAGS.items():
            if tag_name.lower() == key:
                val = exif.get(tag_id)
                if val is not None:
                    text = val.decode("utf-8", errors="replace") if isinstance(val, bytes) else str(val)
                    text = text.strip()
                    if text:
                        return text
        return None

    def generate_media_type_specific_metadata(self) -> MediaTypeMetadata:
        image = self._image
        width = get_image_width(image) if image else None
        height = get_image_height(image) if image else None

        return ImageMetadata(
            width=width,
            height=height,
            pixel_count=width * height if width is not None and height is not None else None,
            artists=get_exif_str(image, "Artist") if image else None,
            copyright=get_exif_str(image, "Copyright") if image else None,
            has_alpha=get_has_alpha(image) if image else None,
        )
