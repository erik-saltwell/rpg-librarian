from __future__ import annotations

from pathlib import Path

from rpg_librarian.catalog.model.mesh_metadata import MeshMetadata
from rpg_librarian.metadata.mesh_extractor import MeshMetadataExtractor


def test_stl_returns_mesh_metadata(fixtures_dir: Path) -> None:
    extractor = MeshMetadataExtractor(fixtures_dir / "mesh" / "dragonlock_clip.stl")
    result = extractor.generate_media_type_specific_metadata()
    assert isinstance(result, MeshMetadata)


def test_stl_bounding_box_is_positive(fixtures_dir: Path) -> None:
    extractor = MeshMetadataExtractor(fixtures_dir / "mesh" / "dragonlock_clip.stl")
    result = extractor.generate_media_type_specific_metadata()
    assert isinstance(result, MeshMetadata)
    assert isinstance(result.bounding_box_x_mm, float) and result.bounding_box_x_mm > 0
    assert isinstance(result.bounding_box_y_mm, float) and result.bounding_box_y_mm > 0
    assert isinstance(result.bounding_box_z_mm, float) and result.bounding_box_z_mm > 0


def test_stl_surface_area_is_positive(fixtures_dir: Path) -> None:
    extractor = MeshMetadataExtractor(fixtures_dir / "mesh" / "dragonlock_clip.stl")
    result = extractor.generate_media_type_specific_metadata()
    assert isinstance(result, MeshMetadata)
    assert isinstance(result.surface_area_cm2, float)
    assert result.surface_area_cm2 > 0


def test_stl_unit_defaults_to_mm(fixtures_dir: Path) -> None:
    extractor = MeshMetadataExtractor(fixtures_dir / "mesh" / "dragonlock_clip.stl")
    result = extractor.generate_media_type_specific_metadata()
    assert isinstance(result, MeshMetadata)
    assert result.unit == "mm"


def test_stl_extract_value_returns_none(fixtures_dir: Path) -> None:
    extractor = MeshMetadataExtractor(fixtures_dir / "mesh" / "dragonlock_clip.stl")
    assert extractor.extract_value("title") is None
    assert extractor.extract_value("artist") is None
