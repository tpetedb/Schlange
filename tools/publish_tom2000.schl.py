# =============================================================================
#  TOM 2000 -- Playlist Veroeffentlichung
# =============================================================================
#
#  Publishes the Tom 2000 playlist to Spotify using URIs from the export.
#  No search API calls needed -- all 2000 URIs come from the streaming history.
#
#  Prerequisites:
#    1. Run: schlange run tools/tom2000.schl.py
#    2. Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET in .env
#    3. Spotify app redirect URI: http://127.0.0.1:8888/callback
#
#  Usage:
#    schlange run tools/publish_tom2000.schl.py
#    schlange run tools/publish_tom2000.schl.py --name "Tom 3000" --public
#    schlange run tools/publish_tom2000.schl.py --seed out/tom3000_playlist_seed.json
#
# =============================================================================

importiert sys
importiert os
importiert json

von dotenv importiert load_dotenv
von schlange.spotify.playlist importiert PlaylistBuilder


defn banner():
    """Der Veroeffentlichungs-Banner."""
    verkuendet("")
    verkuendet("  _____ ___  __  __   ____   ___   ___   ___  ")
    verkuendet(" |_   _/ _ \\|  \\/  | |___ \\ / _ \\ / _ \\ / _ \\ ")
    verkuendet("   | || | | | |\\/| |   __) | | | | | | | | | |")
    verkuendet("   | || |_| | |  | |  / __/| |_| | |_| | |_| |")
    verkuendet("   |_| \\___/|_|  |_| |_____|\\___/ \\___/ \\___/ ")
    verkuendet("")
    verkuendet("   PLAYLIST VEROEFFENTLICHUNG")
    verkuendet("   by Smutzige Hansie -- powered by Schlange")
    verkuendet("   ==========================================")
    verkuendet("")


defn parse_argumente():
    """Parse Kommandozeilen-Argumente."""
    seed_pfad = "out/tom2000_playlist_seed.json"
    uri_pfad = "out/tom2000_uris.json"
    name = "Tom 2000"
    beschreibung = Nichts
    oeffentlich = Falschlich

    args = sys.argv[1:]
    i = 0
    solang i < laenge(args):
        sofern args[i] == "--seed":
            seed_pfad = args[i + 1]
            i = i + 2
        sofernschier args[i] == "--uris":
            uri_pfad = args[i + 1]
            i = i + 2
        sofernschier args[i] == "--name":
            name = args[i + 1]
            i = i + 2
        sofernschier args[i] == "--description":
            beschreibung = args[i + 1]
            i = i + 2
        sofernschier args[i] == "--public":
            oeffentlich = Wahrlich
            i = i + 1
        sonst:
            i = i + 1

    gibzurueck seed_pfad, uri_pfad, name, beschreibung, oeffentlich


defn lade_uris(seed_pfad, uri_pfad):
    """Lade Spotify URIs -- bevorzugt aus der URI-Datei, Fallback auf Seed."""

    # Versuche zuerst die direkte URI-Liste
    sofern os.path.exists(uri_pfad):
        verkuendet(f"  Lade URIs aus: {uri_pfad}")
        mittels oeffne(uri_pfad) als fh:
            uris = json.load(fh)
        verkuendet(f"  {laenge(uris)} URIs geladen")
        gibzurueck uris

    # Fallback: extrahiere URIs aus dem Playlist-Seed
    sofern os.path.exists(seed_pfad):
        verkuendet(f"  Lade URIs aus Seed: {seed_pfad}")
        mittels oeffne(seed_pfad) als fh:
            seed = json.load(fh)
        uris = [eintrag["spotify_uri"] fuerwahr eintrag inwendig seed sofern eintrag.get("spotify_uri")]
        verkuendet(f"  {laenge(uris)} URIs aus Seed extrahiert")
        gibzurueck uris

    verkuendet("FEHLER: Keine URI-Datei gefunden!")
    verkuendet(f"  Erwartet: {uri_pfad} oder {seed_pfad}")
    verkuendet("  Fuehre zuerst aus: schlange run tools/tom2000.schl.py")
    gibzurueck []


defn pruefe_voraussetzungen():
    """Pruefe ob alle Voraussetzungen erfuellt sind."""
    client_id = os.getenv("SPOTIPY_CLIENT_ID", "")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET", "")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI", "")

    fehler = []
    sofern nichten client_id oder client_id == "your_client_id_here":
        fehler.append("SPOTIPY_CLIENT_ID nicht gesetzt")
    sofern nichten client_secret oder client_secret == "your_client_secret_here":
        fehler.append("SPOTIPY_CLIENT_SECRET nicht gesetzt")
    sofern nichten redirect_uri:
        os.environ["SPOTIPY_REDIRECT_URI"] = "http://127.0.0.1:8888/callback"
        verkuendet("  SPOTIPY_REDIRECT_URI auf Standard gesetzt: http://127.0.0.1:8888/callback")

    sofern fehler:
        verkuendet("\nFEHLER: Spotify-Credentials fehlen!")
        fuerwahr f inwendig fehler:
            verkuendet(f"  - {f}")
        verkuendet("\n  Setze die Werte in .env:")
        verkuendet("    SPOTIPY_CLIENT_ID=dein_client_id")
        verkuendet("    SPOTIPY_CLIENT_SECRET=dein_client_secret")
        gibzurueck Falschlich

    verkuendet("  Spotify-Credentials OK")
    gibzurueck Wahrlich


