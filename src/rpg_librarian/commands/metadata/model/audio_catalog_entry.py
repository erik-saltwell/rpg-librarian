from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AudioTechnicalData(BaseModel):
    codec: str | None = None
    container: str | None = None
    duration_seconds: float | None = None
    sample_rate_hz: int | None = None
    channels: int | None = None
    bit_depth: int | None = None
    bitrate_kbps: int | None = None
    is_lossless: bool | None = None


class AudioEmbeddedMetadata(BaseModel):
    title: str | None = None
    artist: str | None = None
    album: str | None = None
    year: str | None = None
    track_number: str | None = None
    genre: str | None = None
    comment: str | None = None
    publisher: str | None = None
    copyright: str | None = None
    bpm: float | None = None
    url_candidates: list[str] = Field(default_factory=list)

    id3: dict = Field(default_factory=dict)
    vorbis: dict = Field(default_factory=dict)
    riff_info: dict = Field(default_factory=dict)


class AudioHashData(BaseModel):
    sha256: str | None = None
    acoustid_fingerprint: str | None = None
    acoustid_duration: float | None = None


class AudioRpgData(BaseModel):
    asset_type: str | None = None
    # ambience, music_track, sfx, stinger, voice_over, loop, unknown

    mood_tags: list[str] = Field(default_factory=list)
    setting_tags: list[str] = Field(default_factory=list)

    is_loop: bool | None = None
    loop_start_ms: int | None = None
    loop_end_ms: int | None = None

    notes: str | None = None


class AudioCatalogEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1.0"
    media_type: Literal["audio"] = "audio"

    id: str
    path: str
    filename: str
    extension: str
    mime_type: str | None = None
    size_bytes: int | None = None
    modified_time_epoch: float | None = None

    audio: AudioTechnicalData = Field(default_factory=AudioTechnicalData)
    hashes: AudioHashData = Field(default_factory=AudioHashData)
    embedded_metadata: AudioEmbeddedMetadata = Field(default_factory=AudioEmbeddedMetadata)
    rpg: AudioRpgData = Field(default_factory=AudioRpgData)

    errors: list[str] = Field(default_factory=list)
