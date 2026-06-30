from __future__ import annotations

from pathlib import Path

from rpg_librarian.catalog.actions.generate_catalog import generate_catalog
from rpg_librarian.catalog.model.catalog import Catalog
from rpg_librarian.catalog.model.catalog_entry import CatalogEntry
from rpg_librarian.catalog.model.library_data import LibraryData


def _entry_for(catalog: Catalog, filename: str) -> CatalogEntry:
    for entry in catalog.entries:
        if entry.file_data is not None and entry.file_data.filename == filename:
            return entry
    raise AssertionError(f"no entry for {filename}")


def _names(catalog: Catalog) -> set[str]:
    return {entry.file_data.filename for entry in catalog.entries if entry.file_data is not None}


def test_unchanged_files_are_reused(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("alpha", encoding="utf-8")
    (tmp_path / "b.txt").write_text("beta", encoding="utf-8")

    first = generate_catalog(tmp_path)
    second = generate_catalog(tmp_path)

    # A reused entry keeps its original (uuid) id; a regenerated one gets a new id.
    assert _entry_for(second, "a.txt").id == _entry_for(first, "a.txt").id
    assert _entry_for(second, "b.txt").id == _entry_for(first, "b.txt").id


def test_changed_file_is_reprocessed(tmp_path: Path) -> None:
    target = tmp_path / "a.txt"
    target.write_text("alpha", encoding="utf-8")
    first_id = _entry_for(generate_catalog(tmp_path), "a.txt").id

    target.write_text("alpha with a different size", encoding="utf-8")
    second_id = _entry_for(generate_catalog(tmp_path), "a.txt").id

    assert second_id != first_id


def test_new_files_added_and_deleted_files_dropped(tmp_path: Path) -> None:
    kept = tmp_path / "kept.txt"
    removed = tmp_path / "removed.txt"
    kept.write_text("kept", encoding="utf-8")
    removed.write_text("gone soon", encoding="utf-8")

    first = generate_catalog(tmp_path)
    kept_id = _entry_for(first, "kept.txt").id

    removed.unlink()
    (tmp_path / "added.txt").write_text("brand new", encoding="utf-8")
    second = generate_catalog(tmp_path)

    assert _names(second) == {"kept.txt", "added.txt"}
    assert _entry_for(second, "kept.txt").id == kept_id  # survivor still reused


def test_previously_errored_entry_is_reprocessed(tmp_path: Path) -> None:
    library = LibraryData(root_folder=tmp_path)
    (tmp_path / "a.txt").write_text("alpha", encoding="utf-8")
    generate_catalog(tmp_path)

    # Simulate a prior failed extraction, then confirm the rebuild retries it
    # (fresh id, errors cleared) instead of reusing the broken entry.
    catalog = Catalog.load(library.index_file)
    errored = _entry_for(catalog, "a.txt")
    original_id = errored.id
    errored.errors = ["transient failure"]
    catalog.save(library.index_file)

    rebuilt = _entry_for(generate_catalog(tmp_path), "a.txt")
    assert rebuilt.id != original_id
    assert rebuilt.errors == []
