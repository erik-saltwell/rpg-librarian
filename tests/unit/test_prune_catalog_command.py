from __future__ import annotations

from pathlib import Path

from rpg_librarian.catalog.model.base_metadata import BaseMetadata
from rpg_librarian.catalog.model.catalog import Catalog
from rpg_librarian.catalog.model.catalog_entry import CatalogEntry
from rpg_librarian.catalog.model.library_data import LibraryData
from rpg_librarian.catalog.model.media_type import MediaType
from rpg_librarian.commands.prune_catalog_command import PruneCatalogCommand
from rpg_librarian.file_data.model.file_data import FileData
from rpg_librarian.utils import NullLogger, Tracer


def _file_data(path: Path) -> FileData:
    return FileData(
        sha256="hash",
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
    )


def _entry(entry_id: str, path: Path | None, errors: list[str] | None = None) -> CatalogEntry:
    return CatalogEntry(
        id=entry_id,
        media_type=MediaType.pdf,
        file_data=_file_data(path) if path is not None else None,
        errors=errors or [],
    )


def test_prune_removes_errored_and_missing_entries_and_keeps_valid(tmp_path: Path) -> None:
    library = LibraryData(root_folder=tmp_path)

    present_path = tmp_path / "present.pdf"
    present_path.write_text("pdf", encoding="utf-8")
    errored_but_present_path = tmp_path / "errored.pdf"
    errored_but_present_path.write_text("pdf", encoding="utf-8")
    missing_path = tmp_path / "missing.pdf"  # never created on disk

    catalog = Catalog(
        library=library,
        entries=[
            _entry("keep", present_path),
            _entry("errored", errored_but_present_path, errors=["Could not read metadata"]),
            _entry("missing", missing_path),
            _entry("no-file-data", None),
        ],
    )
    catalog.save(library.index_file)

    command = PruneCatalogCommand(tmp_path, logger=NullLogger(), tracer=Tracer())
    command.execute_command()

    pruned = Catalog.load(library.index_file)
    assert [entry.id for entry in pruned.entries] == ["keep"]


def test_prune_clears_empty_base_metadata_but_keeps_populated(tmp_path: Path) -> None:
    library = LibraryData(root_folder=tmp_path)
    empty_path = tmp_path / "empty.pdf"
    populated_path = tmp_path / "populated.pdf"
    empty_path.write_text("pdf", encoding="utf-8")
    populated_path.write_text("pdf", encoding="utf-8")

    empty_entry = _entry("empty-meta", empty_path)
    empty_entry.base_metadata = BaseMetadata()
    populated_entry = _entry("populated-meta", populated_path)
    populated_entry.base_metadata = BaseMetadata(title="Keep Me")

    catalog = Catalog(library=library, entries=[empty_entry, populated_entry])
    catalog.save(library.index_file)

    command = PruneCatalogCommand(tmp_path, logger=NullLogger(), tracer=Tracer())
    command.execute_command()

    pruned = {entry.id: entry for entry in Catalog.load(library.index_file).entries}
    assert pruned["empty-meta"].base_metadata is None
    assert pruned["populated-meta"].base_metadata is not None
    assert pruned["populated-meta"].base_metadata.title == "Keep Me"


def test_prune_leaves_clean_catalog_untouched(tmp_path: Path) -> None:
    library = LibraryData(root_folder=tmp_path)
    first = tmp_path / "first.pdf"
    second = tmp_path / "second.pdf"
    first.write_text("pdf", encoding="utf-8")
    second.write_text("pdf", encoding="utf-8")

    catalog = Catalog(
        library=library,
        entries=[_entry("first", first), _entry("second", second)],
    )
    catalog.save(library.index_file)

    command = PruneCatalogCommand(tmp_path, logger=NullLogger(), tracer=Tracer())
    command.execute_command()

    pruned = Catalog.load(library.index_file)
    assert [entry.id for entry in pruned.entries] == ["first", "second"]
