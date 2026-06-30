from __future__ import annotations

from pathlib import Path

import mutagen.id3

from rpg_librarian.metadata.audio_extractor import AudioMetadataExtractor


def test_extract_value_reads_title_tag(tmp_path: Path) -> None:
    audio_file = tmp_path / "test.mp3"
    tags = mutagen.id3.ID3()
    tags.add(mutagen.id3.TIT2(text=["Hello World"]))
    tags.add(mutagen.id3.TPE1(text=["Test Artist"]))
    tags.save(str(audio_file))

    extractor = AudioMetadataExtractor(audio_file)

    assert extractor.extract_value("title") == "Hello World"
    assert extractor.extract_value("artist") == "Test Artist"


def test_extract_value_returns_none_for_unreadable_file(tmp_path: Path) -> None:
    audio_file = tmp_path / "garbage.mp3"
    audio_file.write_bytes(b"\x00" * 64)

    extractor = AudioMetadataExtractor(audio_file)

    assert extractor.extract_value("title") is None
    assert extractor.extract_value("artist") is None
