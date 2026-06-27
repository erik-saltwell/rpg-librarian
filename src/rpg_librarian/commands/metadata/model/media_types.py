from __future__ import annotations

from enum import StrEnum


class MediaType(StrEnum):
    MAP = "map"
    ANIMATED_MAP = "animated_map"
    AUDIO = "audio"
    DOCUMENT = "document"
    MODEL_3D = "3d_model"
    HANDOUT = "handout"
    OTHER = "other"
