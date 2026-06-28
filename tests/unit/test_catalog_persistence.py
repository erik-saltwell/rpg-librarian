from __future__ import annotations

from pathlib import Path

from rpg_librarian.catalog.model.catalog import Catalog
from rpg_librarian.catalog.model.catalog_entry import CatalogEntry
from rpg_librarian.catalog.model.library_data import LibraryData
from rpg_librarian.file_data.model.file_data import FileData


def test_catalog_save_and_load_round_trip(tmp_path: Path) -> None:
    sample_file = tmp_path / "sample.txt"
    sample_file.write_text("hello world", encoding="utf-8")

    catalog = Catalog(
        library=LibraryData(root_folder=tmp_path),
        entries=[
            CatalogEntry(
                id="sample",
                file_data=FileData(
                    sha256="abc123",
                    filepath=sample_file,
                    filename=sample_file.name,
                    extension=sample_file.suffix,
                    size_in_bytes=sample_file.stat().st_size,
                    mime_type="text/plain",
                    root_folder=None,
                    root_child_folder=None,
                    root_grandchild_folder=None,
                    root_greatgrandchild_folder=None,
                    parent_folder=None,
                    grandparent_folder=None,
                ),
            )
        ],
    )

    save_path = tmp_path / "catalog.json"
    catalog.save(save_path)

    loaded_catalog = Catalog.load(save_path)

    assert loaded_catalog.library.root_folder == catalog.library.root_folder
    assert loaded_catalog.entries[0].id == catalog.entries[0].id
    assert loaded_catalog.entries[0].file_data is not None
    assert catalog.entries[0].file_data is not None
    assert loaded_catalog.entries[0].file_data.filepath == catalog.entries[0].file_data.filepath
