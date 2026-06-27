from __future__ import annotations

from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field

from .audio_catalog_entry import AudioCatalogEntry
from .image_catalog_entry import ImageCatalogEntry
from .model3d_catalog_entry import Model3dCatalogEntry
from .pdf_catalog_entry import PdfCatalogEntry
from .video_catalog_entry import VideoCatalogEntry

EntryDetails = Annotated[
    PdfCatalogEntry | ImageCatalogEntry | AudioCatalogEntry | VideoCatalogEntry | Model3dCatalogEntry,
    Field(discriminator="media_type"),
]


class CatalogEntry(BaseModel):
    id: str
    sha256: str
    filepath: Path
    filename: str
    extension: str
    size_in_bytes: int
    mime_type: str
    root_folder: str | None
    root_child_folder: str | None
    root_grandchild_folder: str | None
    root_greatgrandchild_folder: str | None
    parent_folder: str | None
    grandparent_folder: str | None

    details: EntryDetails | None = None
