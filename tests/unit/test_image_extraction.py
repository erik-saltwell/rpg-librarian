from __future__ import annotations

from pathlib import Path

from PIL import Image

from rpg_librarian.catalog.model.image_metadata import ImageMetadata
from rpg_librarian.metadata.image_extractor import ImageMetadataExtractor


def test_decompression_bomb_guard_is_disabled() -> None:
    # Importing the extractor must lift Pillow's pixel limit so that
    # legitimately huge maps/posters in the trusted library still extract.
    assert Image.MAX_IMAGE_PIXELS is None


def test_jpg_returns_image_metadata(fixtures_dir: Path) -> None:
    extractor = ImageMetadataExtractor(fixtures_dir / "image" / "cover_art.jpg")
    result = extractor.generate_media_type_specific_metadata()
    assert isinstance(result, ImageMetadata)


def test_jpg_dimensions_are_positive(fixtures_dir: Path) -> None:
    extractor = ImageMetadataExtractor(fixtures_dir / "image" / "cover_art.jpg")
    result = extractor.generate_media_type_specific_metadata()
    assert isinstance(result, ImageMetadata)
    assert isinstance(result.width, int) and result.width > 0
    assert isinstance(result.height, int) and result.height > 0


def test_jpg_pixel_count_equals_width_times_height(fixtures_dir: Path) -> None:
    extractor = ImageMetadataExtractor(fixtures_dir / "image" / "cover_art.jpg")
    result = extractor.generate_media_type_specific_metadata()
    assert isinstance(result, ImageMetadata)
    assert result.width is not None and result.height is not None
    assert result.pixel_count == result.width * result.height


def test_jpg_has_no_alpha(fixtures_dir: Path) -> None:
    extractor = ImageMetadataExtractor(fixtures_dir / "image" / "cover_art.jpg")
    result = extractor.generate_media_type_specific_metadata()
    assert isinstance(result, ImageMetadata)
    assert result.has_alpha is False


def test_jpg_extract_value_does_not_raise(fixtures_dir: Path) -> None:
    extractor = ImageMetadataExtractor(fixtures_dir / "image" / "cover_art.jpg")
    for field in ("artist", "copyright", "make", "model"):
        result = extractor.extract_value(field)
        assert result is None or isinstance(result, str)
