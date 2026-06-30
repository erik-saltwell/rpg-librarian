from __future__ import annotations

import io
from pathlib import Path

import fitz
import pytest
from PIL import Image
from pymediainfo import MediaInfo

from rpg_librarian.catalog.model.pdf_metadata import PdfMetadata
from rpg_librarian.metadata.pdf_extractor import PdfMetadataExtractor

_EMPTY_GENERAL_TRACK_XML = '<MediaInfo><File><track type="General" /></File></MediaInfo>'


def _patch_media_info(monkeypatch: pytest.MonkeyPatch, xml: str = _EMPTY_GENERAL_TRACK_XML) -> None:
    media_info = MediaInfo(xml)
    monkeypatch.setattr(MediaInfo, "parse", lambda *args, **kwargs: media_info)


def _write_text_pdf(path: Path) -> None:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "This page has a real, selectable text layer with plenty of characters.")
    doc.save(str(path))
    doc.close()


def _write_blank_pdf(path: Path) -> None:
    doc = fitz.open()
    doc.new_page()
    doc.save(str(path))
    doc.close()


def _write_scanned_pdf(path: Path) -> None:
    doc = fitz.open()
    page = doc.new_page(width=200, height=300)
    image = Image.new("RGB", (100, 100), color="red")
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    page.insert_image(page.rect, stream=buf.getvalue())
    doc.save(str(path))
    doc.close()


_PDF_ENCRYPT_AES_256 = 5  # fitz.PDF_ENCRYPT_AES_256 - missing from the bundled type stubs


def _write_encrypted_pdf(path: Path) -> None:
    doc = fitz.open()
    doc.new_page()
    doc.save(str(path), encryption=_PDF_ENCRYPT_AES_256, owner_pw="owner", user_pw="secret")
    doc.close()


def test_pdf_extractor_reads_page_count(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _patch_media_info(monkeypatch)
    pdf_path = tmp_path / "multi_page.pdf"
    doc = fitz.open()
    for _ in range(3):
        doc.new_page()
    doc.save(str(pdf_path))
    doc.close()

    result = PdfMetadataExtractor(pdf_path).generate_media_type_specific_metadata()

    assert isinstance(result, PdfMetadata)
    assert result.page_count == 3
    assert result.is_encrypted is False
    assert result.needs_password is False


def test_pdf_extractor_detects_password_protected_document(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _patch_media_info(monkeypatch)
    pdf_path = tmp_path / "locked.pdf"
    _write_encrypted_pdf(pdf_path)

    result = PdfMetadataExtractor(pdf_path).generate_media_type_specific_metadata()

    assert isinstance(result, PdfMetadata)
    assert result.is_encrypted is True
    assert result.needs_password is True
    # Content can't be read without the password, so text/scan analysis is skipped.
    assert result.has_extractable_text is None
    assert result.likely_scanned is None


@pytest.mark.parametrize("error", [OSError("unreadable"), RuntimeError("parse failed"), ValueError("invalid")])
def test_pdf_extractor_raises_on_parse_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, error: Exception
) -> None:
    def raise_error(*args: object, **kwargs: object) -> MediaInfo:
        raise error

    monkeypatch.setattr(MediaInfo, "parse", raise_error)

    with pytest.raises(Exception, match=r"."):
        PdfMetadataExtractor(tmp_path / "broken.pdf")


def test_pdf_with_text_layer_has_extractable_text(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _patch_media_info(monkeypatch)
    pdf_path = tmp_path / "text.pdf"
    _write_text_pdf(pdf_path)

    result = PdfMetadataExtractor(pdf_path).generate_media_type_specific_metadata()

    assert isinstance(result, PdfMetadata)
    assert result.has_extractable_text is True
    assert result.likely_scanned is False


def test_blank_pdf_has_no_extractable_text_and_is_not_scanned(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _patch_media_info(monkeypatch)
    pdf_path = tmp_path / "blank.pdf"
    _write_blank_pdf(pdf_path)

    result = PdfMetadataExtractor(pdf_path).generate_media_type_specific_metadata()

    assert isinstance(result, PdfMetadata)
    assert result.has_extractable_text is False
    # No text and no image either - not enough evidence to call it "scanned".
    assert result.likely_scanned is False


def test_image_only_pdf_is_likely_scanned(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _patch_media_info(monkeypatch)
    pdf_path = tmp_path / "scanned.pdf"
    _write_scanned_pdf(pdf_path)

    result = PdfMetadataExtractor(pdf_path).generate_media_type_specific_metadata()

    assert isinstance(result, PdfMetadata)
    assert result.has_extractable_text is False
    assert result.likely_scanned is True


def test_scanned_magazine_fixture_is_detected_as_scanned(fixtures_dir: Path) -> None:
    extractor = PdfMetadataExtractor(fixtures_dir / "pdf" / "dungeon_magazine_003.pdf")
    result = extractor.generate_media_type_specific_metadata()

    assert isinstance(result, PdfMetadata)
    assert result.has_extractable_text is False
    assert result.likely_scanned is True


def test_text_fixture_has_extractable_text_and_is_not_scanned(fixtures_dir: Path) -> None:
    extractor = PdfMetadataExtractor(fixtures_dir / "pdf" / "die_glocke.pdf")
    result = extractor.generate_media_type_specific_metadata()

    assert isinstance(result, PdfMetadata)
    assert result.has_extractable_text is True
    assert result.likely_scanned is False
