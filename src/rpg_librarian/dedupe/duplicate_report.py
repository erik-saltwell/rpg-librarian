from __future__ import annotations

from pathlib import Path

from ..catalog.model.library_data import LibraryData

DUPLICATE_REPORT_FILENAME = "duplicates.json"


def duplicate_report_path(library: LibraryData) -> Path:
    """Location of the duplicate report shared by the report/delete commands."""
    return library.catalog_folder / DUPLICATE_REPORT_FILENAME
