"""Schlange keyword dictionary -- Old German to Python mapping.

This is the canonical source of truth for all Schlange keyword translations.
Only NAME tokens matching these keys will be rewritten during transpilation.
"""

# ---------------------------------------------------------------------------
# Core keyword map: German -> Python
# ---------------------------------------------------------------------------
KEYWORDS: dict[str, str] = {
    # -- Imports & aliases --
    "importiert": "import",
    "von": "from",
    "als": "as",
    # -- Functions / classes --
    "defn": "def",
    "klasse": "class",
    # -- Control flow --
    "sofern": "if",
    "sofernschier": "elif",
    "sonst": "else",
    "solang": "while",
    "fuerwahr": "for",
    "inwendig": "in",
    "gibzurueck": "return",
    "brechet": "break",
    "fahrefort": "continue",
    "bestehe": "pass",
    # -- Boolean operators --
    "und": "and",
    "oder": "or",
    "nichten": "not",
    # -- Membership / identity --
    "ist": "is",
    # -- Context managers --
    "mittels": "with",
    # -- Comprehension / scope --
    "allumfassend": "global",
    "nichtlokal": "nonlocal",
    # -- Assertions --
    "behauptet": "assert",
    # -- Deletion --
    "tilget": "del",
    # -- Async (bonus) --
    "erwarte": "await",
    "gleichlaufend": "async",
    # -- Exceptions --
    "probiert": "try",
    "ausser": "except",
    "endlich": "finally",
    "werfet": "raise",
    "alsfehler": "as",  # context-specific: except X alsfehler e
    # -- Booleans / None --
    "Wahrlich": "True",
    "Falschlich": "False",
    "Nichts": "None",
    # -- Yield --
    "ertrag": "yield",
    # -- Lambda --
    "anonym": "lambda",
}

# ---------------------------------------------------------------------------
# Built-in function aliases: German -> Python
# ---------------------------------------------------------------------------
BUILTINS: dict[str, str] = {
    "verkuendet": "print",
    "laenge": "len",
    "bereich": "range",
    "aufzaehlung": "enumerate",
    "reissverschluss": "zip",
    "zuordnung": "map",
    "sieb": "filter",
    "eingabe": "input",
    "ganzzahl": "int",
    "gleitkomma": "float",
    "zeichenkette": "str",
    "liste": "list",
    "woerterbuch": "dict",
    "menge": "set",
    "tupel": "tuple",
    "sortiert": "sorted",
    "umgekehrt": "reversed",
    "absolut": "abs",
    "summe": "sum",
    "minimum": "min",
    "maximum": "max",
    "beliebig": "any",
    "saemtlich": "all",
    "typ": "type",
    "isinstance_von": "isinstance",
    "oeffne": "open",
    "naechstes": "next",
}

# ---------------------------------------------------------------------------
# Combined map used by the transpiler
# ---------------------------------------------------------------------------
FULL_MAP: dict[str, str] = {**KEYWORDS, **BUILTINS}
