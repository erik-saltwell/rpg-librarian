from __future__ import annotations

from pathlib import Path

from rpg_librarian.catalog.model.audio_metadata import AudioMetadata
from rpg_librarian.metadata.audio_extractor import AudioMetadataExtractor


def test_audio_metadata_contains_only_duration() -> None:
    assert AudioMetadata(duration=None).model_dump() == {"duration": None}


def test_wav_returns_audio_metadata(fixtures_dir: Path) -> None:
    extractor = AudioMetadataExtractor(fixtures_dir / "audio" / "button_select.wav")
    result = extractor.generate_media_type_specific_metadata()
    assert isinstance(result, AudioMetadata)


def test_wav_duration_is_positive_float(fixtures_dir: Path) -> None:
    extractor = AudioMetadataExtractor(fixtures_dir / "audio" / "button_select.wav")
    result = extractor.generate_media_type_specific_metadata()
    assert isinstance(result, AudioMetadata)
    assert isinstance(result.duration, float)
    assert result.duration > 0


def test_mp3_duration_is_positive_float(fixtures_dir: Path) -> None:
    extractor = AudioMetadataExtractor(fixtures_dir / "audio" / "the_wedding.mp3")
    result = extractor.generate_media_type_specific_metadata()
    assert isinstance(result, AudioMetadata)
    assert isinstance(result.duration, float)
    assert result.duration > 0


def test_ogg_duration_is_positive_float(fixtures_dir: Path) -> None:
    extractor = AudioMetadataExtractor(fixtures_dir / "audio" / "battle_theme.ogg")
    result = extractor.generate_media_type_specific_metadata()
    assert isinstance(result, AudioMetadata)
    assert isinstance(result.duration, float)
    assert result.duration > 0


def test_extract_value_from_ogg_does_not_raise(fixtures_dir: Path) -> None:
    extractor = AudioMetadataExtractor(fixtures_dir / "audio" / "battle_theme.ogg")
    result = extractor.extract_value("title")
    assert result is None or isinstance(result, str)


def test_extract_value_from_mp3_does_not_raise(fixtures_dir: Path) -> None:
    extractor = AudioMetadataExtractor(fixtures_dir / "audio" / "the_wedding.mp3")
    for field in ("title", "artist", "genre"):
        result = extractor.extract_value(field)
        assert result is None or isinstance(result, str)
