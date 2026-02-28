# Tom 2000 Playlist Builder -- geschrieben in Schlange!
# Run: schlange run tools/make_playlist.schl.py --top 2000 --public false
#
# Resolves tracks from playlist_seed.json against Spotify and creates a playlist.

importiert sys
importiert os

von dotenv importiert load_dotenv
von schlange.spotify.playlist importiert PlaylistBuilder

defn hauptprogramm():
    """Build the Tom 2000 playlist on Spotify."""
    load_dotenv()

    args = sys.argv[1:]
    top_n = 2000
    oeffentlich = Falschlich
    seed_pfad = "out/playlist_seed.json"
    name = "Tom 2000"

    i = 0
    solang i < laenge(args):
        sofern args[i] == "--top":
            top_n = ganzzahl(args[i + 1])
            name = f"Tom {top_n}"
            i = i + 2
        sofernschier args[i] == "--public":
            oeffentlich = args[i + 1].lower() inwendig ["true", "1", "ja"]
            i = i + 2
        sofernschier args[i] == "--seed":
            seed_pfad = args[i + 1]
            i = i + 2
        sofernschier args[i] == "--name":
            name = args[i + 1]
            i = i + 2
        sonst:
            i = i + 1

    sofern nichten os.path.exists(seed_pfad):
        verkuendet(f"Fehler: Seed-Datei nicht gefunden: {seed_pfad}")
        verkuendet("Fuehre zuerst spotify_parse.schl.py aus!")
        gibzurueck

    verkuendet(f"=== {name} Playlist Builder ===")
    verkuendet(f"Seed: {seed_pfad}")
    verkuendet(f"Oeffentlich: {oeffentlich}")

    # Authentifizierung
    verkuendet("\nAuthentifiziere bei Spotify...")
    bauer = PlaylistBuilder()
    probiert:
        bauer.authenticate()
        verkuendet("  Authentifizierung erfolgreich!")
    ausser Exception alsfehler e:
        verkuendet(f"  Authentifizierung fehlgeschlagen: {e}")
        verkuendet("  Pruefe SPOTIPY_CLIENT_ID / SPOTIPY_CLIENT_SECRET in .env")
        gibzurueck

    # Track-Auflosung
    verkuendet("\nLoese Tracks auf...")
    ergebnisse = bauer.resolve_tracks(seed_pfad)

    # Bericht
    bericht = bauer.generate_report(ergebnisse, output_path="out/resolution_report.txt")
    verkuendet(f"\n{bericht}")

    # Playlist erstellen
    gematchte = [e fuerwahr e inwendig ergebnisse sofern e.matched]
    sofern laenge(gematchte) == 0:
        verkuendet("\nKeine Tracks gematcht -- Playlist wird nicht erstellt.")
        gibzurueck

    verkuendet(f"\nErstelle Playlist '{name}' mit {laenge(gematchte)} Tracks...")
    beschreibung = f"Generated from listening history via Schlange -- {laenge(gematchte)} tracks"
    url = bauer.create_playlist(
        ergebnisse,
        name=name,
        description=beschreibung,
        public=oeffentlich,
    )
    verkuendet(f"\nPlaylist erstellt: {url}")
    verkuendet("Fertig!")

hauptprogramm()
