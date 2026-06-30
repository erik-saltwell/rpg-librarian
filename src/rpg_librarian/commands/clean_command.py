from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from ..catalog.model.media_type import MediaType
from ..catalog.tools.media_type_detector import find_media_type_from_mime_type, find_mime_type
from .base_command import BaseCommand

_files_to_clean: list[str] = [".ds_store"]

_directories_to_clean: list[str] = [".thumbs"]


_text_contents_to_clean: list[str] = [
    "﻿Sorry, there was a problem downloading this file from OneDrive. Please try again."
]


def should_clean(trial_path: Path) -> bool:
    if trial_path.is_dir():
        if trial_path.name in _directories_to_clean:
            return True
        else:
            return False
    else:
        try:
            if trial_path.stat().st_size == 0:
                return True
        except OSError:
            return False
        if trial_path.name in _files_to_clean:
            return True
        else:
            if (
                trial_path.suffix == ".txt"
                and find_media_type_from_mime_type(find_mime_type(trial_path)) == MediaType.text
            ):
                # print(f"checking {trial_path} contents...")
                try:
                    text_contents = trial_path.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    return False
                for text_to_check in _text_contents_to_clean:
                    if text_to_check in text_contents:
                        return True
    return False


@dataclass
class CleanCommand(BaseCommand):
    def name(self) -> str:
        return "clean"

    def execute_command(self) -> None:
        for dirpath, dirnames, filenames in os.walk(self.processing_directory, topdown=True):
            directory = Path(dirpath)

            remaining_dirnames: list[str] = []
            for dirname in dirnames:
                dir_path = directory / dirname
                if should_clean(dir_path):
                    self.logger.report_message(f"Removing directory: {dir_path}")
                    shutil.rmtree(dir_path)
                else:
                    remaining_dirnames.append(dirname)
            dirnames[:] = remaining_dirnames

            for filename in filenames:
                file_path = directory / filename
                if should_clean(file_path):
                    self.logger.report_message(f"Removing file: {file_path}")
                    file_path.unlink()

        self._remove_empty_directories()

    def _remove_empty_directories(self) -> None:
        # Walk bottom-up so emptiness cascades: a directory left holding only
        # now-removed empty subdirectories is itself removed in the same pass.
        for dirpath, _dirnames, _filenames in os.walk(self.processing_directory, topdown=False):
            directory = Path(dirpath)
            if directory == self.processing_directory:
                continue  # never remove the root being cleaned
            try:
                next(directory.iterdir())
            except StopIteration:
                self.logger.report_message(f"Removing empty directory: {directory}")
                directory.rmdir()
            except OSError:
                continue
