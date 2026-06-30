from __future__ import annotations

from pathlib import Path

from rpg_librarian.catalog.actions.generate_catalog_entry import generate_catalog_entry
from rpg_librarian.catalog.model.base_metadata import BaseMetadata
from rpg_librarian.catalog.model.library_data import LibraryData


def test_base_metadata_is_omitted_when_empty(fixtures_dir: Path) -> None:
    # viewbox_only.svg carries no title/creator/etc., so the entry should not
    # carry an all-null base-metadata block.
    library = LibraryData(root_folder=fixtures_dir)
    entry = generate_catalog_entry(fixtures_dir / "vector" / "viewbox_only.svg", library)
    assert entry.base_metadata is None


def test_base_metadata_is_kept_when_populated(fixtures_dir: Path) -> None:
    library = LibraryData(root_folder=fixtures_dir)
    entry = generate_catalog_entry(fixtures_dir / "vector" / "flag.svg", library)
    assert entry.base_metadata is not None
    assert entry.base_metadata.artist == "Jane Cartographer"


def test_base_metadata_is_empty_helper() -> None:
    assert BaseMetadata().is_empty() is True
    assert BaseMetadata(genre="Maps").is_empty() is False
