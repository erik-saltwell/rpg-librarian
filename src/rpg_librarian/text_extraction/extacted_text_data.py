from __future__ import annotations

from pydantic import BaseModel


class ExtractedPageText(BaseModel):
    text: str


class ExtractedTextData(BaseModel):
    pages: list[ExtractedPageText]
