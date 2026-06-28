from __future__ import annotations

import struct
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from ..model.image_metadata import ImageMetadata
from ..tools.image_extraction import get_exif_str, get_has_alpha, get_hash, get_image_height, get_image_width


def generate_image_metadata(file_path: Path) -> ImageMetadata:
    try:
        image = Image.open(file_path)
        image.load()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, EOFError, struct.error):
        image = None

    width = get_image_width(image) if image else None
    height = get_image_height(image) if image else None

    return ImageMetadata(
        width=width,
        height=height,
        pixel_count=width * height if width is not None and height is not None else None,
        hash=get_hash(image) if image else None,
        artists=get_exif_str(image, "Artist") if image else None,
        copyright=get_exif_str(image, "Copyright") if image else None,
        has_alpha=get_has_alpha(image) if image else None,
    )
