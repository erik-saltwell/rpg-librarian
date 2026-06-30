from __future__ import annotations

from pathlib import Path

from rpg_librarian.catalog.model.catalog import Catalog
from rpg_librarian.catalog.model.catalog_entry import CatalogEntry
from rpg_librarian.catalog.model.library_data import LibraryData
from rpg_librarian.catalog.model.media_type import MediaType
from rpg_librarian.dedupe.find_duplicates import find_duplicates
from rpg_librarian.file_data.model.file_data import FileData


def _entry(
    entry_id: str,
    path: Path,
    media_type: MediaType,
    sha256: str,
) -> CatalogEntry:
    return CatalogEntry(
        id=entry_id,
        media_type=media_type,
        file_data=FileData(
            sha256=sha256,
            filepath=path,
            filename=path.name,
            extension=path.suffix,
            size_in_bytes=1,
            mime_type="application/octet-stream",
            root_folder=None,
            root_child_folder=None,
            root_grandchild_folder=None,
            root_greatgrandchild_folder=None,
            parent_folder=None,
            grandparent_folder=None,
        ),
    )


def _catalog(tmp_path: Path, entries: list[CatalogEntry]) -> Catalog:
    return Catalog(library=LibraryData(root_folder=tmp_path), entries=entries)


def test_requires_matching_media_type(tmp_path: Path) -> None:
    image = _entry("image", tmp_path / "a.png", MediaType.image, "same")
    audio = _entry("audio", tmp_path / "a.mp3", MediaType.audio, "same")

    assert find_duplicates(_catalog(tmp_path, [image, audio])) == {}


def test_matches_same_sha256(tmp_path: Path) -> None:
    master = _entry("master", tmp_path / "a.png", MediaType.image, "same-sha")
    copy = _entry("copy", tmp_path / "b.png", MediaType.image, "same-sha")

    groups = find_duplicates(_catalog(tmp_path, [master, copy]))

    assert list(groups) == ["master"]
    assert groups["master"].master is master
    assert groups["master"].duplicates == [copy]


def test_differing_sha256_does_not_match(tmp_path: Path) -> None:
    first = _entry("first", tmp_path / "a.png", MediaType.image, "sha-a")
    second = _entry("second", tmp_path / "b.png", MediaType.image, "sha-b")

    assert find_duplicates(_catalog(tmp_path, [first, second])) == {}


def test_prefers_master_inside_drivethrurpg_folder(tmp_path: Path) -> None:
    outside = _entry("outside", tmp_path / "other" / "book.pdf", MediaType.pdf, "same")
    inside = _entry(
        "inside",
        tmp_path / "DriveThruRPG" / "publisher" / "book.pdf",
        MediaType.pdf,
        "same",
    )

    groups = find_duplicates(_catalog(tmp_path, [outside, inside]))

    assert list(groups) == ["inside"]
    assert groups["inside"].master is inside
    assert groups["inside"].duplicates == [outside]


def test_master_is_deepest_when_none_in_drivethrurpg(tmp_path: Path) -> None:
    # No member lives under DriveThruRPG, so the most deeply nested file wins.
    shallow = _entry("shallow", tmp_path / "book.pdf", MediaType.pdf, "same")
    deep = _entry("deep", tmp_path / "a" / "b" / "c" / "book.pdf", MediaType.pdf, "same")

    groups = find_duplicates(_catalog(tmp_path, [shallow, deep]))

    assert list(groups) == ["deep"]
    assert groups["deep"].master is deep
    assert groups["deep"].duplicates == [shallow]


def test_drivethrurpg_master_wins_over_deeper_file(tmp_path: Path) -> None:
    # A deeper non-DriveThruRPG file must not beat a DriveThruRPG member.
    deep_outside = _entry("deep", tmp_path / "a" / "b" / "c" / "d" / "book.pdf", MediaType.pdf, "same")
    inside = _entry("inside", tmp_path / "DriveThruRPG" / "book.pdf", MediaType.pdf, "same")

    groups = find_duplicates(_catalog(tmp_path, [deep_outside, inside]))

    assert list(groups) == ["inside"]
    assert groups["inside"].master is inside


def test_equal_depth_breaks_tie_by_catalog_order(tmp_path: Path) -> None:
    first = _entry("first", tmp_path / "x" / "book.pdf", MediaType.pdf, "same")
    second = _entry("second", tmp_path / "y" / "book.pdf", MediaType.pdf, "same")

    groups = find_duplicates(_catalog(tmp_path, [first, second]))

    assert list(groups) == ["first"]


