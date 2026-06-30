from __future__ import annotations

from pathlib import Path

from rpg_librarian.catalog.model.video_metadata import VideoMetadata
from rpg_librarian.metadata.video_extractor import VideoMetadataExtractor


def test_webm_returns_video_metadata(fixtures_dir: Path) -> None:
    extractor = VideoMetadataExtractor(fixtures_dir / "video" / "city_roofs.webm")
    result = extractor.generate_media_type_specific_metadata()
    assert isinstance(result, VideoMetadata)


def test_webm_duration_is_positive(fixtures_dir: Path) -> None:
    extractor = VideoMetadataExtractor(fixtures_dir / "video" / "city_roofs.webm")
    result = extractor.generate_media_type_specific_metadata()
    assert isinstance(result, VideoMetadata)
    assert isinstance(result.duration_seconds, float)
    assert result.duration_seconds > 0


def test_webm_has_positive_dimensions(fixtures_dir: Path) -> None:
    extractor = VideoMetadataExtractor(fixtures_dir / "video" / "city_roofs.webm")
    result = extractor.generate_media_type_specific_metadata()
    assert isinstance(result, VideoMetadata)
    assert isinstance(result.width, int) and result.width > 0
    assert isinstance(result.height, int) and result.height > 0


def test_webm_has_audio_is_bool(fixtures_dir: Path) -> None:
    extractor = VideoMetadataExtractor(fixtures_dir / "video" / "city_roofs.webm")
    result = extractor.generate_media_type_specific_metadata()
    assert isinstance(result, VideoMetadata)
    assert isinstance(result.has_audio, bool)


def test_extract_value_searches_tracks(fixtures_dir: Path) -> None:
    extractor = VideoMetadataExtractor(fixtures_dir / "video" / "city_roofs.webm")
    for field in ("title", "performer", "comment", "format"):
        result = extractor.extract_value(field)
        assert result is None or isinstance(result, str)
