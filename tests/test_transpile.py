"""Tests for the Schlange transpiler.

Validates that token-based rewriting works correctly and that keywords
inside strings and comments remain untouched.
"""

from __future__ import annotations

import pytest

from schlange.transpile import transpile


class TestBasicKeywords:
    """Keywords are rewritten correctly in simple statements."""

    def test_print_hello(self) -> None:
        source = 'verkuendet("Hallo Welt!")'
        result = transpile(source)
        assert 'print("Hallo Welt!")' in result

    def test_def_function(self) -> None:
        source = "defn gruessen():\n    bestehe"
        result = transpile(source)
        assert "def" in result
        assert "pass" in result

    def test_if_else(self) -> None:
        source = "sofern x > 0:\n    bestehe\nsonst:\n    bestehe"
        result = transpile(source)
        assert "if" in result
        assert "else" in result

    def test_elif(self) -> None:
        source = "sofern x > 0:\n    bestehe\nsofernschier x == 0:\n    bestehe\nsonst:\n    bestehe"
        result = transpile(source)
        assert "elif" in result

    def test_for_loop(self) -> None:
        source = "fuerwahr i inwendig bereich(10):\n    bestehe"
        result = transpile(source)
        assert "for" in result
        assert "in" in result
        assert "range" in result

    def test_while_loop(self) -> None:
        source = "solang Wahrlich:\n    brechet"
        result = transpile(source)
        assert "while" in result
        assert "True" in result
        assert "break" in result

    def test_return(self) -> None:
        source = "defn f():\n    gibzurueck 42"
        result = transpile(source)
        assert "return" in result

    def test_continue(self) -> None:
        source = "fuerwahr i inwendig bereich(5):\n    fahrefort"
        result = transpile(source)
        assert "continue" in result

    def test_booleans_and_none(self) -> None:
        source = "a = Wahrlich\nb = Falschlich\nc = Nichts"
        result = transpile(source)
        assert "True" in result
        assert "False" in result
        assert "None" in result

    def test_import(self) -> None:
        source = "importiert os"
        result = transpile(source)
        assert "import os" in result

    def test_import_as(self) -> None:
        source = "importiert json als j"
        result = transpile(source)
        assert "import" in result
        assert "as" in result

    def test_from_import(self) -> None:
        source = "von os importiert path"
        result = transpile(source)
        assert "from" in result
        assert "import" in result

    def test_boolean_operators(self) -> None:
        source = "sofern a und b oder nichten c:\n    bestehe"
        result = transpile(source)
        assert "and" in result
        assert "or" in result
        assert "not" in result

    def test_is_identity(self) -> None:
        source = "sofern x ist Nichts:\n    bestehe"
        result = transpile(source)
        assert "is" in result
        assert "None" in result

    def test_with_statement(self) -> None:
        source = 'mittels oeffne("f.txt") als fh:\n    bestehe'
        result = transpile(source)
        assert "with" in result
        assert "open" in result
        assert "as" in result

    def test_class_definition(self) -> None:
        source = "klasse Tier:\n    bestehe"
        result = transpile(source)
        assert "class" in result
        assert "pass" in result

    def test_assert(self) -> None:
        source = "behauptet x > 0"
        result = transpile(source)
        assert "assert" in result

    def test_delete(self) -> None:
        source = "tilget variabel"
        result = transpile(source)
        assert "del" in result

    def test_lambda(self) -> None:
        source = "f = anonym x: x * 2"
        result = transpile(source)
        assert "lambda" in result

    def test_yield(self) -> None:
        source = "defn gen():\n    ertrag 1"
        result = transpile(source)
        assert "yield" in result


class TestExceptions:
    """Try/except/finally/raise are handled correctly."""

    def test_try_except(self) -> None:
        source = "probiert:\n    bestehe\nausser Exception:\n    bestehe"
        result = transpile(source)
        assert "try" in result
        assert "except" in result

    def test_try_except_as(self) -> None:
        source = "probiert:\n    bestehe\nausser Exception alsfehler e:\n    bestehe"
        result = transpile(source)
        assert "try" in result
        assert "except" in result
        # alsfehler -> as
        assert "as" in result

    def test_finally(self) -> None:
        source = "probiert:\n    bestehe\nendlich:\n    bestehe"
        result = transpile(source)
        assert "finally" in result

    def test_raise(self) -> None:
        source = 'werfet ValueError("Nein!")'
        result = transpile(source)
        assert "raise" in result


