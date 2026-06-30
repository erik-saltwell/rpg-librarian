from __future__ import annotations

from pydantic import BaseModel


class MeshMetadata(BaseModel):
    bounding_box_x_mm: float | None = None
    bounding_box_y_mm: float | None = None
    bounding_box_z_mm: float | None = None
    surface_area_cm2: float | None = None
    unit: str | None = None
