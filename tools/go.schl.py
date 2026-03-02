b# =============================================================================
#  GO.SCHL.PY -- Der Meister-Orchestrator
# =============================================================================
#
#  CHAOTIC ENGINEERING PROGRAM -- One Button To Rule Them All
#
#  This is the master pipeline that:
#    1. Loads environment config
#    2. Prepares assets from data/
#    3. Generates video script + subtitles
#    4. Renders video (placeholder backend)
#    5. Extracts frames for email
#    6. Generates tri-lingual bombastic email
#    7. Validates ALL mandatory elements
#    8. Sends email (or dry-run)
#
#  Usage:
#    schlange run tools/go.schl.py                          # dry-run
#    schlange run tools/go.schl.py --send                   # actually send
#    schlange run tools/go.schl.py --send --event-date 2026-03-12
#    schlange run tools/go.schl.py --skip-video             # email only
#    schlange run tools/go.schl.py --skip-email             # video only
#    schlange run tools/go.schl.py --validate-only          # just check
#
# =============================================================================

importiert sys
importiert os
importiert json

von dotenv importiert load_dotenv


# =============================================================================
#  BANNER
# =============================================================================

defn banner():
    verkuendet("")
    verkuendet("  ===================================================")
    verkuendet("  =   CHAOTIC ENGINEERING PROGRAM                   =")
    verkuendet("  =   Eine Smutzige Hansi Produktion                =")
    verkuendet("  =   Powered by Schlange -- Python auf Deutsch      =")
    verkuendet("  ===================================================")
    verkuendet("")
    verkuendet("  Donnerstag, 12. Maerz 2026 -- De Vierkant")
    verkuendet("  Sei dabei -- oder sei ein Viereck.")
    verkuendet("")


# =============================================================================
#  ARGUMENT PARSER
# =============================================================================

defn parse_argumente():
    """Parse alle Kommandozeilen-Argumente."""
    config = {
        "senden": Falschlich,
        "skip_video": Falschlich,
        "skip_email": Falschlich,
        "validate_only": Falschlich,
        "event_date": "2026-03-12",
    }

    args = sys.argv[1:]
    i = 0
    solang i < laenge(args):
        sofern args[i] == "--send":
            config["senden"] = Wahrlich
            i = i + 1
        sofernschier args[i] == "--skip-video":
            config["skip_video"] = Wahrlich
            i = i + 1
        sofernschier args[i] == "--skip-email":
            config["skip_email"] = Wahrlich
            i = i + 1
        sofernschier args[i] == "--validate-only":
            config["validate_only"] = Wahrlich
            i = i + 1
        sofernschier args[i] == "--event-date":
            config["event_date"] = args[i + 1]
            i = i + 2
        sonst:
            i = i + 1

    gibzurueck config


# =============================================================================
#  STEP 1: ENVIRONMENT
# =============================================================================

defn schritt_umgebung():
    """Lade .env und pruefe Konfiguration."""
    verkuendet("\n[1/7] Umgebung laden...")
    load_dotenv()

    # Pruefe wichtige Variablen
    checks = {
        "GOODBYE_DATE": os.getenv("GOODBYE_DATE", "2026-03-12"),
        "GOODBYE_LOCATION": os.getenv("GOODBYE_LOCATION", "De Vierkant"),
        "VIDEO_BACKEND": os.getenv("VIDEO_BACKEND", "placeholder"),
    }

    fuerwahr key, wert inwendig checks.items():
        verkuendet(f"  {key} = {wert}")

    gibzurueck checks


# =============================================================================
#  STEP 2: ASSETS
# =============================================================================

defn schritt_assets():
    """Bereite Assets aus data/ vor."""
    verkuendet("\n[2/7] Assets vorbereiten...")

    video_pfad = "data/smutzige_hansie_video.mp4"
    sofern os.path.exists(video_pfad):
        groesse = os.path.getsize(video_pfad) / 1_048_576
        verkuendet(f"  Referenz-Video gefunden: {video_pfad} ({groesse:.1f} MB)")
    sonst:
        verkuendet(f"  WARNUNG: Referenz-Video nicht gefunden: {video_pfad}")

    # Erstelle output-Verzeichnisse
    fuerwahr ordner inwendig ["out/video", "out/email/img"]:
        os.makedirs(ordner, exist_ok=Wahrlich)
        verkuendet(f"  Verzeichnis: {ordner}")

    gibzurueck video_pfad


# =============================================================================
#  STEP 3: VIDEO SCRIPT + SUBTITLES
# =============================================================================

