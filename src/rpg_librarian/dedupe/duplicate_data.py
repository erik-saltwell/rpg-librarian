from __future__ import annotations

from dataclasses import dataclass

from ..catalog.model.catalog_entry import CatalogEntry


@dataclass
class DuplicateData:
    master: CatalogEntry
    duplicates: list[CatalogEntry]
