from __future__ import annotations

from .base_command import BaseCommand


class ExtractTextCommand(BaseCommand):
    def name(self) -> str:
        return "extract_text"

    def execute_command(self) -> None: ...
