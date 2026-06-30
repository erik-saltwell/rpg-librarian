from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class AudioMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")
    acoustic_fingerprint: str
    duration: float | None
