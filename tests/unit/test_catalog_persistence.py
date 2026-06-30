from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

import rpg_librarian.catalog.model.catalog as catalog_module
from rpg_librarian.catalog.model.catalog import Catalog
from rpg_librarian.catalog.model.catalog_entry import CatalogEntry
from rpg_librarian.catalog.model.library_data import LibraryData
from rpg_librarian.file_data.model.file_data import FileData


def _catalog(root: Path, entry_id: str) -> Catalog:
    return Catalog(library=LibraryData(root_folder=root), entries=[CatalogEntry(id=entry_id)])


def test_first_save_creates_no_backup(tmp_path: Path) -> None:
    save_path = tmp_path / "catalog.json"
    _catalog(tmp_path, "first").save(save_path)

    assert not (tmp_path / ".backup").exists()


def test_overwriting_save_backs_up_previous_contents(tmp_path: Path) -> None:
    save_path = tmp_path / "catalog.json"
    _catalog(tmp_path, "original").save(save_path)
    original_bytes = save_path.read_bytes()

    _catalog(tmp_path, "updated").save(save_path)

    backups = list((tmp_path / ".backup").glob("catalog-*.json"))
    assert len(backups) == 1
    # The backup holds the prior state, while the live file holds the new one.
    assert backups[0].read_bytes() == original_bytes
    assert Catalog.load(save_path).entries[0].id == "updated"


def test_each_overwrite_adds_a_backup(tmp_path: Path) -> None:
    save_path = tmp_path / "catalog.json"
    _catalog(tmp_path, "v1").save(save_path)
    _catalog(tmp_path, "v2").save(save_path)
    _catalog(tmp_path, "v3").save(save_path)

    backups = list((tmp_path / ".backup").glob("catalog-*.json"))
    assert len(backups) == 2


def test_retains_only_the_five_newest_backups(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    save_path = tmp_path / "catalog.json"

    # Feed deterministic, strictly increasing timestamps so backups sort in a
    # known order regardless of the host clock's resolution.
    clock = iter(datetime(2026, 6, 30, 12, 0, second) for second in range(20))
    monkeypatch.setattr(catalog_module, "datetime", type("Clock", (), {"now": staticmethod(lambda: next(clock))}))

    # 8 saves create 7 backups (the prior states v0..v6); retention keeps 5.
    for version in range(8):
        _catalog(tmp_path, f"v{version}").save(save_path)

    backups = sorted((tmp_path / ".backup").glob("catalog-*.json"))
    assert len(backups) == 5
    kept_ids = [Catalog.load(backup).entries[0].id for backup in backups]
    assert kept_ids == ["v2", "v3", "v4", "v5", "v6"]


def test_catalog_save_and_load_round_trip(tmp_path: Path) -> None:
    sample_file = tmp_path / "sample.txt"
    sample_file.write_text("hello world", encoding="utf-8")

    catalog = Catalog(
        library=LibraryData(root_folder=tmp_path),
        entries=[
            CatalogEntry(
                id="sample",
                file_data=FileData(
                    sha256="abc123",
                    filepath=sample_file,
                    filename=sample_file.name,
                    extension=sample_file.suffix,
                    size_in_bytes=sample_file.stat().st_size,
                    mime_type="text/plain",
                    root_folder=None,
                    root_child_folder=None,
                    root_grandchild_folder=None,
                    root_greatgrandchild_folder=None,
                    parent_folder=None,
                    grandparent_folder=None,
                ),
            )
        ],
    )

    save_path = tmp_path / "catalog.json"
    catalog.save(save_path)

    loaded_catalog = Catalog.load(save_path)

    assert loaded_catalog.library.root_folder == catalog.library.root_folder
    assert loaded_catalog.entries[0].id == catalog.entries[0].id
    assert loaded_catalog.entries[0].file_data is not None
    assert catalog.entries[0].file_data is not None
    assert loaded_catalog.entries[0].file_data.filepath == catalog.entries[0].file_data.filepath


@pytest.mark.parametrize(
    ("media_type", "removed_field"),
    [("image", "hash"), ("audio", "acoustic_fingerprint")],
)
def test_catalog_load_requires_rebuild_for_removed_metadata(
    tmp_path: Path, media_type: str, removed_field: str
) -> None:
    catalog_path = tmp_path / "index.json"
    catalog_path.write_text(
        json.dumps(
            {
                "library": {"root_folder": str(tmp_path)},
                "entries": [
                    {
                        "id": "legacy",
                        "media_type": media_type,
                        "media_type_metadata": {removed_field: "legacy-value"},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="rerun build-catalog"):
        Catalog.load(catalog_path)
