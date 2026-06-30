from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel


class _KnownNames(StrEnum):
    catalog_dir = ".catalog"
    index_file = "index.json"
    text_fragments_dir = "text_fragments"


class LibraryData(BaseModel):
    root_folder: Path

    @property
    def catalog_folder(self) -> Path:
        return self.root_folder / _KnownNames.catalog_dir

    @property
    def index_file(self) -> Path:
        return self.catalog_folder / _KnownNames.index_file

    @property
    def text_fragments_folder(self) -> Path:
        return self.catalog_folder / _KnownNames.text_fragments_dir
