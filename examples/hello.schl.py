# Hallo Welt! -- The simplest Schlange script
# Run: schlange run examples/hello.schl.py

verkuendet("Hallo Welt!")
verkuendet("Willkommen bei Schlange -- Python auf Deutsch!")

# Keywords inside strings are NOT rewritten (this is correct):
verkuendet("The word 'defn' stays as-is inside a string")

# Variables can be whatever you want
name = "Smutsahansi"
verkuendet(f"Gruss an {name}!")
