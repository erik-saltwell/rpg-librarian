from __future__ import annotations

from .audio_metadata import AudioMetadata
from .image_metadata import ImageMetadata
from .mesh_metadata import MeshMetadata
from .pdf_metadata import PdfMetadata
from .svg_metadata import SvgMetadata
from .video_metadata import VideoMetadata

MediaTypeMetadata = PdfMetadata | ImageMetadata | SvgMetadata | AudioMetadata | MeshMetadata | VideoMetadata | None