defn hauptprogramm():
    """Veroeffentliche die Tom 2000 Playlist auf Spotify."""

    banner()

    # .env laden
    load_dotenv()

    # Argumente parsen
    seed_pfad, uri_pfad, name, beschreibung, oeffentlich = parse_argumente()

    # Voraussetzungen pruefen
    verkuendet("Pruefe Voraussetzungen...")
    sofern nichten pruefe_voraussetzungen():
        gibzurueck

    # URIs laden
    verkuendet(f"\nLade Track-URIs...")
    uris = lade_uris(seed_pfad, uri_pfad)
    sofern laenge(uris) == 0:
        gibzurueck

    # Standardbeschreibung
    sofern beschreibung ist Nichts:
        beschreibung = f"Meine Top {laenge(uris)} -- {laenge(uris)} Tracks aus 6 Jahren Spotify-Geschichte. Generiert von Smutzige Hansie via Schlange."

    # Zusammenfassung vor dem Veroeffentlichen
    verkuendet(f"\n{'=' * 50}")
    verkuendet(f"  PLAYLIST ZUSAMMENFASSUNG")
    verkuendet(f"{'=' * 50}")
    verkuendet(f"  Name:          {name}")
    verkuendet(f"  Tracks:        {laenge(uris)}")
    verkuendet(f"  Oeffentlich:   {'Ja' sofern oeffentlich sonst 'Nein'}")
    verkuendet(f"  Beschreibung:  {beschreibung[:60]}...")
    verkuendet(f"{'=' * 50}")

    # Authentifizierung
    verkuendet(f"\nAuthentifiziere bei Spotify...")
    verkuendet("  (Browser oeffnet sich fuer OAuth -- bitte einloggen und erlauben)")

    bauer = PlaylistBuilder()
    probiert:
        bauer.authenticate()
        verkuendet("  Authentifizierung erfolgreich!")
    ausser Exception alsfehler e:
        verkuendet(f"\n  FEHLER bei Authentifizierung: {e}")
        verkuendet("  Tipps:")
        verkuendet("    - Pruefe Client ID und Secret in .env")
        verkuendet("    - Redirect URI muss in der Spotify App eingetragen sein:")
        verkuendet("      http://127.0.0.1:8888/callback")
        verkuendet("    - Stelle sicher, dass die App im Spotify Developer Dashboard aktiv ist")
        gibzurueck

    # Playlist erstellen und Tracks hinzufuegen
    verkuendet(f"\nErstelle Playlist '{name}' und fuege {laenge(uris)} Tracks hinzu...")
    verkuendet(f"  (Das dauert ca. {laenge(uris) // 100 + 1} API-Aufrufe)")

    probiert:
        url = bauer.create_playlist_from_uris(
            uris=uris,
            name=name,
            description=beschreibung,
            public=oeffentlich,
        )
    ausser Exception alsfehler e:
        verkuendet(f"\n  FEHLER beim Erstellen der Playlist: {e}")
        verkuendet("")
        verkuendet("  === TROUBLESHOOTING ===")
        verkuendet("  Bei 403 Forbidden:")
        verkuendet("    1. Gehe zu: https://developer.spotify.com/dashboard")
        verkuendet("    2. Oeffne deine App")
        verkuendet("    3. Klicke 'Settings'")
        verkuendet("    4. Scrolle zu 'User Management'")
        verkuendet("    5. Fuege deine Spotify-Email-Adresse hinzu")
        verkuendet("    6. Speichern und erneut ausfuehren")
        verkuendet("")
        verkuendet("  Alternativ: loesche .cache und versuche erneut:")
        verkuendet("    rm .cache && schlange run tools/publish_tom2000.schl.py")
        gibzurueck

    # Erfolg!
    verkuendet(f"\n{'=' * 50}")
    verkuendet(f"  TOM 2000 IST LIVE!")
    verkuendet(f"{'=' * 50}")
    verkuendet(f"  Playlist: {url}")
    verkuendet(f"  Tracks:   {laenge(uris)}")
    verkuendet(f"")
    verkuendet(f"  Oeffne den Link oder suche '{name}' in deiner Spotify-App.")
    verkuendet(f"")
    verkuendet(f"  PROBIERT * AUSSER * ENDLICH")
    verkuendet(f"")


# Los geht's, Smutzige Hansie!
hauptprogramm()
