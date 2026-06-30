from __future__ import annotations

from pydantic import BaseModel, Field

from ...file_data.model import FileData
from .base_metadata import BaseMetadata
from .media_type import MediaType
from .media_type_metadata import MediaTypeMetadata


class CatalogEntry(BaseModel):
    id: str
    mime_type: str | None = None
    media_type: MediaType | None = None
    file_data: FileData | None = None
    base_metadata: BaseMetadata | None = None
    media_type_metadata: MediaTypeMetadata = None
    errors: list[str] = Field(default_factory=list)
