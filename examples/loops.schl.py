# Schleifen und Bedingungen -- Loops and conditionals in Schlange
# Run: schlange run examples/loops.schl.py

verkuendet("=== Fuerwahr-Schleife (for loop) ===")

fuerwahr i inwendig bereich(10):
    sofern i % 2 == 0:
        verkuendet(f"  {i} ist gerade")
    sofernschier i % 3 == 0:
        verkuendet(f"  {i} ist durch drei teilbar")
    sonst:
        verkuendet(f"  {i} ist ungerade")

verkuendet("\n=== Solang-Schleife (while loop) ===")

zaehler = 5
solang zaehler > 0:
    verkuendet(f"  Countdown: {zaehler}")
    zaehler = zaehler - 1
verkuendet("  Feuer frei!")

verkuendet("\n=== Funktionen ===")

defn begruessung(name, laut=Falschlich):
    sofern laut:
        gibzurueck f"HALLO {name.upper()}!!!"
    gibzurueck f"Hallo {name}"

verkuendet(begruessung("Welt"))
verkuendet(begruessung("Smutsahansi", laut=Wahrlich))

verkuendet("\n=== Listen und Verarbeitung ===")

zahlen = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
gerade = [z fuerwahr z inwendig zahlen sofern z % 2 == 0]
verkuendet(f"  Gerade Zahlen: {gerade}")
verkuendet(f"  Summe: {summe(gerade)}")
verkuendet(f"  Laenge: {laenge(gerade)}")

verkuendet("\n=== Brechet und Fahrefort ===")

fuerwahr i inwendig bereich(20):
    sofern i == 15:
        verkuendet(f"  {i} erreicht -- brechet!")
        brechet
    sofern i % 4 != 0:
        fahrefort
    verkuendet(f"  {i} ist durch 4 teilbar")
