from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import TypedDict

from ..catalog.model.catalog import Catalog
from ..catalog.model.catalog_entry import CatalogEntry
from ..catalog.model.library_data import LibraryData
from ..dedupe.duplicate_data import DuplicateData
from ..dedupe.duplicate_report import duplicate_report_path
from ..dedupe.find_duplicates import all_share_filename, find_duplicates, is_in_drivethrurpg
from .base_command import BaseCommand


class _ReportEntry(TypedDict):
    master: str
    duplicates: list[str]
    all_same_filename: bool
    master_in_drivethrurpg: bool


def _filepath(entry: CatalogEntry) -> str:
    if entry.file_data is None:
        raise ValueError(f"Duplicate catalog entry {entry.id!r} has no filepath")
    return str(entry.file_data.filepath)


def _report_entry(group: DuplicateData) -> _ReportEntry:
    return {
        "master": _filepath(group.master),
        "duplicates": [_filepath(entry) for entry in group.duplicates],
        "all_same_filename": all_share_filename(group),
        "master_in_drivethrurpg": is_in_drivethrurpg(group.master),
    }


class ReportDuplicatesCommand(BaseCommand):
    ignored_master_extensions: list[str] = [".not-an-extension", ".stl", ".lys"]

    def name(self) -> str:
        return "report-duplicates"

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

        report: dict[str, _ReportEntry] = {
            master_id: _report_entry(duplicate_data) for master_id, duplicate_data in duplicate_groups.items()
        }

        report_path = duplicate_report_path(library)
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

        duplicate_count = sum(len(group.duplicates) for group in duplicate_groups.values())
        self.logger.report_message(
            f"Wrote {duplicate_count} duplicate entries in {len(duplicate_groups)} groups to {report_path}"
        )

        self._report_statistics(report)

    def _report_statistics(self, report: dict[str, _ReportEntry]) -> None:
        total = len(report)
        if total == 0:
            return

        def pct(count: int) -> str:
            return f"{count / total * 100:.1f}%"

        self.logger.add_break()
        same_filename = Counter(entry["all_same_filename"] for entry in report.values())
        self.logger.report_multicolumn_table(
            ["All Same Filename", "Groups", "%"],
            [[str(flag), str(same_filename[flag]), pct(same_filename[flag])] for flag in (True, False)],
        )

        in_drivethru = Counter(entry["master_in_drivethrurpg"] for entry in report.values())
        self.logger.report_multicolumn_table(
            ["Master in DriveThruRPG", "Groups", "%"],
            [[str(flag), str(in_drivethru[flag]), pct(in_drivethru[flag])] for flag in (True, False)],
        )

        duplicates_by_master_extension: Counter[str] = Counter()
        for entry in report.values():
            extension = Path(entry["master"]).suffix.casefold() or "(none)"
            duplicates_by_master_extension[extension] += len(entry["duplicates"])

        total_duplicates = sum(duplicates_by_master_extension.values())
        self.logger.report_multicolumn_table(
            ["Master Extension", "Duplicate Entries", "%"],
            [
                [extension, str(count), f"{count / total_duplicates * 100:.1f}%"]
                for extension, count in sorted(duplicates_by_master_extension.items())
            ],
        )

        by_count = Counter(len(entry["duplicates"]) for entry in report.values())
        first_master_by_count: dict[int, str] = {}
        for entry in report.values():
            first_master_by_count.setdefault(len(entry["duplicates"]), entry["master"])

        self.logger.report_multicolumn_table(
            ["Duplicates in Entry", "Groups", "%", "First Master"],
            [[str(n), str(by_count[n]), pct(by_count[n]), first_master_by_count[n]] for n in sorted(by_count)],
        )


def _master_extension(group: DuplicateData) -> str:
    if group.master.file_data is None:
        return ""
    return group.master.file_data.filepath.suffix.casefold()
