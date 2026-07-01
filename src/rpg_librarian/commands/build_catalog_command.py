from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

from ..catalog.actions.generate_catalog_entry import generate_catalog_entry
from ..catalog.model.catalog import Catalog
from ..catalog.model.catalog_entry import CatalogEntry
from ..catalog.model.library_data import LibraryData
from ..utils.common_paths import ensure_directory
from .base_command import BaseCommand


def _progress_description(error_count: int) -> str:
    color = "green" if error_count == 0 else "red"
    return f"Building Catalog ([{color}]{error_count}[/{color}])"


def _entry_path(entry: CatalogEntry) -> Path | None:
    """The source path of an entry, preferring the always-set filepath and falling
    back to file_data for entries written before filepath existed."""
    if entry.filepath is not None:
        return entry.filepath
    return entry.file_data.filepath if entry.file_data else None


def unseen_files(catalog: Catalog) -> Generator[Path]:
    total_files: int = 0
    seen_paths: set[Path] = {path for entry in catalog.entries if (path := _entry_path(entry)) is not None}
    for dirpath, dirnames, filenames in os.walk(catalog.library.root_folder):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        for filename in sorted(filenames):
            total_files += 1
            file_path = Path(dirpath) / filename
            if file_path not in seen_paths:
                yield file_path
    return


class BuildCatalogCommand(BaseCommand):
    def name(self) -> str:
        return "build_catalog"

    def execute_command(self) -> None:
        library: LibraryData = LibraryData(root_folder=self.processing_directory)
        ensure_directory(library.catalog_folder)
        catalog: Catalog = Catalog(library=library, entries=[])
        if library.index_file.exists():
            catalog: Catalog = Catalog.load(library.index_file)

        to_process: list[Path] = list(unseen_files(catalog))
        error_count: int = 0
        counter: int = 1
        total_files: int = len(to_process)
        catalog.save(library.index_file, backup=True)  # this first save actually backs up the previous catalog.
        with self.logger.progress(_progress_description(error_count), total=total_files) as task:
            for file_path in to_process:
                entry: CatalogEntry = generate_catalog_entry(file_path, catalog.library)
                catalog.entries.append(entry)
                if entry.errors:
                    error_count += 1
                    task.set_description(_progress_description(error_count))
                if counter % 10 == 0:
                    catalog.save(library.index_file, backup=False)
                counter += 1
                task.advance(1)
            task.set_completed(total_files)
        catalog.save(library.index_file, backup=True)
