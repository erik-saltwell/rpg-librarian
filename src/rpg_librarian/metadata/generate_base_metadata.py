from __future__ import annotations

from ..catalog.model.base_metadata import BaseMetadata
from .metadata_extractor import MetadataExtractor

_candidate_names: dict[str, list[str]] = {
    "artist": ["artist", "artists", "creator", "author", "authors", "performer", "performers"],
    "title": ["title", "album", "track"],
    "publisher": ["publisher", "organization"],
    "copyright": ["copyright", "year", "date"],
    "genre": ["genre"],
}


def generate_base_metadata(extractor: MetadataExtractor) -> BaseMetadata:
    return BaseMetadata(
        artist=extractor.extract(_candidate_names["artist"]),
        title=extractor.extract(_candidate_names["title"]),
        publisher=extractor.extract(_candidate_names["publisher"]),
        copyright=extractor.extract(_candidate_names["copyright"]),
        genre=extractor.extract(_candidate_names["genre"]),
    )
