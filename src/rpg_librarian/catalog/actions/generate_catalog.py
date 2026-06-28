from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

from rpg_librarian.catalog.model.catalog import Catalog
from rpg_librarian.catalog.model.library_data import LibraryData
from rpg_librarian.utils.common_paths import ensure_directory

from ...file_data.actions.generate_file_data import generate_file_data
from ..model.catalog_entry import CatalogEntry
from ..tools.id_generator import generate_unique_id


def _generate_catalog_entry(file_path: Path, library: LibraryData) -> CatalogEntry:
    entry_id = generate_unique_id()
    try:
        return CatalogEntry(id=entry_id, file_data=generate_file_data(file_path, library))
    except (OSError, ValueError) as exc:
        return CatalogEntry(id=entry_id, errors=[f"{type(exc).__name__}: {exc}"])


def enumerate_entries(library: LibraryData) -> Generator[CatalogEntry]:
    for dirpath, dirnames, filenames in os.walk(library.root_folder):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        for filename in sorted(filenames):
            yield _generate_catalog_entry(Path(dirpath) / filename, library)


def generate_catalog(root_folder: Path) -> Catalog:
    library: LibraryData = LibraryData(root_folder=root_folder)
    ensure_directory(library.catalog_folder)
    entries: list[CatalogEntry] = list(enumerate_entries(library))
    catalog = Catalog(library=library, entries=entries)
    catalog.save(library.index_file)
    return catalog
