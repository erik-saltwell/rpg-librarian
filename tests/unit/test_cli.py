from __future__ import annotations

import importlib.metadata as im

from typer.testing import CliRunner

from rpg_librarian.console.main import app

runner = CliRunner()


def _dist_name() -> str:
    """
    Best-effort: map the import package name to its installed distribution name.
    This avoids hardcoding kebab-case vs snake_case.
    """
    mapping = im.packages_distributions()
    dists = mapping.get("rpg_librarian") or []
    return dists[0] if dists else "rpg-librarian"


def test_help() -> None:
    result = runner.invoke(app, ["--help"], color=False)
    assert result.exit_code == 0
    assert "Usage" in result.output
    assert "report-duplicates" in result.output
    assert "delete-duplicates" in result.output
    assert "extract-errors" in result.output
    assert "prune-catalog" in result.output


def test_version() -> None:
    dist = _dist_name()
    expected_version = im.version(dist)

    result = runner.invoke(app, ["--version"], color=False)
    assert result.exit_code == 0

    out = result.output.strip()
    assert expected_version in out
    # Optional sanity check: output is typically "name version"
    assert out.endswith(expected_version)
