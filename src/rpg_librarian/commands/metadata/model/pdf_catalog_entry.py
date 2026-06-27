from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class PdfCatalogEntry(BaseModel):
    media_type: Literal["pdf", "pdf-image"] = "pdf"

    path: str
    filename: str
    extension: str
    mime_type: str | None = None
    size_bytes: int
    sha256: str
    modified_at: str

    page_count: int | None = None
    is_encrypted: bool | None = None
    needs_password: bool | None = None
    metadata: dict[str, Any] | None = None

    authors: list[str] = Field(default_factory=list)
    publisher: str | None = None
    publication_year: int | None = None
    copyright_year: int | None = None
    edition: str | None = None

    has_toc: bool | None = None
    toc_entry_count: int | None = None

    has_extractable_text: bool | None = None
    char_count_sampled: int | None = None
    word_count_sampled: int | None = None

    first_pages_text: str | None = None
    isbn_candidates: list[str] = Field(default_factory=list)
    url_candidates: list[str] = Field(default_factory=list)
    copyright_lines: list[str] = Field(default_factory=list)

    image_count_sampled: int | None = None
    large_image_count_sampled: int | None = None
    likely_scanned: bool | None = None

    errors: list[str] = Field(default_factory=list)
