from __future__ import annotations

from pathlib import Path

from ..catalog.model.catalog import Catalog
from ..catalog.model.catalog_entry import CatalogEntry
from ..catalog.model.library_data import LibraryData
from ..dedupe.duplicate_data import DuplicateData
from ..dedupe.find_duplicates import find_duplicates
from .base_command import BaseCommand


class DeleteDuplicatesCommand(BaseCommand):
    """Delete duplicate files found in the catalog, keeping each group's master.

    Duplicates are recomputed from the catalog with the same detection that
    ``report-duplicates`` uses; the report file is not consulted. Only the
    duplicates of each group are removed; the master is kept. A group is skipped
    entirely when its master is missing on disk, so the last surviving copy is
    never deleted. Catalog entries for the removed files are left to the
    ``prune-catalog`` command to clean up.
    """

    ignored_master_extensions: list[str] = [".stl", ".lys"]

    def name(self) -> str:
        return "delete-duplicates"

    def execute_command(self) -> None:
        library = LibraryData(root_folder=self.processing_directory)
        catalog = Catalog.load(library.index_file)
        duplicate_groups = find_duplicates(catalog)
        ignored_extensions = {extension.casefold() for extension in self.ignored_master_extensions}
        duplicate_groups = {
            master_id: group
            for master_id, group in duplicate_groups.items()
            if _master_extension(group) not in ignored_extensions
        }

        deleted = 0
        already_missing = 0
        failed = 0
        skipped_groups = 0
        skipped_duplicates = 0

        duplicate_total = sum(len(group.duplicates) for group in duplicate_groups.values())
        with self.logger.progress("Deleting duplicates", total=duplicate_total) as task:
            for group in duplicate_groups.values():
                master_path = _filepath(group.master)
                if master_path is None or not master_path.exists():
                    self.logger.report_warning(
                        f"Skipping group: master is missing, keeping its duplicates: {master_path}"
                    )
                    skipped_groups += 1
                    skipped_duplicates += len(group.duplicates)
                    task.advance(len(group.duplicates))
                    continue

                for duplicate in group.duplicates:
                    path = _filepath(duplicate)
                    try:
                        if path is None:
                            already_missing += 1
                        elif path.exists():
                            path.unlink()
                            deleted += 1
                        else:
                            already_missing += 1
                    except OSError as error:
                        self.logger.report_warning(f"Could not delete {path}: {error}")
                        failed += 1
                    finally:
                        task.advance()

        self.logger.report_message(f"Deleted {deleted} duplicate files from {len(duplicate_groups)} groups.")
        self.logger.report_multicolumn_table(
            ["Outcome", "Files"],
            [
                ["Deleted", str(deleted)],
                ["Already missing", str(already_missing)],
                ["Failed", str(failed)],
                ["Kept (master missing)", str(skipped_duplicates)],
            ],
        )
        if skipped_groups:
            self.logger.report_warning(
                f"Kept {skipped_duplicates} duplicates across {skipped_groups} groups whose master was missing."
            )


def _filepath(entry: CatalogEntry) -> Path | None:
    return entry.file_data.filepath if entry.file_data is not None else None


def _master_extension(group: DuplicateData) -> str:
    master_path = _filepath(group.master)
    return master_path.suffix.casefold() if master_path is not None else ""
