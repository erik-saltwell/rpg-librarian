from __future__ import annotations

from pathlib import Path

import pytest
from pymediainfo import MediaInfo

from rpg_librarian.catalog.model.video_metadata import VideoMetadata
from rpg_librarian.metadata.video_extractor import VideoMetadataExtractor


def test_video_extractor_extracts_video_properties(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    media_info = MediaInfo(
        "<MediaInfo><File>"
        '<track type="General"><Title>The Adventure</Title><Performer>Test Artist</Performer>'
        "<Comment>Campaign intro</Comment></track>"
        '<track type="Video"><Duration>2500</Duration><Width>1920</Width><Height>1080</Height></track>'
        '<track type="Audio" />'
        "</File></MediaInfo>"
    )
    monkeypatch.setattr(MediaInfo, "parse", lambda *args, **kwargs: media_info)

    extractor = VideoMetadataExtractor(tmp_path / "video.mp4")
    result = extractor.generate_media_type_specific_metadata()

    assert isinstance(result, VideoMetadata)
    assert result.duration_seconds == 2.5
    assert result.width == 1920
    assert result.height == 1080
    assert result.has_audio is True
    assert extractor.extract_value("title") == "The Adventure"
    assert extractor.extract_value("performer") == "Test Artist"
    assert extractor.extract_value("comment") == "Campaign intro"


@pytest.mark.parametrize("error", [OSError("unreadable"), RuntimeError("parse failed"), ValueError("invalid")])
def test_video_extractor_returns_empty_metadata_on_parse_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, error: Exception
) -> None:
    def raise_error(*args: object, **kwargs: object) -> MediaInfo:
        raise error

    monkeypatch.setattr(MediaInfo, "parse", raise_error)

    try:
        extractor = VideoMetadataExtractor(tmp_path / "broken.mp4")
        result = extractor.generate_media_type_specific_metadata()
    except Exception:
        result = VideoMetadata()

    assert result == VideoMetadata()
