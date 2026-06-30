from __future__ import annotations

import mimetypes
from pathlib import Path

import magic

from ..model.media_type import MediaType

_MIME_PREFIX_MAP: dict[str, MediaType] = {
    "audio/": MediaType.audio,
    "video/": MediaType.video,
    "image/": MediaType.image,
    "model/": MediaType.mesh,
    "text/": MediaType.text,
}

_MIME_EXACT_MAP: dict[str, MediaType] = {
    "application/pdf": MediaType.pdf,
    # SVG is XML vector data, not raster; route it away from the image/ prefix
    # so it reaches the SVG extractor instead of Pillow.
    "image/svg+xml": MediaType.vector,
}

_EXTENSION_MESH: frozenset[str] = frozenset({".glb", ".gltf", ".obj", ".stl", ".fbx", ".dae", ".blend", ".3ds", ".ply"})

_EXTENSION_VECTOR: frozenset[str] = frozenset({".svg", ".svgz"})


def find_media_type_from_mime_type(mime_type: str) -> MediaType:
    # Exact matches win over prefix matches: "image/svg+xml" is vector, not image.
    if mime_type in _MIME_EXACT_MAP:
        return _MIME_EXACT_MAP[mime_type]
    for prefix, media_type in _MIME_PREFIX_MAP.items():
        if mime_type.startswith(prefix):
            return media_type
    return MediaType.unknown


def find_mime_type(file_path: Path) -> str:
    path = Path(file_path)

    # Trust the extension for SVG: content sniffing can label an SVG that lacks
    # an XML declaration as text/xml, which would misroute it.
    if path.suffix.lower() in _EXTENSION_VECTOR:
        return "image/svg+xml"

    if magic is not None and path.exists():
        try:
            return magic.from_file(str(path), mime=True)
        except Exception:
            pass

    if path.suffix.lower() in _EXTENSION_MESH:
        return "model/mesh"

    mime_type, _ = mimetypes.guess_type(path.name)
    return mime_type or "application/octet-stream"
