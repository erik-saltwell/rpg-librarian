from __future__ import annotations

import json

from ..catalog.model.catalog import Catalog
from ..catalog.model.library_data import LibraryData
from .base_command import BaseCommand

_ERROR_REPORT_FILENAME = "errors.json"


class ExtractErrorsCommand(BaseCommand):
    def name(self) -> str:
        return "extract_errors"

    def execute_command(self) -> None:
        library = LibraryData(root_folder=self.processing_directory)
        catalog = Catalog.load(library.index_file)

        report = [
            {
                "file_path": str(entry.file_data.filepath) if entry.file_data is not None else None,
                "media_type": entry.media_type.value if entry.media_type is not None else None,
                "errors": entry.errors,
            }
            for entry in catalog.entries
            if entry.errors
        ]

        report_path = library.catalog_folder / _ERROR_REPORT_FILENAME
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        self.logger.report_message(f"Wrote {len(report)} catalog errors to {report_path}")
