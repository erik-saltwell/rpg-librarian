from __future__ import annotations

from pathlib import Path

import fitz
from pymediainfo import MediaInfo

from ..catalog.model.media_type_metadata import MediaTypeMetadata
from ..catalog.model.pdf_metadata import PdfMetadata
from .metadata_extractor import MetadataExtractor

# Only the first few pages are sampled for text/image analysis - enough to
# characterize the document without paying the cost of scanning every page.
_TEXT_SAMPLE_PAGE_LIMIT = 5
_MIN_EXTRACTABLE_TEXT_CHARS = 20
_SCANNED_IMAGE_COVERAGE_THRESHOLD = 0.85


def get_page_count(doc: fitz.Document | None) -> int | None:
    """Return the document's page count."""
    if doc is None:
        return None
    return doc.page_count


def get_is_encrypted(doc: fitz.Document | None) -> bool | None:
    """Return whether the document carries any encryption, password-protected or not."""
    if doc is None:
        return None
    return bool(doc.is_encrypted)


def get_needs_password(doc: fitz.Document | None) -> bool | None:
    """Return whether a password is required to read the document's content."""
    if doc is None:
        return None
    return bool(doc.needs_pass)


def _sample_pages(doc: fitz.Document) -> list[fitz.Page]:
    return [doc[i] for i in range(min(doc.page_count, _TEXT_SAMPLE_PAGE_LIMIT))]


def _page_has_text(page: fitz.Page) -> bool:
    text = str(page.get_text("text"))
    return len(text.strip()) >= _MIN_EXTRACTABLE_TEXT_CHARS


def _page_image_coverage(page: fitz.Page) -> float:
    """Fraction of the page area covered by embedded images."""
    page_area = page.rect.width * page.rect.height
    if page_area <= 0:
        return 0.0
    covered = 0.0
    for image in page.get_images(full=True):
        xref = image[0]
        for rect in page.get_image_rects(xref):
            visible = rect & page.rect
            covered += visible.width * visible.height
    return covered / page_area


def get_has_extractable_text(doc: fitz.Document | None) -> bool | None:
    """Return whether any sampled page contains a real text layer."""
    if doc is None or doc.needs_pass or doc.page_count == 0:
        return None
    return any(_page_has_text(page) for page in _sample_pages(doc))


def get_likely_scanned(doc: fitz.Document | None) -> bool | None:
    """Return whether sampled pages look like scans: image-dominated with no text layer."""
    if doc is None or doc.needs_pass or doc.page_count == 0:
        return None
    for page in _sample_pages(doc):
        if _page_has_text(page) or _page_image_coverage(page) < _SCANNED_IMAGE_COVERAGE_THRESHOLD:
            return False
    return True


class PdfMetadataExtractor(MetadataExtractor):
    def __init__(self, file_path: Path):
        self._media_info: MediaInfo = MediaInfo.parse(filename=file_path)
        try:
            self._doc: fitz.Document | None = fitz.open(file_path)
        except Exception:
            self._doc = None

    def extract_value(self, candidate: str) -> str | None:
        key = candidate.lower()
        for track in self._media_info.general_tracks:
            value = getattr(track, key, None)
            if value is not None:
                text = str(value).strip()
                if text:
                    return text
        return None

    def generate_media_type_specific_metadata(self) -> MediaTypeMetadata:
        return PdfMetadata(
            page_count=get_page_count(self._doc),
            is_encrypted=get_is_encrypted(self._doc),
            needs_password=get_needs_password(self._doc),
            has_extractable_text=get_has_extractable_text(self._doc),
            likely_scanned=get_likely_scanned(self._doc),
        )
