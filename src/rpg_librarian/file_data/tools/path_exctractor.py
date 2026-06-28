from __future__ import annotations

from pathlib import Path


def _normalize(path: str | Path) -> Path:
    return Path(path).expanduser().resolve(strict=False)


def _relative_parts(file_path: str | Path, containing_folder: str | Path) -> tuple[Path, Path, tuple[str, ...]]:
    """
    Returns:
        file_path: normalized full file path
        root: normalized containing/root folder
        parts: path parts between root and the file name

    Example:
        file_path = C:/rpg/books/dnd5e/rules/phb.pdf
        root = C:/rpg

        parts = ("books", "dnd5e", "rules")
    """
    file_path = _normalize(file_path)
    root = _normalize(containing_folder)

    try:
        relative = file_path.relative_to(root)
    except ValueError as e:
        raise ValueError(f"File path is not inside containing folder: {file_path} is not under {root}") from e

    # Drop the filename; keep only containing directory parts.
    return file_path, root, relative.parent.parts


def _descendant_folder(
    file_path: str | Path,
    containing_folder: str | Path,
    depth: int,
) -> str | None:
    """
    Returns folder at a depth relative to containing_folder.

    depth=1 -> root_folder
    depth=2 -> child_folder
    depth=3 -> grandchild_folder
    depth=4 -> great_grandchild_folder
    """
    _file_path, root, parts = _relative_parts(file_path, containing_folder)

    if len(parts) < depth:
        return None

    return root.joinpath(*parts[:depth]).name


def _ancestor_folder(
    file_path: str | Path,
    containing_folder: str | Path,
    levels_up_from_file: int,
) -> str | None:
    """
    Returns folder relative to the file.

    levels_up_from_file=1 -> parent_folder
    levels_up_from_file=2 -> grandparent_folder
    levels_up_from_file=3 -> great_grandparent_folder

    Does not return folders above the containing_folder.
    """
    file_path, root, _parts = _relative_parts(file_path, containing_folder)

    folder = file_path.parent

    for _ in range(levels_up_from_file - 1):
        folder = folder.parent

    try:
        folder.relative_to(root)
    except ValueError:
        return None

    return folder.name


def root_folder(file_path: str | Path, containing_folder: str | Path) -> str | None:
    return _descendant_folder(file_path, containing_folder, depth=1)


def child_folder(file_path: str | Path, containing_folder: str | Path) -> str | None:
    return _descendant_folder(file_path, containing_folder, depth=2)


def grandchild_folder(file_path: str | Path, containing_folder: str | Path) -> str | None:
    return _descendant_folder(file_path, containing_folder, depth=3)


def great_grandchild_folder(file_path: str | Path, containing_folder: str | Path) -> str | None:
    return _descendant_folder(file_path, containing_folder, depth=4)


def parent_folder(file_path: str | Path, containing_folder: str | Path) -> str | None:
    return _ancestor_folder(file_path, containing_folder, levels_up_from_file=1)


def grandparent_folder(file_path: str | Path, containing_folder: str | Path) -> str | None:
    return _ancestor_folder(file_path, containing_folder, levels_up_from_file=2)


def great_grandparent_folder(file_path: str | Path, containing_folder: str | Path) -> str | None:
    return _ancestor_folder(file_path, containing_folder, levels_up_from_file=3)
