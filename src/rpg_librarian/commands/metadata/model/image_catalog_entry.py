from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

ImageOrientation = Literal["square", "landscape", "portrait", "unknown"]


class ImageTechnicalData(BaseModel):
    format: str | None = None
    width: int | None = None
    height: int | None = None
    aspect_ratio: float | None = None
    orientation: ImageOrientation = "unknown"

    mode: str | None = None
    has_alpha: bool | None = None

    is_animated: bool = False
    frame_count: int = 1

    pixel_count: int | None = None
    megapixels: float | None = None


class ImageHashData(BaseModel):
    sha256: str | None = None

    average_hash: str | None = None
    phash: str | None = None
    dhash: str | None = None


class ImageEmbeddedMetadata(BaseModel):
    exif: dict[str, Any] = Field(default_factory=dict)
    xmp: dict[str, Any] = Field(default_factory=dict)
    iptc: dict[str, Any] = Field(default_factory=dict)

    # Useful when using Pillow, even before full ExifTool support.
    pillow_info: dict[str, Any] = Field(default_factory=dict)

    # Useful when using ExifTool later.
    exiftool: dict[str, Any] = Field(default_factory=dict)


class ImageRpgData(BaseModel):
    asset_type: str | None = None
    # Example values:
    # battlemap, regional_map, world_map, city_map, dungeon_map,
    # token, portrait, handout, prop, ui_asset, unknown

    setting_tags: list[str] = Field(default_factory=list)
    genre_tags: list[str] = Field(default_factory=list)
    mood_tags: list[str] = Field(default_factory=list)
    lighting_tags: list[str] = Field(default_factory=list)

    grid_detected: bool | None = None
    grid_type: Literal["square", "hex", "none", "unknown"] | None = None
    estimated_cell_px: int | None = None

    vtt_ready: bool | None = None
    contains_text: bool | None = None
    transparent_background: bool | None = None

    notes: str | None = None


class ImageCatalogEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1.0"
    media_type: Literal["image"] = "image"

    # Generic file data
    id: str
    path: Path
    filename: str
    extension: str
    mime_type: str | None = None
    size_bytes: int | None = None
    modified_time_epoch: float | None = None

    # Folder/path organization data
    root_folder: Path | None = None
    child_folder: Path | None = None
    grandchild_folder: Path | None = None
    great_grandchild_folder: Path | None = None

    parent_folder: Path | None = None
    grandparent_folder: Path | None = None
    great_grandparent_folder: Path | None = None

    # Image-specific data
    image: ImageTechnicalData = Field(default_factory=ImageTechnicalData)
    hashes: ImageHashData = Field(default_factory=ImageHashData)
    embedded_metadata: ImageEmbeddedMetadata = Field(default_factory=ImageEmbeddedMetadata)

    # Catalog-derived data
    thumbnail_path: Path | None = None
    errors: list[str] = Field(default_factory=list)

    # RPG/media-library enrichment data
    rpg: ImageRpgData = Field(default_factory=ImageRpgData)
