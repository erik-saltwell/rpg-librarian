from __future__ import annotations

import os
import stat
import sys

import pytest

from rpg_librarian.catalog.model.catalog import Catalog
from rpg_librarian.catalog.model.library_data import LibraryData
from rpg_librarian.commands.build_catalog_command import BuildCatalogCommand
from rpg_librarian.utils import NullLogger, Tracer


@pytest.mark.skipif(
    sys.platform == "win32" or os.getuid() == 0,
    reason="requires POSIX read-permission semantics and a non-root user",
)
def test_build_catalog_unreadable_file_records_error_and_continues(tmp_path) -> None:
    readable = tmp_path / "readable.txt"
    readable.write_text("hello", encoding="utf-8")
    unreadable = tmp_path / "locked.txt"
    unreadable.write_text("secret", encoding="utf-8")
    unreadable.chmod(stat.S_IWRITE)  # write-only: no read permission

    library_data = LibraryData(root_folder=tmp_path)
    BuildCatalogCommand(tmp_path, logger=NullLogger(), tracer=Tracer()).execute_command()
    entries = Catalog.load(library_data.index_file).entries

    # Restore permissions so tmp_path cleanup works.
    unreadable.chmod(stat.S_IRUSR | stat.S_IWUSR)

    filenames = {e.file_data.filename if e.file_data else None for e in entries}
    assert "readable.txt" in filenames
    error_entries = [e for e in entries if e.errors]
    assert len(error_entries) == 1
    assert error_entries[0].file_data is None


def test_build_catalog_skips_hidden_directories(tmp_path) -> None:
    visible_dir = tmp_path / "visible"
    visible_dir.mkdir()
    hidden_dir = tmp_path / ".hidden"
    hidden_dir.mkdir()
    catalog_dir = tmp_path / ".catalog"
    catalog_dir.mkdir()

    visible_file = visible_dir / "entry.txt"
    visible_file.write_text("hello", encoding="utf-8")
    hidden_file = hidden_dir / "ignored.txt"
    hidden_file.write_text("ignore me", encoding="utf-8")
    catalog_file = catalog_dir / "catalog-entry.txt"
    catalog_file.write_text("ignore me", encoding="utf-8")

    library_data = LibraryData(root_folder=tmp_path)

    BuildCatalogCommand(tmp_path, logger=NullLogger(), tracer=Tracer()).execute_command()
    entries = Catalog.load(library_data.index_file).entries

    assert [e.file_data.filename if e.file_data else None for e in entries] == ["entry.txt"]
