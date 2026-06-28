from __future__ import annotations

from pathlib import Path

import mutagen.id3

from rpg_librarian.metadata.actions.generate_audio_metadata import generate_audio_metadata
from rpg_librarian.metadata.model.audio_metadata import AudioMetadata


def test_generate_audio_metadata_reads_tags(tmp_path: Path) -> None:
    audio_file = tmp_path / "test.mp3"
    tags = mutagen.id3.ID3()
    tags.add(mutagen.id3.TIT2(text=["Hello World"]))
    tags.add(mutagen.id3.TPE1(text=["Test Artist"]))
    tags.save(str(audio_file))

    metadata = generate_audio_metadata(audio_file)

    assert isinstance(metadata, AudioMetadata)
    assert metadata.title == "Hello World"
    assert metadata.artist == "Test Artist"
    assert metadata.duration is None or isinstance(metadata.duration, float)


def test_generate_audio_metadata_unreadable_file_returns_empty(tmp_path: Path) -> None:
    audio_file = tmp_path / "garbage.mp3"
    audio_file.write_bytes(b"\x00" * 64)

    metadata = generate_audio_metadata(audio_file)

    assert isinstance(metadata, AudioMetadata)
    assert metadata.title is None
    assert metadata.artist is None
    assert metadata.duration is None
