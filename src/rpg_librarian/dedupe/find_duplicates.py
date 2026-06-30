from __future__ import annotations

from ..catalog.model.audio_metadata import AudioMetadata
from ..catalog.model.catalog import Catalog
from ..catalog.model.catalog_entry import CatalogEntry
from ..catalog.model.image_metadata import ImageMetadata
from ..catalog.model.media_type import MediaType
from .duplicate_data import DuplicateData


def find_duplicates(
    catalog: Catalog,
    use_perceptual_hash: bool,
    only_find_duplicates_with_shared_name: bool = False,
    only_find_duplicates_with_master_in_drivethrurpg: bool = False,
) -> dict[str, DuplicateData]:
    """Return duplicate groups, keyed by the ID of each group's master entry.

    Entries are joined when they have the same media type and their file hashes
    match.  When ``use_perceptual_hash`` is true, entries are also joined when
    their perceptual hashes (images) or acoustic fingerprints (audio) match;
    when false, only the file sha256 is considered.  Joining is transitive so an
    entry can belong to only one duplicate group.

    The master of each group is chosen by narrowing the members through these
    rules in order, each applied to whatever candidates the previous rule left:

    1. If any member lives inside a DriveThruRPG folder, drop every member that
       does not.
    2. If exactly two candidates remain and they are a ``.txt``/``.md`` pair
       sharing the same stem in the same directory, keep only the ``.md`` one.
    3. If more than one candidate remains, keep only those nested in the deepest
       folder (the longest path).
    4. If more than one candidate still remains, pick one arbitrarily (in an
       implementation-dependent way; currently the first in catalog order).

    When ``only_find_duplicates_with_shared_name`` is true, only groups whose
    master and duplicates all share a single filename are returned.  When
    ``only_find_duplicates_with_master_in_drivethrurpg`` is true, only groups
    whose master lives somewhere inside a DriveThruRPG folder are returned.
    Both default to false, leaving the unfiltered behavior unchanged.
    """
    entries = catalog.entries
    parents = list(range(len(entries)))

    def find(index: int) -> int:
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            parents[right_root] = left_root

    first_entry_by_hash: dict[tuple[MediaType, str, str], int] = {}
    for index, entry in enumerate(entries):
        if entry.media_type is None:
            continue

        hashes: list[tuple[str, str]] = []
        if entry.file_data is not None and entry.file_data.sha256:
            hashes.append(("sha256", entry.file_data.sha256))

        if use_perceptual_hash:
            perceptual_hash = _perceptual_hash(entry)
            if perceptual_hash:
                hashes.append(("perceptual", perceptual_hash))

        for hash_kind, hash_value in hashes:
            key = (entry.media_type, hash_kind, hash_value)
            matching_index = first_entry_by_hash.setdefault(key, index)
            union(index, matching_index)

    members_by_root: dict[int, list[CatalogEntry]] = {}
    for index, entry in enumerate(entries):
        members_by_root.setdefault(find(index), []).append(entry)

    result: dict[str, DuplicateData] = {}
    for members in members_by_root.values():
        if len(members) < 2:
            continue

        master = _select_master(members)
        if only_find_duplicates_with_master_in_drivethrurpg and not is_in_drivethrurpg(master):
            continue

        group = DuplicateData(
            master=master,
            duplicates=[entry for entry in members if entry is not master],
        )
        if only_find_duplicates_with_shared_name and not all_share_filename(group):
            continue

        result[master.id] = group

    return result


def _select_master(members: list[CatalogEntry]) -> CatalogEntry:
    """Pick the master of a duplicate group; see ``find_duplicates`` for the rules."""
    candidates = members

    # Rule 1: prefer DriveThruRPG copies whenever the group has any.
    in_drivethrurpg = [entry for entry in candidates if is_in_drivethrurpg(entry)]
    if in_drivethrurpg:
        candidates = in_drivethrurpg

    # Rule 2: a co-located .txt/.md pair of the same name collapses to the .md copy.
    if len(candidates) == 2 and _is_txt_md_pair(candidates):
        candidates = [entry for entry in candidates if _suffix(entry) == ".md"]

    # Rule 3: keep only the most deeply nested copies.
    if len(candidates) > 1:
        deepest = max(_nesting_depth(entry) for entry in candidates)
        candidates = [entry for entry in candidates if _nesting_depth(entry) == deepest]

    # Rule 4: break any remaining tie arbitrarily (catalog order).
    return candidates[0]


def _is_txt_md_pair(candidates: list[CatalogEntry]) -> bool:
    """Whether the two candidates are a same-name .txt/.md pair in the same directory."""
    first, second = candidates
    if first.file_data is None or second.file_data is None:
        return False
    first_path = first.file_data.filepath
    second_path = second.file_data.filepath
    return (
        {first_path.suffix.lower(), second_path.suffix.lower()} == {".txt", ".md"}
        and first_path.stem.casefold() == second_path.stem.casefold()
        and first_path.parent == second_path.parent
    )


def _suffix(entry: CatalogEntry) -> str:
    return entry.file_data.filepath.suffix.lower() if entry.file_data is not None else ""


def _nesting_depth(entry: CatalogEntry) -> int:
    """How deeply the entry's file is nested; used to pick the deepest-living master."""
    if entry.file_data is None:
        return -1
    return len(entry.file_data.filepath.parts)


def all_share_filename(group: DuplicateData) -> bool:
    """Whether every file in the group shares one filename (folder ignored, case-insensitive)."""
    members = [group.master, *group.duplicates]
    filenames = {entry.file_data.filename.casefold() for entry in members if entry.file_data is not None}
    return len(filenames) == 1


def _perceptual_hash(entry: CatalogEntry) -> str | None:
    metadata = entry.media_type_metadata
    if entry.media_type == MediaType.image and isinstance(metadata, ImageMetadata):
        return _usable_perceptual_hash(metadata.hash)
    if entry.media_type == MediaType.audio and isinstance(metadata, AudioMetadata):
        return _usable_perceptual_hash(metadata.acoustic_fingerprint)
    return None


def _usable_perceptual_hash(value: str | None) -> str | None:
    """Return the perceptual hash, or None when it carries no signal.

    An all-zero hash collapses unrelated content into one group (e.g. mostly
    white document images), so we drop it and let the entry fall back to
    matching on its file sha256 instead.
    """
    if not value or set(value) == {"0"}:
        return None
    return value


def is_in_drivethrurpg(entry: CatalogEntry) -> bool:
    if entry.file_data is None:
        return False
    return any(part.casefold() == "drivethrurpg" for part in entry.file_data.filepath.parent.parts)
