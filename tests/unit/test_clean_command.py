from __future__ import annotations

from pathlib import Path

from rpg_librarian.commands.clean_command import CleanCommand
from rpg_librarian.utils import NullLogger, Tracer


def _run(root: Path) -> None:
    CleanCommand(root, logger=NullLogger(), tracer=Tracer()).execute_command()


def test_removes_empty_directory(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()

    _run(tmp_path)

    assert not empty.exists()


def test_keeps_non_empty_directory(tmp_path: Path) -> None:
    keep = tmp_path / "keep"
    keep.mkdir()
    (keep / "book.pdf").write_bytes(b"content")

    _run(tmp_path)

    assert keep.exists()
    assert (keep / "book.pdf").exists()


def test_removes_nested_empty_directories_cascading(tmp_path: Path) -> None:
    nested = tmp_path / "outer" / "inner"
    nested.mkdir(parents=True)

    _run(tmp_path)

    # The leaf is empty, and once removed its parent is empty too: both go.
    assert not (tmp_path / "outer").exists()


def test_removes_directory_left_empty_after_file_cleaning(tmp_path: Path) -> None:
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    (stub_dir / "debug.log").write_bytes(b"")  # zero-byte file gets cleaned

    _run(tmp_path)

    # The empty file is removed, leaving the directory empty, which is then removed.
    assert not stub_dir.exists()


def test_does_not_remove_root_even_when_empty(tmp_path: Path) -> None:
    _run(tmp_path)

    assert tmp_path.exists()
