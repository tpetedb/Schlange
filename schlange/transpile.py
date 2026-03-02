"""Token-based transpiler: rewrites Schlange (German) tokens to valid Python.

Uses Python's ``tokenize`` module so that keywords inside strings and comments
are never touched.  Only NAME tokens that match the keyword dictionary are
rewritten.

The ``anfuehrungszeichen`` pre-pass runs *before* tokenization, converting
German quote words into actual quote characters so the tokenizer sees proper
string literals.
"""

from __future__ import annotations

import io
import re
import tokenize
from typing import Iterator

from schlange.keywords import FULL_MAP, QUOTE_MAP, QUOTE_PREFIXES


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


# ---------------------------------------------------------------------------
# Pre-pass: anfuehrungszeichen -> actual quotes
# ---------------------------------------------------------------------------


def _build_quote_pattern() -> re.Pattern[str]:
    """Build a regex that matches quote words with surrounding whitespace.

    Captures three groups:
      (1) optional leading whitespace
      (2) the quote word itself
      (3) optional trailing whitespace

    The replacer decides which whitespace to keep based on open/close position.
    """
    all_words = sorted(
        list(QUOTE_PREFIXES.keys()) + list(QUOTE_MAP.keys()),
        key=len,
        reverse=True,
    )
    word_pattern = "|".join(re.escape(w) for w in all_words)
    return re.compile(r"( ?)" + "(" + word_pattern + ")" + r"( ?)")


_QUOTE_RE = _build_quote_pattern()
_ALL_QUOTES = {**QUOTE_PREFIXES, **QUOTE_MAP}


def _apply_quote_prepass(source: str) -> str:
    """Replace anfuehrungszeichen (and variants) with actual quote characters.

    Handles matched pairs: opening word becomes the opening quote, closing word
    becomes the closing quote.  For prefixed variants like f-anfuehrungszeichen,
    the opening carries the prefix (f") and the closing is just (").

    Boundary whitespace between the quote word and the string content is
    consumed so that ``anfuehrungszeichen Hallo anfuehrungszeichen`` becomes
    ``"Hallo"`` not ``" Hallo "``.

    The space on the *outside* of the quote pair is preserved:
      ``x = anfuehrungszeichen a anfuehrungszeichen + 1``
    becomes ``x = "a" + 1`` (space before " and after " are kept).

    Lines starting with # (comments) are skipped entirely.
    """
    lines = source.split("\n")
    result_lines: list[str] = []

    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("#"):
            result_lines.append(line)
            continue

        open_stack: list[str] = []

        def replacer(match: re.Match[str]) -> str:
            leading = match.group(1)  # space before the word
            word = match.group(2)  # the quote word
            trailing = match.group(3)  # space after the word

            if open_stack:
                # Closing quote: drop leading space (inside string), keep trailing
                return open_stack.pop() + trailing
            else:
                # Opening quote: keep leading space (syntactic), drop trailing
                if word in QUOTE_PREFIXES:
                    prefix_quote = QUOTE_PREFIXES[word]
                    open_stack.append(prefix_quote[-1])
                    return leading + prefix_quote
                else:
                    quote_char = QUOTE_MAP[word]
                    open_stack.append(quote_char)
                    return leading + quote_char

        line = _QUOTE_RE.sub(replacer, line)
        result_lines.append(line)

    return "\n".join(result_lines)


def transpile(source: str) -> str:
    """Transpile a Schlange source string to valid Python.

    Runs the anfuehrungszeichen pre-pass first, then token-based rewriting.

    Args:
        source: The Schlange (.schl.py) source code.

    Returns:
        Valid Python source code.

    Raises:
        tokenize.TokenError: If the source has unterminated strings / brackets.
    """
    source = _apply_quote_prepass(source)
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