def test_txt_md_pair_collapses_to_md(tmp_path: Path) -> None:
    # Same-name .txt/.md pair in one directory: the .md copy becomes master.
    txt = _entry("txt", tmp_path / "notes" / "dressing.txt", MediaType.text, "same")
    md = _entry("md", tmp_path / "notes" / "dressing.md", MediaType.text, "same")

    groups = find_duplicates(_catalog(tmp_path, [txt, md]))

    assert list(groups) == ["md"]
    assert groups["md"].master is md
    assert groups["md"].duplicates == [txt]


def test_txt_md_pair_in_different_directories_falls_through_to_depth(tmp_path: Path) -> None:
    # Not co-located, so the .md rule does not apply; the deepest file wins.
    md = _entry("md", tmp_path / "dressing.md", MediaType.text, "same")
    txt = _entry("txt", tmp_path / "a" / "b" / "dressing.txt", MediaType.text, "same")

    groups = find_duplicates(_catalog(tmp_path, [md, txt]))

    assert list(groups) == ["txt"]
    assert groups["txt"].master is txt


def test_only_shared_name_keeps_only_matching_groups(tmp_path: Path) -> None:
    # Group "shared": every file is book.pdf. Group "renamed": names differ.
    shared_master = _entry("shared", tmp_path / "a" / "book.pdf", MediaType.pdf, "shared-sha")
    shared_copy = _entry("shared-copy", tmp_path / "b" / "book.pdf", MediaType.pdf, "shared-sha")
    renamed_master = _entry("renamed", tmp_path / "c" / "guide.pdf", MediaType.pdf, "renamed-sha")
    renamed_copy = _entry("renamed-copy", tmp_path / "d" / "guide_v2.pdf", MediaType.pdf, "renamed-sha")
    catalog = _catalog(tmp_path, [shared_master, shared_copy, renamed_master, renamed_copy])

    # Default: both groups are returned.
    assert set(find_duplicates(catalog)) == {"shared", "renamed"}

    # Filtered: only the shared-name group survives.
    filtered = find_duplicates(catalog, only_find_duplicates_with_shared_name=True)
    assert list(filtered) == ["shared"]
    assert filtered["shared"].duplicates == [shared_copy]


def test_shared_name_is_case_insensitive(tmp_path: Path) -> None:
    master = _entry("master", tmp_path / "a" / "Book.PDF", MediaType.pdf, "same")
    copy = _entry("copy", tmp_path / "b" / "book.pdf", MediaType.pdf, "same")

    filtered = find_duplicates(
        _catalog(tmp_path, [master, copy]),
        only_find_duplicates_with_shared_name=True,
    )

    assert list(filtered) == ["master"]


def test_only_master_in_drivethrurpg_keeps_only_matching_groups(tmp_path: Path) -> None:
    # Group with a DriveThruRPG master.
    dtrpg_master = _entry("dtrpg", tmp_path / "DriveThruRPG" / "pub" / "book.pdf", MediaType.pdf, "dt-sha")
    dtrpg_copy = _entry("dtrpg-copy", tmp_path / "loose" / "book.pdf", MediaType.pdf, "dt-sha")
    # Group with no DriveThruRPG member at all -> master stays outside.
    outside_master = _entry("outside", tmp_path / "x" / "guide.pdf", MediaType.pdf, "out-sha")
    outside_copy = _entry("outside-copy", tmp_path / "y" / "guide.pdf", MediaType.pdf, "out-sha")
    catalog = _catalog(tmp_path, [dtrpg_master, dtrpg_copy, outside_master, outside_copy])

    # Default: both groups are returned.
    assert set(find_duplicates(catalog)) == {"dtrpg", "outside"}

    # Filtered: only the group whose master is in DriveThruRPG survives.
    filtered = find_duplicates(catalog, only_find_duplicates_with_master_in_drivethrurpg=True)
    assert list(filtered) == ["dtrpg"]
    assert filtered["dtrpg"].duplicates == [dtrpg_copy]


def test_both_filters_combine(tmp_path: Path) -> None:
    # Passes both filters: DriveThruRPG master and a shared filename.
    keep_master = _entry("keep", tmp_path / "DriveThruRPG" / "p" / "book.pdf", MediaType.pdf, "keep-sha")
    keep_copy = _entry("keep-copy", tmp_path / "loose" / "book.pdf", MediaType.pdf, "keep-sha")
    # DriveThruRPG master but the names differ -> fails the shared-name filter.
    drop_master = _entry("drop", tmp_path / "DriveThruRPG" / "p" / "atlas.pdf", MediaType.pdf, "drop-sha")
    drop_copy = _entry("drop-copy", tmp_path / "loose" / "atlas_v2.pdf", MediaType.pdf, "drop-sha")
    catalog = _catalog(tmp_path, [keep_master, keep_copy, drop_master, drop_copy])

    filtered = find_duplicates(
        catalog,
        only_find_duplicates_with_shared_name=True,
        only_find_duplicates_with_master_in_drivethrurpg=True,
    )

    assert list(filtered) == ["keep"]
