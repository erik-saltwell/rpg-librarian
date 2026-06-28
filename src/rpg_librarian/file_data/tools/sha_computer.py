from __future__ import annotations

import hashlib
from pathlib import Path


def generate_hash(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Compute SHA-256 for a file without loading the whole file into memory."""
    digest = hashlib.sha256()

    with path.open("rb") as f:
        while chunk := f.read(chunk_size):
            digest.update(chunk)

    return digest.hexdigest()
