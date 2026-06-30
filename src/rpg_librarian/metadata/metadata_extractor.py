from __future__ import annotations

from abc import ABC, abstractmethod

from ..catalog.model.media_type_metadata import MediaTypeMetadata


class MetadataExtractor(ABC):
    @abstractmethod
    def extract_value(self, candidate: str) -> str | None: ...
    @abstractmethod
    def generate_media_type_specific_metadata(self) -> MediaTypeMetadata: ...
    def extract(self, candidates: list[str]) -> str | None:
        for candidate in candidates:
            temp_value = self.extract_value(candidate=candidate)
            if temp_value:
                return temp_value
        return None
