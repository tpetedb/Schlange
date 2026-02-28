# Smutsahansi Video Generator -- geschrieben in Schlange!
# Run: schlange run tools/make_video.schl.py
#
# Loads the storyboard from assets/assets.json and generates the video.

importiert os
von dotenv importiert load_dotenv
von schlange.video importiert render_video, PlaceholderBackend

defn hauptprogramm():
    """Generate the Smutsahansi reveal video."""
    load_dotenv()

    assets_pfad = "assets/assets.json"
    audio_pfad = os.getenv("VIDEO_AUDIO_TRACK", Nichts)
    ausgabe = "out/video/schlange_presentiert.mp4"

    sofern nichten os.path.exists(assets_pfad):
        verkuendet(f"Fehler: Storyboard nicht gefunden: {assets_pfad}")
        verkuendet("Erstelle eine assets/assets.json Datei mit deinem Storyboard.")
        gibzurueck

    verkuendet("=== SCHLANGE PRESENTIERT ===")
    verkuendet("Smutsahansi Video Pipeline\n")

    # Backend auswaehlen (placeholder fuer Entwicklung)
    backend_typ = os.getenv("VIDEO_BACKEND", "placeholder")
    sofern backend_typ == "placeholder":
        verkuendet("Verwende Placeholder-Backend (kein echtes Video)")
        backend = PlaceholderBackend(output_dir="out/video")
    sonst:
        verkuendet(f"Backend '{backend_typ}' noch nicht implementiert, verwende Placeholder")
        backend = PlaceholderBackend(output_dir="out/video")

    # Pipeline ausfuehren
    probiert:
        ergebnis = render_video(
            assets_json_path=assets_pfad,
            backend=backend,
            audio_track=audio_pfad,
            output_path=ausgabe,
        )
        verkuendet(f"\nErgebnis: {ergebnis}")
        verkuendet("PROBIERT * AUSSER * ENDLICH")
    ausser Exception alsfehler e:
        verkuendet(f"Fehler in der Video-Pipeline: {e}")

hauptprogramm()
