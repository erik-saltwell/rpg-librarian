from __future__ import annotations

from pathlib import Path

from ...catalog.model.library_data import LibraryData
from ..model.file_data import FileData
from ..tools import path_exctractor as path_extractor
from ..tools.mime_detector import detect_mime_type
from ..tools.sha_computer import generate_hash


def generate_file_data(
    file_path: Path,
    library: LibraryData,
) -> FileData:
    containing_folder: Path = library.root_folder
    return FileData(
        sha256=generate_hash(file_path),
        filepath=file_path,
        filename=file_path.name,
        extension=file_path.suffix,
        size_in_bytes=file_path.stat().st_size,
        mime_type=detect_mime_type(file_path),
        root_folder=path_extractor.root_folder(file_path, containing_folder),
        root_child_folder=path_extractor.child_folder(file_path, containing_folder),
        root_grandchild_folder=path_extractor.grandchild_folder(file_path, containing_folder),
        root_greatgrandchild_folder=path_extractor.great_grandchild_folder(file_path, containing_folder),
        parent_folder=path_extractor.parent_folder(file_path, containing_folder),
        grandparent_folder=path_extractor.grandparent_folder(file_path, containing_folder),
    )
