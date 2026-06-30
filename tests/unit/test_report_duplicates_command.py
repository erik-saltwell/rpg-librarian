from __future__ import annotations

import json
from pathlib import Path

from rpg_librarian.catalog.model.catalog import Catalog
from rpg_librarian.catalog.model.catalog_entry import CatalogEntry
from rpg_librarian.catalog.model.library_data import LibraryData
from rpg_librarian.catalog.model.media_type import MediaType
from rpg_librarian.commands.report_duplicates_command import ReportDuplicatesCommand
from rpg_librarian.file_data.model.file_data import FileData
from rpg_librarian.utils import NullLogger, Tracer


class _CapturingLogger(NullLogger):
    """NullLogger that records the multicolumn tables it is asked to render."""

    def __init__(self) -> None:
        self.tables: list[tuple[list[str], list[list[str]]]] = []

    def report_multicolumn_table(self, headers: list[str], rows: list[list[str]]) -> None:
        self.tables.append((headers, rows))


def _entry(entry_id: str, path: Path, sha256: str) -> CatalogEntry:
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


def test_execute_command_writes_duplicate_report(tmp_path: Path) -> None:
    library = LibraryData(root_folder=tmp_path)
    catalog = Catalog(
        library=library,
        entries=[
            _entry("master", tmp_path / "book.pdf", "same"),
            _entry("copy", tmp_path / "copy.pdf", "same"),
            _entry("unique", tmp_path / "unique.pdf", "different"),
        ],
    )
    catalog.save(library.index_file)

    command = ReportDuplicatesCommand(tmp_path, logger=NullLogger(), tracer=Tracer())
    command.execute_command()

    report = json.loads((library.catalog_folder / "duplicates.json").read_text(encoding="utf-8"))
    assert list(report) == ["master"]
    assert report["master"]["master"] == str(tmp_path / "book.pdf")
    assert report["master"]["duplicates"] == [str(tmp_path / "copy.pdf")]
    # book.pdf vs copy.pdf differ, and neither lives under DriveThruRPG.
    assert report["master"]["all_same_filename"] is False
    assert report["master"]["master_in_drivethrurpg"] is False


def test_report_flags_same_filename_and_drivethrurpg_master(tmp_path: Path) -> None:
    library = LibraryData(root_folder=tmp_path)
    master_path = tmp_path / "DriveThruRPG" / "publisher" / "book.pdf"
    copy_path = tmp_path / "backups" / "book.pdf"
    catalog = Catalog(
        library=library,
        entries=[
            _entry("loose", copy_path, "same"),
            _entry("canonical", master_path, "same"),
        ],
    )
    catalog.save(library.index_file)

    command = ReportDuplicatesCommand(tmp_path, logger=NullLogger(), tracer=Tracer())
    command.execute_command()

    report = json.loads((library.catalog_folder / "duplicates.json").read_text(encoding="utf-8"))
    # The DriveThruRPG copy is chosen as master; both files are named book.pdf.
    assert list(report) == ["canonical"]
    assert report["canonical"]["master"] == str(master_path)
    assert report["canonical"]["all_same_filename"] is True
    assert report["canonical"]["master_in_drivethrurpg"] is True


def test_reports_breakdown_tables(tmp_path: Path) -> None:
    library = LibraryData(root_folder=tmp_path)
    catalog = Catalog(
        library=library,
        entries=[
            # Group A: master in DriveThruRPG, same filename, 1 duplicate.
            _entry("a-master", tmp_path / "DriveThruRPG" / "pub" / "book.pdf", "a"),
            _entry("a-copy", tmp_path / "backups" / "book.pdf", "a"),
            # Group B: not in DriveThruRPG, different filenames, 2 duplicates.
            _entry("b-master", tmp_path / "x" / "guide.epub", "b"),
            _entry("b-copy1", tmp_path / "y" / "guide_copy.epub", "b"),
            _entry("b-copy2", tmp_path / "z" / "guide_backup.epub", "b"),
        ],
    )
    catalog.save(library.index_file)

    logger = _CapturingLogger()
    command = ReportDuplicatesCommand(tmp_path, logger=logger, tracer=Tracer())
    command.execute_command()

    same_filename, in_drivethru, by_extension, by_count = logger.tables
    assert same_filename[0] == ["All Same Filename", "Groups", "%"]
    assert same_filename[1] == [["True", "1", "50.0%"], ["False", "1", "50.0%"]]
    assert in_drivethru[0] == ["Master in DriveThruRPG", "Groups", "%"]
    assert in_drivethru[1] == [["True", "1", "50.0%"], ["False", "1", "50.0%"]]
    assert by_extension[0] == ["Master Extension", "Duplicate Entries", "%"]
    assert by_extension[1] == [[".epub", "2", "66.7%"], [".pdf", "1", "33.3%"]]
    assert by_count[0] == ["Duplicates in Entry", "Groups", "%", "First Master"]
    assert by_count[1] == [
        ["1", "1", "50.0%", str(tmp_path / "DriveThruRPG" / "pub" / "book.pdf")],
        ["2", "1", "50.0%", str(tmp_path / "x" / "guide.epub")],
    ]


def test_no_statistics_tables_when_no_duplicates(tmp_path: Path) -> None:
    library = LibraryData(root_folder=tmp_path)
    catalog = Catalog(
        library=library,
        entries=[_entry("only", tmp_path / "solo.pdf", "unique")],
    )
    catalog.save(library.index_file)

    logger = _CapturingLogger()
    command = ReportDuplicatesCommand(tmp_path, logger=logger, tracer=Tracer())
    command.execute_command()

    assert logger.tables == []


def test_same_filename_is_case_insensitive(tmp_path: Path) -> None:
    library = LibraryData(root_folder=tmp_path)
    catalog = Catalog(
        library=library,
        entries=[
            _entry("master", tmp_path / "a" / "Book.PDF", "same"),
            _entry("copy", tmp_path / "b" / "book.pdf", "same"),
        ],
    )
    catalog.save(library.index_file)

    command = ReportDuplicatesCommand(tmp_path, logger=NullLogger(), tracer=Tracer())
    command.execute_command()

    report = json.loads((library.catalog_folder / "duplicates.json").read_text(encoding="utf-8"))
    assert report["master"]["all_same_filename"] is True


def test_ignores_groups_whose_master_has_ignored_extension(tmp_path: Path) -> None:
    library = LibraryData(root_folder=tmp_path)
    catalog = Catalog(
        library=library,
        entries=[
            _entry("master", tmp_path / "models" / "mini.STL", "same"),
            _entry("copy", tmp_path / "backups" / "mini.STL", "same"),
        ],
    )
    catalog.save(library.index_file)

    command = ReportDuplicatesCommand(tmp_path, logger=NullLogger(), tracer=Tracer())
    command.execute_command()

    report = json.loads((library.catalog_folder / "duplicates.json").read_text(encoding="utf-8"))
    assert report == {}
