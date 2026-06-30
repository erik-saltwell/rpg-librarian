from __future__ import annotations

import json
from pathlib import Path

from rpg_librarian.catalog.model.catalog import Catalog
from rpg_librarian.catalog.model.catalog_entry import CatalogEntry
from rpg_librarian.catalog.model.library_data import LibraryData
from rpg_librarian.catalog.model.media_type import MediaType
from rpg_librarian.commands.extract_errors_command import ExtractErrorsCommand
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


def test_execute_command_writes_only_entries_with_errors(tmp_path: Path) -> None:
    library = LibraryData(root_folder=tmp_path)
    failed_path = tmp_path / "failed.pdf"
    catalog = Catalog(
        library=library,
        entries=[
            CatalogEntry(
                id="failed",
                media_type=MediaType.pdf,
                file_data=_file_data(failed_path),
                errors=["Could not read metadata"],
            ),
            CatalogEntry(
                id="successful",
                media_type=MediaType.pdf,
                file_data=_file_data(tmp_path / "successful.pdf"),
            ),
            CatalogEntry(id="missing-data", errors=["Could not read file"]),
        ],
    )
    catalog.save(library.index_file)

    command = ExtractErrorsCommand(tmp_path, logger=NullLogger(), tracer=Tracer())
    command.execute_command()

    report = json.loads((library.catalog_folder / "errors.json").read_text(encoding="utf-8"))
    assert report == [
        {
            "file_path": str(failed_path),
            "media_type": "pdf",
            "errors": ["Could not read metadata"],
        },
        {
            "file_path": None,
            "media_type": None,
            "errors": ["Could not read file"],
        },
    ]
