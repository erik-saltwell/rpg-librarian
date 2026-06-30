from __future__ import annotations

from .audio_metadata import AudioMetadata
from .image_metadata import ImageMetadata
from .mesh_metadata import MeshMetadata
from .video_metadata import VideoMetadata

MediaTypeMetadata = ImageMetadata | AudioMetadata | MeshMetadata | VideoMetadata | None
