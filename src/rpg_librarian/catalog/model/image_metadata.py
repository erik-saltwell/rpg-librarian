from __future__ import annotations

from pydantic import BaseModel


class ImageMetadata(BaseModel):
    width: int | None = None
    height: int | None = None
    pixel_count: int | None = None
    artists: str | None = None
    copyright: str | None = None
    has_alpha: bool | None = None
