from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

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


def test_progress_reaches_total_on_incremental_rebuild(tmp_path: Path) -> None:
    _make_files(tmp_path, ["a.txt", "b.txt"])
    BuildCatalogCommand(tmp_path, logger=NullLogger(), tracer=Tracer()).execute_command()

    # Second run reuses the unchanged entries, but the bar must still complete.
    logger = _RecordingLogger()
    BuildCatalogCommand(tmp_path, logger=logger, tracer=Tracer()).execute_command()

    assert logger.progress_total == 2
    assert logger.task.advances == 2
    assert logger.task.completed == 2
