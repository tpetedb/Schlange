"""Token-based transpiler: rewrites Schlange (German) tokens to valid Python.

Uses Python's ``tokenize`` module so that keywords inside strings and comments
are never touched.  Only NAME tokens that match the keyword dictionary are
rewritten.
"""

from __future__ import annotations

import io
import tokenize
from typing import Iterator

from schlange.keywords import FULL_MAP


def _rewrite_tokens(source: str) -> str:
    """Rewrite German keyword tokens in *source* to their Python equivalents.

    The function operates on the token stream produced by ``tokenize.generate_tokens``.
    Only tokens of type ``NAME`` whose string value appears in ``FULL_MAP`` are
    replaced.  Everything else (strings, comments, operators, whitespace) passes
    through unchanged.

    Returns the fully rewritten source code as a string.
    """
    readline = io.StringIO(source).readline
    tokens: list[tokenize.TokenInfo] = list(tokenize.generate_tokens(readline))
    result_parts: list[str] = []

    # We rebuild the source by walking character positions.
    # tokenize gives us (row, col) positions for every token.
    prev_row = 1
    prev_col = 0

    for tok in tokens:
        tok_type, tok_string, tok_start, tok_end, _ = tok
        start_row, start_col = tok_start

        # Preserve whitespace / newlines between tokens
        if start_row > prev_row:
            # Add newlines
            result_parts.append("\n" * (start_row - prev_row))
            # Indent to start_col
            result_parts.append(" " * start_col)
        elif start_col > prev_col:
            # Same row, fill gap with spaces
            result_parts.append(" " * (start_col - prev_col))

        # Rewrite NAME tokens that are in our map
        if tok_type == tokenize.NAME and tok_string in FULL_MAP:
            result_parts.append(FULL_MAP[tok_string])
        elif tok_type == tokenize.ENDMARKER:
            pass  # skip end marker
        else:
            result_parts.append(tok_string)

        prev_row, prev_col = tok_end

    return "".join(result_parts)


def transpile(source: str) -> str:
    """Transpile a Schlange source string to valid Python.

    Args:
        source: The Schlange (.schl.py) source code.

    Returns:
        Valid Python source code.

    Raises:
        tokenize.TokenError: If the source has unterminated strings / brackets.
    """
    return _rewrite_tokens(source)


def transpile_file(path: str) -> str:
    """Read a file, transpile it, and return the Python source.

    Args:
        path: Path to a ``.schl.py`` file.

    Returns:
        The transpiled Python source code string.
    """
    with open(path, encoding="utf-8") as fh:
        source = fh.read()
    return transpile(source)
