"""Tests for the Schlange CLI."""

from __future__ import annotations

import os

from click.testing import CliRunner

from schlange.cli import main


def _example_path(name: str) -> str:
    """Return the path to an example script."""
    return os.path.join(os.path.dirname(__file__), "..", "examples", name)


class TestCLI:
    """CLI commands work end-to-end."""

    def test_version(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "schlange" in result.output.lower()

    def test_emit_hello(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["emit", _example_path("hello.schl.py")])
        assert result.exit_code == 0
        assert "print" in result.output
        assert "Hallo Welt!" in result.output

    def test_run_hello(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["run", _example_path("hello.schl.py")])
        assert result.exit_code == 0
        assert "Hallo Welt!" in result.output

    def test_run_loops(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["run", _example_path("loops.schl.py")])
        assert result.exit_code == 0
        assert "gerade" in result.output

    def test_run_fehler(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["run", _example_path("fehler.schl.py")])
        assert result.exit_code == 0
        assert "Fehler gefangen" in result.output

    def test_woerterbuch(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["woerterbuch"])
        assert result.exit_code == 0
        assert "verkuendet" in result.output
        assert "print" in result.output

    def test_emit_to_file(self, tmp_path) -> None:
        runner = CliRunner()
        out = str(tmp_path / "output.py")
        result = runner.invoke(main, ["emit", _example_path("hello.schl.py"), "-o", out])
        assert result.exit_code == 0
        with open(out) as fh:
            content = fh.read()
        assert "print" in content
