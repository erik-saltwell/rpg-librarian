from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import KW_ONLY, dataclass
from pathlib import Path
from time import perf_counter

from ..utils import LoggingProtocol, Tracer, duration_from_perfcounters
from .command_protocol import CommandProtocol, CommandResult


@dataclass
class BaseCommand(ABC, CommandProtocol):
    processing_directory: Path
    _: KW_ONLY
    logger: LoggingProtocol
    tracer: Tracer

    def __post_init__(self) -> None:
        if not self.processing_directory.is_dir():
            raise NotADirectoryError(f"path must be a directory: {self.processing_directory}")

    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def execute_command(self) -> None: ...

    def execute(self) -> CommandResult:
        start_counter = perf_counter()
        error: Exception | None = None
        try:
            self.execute_command()
        except Exception as caught_error:
            error = caught_error

        end_counter = perf_counter()
        duration = duration_from_perfcounters(start_counter, end_counter)
        self.tracer.add_context("cmd_duration", duration)

        if error is not None:
            self.tracer.log_exception(error, self.name())
            self.logger.report_exception(self.name(), error)
            result = CommandResult.FAILURE
        else:
            self.tracer.log(self.name())
            result = CommandResult.SUCCESS

        self.logger.report_message(f"Finished {self.name()} in {duration} seconds")
        return result
