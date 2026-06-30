from __future__ import annotations

from pydantic import BaseModel


class VideoMetadata(BaseModel):
    duration_seconds: float | None = None
    width: int | None = None
    height: int | None = None
    has_audio: bool | None = None
    title: str | None = None
    artist: str | None = None
    comment: str | None = None
