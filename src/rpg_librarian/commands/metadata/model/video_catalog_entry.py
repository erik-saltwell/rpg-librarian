from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class VideoTechnicalData(BaseModel):
    container: str | None = None
    video_codec: str | None = None
    audio_codec: str | None = None
    duration_seconds: float | None = None
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    bitrate_kbps: int | None = None
    has_audio: bool | None = None


class VideoEmbeddedMetadata(BaseModel):
    title: str | None = None
    artist: str | None = None
    comment: str | None = None
    copyright: str | None = None
    creation_date: str | None = None
    url_candidates: list[str] = Field(default_factory=list)
    raw: dict = Field(default_factory=dict)


class VideoRpgData(BaseModel):
    asset_type: str | None = None
    # animated_map, ambience_loop, intro_video, tutorial, cutscene, unknown

    grid_detected: bool | None = None
    grid_type: Literal["square", "hex", "none", "unknown"] | None = None
    estimated_cell_px: int | None = None

    vtt_ready: bool | None = None
    is_seamless_loop: bool | None = None

    mood_tags: list[str] = Field(default_factory=list)
    setting_tags: list[str] = Field(default_factory=list)

    notes: str | None = None


class VideoCatalogEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1.0"
    media_type: Literal["video"] = "video"

    id: str
    path: str
    filename: str
    extension: str
    mime_type: str | None = None
    size_bytes: int | None = None
    modified_time_epoch: float | None = None

    video: VideoTechnicalData = Field(default_factory=VideoTechnicalData)
    embedded_metadata: VideoEmbeddedMetadata = Field(default_factory=VideoEmbeddedMetadata)
    rpg: VideoRpgData = Field(default_factory=VideoRpgData)

    errors: list[str] = Field(default_factory=list)
