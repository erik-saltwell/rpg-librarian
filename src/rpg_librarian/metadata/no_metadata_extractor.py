from __future__ import annotations

from ..catalog.model.media_type_metadata import MediaTypeMetadata
from .metadata_extractor import MetadataExtractor


class NoMetadataExtractor(MetadataExtractor):
    def extract_value(self, candidate: str) -> str | None:
        return None

    def generate_media_type_specific_metadata(self) -> MediaTypeMetadata:
        return None
