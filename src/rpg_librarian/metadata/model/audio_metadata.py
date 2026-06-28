from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class AudioMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")
    acoustic_fingerprint: str
    duration: float | None
    title: str | None
    artist: str | None
    album: str | None
    year: str | None
    track_number: str | None
    genre: str | None
    publisher: str | None
    copyright: str | None
