from __future__ import annotations

import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import NamedTuple

import trimesh
import trimesh.util
import trimesh.visual

from ..catalog.model.media_type_metadata import MediaTypeMetadata
from ..catalog.model.mesh_metadata import MeshMetadata
from .metadata_extractor import MetadataExtractor


class BoundingBoxExtents(NamedTuple):
    x_mm: float
    y_mm: float
    z_mm: float


_3MF_NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"

# STL files have no embedded unit; millimetres is the 3D printing convention.
_STL_ASSUMED_UNIT = "mm"

# 3MF spec defaults to millimetres.
_3MF_UNIT_MAP = {
    "millimeter": "mm",
    "centimeter": "cm",
    "inch": "in",
    "foot": "ft",
    "meter": "m",
    "micron": "um",
}


def units_from_metadata(file_path: Path) -> str:
    try:
        with zipfile.ZipFile(file_path) as zf:
            model_files = [n for n in zf.namelist() if n.lower().endswith(".model")]
            for model_file in model_files:
                with zf.open(model_file) as f:
                    try:
                        tree = ET.parse(f)
                    except ET.ParseError:
                        return "mm"

                    root = tree.getroot()
                    raw_unit = root.get("unit")
                    if raw_unit:
                        unit = _3MF_UNIT_MAP.get(raw_unit.lower(), raw_unit)
                        return unit
        return "mm"

    except (zipfile.BadZipFile, Exception):
        return "mm"


def _extract_3mf_metadata(path: Path) -> dict[str, str]:
    meta: dict[str, str] = {}

    try:
        with zipfile.ZipFile(path) as zf:
            model_files = [n for n in zf.namelist() if n.lower().endswith(".model")]
            for model_file in model_files:
                with zf.open(model_file) as f:
                    try:
                        tree = ET.parse(f)
                    except ET.ParseError:
                        continue

                    root = tree.getroot()

                    for md in root.findall(f"{{{_3MF_NS}}}metadata"):
                        name = (md.get("name") or "").lower().strip()
                        value = (md.text or "").strip()
                        if name and value:
                            meta[name] = value

    except (zipfile.BadZipFile, Exception):
        pass

    return meta


def get_extents_from_mesh(mesh: trimesh.Trimesh) -> BoundingBoxExtents:
    extents = mesh.bounding_box.extents
    return BoundingBoxExtents(
        x_mm=round(float(extents[0]), 4),
        y_mm=round(float(extents[1]), 4),
        z_mm=round(float(extents[2]), 4),
    )


def get_surface_area_cm_from_mesh(mesh: trimesh.Trimesh) -> float | None:
    surface_area: float | None = None
    try:
        surface_area = round(float(mesh.area) / 100, 4)  # mm² → cm²
    except Exception:
        pass
    return surface_area


def has_textures_from_mesh(mesh: trimesh.Trimesh) -> bool:
    return isinstance(mesh.visual, trimesh.visual.TextureVisuals)


def units_from_mesh(file_path: Path) -> str | None:
    return _STL_ASSUMED_UNIT


class MeshMetadataExtractor(MetadataExtractor):
    def __init__(self, file_path: Path):
        self._path = file_path
        self._meta = _extract_3mf_metadata(file_path)
        try:
            loaded = trimesh.load(str(file_path), force="mesh")
            self._mesh: trimesh.Trimesh | None = loaded if isinstance(loaded, trimesh.Trimesh) else None
        except Exception:
            self._mesh = None

    def extract_value(self, candidate: str) -> str | None:
        key = candidate.lower()
        for meta_key, meta_value in self._meta.items():
            if meta_key.lower() == key:
                text = meta_value.strip()
                if text:
                    return text
        return None

    def generate_media_type_specific_metadata(self) -> MediaTypeMetadata:
        extents: BoundingBoxExtents | None = None
        surface_area: float | None = None
        if self._mesh is not None:
            extents = get_extents_from_mesh(self._mesh)
            surface_area = get_surface_area_cm_from_mesh(self._mesh)
        return MeshMetadata(
            bounding_box_x_mm=extents.x_mm if extents else None,
            bounding_box_y_mm=extents.y_mm if extents else None,
            bounding_box_z_mm=extents.z_mm if extents else None,
            surface_area_cm2=surface_area,
            unit=units_from_metadata(self._path),
        )
