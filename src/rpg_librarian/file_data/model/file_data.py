from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel


class FileData(BaseModel):
    sha256: str
    filepath: Path
    filename: str
    extension: str
    size_in_bytes: int
    mime_type: str
    root_folder: str | None
    root_child_folder: str | None
    root_grandchild_folder: str | None
    root_greatgrandchild_folder: str | None
    parent_folder: str | None
    grandparent_folder: str | None
