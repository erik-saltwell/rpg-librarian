from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from ...file_data.model import FileData
from .base_metadata import BaseMetadata
from .media_type import MediaType
from .media_type_metadata import MediaTypeMetadata


class CatalogEntry(BaseModel):
    id: str
    # The source file this entry describes. Always set for entries built going
    # forward, even when file_data extraction fails, so an entry is identifiable
    # by path regardless of extraction success. Optional only so catalogs written
    # before this field existed still load.
    filepath: Path | None = None
    mime_type: str | None = None
    media_type: MediaType | None = None
    file_data: FileData | None = None
    base_metadata: BaseMetadata | None = None
    media_type_metadata: MediaTypeMetadata = None
    errors: list[str] = Field(default_factory=list)
