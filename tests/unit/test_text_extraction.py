from pathlib import Path

import pymupdf

from rpg_librarian.catalog.model.catalog_entry import CatalogEntry
from rpg_librarian.catalog.model.media_type import MediaType
from rpg_librarian.text_extraction.extract_text import _extract_page_text


def _entry(filepath: Path) -> CatalogEntry:
    return CatalogEntry(id="test-pdf", filepath=filepath, media_type=MediaType.pdf)


def test_extract_page_text_returns_embedded_text(tmp_path: Path) -> None:
    filepath = tmp_path / "with-text.pdf"
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "Tavern rumors and ancient dragons")
    document.save(filepath)
    document.close()

    assert "Tavern rumors and ancient dragons" in _extract_page_text(_entry(filepath), 0)


def test_extract_page_text_returns_empty_string_when_page_has_no_text(tmp_path: Path) -> None:
    filepath = tmp_path / "without-text.pdf"
    document = pymupdf.open()
    document.new_page()
    document.save(filepath)
    document.close()

    assert _extract_page_text(_entry(filepath), 0) == ""
