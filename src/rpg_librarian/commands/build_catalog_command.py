from __future__ import annotations

from collections import defaultdict
from time import perf_counter

from ..catalog.actions.generate_catalog import count_files, enumerate_entries
from ..catalog.model.catalog import Catalog
from ..catalog.model.catalog_entry import CatalogEntry
from ..catalog.model.library_data import LibraryData
from ..utils.common_paths import ensure_directory
from .base_command import BaseCommand


def _progress_description(error_count: int) -> str:
    color = "green" if error_count == 0 else "red"
    return f"Building Catalog ([{color}]{error_count}[/{color}])"


class BuildCatalogCommand(BaseCommand):
    def name(self) -> str:
        return "build_catalog"

    def _report_timing_stats(self, durations_by_media_type: dict[str, list[float]]) -> None:
        headers = ["Media Type", "Count", "Total Time (s)", "Avg Time (s)"]
        rows: list[list[str]] = []
        ranked_media_types = sorted(
            durations_by_media_type, key=lambda k: sum(durations_by_media_type[k]), reverse=True
        )
        for media_type_label in ranked_media_types:
            durations = durations_by_media_type[media_type_label]
            total = sum(durations)
            average = total / len(durations)
            rows.append([media_type_label, str(len(durations)), f"{total:.3f}", f"{average:.3f}"])

        self.logger.report_multicolumn_table(headers, rows)

    def execute_command(self) -> None:
        library: LibraryData = LibraryData(root_folder=self.processing_directory)
        ensure_directory(library.catalog_folder)

        total_files: int = count_files(library)
        error_count: int = 0
        entries: list[CatalogEntry] = []
        durations_by_media_type: dict[str, list[float]] = defaultdict(list)

        with self.logger.progress(_progress_description(error_count), total=total_files) as task:
            start = perf_counter()
            for entry in enumerate_entries(library):
                elapsed = perf_counter() - start

                media_type_label: str = entry.media_type.value if entry.media_type else "unknown"
                durations_by_media_type[media_type_label].append(elapsed)

                entries.append(entry)
                if entry.errors:
                    error_count += 1
                    task.set_description(_progress_description(error_count))
                task.advance(1)

                start = perf_counter()

        catalog: Catalog = Catalog(library=library, entries=entries)
        catalog.save(library.index_file)

        self._report_timing_stats(durations_by_media_type)
