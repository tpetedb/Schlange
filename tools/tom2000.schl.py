# =============================================================================
#  TOM 2000 -- by Smutzige Hansie, powered by Schlange
# =============================================================================
#
#  Parses Tom's full Spotify Extended Streaming History, ranks all tracks,
#  exports the Top 2000 as CSV + playlist seed, and prints stats.
#
#  Usage:
#    schlange run tools/tom2000.schl.py
#    schlange run tools/tom2000.schl.py --top 3000
#    schlange run tools/tom2000.schl.py --min-ms 60000
#
# =============================================================================

importiert sys
importiert os
importiert json

von schlange.spotify.parser importiert load_export, rank_tracks, export_csv, export_playlist_seed, print_stats

# --- Konfiguration ---
DATEN_PFAD = "data/extracted/Spotify Extended Streaming History"
AUSGABE_ORDNER = "out"
TOP_N = 2000
MIN_MS = 30000  # 30 Sekunden Minimum


defn banner():
    """Der grosse Tom 2000 Banner."""
    verkuendet("")
    verkuendet("  _____ ___  __  __   ____   ___   ___   ___  ")
    verkuendet(" |_   _/ _ \\|  \\/  | |___ \\ / _ \\ / _ \\ / _ \\ ")
    verkuendet("   | || | | | |\\/| |   __) | | | | | | | | | |")
    verkuendet("   | || |_| | |  | |  / __/| |_| | |_| | |_| |")
    verkuendet("   |_| \\___/|_|  |_| |_____|\\___/ \\___/ \\___/ ")
    verkuendet("")
    verkuendet("   by Smutzige Hansie -- powered by Schlange")
    verkuendet("   ==========================================")
    verkuendet("")


defn parse_argumente():
    """Parse Kommandozeilen-Argumente."""
    top_n = TOP_N
    min_ms = MIN_MS
    daten_pfad = DATEN_PFAD
    ausgabe = AUSGABE_ORDNER

    args = sys.argv[1:]
    i = 0
    solang i < laenge(args):
        sofern args[i] == "--top":
            top_n = ganzzahl(args[i + 1])
            i = i + 2
        sofernschier args[i] == "--min-ms":
            min_ms = ganzzahl(args[i + 1])
            i = i + 2
        sofernschier args[i] == "--input":
            daten_pfad = args[i + 1]
            i = i + 2
        sofernschier args[i] == "--out":
            ausgabe = args[i + 1]
            i = i + 2
        sonst:
            i = i + 1

    gibzurueck top_n, min_ms, daten_pfad, ausgabe


defn lade_und_filtere(daten_pfad, min_ms):
    """Lade alle Wiedergaben und filtere nach Mindest-Spielzeit."""
    verkuendet(f"Lade Spotify Extended Streaming History...")
    verkuendet(f"  Pfad: {daten_pfad}")
    verkuendet(f"  Mindest-Spielzeit: {min_ms / 1000:.0f} Sekunden")

    alle_wiedergaben = load_export(daten_pfad)
    verkuendet(f"  {laenge(alle_wiedergaben):,} Wiedergaben geladen (nach Filter)")

    gibzurueck alle_wiedergaben


defn zeige_top_liste(rangliste, anzahl=25):
    """Zeige die Top N Tracks mit Formatierung."""
    verkuendet(f"\n{'=' * 70}")
    verkuendet(f"  TOP {anzahl} -- TOM 2000 RANGLISTE")
    verkuendet(f"{'=' * 70}")
    verkuendet(f"  {'#':>4}  {'Plays':>5}  {'Stunden':>7}  Artist - Track")
    verkuendet(f"  {'':->4}  {'':->5}  {'':->7}  {'':-<40}")

    fuerwahr eintrag inwendig rangliste[:anzahl]:
        stunden = eintrag.total_ms / 3_600_000
        uri_marker = " *" sofern eintrag.spotify_uri sonst ""
        verkuendet(
            f"  {eintrag.rank:>4}  {eintrag.play_count:>5}  {stunden:>7.1f}  "
            f"{eintrag.artist_name} - {eintrag.track_name}{uri_marker}"
        )

    verkuendet(f"\n  (* = Spotify URI vorhanden)")


defn zeige_genre_mix(rangliste):
    """Zeige eine grobe Verteilung der Top-Artisten."""
    artisten_plays = {}
    fuerwahr eintrag inwendig rangliste:
        sofern eintrag.artist_name nichten inwendig artisten_plays:
            artisten_plays[eintrag.artist_name] = 0
        artisten_plays[eintrag.artist_name] = artisten_plays[eintrag.artist_name] + eintrag.play_count

    # Top 15 Artisten
    sortierte_artisten = sortiert(artisten_plays.items(), key=anonym x: x[1], reverse=Wahrlich)

    verkuendet(f"\n{'=' * 50}")
    verkuendet(f"  TOP 15 ARTISTEN (nach Plays in Top 2000)")
    verkuendet(f"{'=' * 50}")
    fuerwahr i, (artist, plays) inwendig aufzaehlung(sortierte_artisten[:15], 1):
        balken = "#" * minimum(plays, 40)
        verkuendet(f"  {i:>2}. {artist:<30s} {plays:>4} {balken}")