class TestStringsAndComments:
    """Keywords inside strings and comments must NOT be rewritten."""

    def test_keyword_in_string(self) -> None:
        source = 'x = "defn ist kein Python keyword"'
        result = transpile(source)
        assert '"defn ist kein Python keyword"' in result

    def test_keyword_in_fstring(self) -> None:
        source = 'verkuendet(f"sofern wir {x} haben")'
        result = transpile(source)
        # The string content should stay, but verkuendet -> print
        assert "print" in result
        assert "sofern" in result  # still inside string

    def test_keyword_in_comment(self) -> None:
        source = "# defn sofern solang -- diese bleiben\nx = 1"
        result = transpile(source)
        assert "# defn sofern solang" in result

    def test_keyword_in_multiline_string(self) -> None:
        source = '"""\ndefn gibzurueck probiert\n"""\nx = 1'
        result = transpile(source)
        assert "defn gibzurueck probiert" in result


class TestBuiltinAliases:
    """Built-in function aliases are rewritten correctly."""

    def test_len(self) -> None:
        source = "laenge([1, 2, 3])"
        result = transpile(source)
        assert "len" in result

    def test_range(self) -> None:
        source = "bereich(10)"
        result = transpile(source)
        assert "range" in result

    def test_enumerate(self) -> None:
        source = "aufzaehlung(liste)"
        result = transpile(source)
        assert "enumerate" in result

    def test_int_float_str(self) -> None:
        source = 'ganzzahl("42")\ngleitkomma("3.14")\nzeichenkette(42)'
        result = transpile(source)
        assert "int" in result
        assert "float" in result
        assert "str" in result

    def test_sorted(self) -> None:
        source = "sortiert([3, 1, 2])"
        result = transpile(source)
        assert "sorted" in result

    def test_type(self) -> None:
        source = "typ(x)"
        result = transpile(source)
        assert "type" in result


class TestExecution:
    """Transpiled code actually executes correctly."""

    def test_hello_world_executes(self, capsys: pytest.CaptureFixture) -> None:
        source = 'verkuendet("Schlange lebt!")'
        python_code = transpile(source)
        exec(python_code)
        captured = capsys.readouterr()
        assert "Schlange lebt!" in captured.out

    def test_function_executes(self) -> None:
        source = "defn verdoppeln(x):\n    gibzurueck x * 2"
        python_code = transpile(source)
        ns: dict = {}
        exec(python_code, ns)
        assert ns["verdoppeln"](21) == 42

    def test_loop_executes(self, capsys: pytest.CaptureFixture) -> None:
        source = "fuerwahr i inwendig bereich(3):\n    verkuendet(i)"
        python_code = transpile(source)
        exec(python_code)
        captured = capsys.readouterr()
        assert "0" in captured.out
        assert "1" in captured.out
        assert "2" in captured.out

    def test_try_except_executes(self, capsys: pytest.CaptureFixture) -> None:
        source = (
            "probiert:\n"
            "    x = 1 / 0\n"
            "ausser ZeroDivisionError alsfehler e:\n"
            '    verkuendet("gefangen")\n'
            "endlich:\n"
            '    verkuendet("fertig")'
        )
        python_code = transpile(source)
        exec(python_code)
        captured = capsys.readouterr()
        assert "gefangen" in captured.out
        assert "fertig" in captured.out

    def test_class_executes(self) -> None:
        source = (
            "klasse Rechner:\n"
            "    defn __init__(self, wert):\n"
            "        self.wert = wert\n"
            "    defn verdoppeln(self):\n"
            "        gibzurueck self.wert * 2"
        )
        python_code = transpile(source)
        ns: dict = {}
        exec(python_code, ns)
        r = ns["Rechner"](21)
        assert r.verdoppeln() == 42

    def test_list_comprehension_executes(self) -> None:
        source = "ergebnis = [x * 2 fuerwahr x inwendig bereich(5) sofern x > 1]"
        python_code = transpile(source)
        ns: dict = {}
        exec(python_code, ns)
        assert ns["ergebnis"] == [4, 6, 8]
