from __future__ import annotations

from pathlib import Path

import pytest

from rpg_librarian.commands.base_command import BaseCommand
from rpg_librarian.commands.command_protocol import CommandResult
from rpg_librarian.utils import NullLogger, Tracer


class _CapturingLogger(NullLogger):
    def __init__(self) -> None:
        self.messages: list[str] = []
        self.exceptions: list[tuple[str, BaseException]] = []

    def report_message(self, message: str) -> None:
        self.messages.append(message)

    def report_exception(self, context: str, exc: BaseException) -> None:
        self.exceptions.append((context, exc))


class _CapturingTracer(Tracer):
    def __init__(self) -> None:
        self.context: dict[str, object] = {}

    def add_context(self, name: str, value: object) -> None:
        self.context[name] = value

    def log(self, event_name: str) -> None:
        return

    def log_exception(self, exception: BaseException, event_name: str | None = None) -> None:
        return


class _Command(BaseCommand):
    should_fail: bool = False

    def name(self) -> str:
        return "sample-command"

    def execute_command(self) -> None:
        if self.should_fail:
            raise RuntimeError("boom")


@pytest.mark.parametrize(
    ("should_fail", "expected_result"),
    [(False, CommandResult.SUCCESS), (True, CommandResult.FAILURE)],
)
def test_execute_reports_duration_for_every_outcome(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    should_fail: bool,
    expected_result: CommandResult,
) -> None:
    counters = iter([10.0, 12.34567])
    monkeypatch.setattr("rpg_librarian.commands.base_command.perf_counter", lambda: next(counters))
    logger = _CapturingLogger()
    tracer = _CapturingTracer()
    command = _Command(tmp_path, logger=logger, tracer=tracer)
    command.should_fail = should_fail

    result = command.execute()

    assert result == expected_result
    assert logger.messages == ["Finished sample-command in 2.3457 seconds"]
    assert len(logger.exceptions) == int(should_fail)
    assert tracer.context["cmd_duration"] == "2.3457"
