from __future__ import annotations

from pathlib import Path

from mutagen import File as MutagenFile
from mutagen import MutagenError
from mutagen.easyid3 import EasyID3

from ..model.audio_metadata import AudioMetadata
from ..tools.audio_extraction import get_duration, get_fingerprint, get_tag


def _open_audio(file_path: Path) -> object | None:
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


def generate_audio_metadata(file_path: Path) -> AudioMetadata:
    audio_file = _open_audio(file_path)

    return AudioMetadata(
        acoustic_fingerprint=get_fingerprint(file_path),
        duration=get_duration(audio_file),
        title=get_tag(audio_file, "title"),
        artist=get_tag(audio_file, "artist"),
        album=get_tag(audio_file, "album"),
        year=get_tag(audio_file, "date"),
        track_number=get_tag(audio_file, "tracknumber"),
        genre=get_tag(audio_file, "genre"),
        publisher=get_tag(audio_file, "organization"),
        copyright=get_tag(audio_file, "copyright"),
    )
