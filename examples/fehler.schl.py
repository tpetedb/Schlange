# Fehlerbehandlung -- Try/Except in Schlange
# Run: schlange run examples/fehler.schl.py

verkuendet("=== Beispiel 1: Division durch Null ===")

probiert:
    ergebnis = 10 / 0
    verkuendet(f"Ergebnis: {ergebnis}")
ausser ZeroDivisionError alsfehler e:
    verkuendet(f"  Fehler gefangen: {e}")
endlich:
    verkuendet("  Endlich-Block ausgefuehrt (cleanup)")

verkuendet("\n=== Beispiel 2: Eigene Fehlerklasse ===")

klasse SchlangenFehler(Exception):
    """Ein spezieller Schlange-Fehler."""
    bestehe

defn pruefe_alter(alter):
    sofern nichten isinstance_von(alter, ganzzahl):
        werfet SchlangenFehler(f"Alter muss eine Ganzzahl sein, nicht {typ(alter).__name__}")
    sofern alter < 0:
        werfet SchlangenFehler(f"Alter kann nicht negativ sein: {alter}")
    sofern alter > 150:
        werfet SchlangenFehler(f"Unplausibles Alter: {alter}")
    gibzurueck f"Alter {alter} ist gueltig"

# Teste verschiedene Alter
fuerwahr test_alter inwendig [25, -5, "zwanzig", 200, 42]:
    probiert:
        ergebnis = pruefe_alter(test_alter)
        verkuendet(f"  {test_alter}: {ergebnis}")
    ausser SchlangenFehler alsfehler e:
        verkuendet(f"  {test_alter}: FEHLER -- {e}")

verkuendet("\n=== Beispiel 3: Verschachtelte Ausnahmen ===")

defn riskante_operation(wert):
    probiert:
        probiert:
            zahl = ganzzahl(wert)
            ergebnis = 100 / zahl
            gibzurueck ergebnis
        ausser ValueError:
            verkuendet(f"  '{wert}' ist keine gueltige Zahl")
            gibzurueck Nichts
    ausser ZeroDivisionError:
        verkuendet(f"  Division durch Null mit '{wert}'")
        gibzurueck Nichts

fuerwahr w inwendig ["10", "0", "abc", "5"]:
    ergebnis = riskante_operation(w)
    sofern ergebnis ist nichten Nichts:
        verkuendet(f"  {w} -> {ergebnis}")
