from __future__ import annotations

from dataclasses import dataclass

from .base_command import BaseCommand


@dataclass
class TestCommand(BaseCommand):
    def name(self) -> str:
        return "Test Command"

    def execute_command(self) -> None:
        self.logger.report_message("[green]Hello world.[/green]")
        return
