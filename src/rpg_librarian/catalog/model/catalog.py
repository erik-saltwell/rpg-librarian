from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel

from rpg_librarian.catalog.model.catalog_entry import CatalogEntry

from ...catalog.model.library_data import LibraryData


class Catalog(BaseModel):
    library: LibraryData
    entries: list[CatalogEntry]

    def save(self, path: str | Path) -> None:
        target_path = Path(path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(json.dumps(self.model_dump(mode="json"), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> Catalog:
        target_path = Path(path)
        payload = json.loads(target_path.read_text(encoding="utf-8"))
        return cls.model_validate(payload)
