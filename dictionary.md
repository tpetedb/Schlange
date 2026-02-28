# Schlange Woerterbuch (Dictionary) v0.1

The canonical keyword mapping for the Schlange preprocessor.

## Schluesselwoerter (Keywords)

| Schlange | Python | Category | Example |
|---|---|---|---|
| `importiert` | `import` | Imports | `importiert os` |
| `von` | `from` | Imports | `von os importiert pfad` |
| `als` | `as` | Imports / Aliases | `importiert json als j` |
| `defn` | `def` | Functions | `defn gruessen(name):` |
| `klasse` | `class` | Classes | `klasse Tier:` |
| `sofern` | `if` | Control flow | `sofern x > 0:` |
| `sofernschier` | `elif` | Control flow | `sofernschier x == 0:` |
| `sonst` | `else` | Control flow | `sonst:` |
| `solang` | `while` | Loops | `solang Wahrlich:` |
| `fuerwahr` | `for` | Loops | `fuerwahr i inwendig bereich(10):` |
| `inwendig` | `in` | Membership | `sofern x inwendig liste:` |
| `gibzurueck` | `return` | Functions | `gibzurueck ergebnis` |
| `brechet` | `break` | Loops | `brechet` |
| `fahrefort` | `continue` | Loops | `fahrefort` |
| `bestehe` | `pass` | Control flow | `bestehe` |
| `und` | `and` | Boolean ops | `sofern a und b:` |
| `oder` | `or` | Boolean ops | `sofern a oder b:` |
| `nichten` | `not` | Boolean ops | `sofern nichten fertig:` |
| `ist` | `is` | Identity | `sofern x ist Nichts:` |
| `mittels` | `with` | Context mgr | `mittels oeffne("f") als fh:` |
| `allumfassend` | `global` | Scope | `allumfassend zaehler` |
| `nichtlokal` | `nonlocal` | Scope | `nichtlokal x` |
| `behauptet` | `assert` | Assertions | `behauptet x > 0` |
| `tilget` | `del` | Deletion | `tilget variabel` |
| `erwarte` | `await` | Async | `erwarte aufgabe()` |
| `gleichlaufend` | `async` | Async | `gleichlaufend defn laden():` |
| `probiert` | `try` | Exceptions | `probiert:` |
| `ausser` | `except` | Exceptions | `ausser ValueError:` |
| `endlich` | `finally` | Exceptions | `endlich:` |
| `werfet` | `raise` | Exceptions | `werfet ValueError("Nein!")` |
| `alsfehler` | `as` | Exceptions | `ausser Exception alsfehler e:` |
| `Wahrlich` | `True` | Booleans | `fertig = Wahrlich` |
| `Falschlich` | `False` | Booleans | `aktiv = Falschlich` |
| `Nichts` | `None` | None | `gibzurueck Nichts` |
| `ertrag` | `yield` | Generators | `ertrag wert` |
| `anonym` | `lambda` | Lambda | `anonym x: x * 2` |

## Eingebaute Funktionen (Built-in Aliases)

| Schlange | Python | Example |
|---|---|---|
| `verkuendet` | `print` | `verkuendet("Hallo Welt!")` |
| `laenge` | `len` | `laenge(liste)` |
| `bereich` | `range` | `bereich(10)` |
| `aufzaehlung` | `enumerate` | `aufzaehlung(sachen)` |
| `reissverschluss` | `zip` | `reissverschluss(a, b)` |
| `zuordnung` | `map` | `zuordnung(fn, liste)` |
| `sieb` | `filter` | `sieb(fn, liste)` |
| `eingabe` | `input` | `eingabe("Name? ")` |
| `ganzzahl` | `int` | `ganzzahl("42")` |
| `gleitkomma` | `float` | `gleitkomma("3.14")` |
| `zeichenkette` | `str` | `zeichenkette(42)` |
| `liste` | `list` | `liste(bereich(5))` |
| `woerterbuch` | `dict` | `woerterbuch(a=1)` |
| `menge` | `set` | `menge([1,2,3])` |
| `tupel` | `tuple` | `tupel([1,2])` |
| `sortiert` | `sorted` | `sortiert(zahlen)` |
| `umgekehrt` | `reversed` | `umgekehrt(liste)` |
| `absolut` | `abs` | `absolut(-5)` |
| `summe` | `sum` | `summe([1,2,3])` |
| `minimum` | `min` | `minimum(a, b)` |
| `maximum` | `max` | `maximum(a, b)` |
| `beliebig` | `any` | `beliebig(flags)` |
| `saemtlich` | `all` | `saemtlich(flags)` |
| `typ` | `type` | `typ(objekt)` |
| `isinstance_von` | `isinstance` | `isinstance_von(x, ganzzahl)` |
| `oeffne` | `open` | `oeffne("datei.txt")` |
| `naechstes` | `next` | `naechstes(iterator)` |

## Design Principles

1. **Token-based only** -- keywords inside strings and comments are never rewritten
2. **Stable core** -- this dictionary is intentionally limited; don't translate everything
3. **Old German flavor** -- deliberately archaic word choices for comedic effect
4. **One canonical source** -- the Python dict in `schlange/keywords.py` is the runtime truth; this doc mirrors it

## Example: Hello World

```python
# hallo.schl.py
verkuendet("Hallo Welt!")
```

## Example: Loops and Conditionals

```python
# schleifen.schl.py
fuerwahr i inwendig bereich(5):
    sofern i % 2 == 0:
        verkuendet(f"{i} ist gerade")
    sonst:
        verkuendet(f"{i} ist ungerade")
```

## Example: Try/Except

```python
# fehler.schl.py
probiert:
    ergebnis = 10 / 0
ausser ZeroDivisionError alsfehler e:
    verkuendet(f"Fehler gefangen: {e}")
endlich:
    verkuendet("Aufgeraeumt!")
```
