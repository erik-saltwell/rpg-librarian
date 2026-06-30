from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

from ..catalog.model.media_type_metadata import MediaTypeMetadata
from ..catalog.model.svg_metadata import SvgMetadata
from .metadata_extractor import MetadataExtractor

# Maps base-metadata candidate names onto the local element name that carries
# the value inside an SVG. Titles come from either <title> or Dublin Core
# <dc:title>; the remaining fields are Dublin Core elements in <metadata>.
_FIELD_MAP: dict[str, str] = {
    "title": "title",
    "artist": "creator",
    "artists": "creator",
    "creator": "creator",
    "author": "creator",
    "authors": "creator",
    "publisher": "publisher",
    "organization": "publisher",
    "copyright": "rights",
    "rights": "rights",
    "date": "date",
}

_LENGTH_RE = re.compile(r"^\s*([+-]?[0-9]*\.?[0-9]+)\s*([a-z%]*)\s*$", re.IGNORECASE)


def _local_name(tag: str) -> str:
    """Strip any XML namespace, so '{http://www.w3.org/2000/svg}title' -> 'title'."""
    return tag.rsplit("}", 1)[-1]


def parse_length(raw: str | None) -> tuple[float | None, str | None]:
    """Split an SVG length like '64px' or '20mm' into (value, unit).

    Percentages and unparsable values yield (None, None): they carry no
    intrinsic size, so the caller should fall back to the viewBox.
    """
    if not raw:
        return None, None
    match = _LENGTH_RE.match(raw)
    if match is None:
        return None, None
    unit = match.group(2).lower() or None
    if unit == "%":
        return None, None
    return float(match.group(1)), unit


def parse_view_box(raw: str | None) -> tuple[float | None, float | None]:
    """Return the (width, height) carried by a 'min-x min-y width height' viewBox."""
    if not raw:
        return None, None
    parts = re.split(r"[\s,]+", raw.strip())
    if len(parts) != 4:
        return None, None
    try:
        return float(parts[2]), float(parts[3])
    except ValueError:
        return None, None


class SvgMetadataExtractor(MetadataExtractor):
    def __init__(self, file_path: Path):
        # SVG is XML, not raster data; parse the document tree once. Malformed
        # or unreadable files degrade to empty metadata rather than raising,
        # matching how the mesh/pdf extractors handle unparsable inputs.
        self._root: ET.Element | None
        try:
            self._root = ET.parse(file_path).getroot()
        except (ET.ParseError, OSError):
            self._root = None

    def extract_value(self, candidate: str) -> str | None:
        if self._root is None:
            return None
        field = _FIELD_MAP.get(candidate.lower())
        if field is None:
            return None
        for element in self._root.iter():
            if _local_name(element.tag) == field and element.text:
                text = element.text.strip()
                if text:
                    return text
        return None

    def generate_media_type_specific_metadata(self) -> MediaTypeMetadata:
        if self._root is None:
            return SvgMetadata()

        width, units = parse_length(self._root.get("width"))
        height, height_units = parse_length(self._root.get("height"))
        if units is None:
            units = height_units

        # When width/height are absent or percentage-based, the viewBox gives the
        # intrinsic drawing size in user units.
        if width is None or height is None:
            vb_width, vb_height = parse_view_box(self._root.get("viewBox"))
            width = width if width is not None else vb_width
            height = height if height is not None else vb_height

        return SvgMetadata(
            width=width,
            height=height,
            units=units,
            view_box=self._root.get("viewBox"),
        )
