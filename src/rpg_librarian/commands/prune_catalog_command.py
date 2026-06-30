from __future__ import annotations

from ..catalog.model.catalog import Catalog
from ..catalog.model.catalog_entry import CatalogEntry
from ..catalog.model.library_data import LibraryData
from .base_command import BaseCommand


def _file_exists(entry: CatalogEntry) -> bool:
    """Whether the entry still points to a file present on disk.

    An entry with no file_data points to nothing, so it counts as missing.
    """
    return entry.file_data is not None and entry.file_data.filepath.exists()


def _clear_empty_base_metadata(entry: CatalogEntry) -> bool:
    """Drop a base-metadata block that holds no values. Returns whether it cleared one."""
    if entry.base_metadata is not None and entry.base_metadata.is_empty():
        entry.base_metadata = None
        return True
    return False


class PruneCatalogCommand(BaseCommand):
    def name(self) -> str:
        return "prune_catalog"

    def execute_command(self) -> None:
        library = LibraryData(root_folder=self.processing_directory)
        catalog = Catalog.load(library.index_file)

        kept: list[CatalogEntry] = []
        removed_errors = 0
        removed_missing = 0
        for entry in catalog.entries:
            if entry.errors:
                removed_errors += 1
            elif not _file_exists(entry):
                removed_missing += 1
            else:
                kept.append(entry)

        cleared_base_metadata = sum(_clear_empty_base_metadata(entry) for entry in kept)

        pruned = Catalog(library=catalog.library, entries=kept)
        pruned.save(library.index_file)

        self.logger.report_message(
            f"Pruned {removed_errors + removed_missing} catalog entries "
            f"({removed_errors} with errors, {removed_missing} missing on disk); "
            f"cleared {cleared_base_metadata} empty base-metadata blocks; {len(kept)} remain."
        )