defn schritt_script():
    """Generiere Video-Script und Untertitel."""
    verkuendet("\n[3/7] Script und Untertitel generieren...")

    von schlange.video.script importiert generate_script, generate_subtitles, generate_metadata

    script = generate_script("out/video/script_de.txt")
    verkuendet(f"  Script generiert: out/video/script_de.txt")

    srt = generate_subtitles("out/video/subtitles.srt")
    verkuendet(f"  Untertitel generiert: out/video/subtitles.srt")

    metadaten = generate_metadata("out/video/metadata.json")
    verkuendet(f"  Metadaten generiert: out/video/metadata.json")
    verkuendet(f"  Gesamtdauer: {metadaten['duration_seconds']}s ({metadaten['scenes']} Szenen)")


# =============================================================================
#  STEP 4: VIDEO RENDER
# =============================================================================

defn schritt_video(video_pfad):
    """Rendere das Video mit dem konfigurierten Backend."""
    verkuendet("\n[4/7] Video rendern...")

    von schlange.video importiert render_video, get_backend

    # Aktualisiere die Storyboard-Datei
    _aktualisiere_storyboard()

    backend_name = os.getenv("VIDEO_BACKEND", "placeholder")
    verkuendet(f"  Backend: {backend_name}")

    sofern backend_name inwendig ("veo3", "veo", "veo3.1", "gemini"):
        verkuendet(f"  Modell: {os.getenv('VEO_MODEL', 'veo3.1')}")
        verkuendet(f"  Aufloesung: {os.getenv('VEO_RESOLUTION', '720p')}")
        verkuendet(f"  Geschaetzte Kosten: ~$3.20 (8 Szenen x $0.40)")
        verkuendet(f"  Geschaetzte Dauer: 1-6 Minuten pro Szene")

    backend = get_backend(output_dir="out/video")

    ergebnis = render_video(
        assets_json_path="assets/assets.json",
        backend=backend,
        output_path="final.mp4",
    )
    verkuendet(f"  Video-Pipeline abgeschlossen: {ergebnis}")


defn _aktualisiere_storyboard():
    """Stelle sicher, dass assets.json zum Spec passt."""
    # Die assets.json wird direkt aus dem Repo geladen
    sofern os.path.exists("assets/assets.json"):
        verkuendet(f"  Storyboard: assets/assets.json")
    sonst:
        verkuendet(f"  WARNUNG: assets/assets.json nicht gefunden!")


# =============================================================================
#  STEP 5: FRAME EXTRACTION
# =============================================================================

defn schritt_frames(video_pfad):
    """Extrahiere Frames aus dem Referenz-Video."""
    verkuendet("\n[5/7] Frames extrahieren...")

    von schlange.video.frames importiert extract_frames_ffmpeg, generate_assets_manifest

    frames = extract_frames_ffmpeg(
        video_path=video_pfad,
        output_dir="out/email/img",
        num_frames=4,
        prefix="frame",
    )
    verkuendet(f"  {laenge(frames)} Frames extrahiert")

    manifest = generate_assets_manifest(frames, video_pfad, "assets_manifest.json")
    verkuendet(f"  Assets-Manifest: assets_manifest.json")

    gibzurueck frames


# =============================================================================
#  STEP 6: EMAIL GENERATION
# =============================================================================

defn schritt_email(frames):
    """Generiere die tri-linguale bombastische Email."""
    verkuendet("\n[6/7] Tri-linguale Email generieren...")

    von schlange.email.template importiert generate_email_html

    # Links zusammenstellen
    links = {
        "GitHub": os.getenv("GITHUB_REPO_URL", "https://github.com/tpetedb/Schlange"),
        "Spotify Tom 2000": os.getenv("SPOTIFY_PLAYLIST_URL", ""),
        "Website": os.getenv("TOM_WEBSITE_URL", ""),
    }
    # Entferne leere Links
    links = {k: v fuerwahr k, v inwendig links.items() sofern v}

    # CID fuer erstes Frame-Bild
    img_cid = Nichts
    sofern frames und laenge(frames) > 0:
        img_cid = "frame_coding"

    html = generate_email_html(
        links=links,
        img_cid=img_cid,
        output_path="out/email/email_trilingual.html",
    )
    verkuendet(f"  Email generiert: out/email/email_trilingual.html")
    verkuendet(f"  Sprachen: DE / EN / NL")
    verkuendet(f"  Links: {', '.join(links.keys())}")
    sofern img_cid:
        verkuendet(f"  Inline-Bild: CID={img_cid}")

    gibzurueck html, frames, img_cid


# =============================================================================
#  STEP 7: VALIDATION
# =============================================================================

defn schritt_validierung():
    """Validiere alle Pflicht-Inhalte."""
    verkuendet("\n[7/7] Validierung...")

    von schlange.validate importiert validate_all

    bericht = validate_all()
    verkuendet(bericht.summary())

    gibzurueck bericht


