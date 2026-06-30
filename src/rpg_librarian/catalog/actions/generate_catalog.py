from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

from rpg_librarian.catalog.model.catalog import Catalog
from rpg_librarian.catalog.model.library_data import LibraryData
from rpg_librarian.utils.common_paths import ensure_directory

from ..model.catalog_entry import CatalogEntry
from .generate_catalog_entry import generate_catalog_entry


def enumerate_entries(library: LibraryData) -> Generator[CatalogEntry]:
    for dirpath, dirnames, filenames in os.walk(library.root_folder):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        for filename in sorted(filenames):
            yield generate_catalog_entry(Path(dirpath) / filename, library)


def generate_catalog(root_folder: Path) -> Catalog:
    library: LibraryData = LibraryData(root_folder=root_folder)
    ensure_directory(library.catalog_folder)
    entries: list[CatalogEntry] = list(enumerate_entries(library))
    catalog = Catalog(library=library, entries=entries)
    catalog.save(library.index_file)
    return catalog
