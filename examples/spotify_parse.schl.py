# Spotify Export Parser -- geschrieben in Schlange!
# Run: schlange run examples/spotify_parse.schl.py --input my.json --out out/
#
# Parses your Spotify listening history export and ranks tracks.

importiert sys
importiert os

# Schlange uses standard Python imports -- the module names stay as-is
von schlange.spotify.parser importiert load_export, rank_tracks, export_csv, export_playlist_seed

defn hauptprogramm():
    """Parse Spotify export and generate rankings."""

    # Simple arg parsing (no click dependency in the example itself)
    args = sys.argv[1:]
    eingabe_pfad = Nichts
    ausgabe_ordner = "out"
    top_n = 2000

    i = 0
    solang i < laenge(args):
        sofern args[i] == "--input":
            eingabe_pfad = args[i + 1]
            i = i + 2
        sofernschier args[i] == "--out":
            ausgabe_ordner = args[i + 1]
            i = i + 2
        sofernschier args[i] == "--top":
            top_n = ganzzahl(args[i + 1])
            i = i + 2
        sonst:
            i = i + 1

    sofern eingabe_pfad ist Nichts:
        verkuendet("Verwendung: schlange run examples/spotify_parse.schl.py --input <pfad> --out <ordner>")
        verkuendet("  --input   Pfad zur Spotify export JSON Datei oder Ordner")
        verkuendet("  --out     Ausgabeordner (Standard: out/)")
        verkuendet("  --top     Anzahl Top-Tracks (Standard: 2000)")
        gibzurueck

    verkuendet(f"Lade Spotify-Export von: {eingabe_pfad}")
    wiedergaben = load_export(eingabe_pfad)
    verkuendet(f"  {laenge(wiedergaben)} Wiedergaben geladen")

    sofern laenge(wiedergaben) == 0:
        verkuendet("Keine Wiedergaben gefunden. Pruefe das Dateiformat.")
        gibzurueck

    verkuendet(f"\nRanking der Top {top_n} Tracks...")
    rangliste = rank_tracks(wiedergaben, top_n=top_n)
    verkuendet(f"  {laenge(rangliste)} Tracks im Ranking")

    # Top 10 anzeigen
    verkuendet("\n=== Top 10 ===")
    fuerwahr eintrag inwendig rangliste[:10]:
        verkuendet(f"  #{eintrag.rank}: {eintrag.artist_name} - {eintrag.track_name} ({eintrag.play_count}x)")

    # Exportieren
    csv_pfad = os.path.join(ausgabe_ordner, "top_tracks.csv")
    seed_pfad = os.path.join(ausgabe_ordner, "playlist_seed.json")

    export_csv(rangliste, csv_pfad)
    verkuendet(f"\nCSV exportiert nach: {csv_pfad}")

    export_playlist_seed(rangliste, seed_pfad)
    verkuendet(f"Playlist-Seed exportiert nach: {seed_pfad}")

    verkuendet("\nFertig! Verwende den Seed fuer den Playlist-Builder.")

hauptprogramm()
