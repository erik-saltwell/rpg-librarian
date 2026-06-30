from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

from rpg_librarian.catalog.model.catalog_entry import CatalogEntry

from ...catalog.model.library_data import LibraryData

_BACKUP_DIR_NAME = ".backup"
_RETAINED_BACKUPS = 5
_REMOVED_METADATA_FIELDS = {
    "audio": "acoustic_fingerprint",
    "image": "hash",
}


def _reject_catalog_with_removed_metadata(payload: object) -> None:
    if not isinstance(payload, dict):
        return
    entries = payload.get("entries")
    if not isinstance(entries, list):
        return

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        removed_field = _REMOVED_METADATA_FIELDS.get(entry.get("media_type"))
        metadata = entry.get("media_type_metadata")
        if removed_field is not None and isinstance(metadata, dict) and removed_field in metadata:
            raise ValueError(
                f"Catalog contains removed metadata field {removed_field!r}; rerun build-catalog to rebuild the index"
            )


def _backup_existing(target_path: Path) -> None:
    """Copy the current file (if any) into a .backup sibling directory before it
    is overwritten, naming it after the file plus a timestamp so prior catalog
    states are recoverable. A first-time save has nothing to back up. Only the
    most recent _RETAINED_BACKUPS copies are kept; older ones are pruned."""
    if not target_path.exists():
        return
    backup_dir = target_path.parent / _BACKUP_DIR_NAME
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    # The OS clock can repeat a timestamp across rapid saves; never clobber an
    # existing backup, so add a counter until the name is unique.
    backup_path = backup_dir / f"{target_path.stem}-{timestamp}{target_path.suffix}"
    counter = 1
    while backup_path.exists():
        backup_path = backup_dir / f"{target_path.stem}-{timestamp}-{counter}{target_path.suffix}"
        counter += 1
    shutil.copy2(target_path, backup_path)
    _prune_old_backups(backup_dir, target_path)


def _prune_old_backups(backup_dir: Path, target_path: Path) -> None:
    """Delete all but the newest _RETAINED_BACKUPS backups. The timestamped name
    sorts chronologically, so the oldest are at the front of the sorted list."""
    backups = sorted(backup_dir.glob(f"{target_path.stem}-*{target_path.suffix}"))
    for stale in backups[:-_RETAINED_BACKUPS]:
        stale.unlink(missing_ok=True)


class Catalog(BaseModel):
    library: LibraryData
    entries: list[CatalogEntry]

    def save(self, path: str | Path) -> None:
        target_path = Path(path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        _backup_existing(target_path)
        target_path.write_text(json.dumps(self.model_dump(mode="json"), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> Catalog:
        target_path = Path(path)
        payload = json.loads(target_path.read_text(encoding="utf-8"))
        _reject_catalog_with_removed_metadata(payload)
        return cls.model_validate(payload)