# =============================================================================
#  EMAIL SENDEN
# =============================================================================

defn schritt_senden(html, frames, img_cid, senden):
    """Sende die Email (oder dry-run)."""
    von schlange.email.sender importiert load_recipients, send_email

    verkuendet("\n=== EMAIL VERSAND ===")

    empfaenger = load_recipients()

    sofern laenge(empfaenger) == 0:
        verkuendet("  Keine Empfaenger gefunden!")
        verkuendet("  Erstelle data/recipients.csv oder setze RECIPIENTS in .env")
        gibzurueck

    # Bilder vorbereiten
    bild_pfade = []
    bild_cids = []
    sofern img_cid und frames:
        # Erstes Frame als Inline-Bild
        bild_pfade = [frames[0]]
        bild_cids = [img_cid]

    ergebnis = send_email(
        html_body=html,
        recipients=empfaenger,
        subject="CHAOTIC ENGINEERING PROGRAM -- Donnerstag, 12. Maerz 2026",
        image_paths=bild_pfade,
        image_cids=bild_cids,
        dry_run=nichten senden,
    )

    sofern ergebnis.get("errors"):
        verkuendet("  Fehler:")
        fuerwahr fehler inwendig ergebnis["errors"]:
            verkuendet(f"    - {fehler}")


# =============================================================================
#  HAUPTPROGRAMM
# =============================================================================

defn hauptprogramm():
    """Der Meister-Orchestrator -- Ein Knopf fuer Alles."""

    banner()

    config = parse_argumente()

    # Modus anzeigen
    sofern config["validate_only"]:
        verkuendet("  Modus: NUR VALIDIERUNG")
    sofernschier config["senden"]:
        verkuendet("  Modus: SENDEN (LIVE!)")
    sonst:
        verkuendet("  Modus: DRY-RUN (kein Versand)")

    # Step 1: Umgebung
    env_config = schritt_umgebung()

    # Nur validieren?
    sofern config["validate_only"]:
        bericht = schritt_validierung()
        sofern nichten bericht.passed:
            verkuendet("\n  BUILD FAILED -- Pflicht-Inhalte fehlen!")
            sys.exit(1)
        verkuendet("\n  BUILD PASSED -- Alles in Ordnung!")
        gibzurueck

    # Step 2: Assets
    video_pfad = schritt_assets()

    # Step 3: Script + Subtitles
    sofern nichten config["skip_video"]:
        schritt_script()
    sonst:
        verkuendet("\n[3/7] Script -- UEBERSPRUNGEN (--skip-video)")

    # Step 4: Video
    sofern nichten config["skip_video"]:
        schritt_video(video_pfad)
    sonst:
        verkuendet("\n[4/7] Video -- UEBERSPRUNGEN (--skip-video)")

    # Step 5: Frames
    frames = []
    sofern nichten config["skip_video"]:
        frames = schritt_frames(video_pfad)
    sonst:
        verkuendet("\n[5/7] Frames -- UEBERSPRUNGEN (--skip-video)")
        # Versuche existierende Frames zu laden
        sofern os.path.isdir("out/email/img"):
            frames = sortiert([
                os.path.join("out/email/img", f)
                fuerwahr f inwendig os.listdir("out/email/img")
                sofern f.startswith("frame_")
            ])

    # Step 6: Email
    html = ""
    img_cid = Nichts
    sofern nichten config["skip_email"]:
        html, frames, img_cid = schritt_email(frames)
    sonst:
        verkuendet("\n[6/7] Email -- UEBERSPRUNGEN (--skip-email)")

    # Step 7: Validierung
    bericht = schritt_validierung()

    sofern nichten bericht.passed:
        verkuendet("\n  BUILD FAILED -- Pflicht-Inhalte fehlen!")
        verkuendet("  Pipeline stoppt. Behebe die Fehler und versuche es erneut.")
        sys.exit(1)

    # Senden
    sofern html und nichten config["skip_email"]:
        schritt_senden(html, frames, img_cid, config["senden"])

    # Abschluss
    verkuendet("\n" + "=" * 55)
    verkuendet("  CHAOTIC ENGINEERING PROGRAM -- PIPELINE ABGESCHLOSSEN")
    verkuendet("=" * 55)
    verkuendet("  Video:   out/video/final.mp4")
    verkuendet("  Script:  out/video/script_de.txt")
    verkuendet("  Email:   out/email/email_trilingual.html")
    verkuendet("  Frames:  out/email/img/")
    verkuendet("")
    verkuendet("  Donnerstag, 12. Maerz 2026 -- De Vierkant")
    verkuendet("  PROBIERT * AUSSER * ENDLICH")
    verkuendet("")


# Los geht's!
hauptprogramm()
