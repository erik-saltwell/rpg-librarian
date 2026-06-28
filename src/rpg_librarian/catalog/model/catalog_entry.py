from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from ...file_data.model import FileData


class EntryFileType(StrEnum):
    text = "text"
    image = "image"
    video = "video"
    pdf = "pdf"
    mesh = "mesh"
    unknown = "unknown"


class CatalogEntry(BaseModel):
    id: str
    file_data: FileData | None = None
    file_type: EntryFileType = Field(default=EntryFileType.unknown)
    errors: list[str] = Field(default_factory=list)
