from __future__ import annotations

from pathlib import Path

from pymediainfo import MediaInfo

from ..catalog.model.media_type_metadata import MediaTypeMetadata
from ..catalog.model.video_metadata import VideoMetadata
from .metadata_extractor import MetadataExtractor


def get_duration(media_info: MediaInfo | None) -> float | None:
    """Return the first video track's duration in seconds."""
    if media_info is None or not media_info.video_tracks:
        return None

    duration_milliseconds = media_info.video_tracks[0].duration
    if duration_milliseconds is None:
        return None

    try:
        return round(float(duration_milliseconds) / 1000, 3)
    except (TypeError, ValueError):
        return None


def get_width(media_info: MediaInfo | None) -> int | None:
    """Return the first video track's width in pixels."""
    if media_info is None or not media_info.video_tracks:
        return None

    try:
        return int(media_info.video_tracks[0].width)
    except (TypeError, ValueError):
        return None


def get_height(media_info: MediaInfo | None) -> int | None:
    """Return the first video track's height in pixels."""
    if media_info is None or not media_info.video_tracks:
        return None

    try:
        return int(media_info.video_tracks[0].height)
    except (TypeError, ValueError):
        return None


def get_has_audio(media_info: MediaInfo | None) -> bool | None:
    """Return whether the media contains at least one audio track."""
    if media_info is None:
        return None
    return bool(media_info.audio_tracks)


class VideoMetadataExtractor(MetadataExtractor):
    def __init__(self, file_path: Path):
        self._media_info: MediaInfo = MediaInfo.parse(filename=file_path)

    def extract_value(self, candidate: str) -> str | None:
        key = candidate.lower()
        for track in [*self._media_info.general_tracks, *self._media_info.video_tracks]:
            value = getattr(track, key, None)
            if value is not None:
                text = str(value).strip()
                if text:
                    return text
        return None

    def generate_media_type_specific_metadata(self) -> MediaTypeMetadata:
        return VideoMetadata(
            duration_seconds=get_duration(self._media_info),
            width=get_width(self._media_info),
            height=get_height(self._media_info),
            has_audio=get_has_audio(self._media_info),
        )
