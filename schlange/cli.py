"""Schlange CLI -- run or transpile Germanized Python scripts.

Usage:
    schlange run   examples/hello.schl.py
    schlange emit  examples/hello.schl.py
    schlange repl
"""

from __future__ import annotations

import os
import sys
import tempfile
import textwrap
import traceback

import click

from schlange import __version__
from schlange.transpile import transpile, transpile_file


@click.group()
@click.version_option(version=__version__, prog_name="schlange")
def main() -> None:
    """Schlange -- write Python in Old German, run it for real."""


@main.command()
@click.argument("script", type=click.Path(exists=True))
@click.argument("args", nargs=-1)
def run(script: str, args: tuple[str, ...]) -> None:
    """Transpile and execute a .schl.py script."""
    python_source = transpile_file(script)

    # Write to a temp file so tracebacks show readable paths
    fd, tmp_path = tempfile.mkstemp(suffix=".py", prefix="schlange_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(python_source)

        # Patch sys.argv so the script sees its own args
        original_argv = sys.argv[:]
        sys.argv = [script] + list(args)

        # Execute
        code = compile(python_source, script, "exec")
        globs: dict = {"__name__": "__main__", "__file__": script}
        try:
            exec(code, globs)
        except SystemExit:
            raise
        except Exception:
            traceback.print_exc()
            sys.exit(1)
        finally:
            sys.argv = original_argv
    finally:
        os.unlink(tmp_path)


@main.command()
@click.argument("script", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), default=None, help="Write transpiled Python to file instead of stdout.")
def emit(script: str, output: str | None) -> None:
    """Output the transpiled Python source (for debugging)."""
    python_source = transpile_file(script)
    if output:
        with open(output, "w", encoding="utf-8") as fh:
            fh.write(python_source)
        click.echo(f"Transpiled output written to {output}")
    else:
        click.echo(python_source)


@main.command()
def repl() -> None:
    """Start an interactive Schlange REPL (experimental)."""
    click.echo(f"Schlange REPL v{__version__} -- type 'ausgang' to exit")
    click.echo("Tip: verkuendet('Hallo Welt!')")
    while True:
        try:
            line = input("schlange>>> ")
        except (EOFError, KeyboardInterrupt):
            click.echo("\nAuf Wiedersehen!")
            break
        if line.strip() in ("ausgang", "exit", "quit"):
            click.echo("Auf Wiedersehen!")
            break
        if not line.strip():
            continue
        try:
            python_line = transpile(line)
            # Try eval first (expressions), fall back to exec (statements)
            try:
                result = eval(python_line)
                if result is not None:
                    print(repr(result))
            except SyntaxError:
                exec(python_line)
        except Exception as exc:
            click.echo(f"Fehler: {exc}", err=True)


@main.command()
def woerterbuch() -> None:
    """Print the full Schlange keyword dictionary."""
    from schlange.keywords import KEYWORDS, BUILTINS

    click.echo("=== Schluesselwoerter (Keywords) ===\n")
    for de, py in sorted(KEYWORDS.items()):
        click.echo(f"  {de:20s} -> {py}")

    click.echo("\n=== Eingebaute Funktionen (Builtins) ===\n")
    for de, py in sorted(BUILTINS.items()):
        click.echo(f"  {de:20s} -> {py}")


if __name__ == "__main__":
    main()
