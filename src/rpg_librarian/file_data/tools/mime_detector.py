from __future__ import annotations

import mimetypes
from pathlib import Path

import magic


def _detect_mime_type_using_contents(path: Path) -> str | None:
    """Detect MIME type from file contents using libmagic."""
    try:
        return magic.from_file(str(path), mime=True)
    except Exception:
        return None


def _detect_mime_from_extension(path: Path) -> str | None:
    """Guess MIME type from filename extension only."""
    mime_type, _encoding = mimetypes.guess_type(path.name)
    return mime_type


def detect_mime_type(path: Path) -> str:
    mime_type: str | None = _detect_mime_type_using_contents(path)
    if not mime_type:
        mime_type = _detect_mime_from_extension(path)
    if not mime_type:
        return "application/octet-stream"
    else:
        return mime_type
