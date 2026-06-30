from __future__ import annotations

from pydantic import BaseModel


class SvgMetadata(BaseModel):
    width: float | None = None
    height: float | None = None
    units: str | None = None
    view_box: str | None = None
