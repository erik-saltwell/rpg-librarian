from __future__ import annotations

from pathlib import Path
from typing import Any

import acoustid


def get_tag(audio_file: Any, key: str) -> str | None:
    if audio_file is None:
        return None
    val = audio_file.get(key)
    return str(val[0]) if val else None


def get_duration(audio_file: Any) -> float | None:
    info = getattr(audio_file, "info", None)
    return round(info.length, 3) if info and hasattr(info, "length") else None


def get_fingerprint(file_path: Path) -> str:
    try:
        _, fp = acoustid.fingerprint_file(file_path)
    except acoustid.FingerprintGenerationError:
        return ""
    return fp.decode("ascii") if isinstance(fp, bytes) else str(fp)
