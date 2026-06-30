from __future__ import annotations

from pydantic import BaseModel


class BaseMetadata(BaseModel):
    artist: str | None = None
    title: str | None = None
    publisher: str | None = None
    copyright: str | None = None
    genre: str | None = None
