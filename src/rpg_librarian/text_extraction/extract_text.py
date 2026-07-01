from __future__ import annotations

import pymupdf

from ..catalog.model.catalog_entry import CatalogEntry
from ..catalog.model.media_type import MediaType

isbn_pattern = (
    r"\b(?:ISBN(?:-1[03])?:?\s*)?(?=[-0-9X]{10,17}\b)(?:97[89][- ]?)?[0-9]{1,5}[- ]?[0-9]+[- ]?[0-9]+[- ]?[0-9X]\b"
)


def _extract_page_text(entry: CatalogEntry, page_number: int) -> str:
    """Extract text from a specific page of a PDF file."""
    if entry.filepath is None:
        raise ValueError("Cannot extract page text from an entry without a filepath.")

    with pymupdf.open(entry.filepath) as document:
        page = document.load_page(page_number)
        return page.get_text("text")


def extract_text_from_file(entry: CatalogEntry, max_page_count: int = 8) -> str:
    if not entry.media_type == MediaType.pdf:
        raise RuntimeError("Cannot extract text from non-PDF file.")

    return ""
