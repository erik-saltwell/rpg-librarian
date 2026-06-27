from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Model3dMeshData(BaseModel):
    file_format: str | None = None
    triangle_count: int | None = None
    vertex_count: int | None = None
    bounding_box_x_mm: float | None = None
    bounding_box_y_mm: float | None = None
    bounding_box_z_mm: float | None = None
    surface_area_cm2: float | None = None
    unit: str | None = None
    has_color: bool | None = None
    has_textures: bool | None = None


class Model3dEmbeddedMetadata(BaseModel):
    title: str | None = None
    designer: str | None = None
    description: str | None = None
    license: str | None = None
    source_url: str | None = None
    tags: list[str] = Field(default_factory=list)
    creation_date: str | None = None
    raw: dict = Field(default_factory=dict)


class Model3dRpgData(BaseModel):
    asset_type: str | None = None
    # miniature, base, terrain_tile, dungeon_tile, building,
    # prop, scatter, vehicle, unknown

    scale: str | None = None
    base_type: Literal["round", "square", "hex", "none", "unknown"] | None = None
    base_diameter_mm: float | None = None

    supports_needed: bool | None = None
    estimated_print_time_minutes: int | None = None

    source_marketplace: str | None = None
    # thingiverse, printables, myminifactory, patreon, drivethru, kickstarter, etc.
    product_url_candidates: list[str] = Field(default_factory=list)

    notes: str | None = None


class Model3dCatalogEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1.0"
    media_type: Literal["3d_model"] = "3d_model"

    id: str
    path: str
    filename: str
    extension: str
    mime_type: str | None = None
    size_bytes: int | None = None
    modified_time_epoch: float | None = None

    mesh: Model3dMeshData = Field(default_factory=Model3dMeshData)
    embedded_metadata: Model3dEmbeddedMetadata = Field(default_factory=Model3dEmbeddedMetadata)
    rpg: Model3dRpgData = Field(default_factory=Model3dRpgData)

    errors: list[str] = Field(default_factory=list)
