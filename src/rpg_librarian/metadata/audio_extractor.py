from __future__ import annotations

from pathlib import Path
from typing import Any

from mutagen import File as MutagenFile
from mutagen import FileType, MutagenError
from mutagen.easyid3 import EasyID3

from ..catalog.model.audio_metadata import AudioMetadata
from ..catalog.model.media_type_metadata import MediaTypeMetadata
from .metadata_extractor import MetadataExtractor

type AudioFile = FileType | EasyID3


def get_duration(audio_file: Any) -> float | None:
    info = getattr(audio_file, "info", None)
    return round(info.length, 3) if info and hasattr(info, "length") else None


def _open_audio(file_path: Path) -> AudioFile | None:
    try:
        audio_file = MutagenFile(file_path, easy=True)
    except MutagenError:
        audio_file = None

    if audio_file is not None:
        return audio_file

    try:
        return EasyID3(file_path)
    except MutagenError:
        return None


class AudioMetadataExtractor(MetadataExtractor):
    def __init__(self, file_path: Path):
        self._audio: AudioFile | None = _open_audio(file_path=file_path)

    def extract_value(self, candidate: str) -> str | None:
        if self._audio is None:
            return None
        key = candidate.lower()
        for tag_key, tag_value in self._audio.items():
            if tag_key.lower() == key:
                values = tag_value if isinstance(tag_value, list) else [tag_value]
                for v in values:
                    text = str(v).strip()
                    if text:
                        return text
        return None

    def generate_media_type_specific_metadata(self) -> MediaTypeMetadata:
        return AudioMetadata(duration=get_duration(self._audio))
