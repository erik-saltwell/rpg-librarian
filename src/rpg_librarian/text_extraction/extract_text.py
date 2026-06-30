from __future__ import annotations

import re

from ..catalog.model.catalog_entry import CatalogEntry
from ..catalog.model.media_type import MediaType


def _has_isbn(page_text: str) -> bool:
    """Check if the given page text contains an ISBN number."""

    # Regular expression pattern to match ISBN-10 or ISBN-13
    isbn_pattern = (
        r"\b(?:ISBN(?:-1[03])?:?\s*)?(?=[-0-9X]{10,17}\b)(?:97[89][- ]?)?[0-9]{1,5}[- ]?[0-9]+[- ]?[0-9]+[- ]?[0-9X]\b"
    )

    # Search for the pattern in the page text
    match = re.search(isbn_pattern, page_text)

    return match is not None


def _extract_page_text(entry: CatalogEntry, page_number: int) -> str:
    """Extract text from a specific page of a PDF file."""
    # Placeholder implementation; replace with actual PDF text extraction logic
    raise NotImplementedError("PDF text extraction is not implemented yet.")


def extract_text_from_file(entry: CatalogEntry, max_page_count: int = 8) -> str:
    if not entry.media_type == MediaType.pdf:
        raise RuntimeError("Cannot extract text from non-PDF file.")

    return ""
