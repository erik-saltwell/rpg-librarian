from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

from rpg_librarian.catalog.model.catalog import Catalog
from rpg_librarian.catalog.model.catalog_entry import CatalogEntry
from rpg_librarian.catalog.model.library_data import LibraryData
from rpg_librarian.utils.common_paths import ensure_directory

from .generate_catalog_entry import generate_catalog_entry


def build_reuse_index(library: LibraryData) -> dict[str, CatalogEntry]:
    """Index already-cataloged, error-free entries by file path for incremental reuse.

    Previously-failed entries are deliberately excluded so they get reprocessed: a
    fix (a new extractor, a repaired file) may now let them succeed. Files that have
    since been deleted simply never come up in the walk, so they drop out."""
    if not library.index_file.exists():
        return {}
    catalog = Catalog.load(library.index_file)
    return {
        str(entry.file_data.filepath): entry
        for entry in catalog.entries
        if entry.file_data is not None and not entry.errors
    }


def list_library_files(library: LibraryData) -> list[Path]:
    """The single ordered walk of the library, skipping hidden dirs such as .catalog.

    This is the one source of truth for which files a build processes: taking a
    progress total from len(...) and iterating this same list guarantees the count
    and the work cannot drift apart across two independent filesystem walks."""
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(library.root_folder):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        for filename in sorted(filenames):
            files.append(Path(dirpath) / filename)
    return files


def _can_reuse(entry: CatalogEntry, file_path: Path) -> bool:
    """Whether the on-disk file still matches the existing entry's recorded size."""
    if entry.file_data is None:
        return False
    try:
        return file_path.stat().st_size == entry.file_data.size_in_bytes
    except OSError:
        return False


def resolve_entry(file_path: Path, library: LibraryData, reusable: dict[str, CatalogEntry]) -> CatalogEntry:
    """Reuse an unchanged, error-free existing entry, or (re)generate one otherwise.

    Always returns exactly one entry per file, so callers can rely on one result
    per path even when generation hits an error (it is captured on the entry)."""
    existing = reusable.get(str(file_path))
    if existing is not None and _can_reuse(existing, file_path):
        return existing
    return generate_catalog_entry(file_path, library)


def enumerate_entries(library: LibraryData) -> Generator[CatalogEntry]:
    reusable = build_reuse_index(library)
    for file_path in list_library_files(library):
        yield resolve_entry(file_path, library, reusable)


def generate_catalog(root_folder: Path) -> Catalog:
    library: LibraryData = LibraryData(root_folder=root_folder)
    ensure_directory(library.catalog_folder)
    entries: list[CatalogEntry] = list(enumerate_entries(library))
    catalog = Catalog(library=library, entries=entries)
    catalog.save(library.index_file)
    return catalog
