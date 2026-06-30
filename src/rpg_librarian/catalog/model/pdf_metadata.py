from __future__ import annotations

from pydantic import BaseModel


class PdfMetadata(BaseModel):
    page_count: int | None = None
    is_encrypted: bool | None = None
    needs_password: bool | None = None
    has_extractable_text: bool | None = None
    likely_scanned: bool | None = None
