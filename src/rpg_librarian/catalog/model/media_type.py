from __future__ import annotations

from enum import StrEnum


class MediaType(StrEnum):
    audio = "audio"
    video = "video"
    image = "image"
    vector = "vector"
    pdf = "pdf"
    mesh = "mesh"
    text = "text"
    unknown = "unknown"
