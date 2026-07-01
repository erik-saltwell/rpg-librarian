from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest

import rpg_librarian.commands.build_catalog_command as build_catalog_command
from rpg_librarian.catalog.model.catalog import Catalog
from rpg_librarian.catalog.model.library_data import LibraryData
from rpg_librarian.commands.build_catalog_command import BuildCatalogCommand
from rpg_librarian.utils import NullLogger, ProgressTask, Tracer


class _RecordingTask(ProgressTask):
    def __init__(self) -> None:
        self.advances = 0
        self.completed: int | None = None

    def advance(self, n: int = 1) -> None:
        self.advances += n

    def set_total(self, total: int | None) -> None:
        pass

    def set_completed(self, completed: int) -> None:
        self.completed = completed

    def set_description(self, description: str) -> None:
        pass

    def close(self) -> None:
        pass


class _RecordingLogger(NullLogger):
    def __init__(self) -> None:
        self.task = _RecordingTask()
        self.progress_total: int | None = None

    @contextmanager
    def progress(self, description: str, total: int | None = None) -> Iterator[ProgressTask]:
        self.progress_total = total
        yield self.task


def _make_files(directory: Path, names: list[str]) -> None:
    for name in names:
        (directory / name).write_text(name, encoding="utf-8")


def test_progress_reaches_total_on_full_build(tmp_path: Path) -> None:
    _make_files(tmp_path, ["a.txt", "b.txt", "c.txt"])
    logger = _RecordingLogger()

    BuildCatalogCommand(tmp_path, logger=logger, tracer=Tracer()).execute_command()

    assert logger.progress_total == 3
    assert logger.task.advances == 3
    assert logger.task.completed == 3  # snapped to 100%


def test_incremental_rebuild_skips_already_cataloged_files(tmp_path: Path) -> None:
    _make_files(tmp_path, ["a.txt", "b.txt"])
    BuildCatalogCommand(tmp_path, logger=NullLogger(), tracer=Tracer()).execute_command()

    # An append-only rebuild has no work when every file is already cataloged.
    logger = _RecordingLogger()
    BuildCatalogCommand(tmp_path, logger=logger, tracer=Tracer()).execute_command()

    assert logger.progress_total == 0
    assert logger.task.advances == 0
    assert logger.task.completed == 0


def _catalog_filenames(library: LibraryData) -> set[str]:
    return {
        entry.file_data.filename
        for entry in Catalog.load(library.index_file).entries
        if entry.file_data is not None
    }


def test_empty_library_still_writes_an_index(tmp_path: Path) -> None:
    BuildCatalogCommand(tmp_path, logger=NullLogger(), tracer=Tracer()).execute_command()

    library = LibraryData(root_folder=tmp_path)
    assert library.index_file.exists()
    assert Catalog.load(library.index_file).entries == []


def test_saves_initial_state_every_ten_entries_and_final_remainder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _make_files(tmp_path, [f"{number:02}.txt" for number in range(11)])
    save_calls: list[tuple[int, bool]] = []
    original_save = Catalog.save

    def recording_save(self: Catalog, path: str | Path, backup: bool = True) -> None:
        save_calls.append((len(self.entries), backup))
        original_save(self, path, backup=backup)

    monkeypatch.setattr(Catalog, "save", recording_save)

    BuildCatalogCommand(tmp_path, logger=NullLogger(), tracer=Tracer()).execute_command()

    assert save_calls == [(0, True), (10, False), (11, True)]


def test_file_that_fails_extraction_is_not_reprocessed_or_duplicated(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _make_files(tmp_path, ["broken.txt"])
    library = LibraryData(root_folder=tmp_path)

    # Simulate an entry whose file_data extraction failed: no file_data, but the
    # filepath is still recorded. Such an entry must count as already-seen so it is
    # neither reprocessed nor appended again on the next run.
    from rpg_librarian.catalog.model.catalog_entry import CatalogEntry

    original = build_catalog_command.generate_catalog_entry

    def failed_extraction(file_path: Path, lib: object) -> CatalogEntry:
        entry = original(file_path, lib)
        return CatalogEntry(id=entry.id, filepath=file_path, errors=["boom"])

    monkeypatch.setattr(build_catalog_command, "generate_catalog_entry", failed_extraction)
    BuildCatalogCommand(tmp_path, logger=NullLogger(), tracer=Tracer()).execute_command()

    logger = _RecordingLogger()
    BuildCatalogCommand(tmp_path, logger=logger, tracer=Tracer()).execute_command()

    assert logger.progress_total == 0  # the failed file is recognized, not retried
    entries = Catalog.load(library.index_file).entries
    assert [str(entry.filepath) for entry in entries] == [str(tmp_path / "broken.txt")]


def test_crash_mid_run_preserves_prior_progress(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _make_files(tmp_path, ["a.txt", "b.txt"])
    BuildCatalogCommand(tmp_path, logger=NullLogger(), tracer=Tracer()).execute_command()

    library = LibraryData(root_folder=tmp_path)
    assert _catalog_filenames(library) == {"a.txt", "b.txt"}

    # Add unseen work, then simulate a crash while processing it. The initial save
    # must leave the entries from the prior successful run intact.
    _make_files(tmp_path, ["c.txt"])

    def boom(*args: object, **kwargs: object) -> object:
        raise RuntimeError("simulated crash")

    monkeypatch.setattr(build_catalog_command, "generate_catalog_entry", boom)

    with pytest.raises(RuntimeError, match="simulated crash"):
        BuildCatalogCommand(tmp_path, logger=NullLogger(), tracer=Tracer()).execute_command()

    assert _catalog_filenames(library) == {"a.txt", "b.txt"}