defn exportiere_alles(rangliste, ausgabe, top_n):
    """Exportiere CSV, Playlist-Seed und Zusammenfassung."""
    os.makedirs(ausgabe, exist_ok=Wahrlich)

    csv_pfad = os.path.join(ausgabe, f"tom{top_n}_rangliste.csv")
    seed_pfad = os.path.join(ausgabe, f"tom{top_n}_playlist_seed.json")
    stats_pfad = os.path.join(ausgabe, f"tom{top_n}_zusammenfassung.txt")

    # CSV
    export_csv(rangliste, csv_pfad)
    verkuendet(f"\n  CSV:           {csv_pfad}")

    # Playlist Seed (mit Spotify URIs!)
    export_playlist_seed(rangliste, seed_pfad)
    verkuendet(f"  Playlist Seed: {seed_pfad}")

    # URI-Statistik
    mit_uri = summe(1 fuerwahr t inwendig rangliste sofern t.spotify_uri)
    ohne_uri = laenge(rangliste) - mit_uri

    # Zusammenfassung als Text
    mittels oeffne(stats_pfad, "w") als fh:
        fh.write(f"TOM {top_n} -- Zusammenfassung\n")
        fh.write(f"{'=' * 40}\n\n")
        fh.write(f"Tracks im Ranking: {laenge(rangliste)}\n")
        fh.write(f"Mit Spotify URI:   {mit_uri} ({100 * mit_uri / laenge(rangliste):.1f}%)\n")
        fh.write(f"Ohne Spotify URI:  {ohne_uri}\n\n")
        fh.write(f"Top 10:\n")
        fuerwahr e inwendig rangliste[:10]:
            fh.write(f"  #{e.rank}: {e.artist_name} - {e.track_name} ({e.play_count}x)\n")

    verkuendet(f"  Zusammenfassung: {stats_pfad}")

    # Direkt nutzbare URI-Liste fuer Spotify API
    uri_liste = [t.spotify_uri fuerwahr t inwendig rangliste sofern t.spotify_uri]
    sofern uri_liste:
        uri_pfad = os.path.join(ausgabe, f"tom{top_n}_uris.json")
        mittels oeffne(uri_pfad, "w") als fh:
            json.dump(uri_liste, fh, indent=2)
        verkuendet(f"  Spotify URIs:  {uri_pfad} ({laenge(uri_liste)} tracks)")

    gibzurueck mit_uri, ohne_uri


defn hauptprogramm():
    """Das Hauptprogramm -- Tom 2000 Pipeline."""
    banner()

    top_n, min_ms, daten_pfad, ausgabe = parse_argumente()

    # Pruefe ob Daten vorhanden
    sofern nichten os.path.exists(daten_pfad):
        verkuendet(f"FEHLER: Datenordner nicht gefunden: {daten_pfad}")
        verkuendet("  Entpacke zuerst: unzip data/my_spotify_data.zip -d data/extracted/")
        gibzurueck

    # Lade und parse
    wiedergaben = lade_und_filtere(daten_pfad, min_ms)

    sofern laenge(wiedergaben) == 0:
        verkuendet("Keine Wiedergaben gefunden!")
        gibzurueck

    # Ranking
    verkuendet(f"\nErstelle Tom {top_n} Rangliste...")
    rangliste = rank_tracks(wiedergaben, top_n=top_n)
    verkuendet(f"  {laenge(rangliste)} Tracks im finalen Ranking")

    # Statistiken
    print_stats(wiedergaben, rangliste)

    # Top 25 anzeigen
    zeige_top_liste(rangliste, anzahl=25)

    # Artisten-Verteilung
    zeige_genre_mix(rangliste)

    # Exportieren
    verkuendet(f"\nExportiere Tom {top_n}...")
    mit_uri, ohne_uri = exportiere_alles(rangliste, ausgabe, top_n)

    # Abschluss
    verkuendet(f"\n{'=' * 50}")
    verkuendet(f"  TOM {top_n} IST FERTIG!")
    verkuendet(f"{'=' * 50}")
    verkuendet(f"  {laenge(rangliste)} Tracks gerankt")
    verkuendet(f"  {mit_uri} mit Spotify URI (direkt spielbar)")
    sofern ohne_uri > 0:
        verkuendet(f"  {ohne_uri} brauchen noch manuelle Zuordnung")
    verkuendet(f"\n  Naechster Schritt:")
    verkuendet(f"    schlange run tools/make_playlist.schl.py --seed out/tom{top_n}_playlist_seed.json")
    verkuendet(f"\n  PROBIERT * AUSSER * ENDLICH")
    verkuendet("")


# Los geht's!
hauptprogramm()
