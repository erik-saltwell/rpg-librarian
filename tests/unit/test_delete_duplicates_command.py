from __future__ import annotations

from pathlib import Path

from rpg_librarian.catalog.model.catalog import Catalog
from rpg_librarian.catalog.model.catalog_entry import CatalogEntry
from rpg_librarian.catalog.model.library_data import LibraryData
from rpg_librarian.catalog.model.media_type import MediaType
from rpg_librarian.commands.delete_duplicates_command import DeleteDuplicatesCommand
from rpg_librarian.file_data.model.file_data import FileData
from rpg_librarian.utils import NullLogger, Tracer


def _entry(entry_id: str, path: Path, sha256: str, *, create: bool = True) -> CatalogEntry:
    if create:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"x")
    return CatalogEntry(
        id=entry_id,
        media_type=MediaType.pdf,
        file_data=FileData(
            sha256=sha256,
            filepath=path,
            filename=path.name,
            extension=path.suffix,
            size_in_bytes=1,
            mime_type="application/pdf",
            root_folder=None,
            root_child_folder=None,
            root_grandchild_folder=None,
            root_greatgrandchild_folder=None,
            parent_folder=None,
            grandparent_folder=None,
        ),
    )


def _run(root: Path, entries: list[CatalogEntry]) -> None:
    library = LibraryData(root_folder=root)
    Catalog(library=library, entries=entries).save(library.index_file)
    DeleteDuplicatesCommand(root, logger=NullLogger(), tracer=Tracer()).execute_command()


def test_deletes_duplicates_and_keeps_master(tmp_path: Path) -> None:
    # All files share one name so the shared-name-only deletion applies.
    master = tmp_path / "DriveThruRPG" / "book.pdf"
    dup1 = tmp_path / "backups" / "book.pdf"
    dup2 = tmp_path / "more" / "book.pdf"
    _run(
        tmp_path,
        [
            _entry("master", master, "same"),
            _entry("dup1", dup1, "same"),
            _entry("dup2", dup2, "same"),
        ],
    )

    assert master.exists()
    assert not dup1.exists()
    assert not dup2.exists()


def test_skips_group_when_master_missing(tmp_path: Path) -> None:
    master = tmp_path / "DriveThruRPG" / "gone.pdf"  # in catalog but not on disk
    dup = tmp_path / "backups" / "gone.pdf"
    _run(
        tmp_path,
        [
            _entry("master", master, "same", create=False),
            _entry("dup", dup, "same"),
        ],
    )

    # The only surviving copy must not be deleted when the master is missing.
    assert dup.exists()


def test_tolerates_already_missing_duplicate(tmp_path: Path) -> None:
    # The deeper file is the master (no DriveThruRPG member); the shallower
    # duplicate is in the catalog but already gone from disk.
    master = tmp_path / "deep" / "nested" / "book.pdf"
    dup = tmp_path / "book.pdf"  # in catalog but not on disk
    _run(
        tmp_path,
        [
            _entry("master", master, "same"),
            _entry("dup", dup, "same", create=False),
        ],
    )

    assert master.exists()  # must not raise


def test_no_duplicates_deletes_nothing(tmp_path: Path) -> None:
    solo = tmp_path / "solo.pdf"
    _run(tmp_path, [_entry("solo", solo, "unique")])

    assert solo.exists()


def test_keeps_group_whose_master_has_ignored_extension(tmp_path: Path) -> None:
    master = tmp_path / "DriveThruRPG" / "mini.STL"
    duplicate = tmp_path / "backups" / "mini.STL"
    _run(
        tmp_path,
        [
            _entry("master", master, "same"),
            _entry("duplicate", duplicate, "same"),
        ],
    )

    assert master.exists()
    assert duplicate.exists()
