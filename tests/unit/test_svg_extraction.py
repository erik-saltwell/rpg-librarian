from __future__ import annotations

from pathlib import Path

from rpg_librarian.catalog.model.media_type import MediaType
from rpg_librarian.catalog.model.svg_metadata import SvgMetadata
from rpg_librarian.catalog.tools.media_type_detector import (
    find_media_type_from_mime_type,
    find_mime_type,
)
from rpg_librarian.metadata.generate_extractor import generate_extractor
from rpg_librarian.metadata.svg_extractor import SvgMetadataExtractor


def test_svg_returns_svg_metadata(fixtures_dir: Path) -> None:
    extractor = SvgMetadataExtractor(fixtures_dir / "vector" / "flag.svg")
    result = extractor.generate_media_type_specific_metadata()
    assert isinstance(result, SvgMetadata)


def test_svg_width_height_from_attributes(fixtures_dir: Path) -> None:
    extractor = SvgMetadataExtractor(fixtures_dir / "vector" / "flag.svg")
    result = extractor.generate_media_type_specific_metadata()
    assert isinstance(result, SvgMetadata)
    assert result.width == 64.0
    assert result.height == 48.0
    assert result.units == "px"
    assert result.view_box == "0 0 640 480"


def test_svg_dimensions_fall_back_to_view_box(fixtures_dir: Path) -> None:
    extractor = SvgMetadataExtractor(fixtures_dir / "vector" / "viewbox_only.svg")
    result = extractor.generate_media_type_specific_metadata()
    assert isinstance(result, SvgMetadata)
    assert result.width == 100.0
    assert result.height == 200.0
    assert result.units is None
    assert result.view_box == "0 0 100 200"


def test_svg_extract_base_metadata(fixtures_dir: Path) -> None:
    extractor = SvgMetadataExtractor(fixtures_dir / "vector" / "flag.svg")
    assert extractor.extract_value("title") == "Flag of Testland"
    assert extractor.extract_value("artist") == "Jane Cartographer"
    assert extractor.extract_value("publisher") == "Arc Dream Publishing"
    assert extractor.extract_value("copyright") == "CC-BY-4.0"
    assert extractor.extract_value("genre") is None


def test_svg_mime_maps_to_vector() -> None:
    assert find_media_type_from_mime_type("image/svg+xml") == MediaType.vector


def test_svg_extension_routes_to_vector(fixtures_dir: Path) -> None:
    mime_type = find_mime_type(fixtures_dir / "vector" / "flag.svg")
    assert find_media_type_from_mime_type(mime_type) == MediaType.vector


def test_generate_extractor_returns_svg_extractor(fixtures_dir: Path) -> None:
    extractor = generate_extractor(MediaType.vector, fixtures_dir / "vector" / "flag.svg")
    assert isinstance(extractor, SvgMetadataExtractor)


def test_malformed_svg_degrades_to_empty_metadata(fixtures_dir: Path) -> None:
    extractor = SvgMetadataExtractor(fixtures_dir / "vector" / "malformed.svg")
    result = extractor.generate_media_type_specific_metadata()
    assert isinstance(result, SvgMetadata)
    assert result.width is None
    assert result.height is None
    assert extractor.extract_value("title") is None
