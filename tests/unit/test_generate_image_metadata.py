from __future__ import annotations

import struct
from pathlib import Path
from types import SimpleNamespace
from typing import cast

import pytest
from PIL import ExifTags, Image

from rpg_librarian.catalog.model.image_metadata import ImageMetadata
from rpg_librarian.metadata.image_extractor import ImageMetadataExtractor, get_exif_str, get_has_alpha


class _UnloadableImage:
    def __init__(self, error: Exception) -> None:
        self.error = error

    def load(self) -> None:
        raise self.error


def test_image_metadata_fields_default_to_none() -> None:
    assert ImageMetadata().model_dump() == {
        "width": None,
        "height": None,
        "pixel_count": None,
        "hash": None,
        "artists": None,
        "copyright": None,
        "has_alpha": None,
    }


@pytest.mark.parametrize(
    "error",
    [
        Image.DecompressionBombError("image too large"),
        EOFError("truncated image"),
        struct.error("invalid image structure"),
    ],
)
def test_image_extractor_raises_for_load_failures(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, error: Exception
) -> None:
    monkeypatch.setattr(Image, "open", lambda _: _UnloadableImage(error))

    with pytest.raises(Exception, match=r"."):
        ImageMetadataExtractor(tmp_path / "broken-image")


def test_image_extractor_reads_a_valid_image(tmp_path: Path) -> None:
    image_path = tmp_path / "image.png"
    Image.new("RGBA", (12, 8)).save(image_path)

    extractor = ImageMetadataExtractor(image_path)
    metadata = extractor.generate_media_type_specific_metadata()

    assert isinstance(metadata, ImageMetadata)
    assert metadata.width == 12
    assert metadata.height == 8
    assert metadata.pixel_count == 96
    assert isinstance(metadata.hash, str)
    assert metadata.has_alpha is True


def test_get_exif_str_decodes_bytes_as_utf8() -> None:
    artist_tag = next(tag_id for tag_id, name in ExifTags.TAGS.items() if name == "Artist")
    image = cast(Image.Image, SimpleNamespace(getexif=lambda: {artist_tag: b"  John \xffDoe  "}))

    assert get_exif_str(image, "Artist") == "John �Doe"


@pytest.mark.parametrize("mode", ["RGBA", "RGBa", "LA", "La", "PA"])
def test_get_has_alpha_recognizes_alpha_modes(mode: str) -> None:
    image = cast(Image.Image, SimpleNamespace(mode=mode, info={}))

    assert get_has_alpha(image) is True
