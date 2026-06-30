from __future__ import annotations

from pathlib import Path

from ..catalog.model.media_type import MediaType
from .audio_extractor import AudioMetadataExtractor
from .image_extractor import ImageMetadataExtractor
from .mesh_extractor import MeshMetadataExtractor
from .metadata_extractor import MetadataExtractor
from .no_metadata_extractor import NoMetadataExtractor
from .pdf_extractor import PdfMetadataExtractor
from .svg_extractor import SvgMetadataExtractor
from .video_extractor import VideoMetadataExtractor


def generate_extractor(media_type: MediaType, file_path: Path) -> MetadataExtractor:
    match media_type:
        case MediaType.audio:
            return AudioMetadataExtractor(file_path)
        case MediaType.image:
            return ImageMetadataExtractor(file_path)
        case MediaType.vector:
            return SvgMetadataExtractor(file_path)
        case MediaType.mesh:
            return MeshMetadataExtractor(file_path)
        case MediaType.video:
            return VideoMetadataExtractor(file_path)
        case MediaType.pdf:
            return PdfMetadataExtractor(file_path)
        case _:
            return NoMetadataExtractor()
