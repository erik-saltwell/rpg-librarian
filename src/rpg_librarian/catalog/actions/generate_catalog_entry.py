from __future__ import annotations

from pathlib import Path

from ...catalog.model.base_metadata import BaseMetadata
from ...catalog.model.media_type_metadata import MediaTypeMetadata
from ...file_data.actions.generate_file_data import generate_file_data
from ...file_data.model.file_data import FileData
from ...metadata.generate_base_metadata import generate_base_metadata
from ...metadata.generate_extractor import generate_extractor
from ...metadata.metadata_extractor import MetadataExtractor
from ..model.catalog_entry import CatalogEntry
from ..model.library_data import LibraryData
from ..model.media_type import MediaType
from ..tools.id_generator import generate_unique_id
from ..tools.media_type_detector import find_media_type_from_mime_type, find_mime_type


def generate_catalog_entry(file_path: Path, library: LibraryData) -> CatalogEntry:
    errors: list[str] = []
    entry_id: str = generate_unique_id()

    mime_type: str | None = None
    try:
        mime_type = find_mime_type(file_path)
    except Exception as e:
        errors.append(f"Failed to detect MIME type: {e}")

    media_type: MediaType | None = None
    if mime_type is not None:
        try:
            media_type = find_media_type_from_mime_type(mime_type)
        except Exception as e:
            errors.append(f"Failed to detect media type: {e}")

    extractor: MetadataExtractor | None = None
    if media_type is not None:
        try:
            extractor = generate_extractor(media_type=media_type, file_path=file_path)
        except Exception as e:
            errors.append(f"Failed to create metadata extractor: {e}")

    base_metadata: BaseMetadata | None = None
    if extractor is not None:
        try:
            base_metadata = generate_base_metadata(extractor=extractor)
        except Exception as e:
            errors.append(f"Failed to generate base metadata: {e}")

    media_type_metadata: MediaTypeMetadata = None
    if extractor is not None:
        try:
            media_type_metadata = extractor.generate_media_type_specific_metadata()
        except Exception as e:
            errors.append(f"Failed to generate media type metadata: {e}")

    file_data: FileData | None = None
    try:
        file_data = generate_file_data(file_path=file_path, library=library)
    except Exception as e:
        errors.append(f"Failed to generate file data: {e}")

    return CatalogEntry(
        id=entry_id,
        file_data=file_data,
        mime_type=mime_type,
        media_type=media_type,
        base_metadata=base_metadata,
        media_type_metadata=media_type_metadata,
        errors=errors,
    )
