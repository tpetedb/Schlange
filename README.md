# Schlange

**Write Python in Old German. Run it for real.**

Schlange is a Germanized Python preprocessor that lets you write Python using archaic German keywords. It uses token-based rewriting (not naive text replacement) so keywords inside strings and comments are never touched.

It also powers the **CHAOTIC ENGINEERING PROGRAM** -- a fully automated pipeline that parses 6 years of Spotify history, generates a bombastic goodbye video, and sends a tri-lingual email invitation. One command. Pure chaos.

```python
# hello.schl.py
defn begruessung(name):
    sofern name ist Nichts:
        gibzurueck "Kein Name angegeben"
    gibzurueck f"Hallo {name}!"

verkuendet(begruessung("Welt"))
```

```
$ schlange run hello.schl.py
Hallo Welt!
```

---

## Quick Start

```bash
# Clone and install
git clone https://github.com/tpetedb/Schlange.git
cd Schlange
pip install -e ".[dev]"

# Run your first Schlange script
schlange run examples/hello.schl.py

# See the transpiled Python output
schlange emit examples/hello.schl.py

# Print the full keyword dictionary
schlange woerterbuch
```

## The Full Pipeline

One command to rule them all:

```bash
# Dry-run (no email sent)
schlange run tools/go.schl.py

# Actually send the email
schlange run tools/go.schl.py --send

# Skip video, just email
schlange run tools/go.schl.py --send --skip-video

# Only validate mandatory content
schlange run tools/go.schl.py --validate-only
```

### What it does

1. **Parses Spotify history** -- 83,364 plays across 6 years, ranked into the Tom 2000
2. **Generates video script** -- 8-scene German narration with SRT subtitles
3. **Renders video** -- placeholder backend (swap in a real API when ready)
4. **Extracts frames** -- key frames from reference video for email embedding
5. **Generates email** -- tri-lingual (DE/EN/NL) bombastic HTML invitation
6. **Validates everything** -- mandatory content checks (cow line, event date, coding refs)
7. **Sends email** -- SMTP with CID inline images (or dry-run)

## Features

- **Token-based transpiler** -- uses Python's `tokenize` module; strings and comments are never rewritten
- **CLI with subcommands** -- `run`, `emit`, `repl`, `woerterbuch`
- **Interactive REPL** -- `schlange repl` for live experimentation
- **Spotify integration** -- parse your listening history, rank tracks, build playlists
- **Video pipeline** -- provider-agnostic scene generation with placeholder backend
- **Email engine** -- tri-lingual HTML with CID images, Outlook-safe table layout
- **Validation** -- mandatory content checks that fail the build if anything is missing

## Project Structure

```
Schlange/
  schlange/              # Core package
    __init__.py
    cli.py               # Click CLI entrypoint
    keywords.py          # German -> Python keyword dictionary
    transpile.py         # Token-based transpiler
    validate.py          # Mandatory content validation
    spotify/             # Spotify integration
      parser.py          # Export JSON parser + ranking
      playlist.py        # Spotify API + playlist builder
    video/               # Video pipeline
      __init__.py        # Provider-agnostic pipeline
      script.py          # Script + subtitle generator
      frames.py          # Frame extraction from video
    email/               # Email engine
      template.py        # Tri-lingual HTML template
      sender.py          # SMTP sender with CID images
  examples/              # Demo scripts in Schlange
    hello.schl.py
    loops.schl.py
    fehler.schl.py
  tools/                 # Pipeline scripts
    go.schl.py           # Master orchestrator
    tom2000.schl.py      # Spotify data pipeline
    publish_tom2000.schl.py  # Playlist publisher
  video/
    spec.yaml            # 8-scene video specification
  assets/
    assets.json          # Scene storyboard (8 scenes)
  data/                  # Input data (gitignored)
  out/                   # Output artifacts (gitignored)
  tests/                 # pytest test suite
  dictionary.md          # Full keyword reference
  pyproject.toml         # Build config
```

## Keyword Reference (v0.1)

| Schlange | Python | Example |
|---|---|---|
| `importiert` | `import` | `importiert os` |
| `von` | `from` | `von os importiert path` |
| `als` | `as` | `importiert json als j` |
| `defn` | `def` | `defn gruessen():` |
| `klasse` | `class` | `klasse Tier:` |
| `sofern` | `if` | `sofern x > 0:` |
| `sofernschier` | `elif` | `sofernschier x == 0:` |
| `sonst` | `else` | `sonst:` |
| `solang` | `while` | `solang Wahrlich:` |
| `fuerwahr` | `for` | `fuerwahr i inwendig bereich(10):` |
| `inwendig` | `in` | `sofern x inwendig liste:` |
| `gibzurueck` | `return` | `gibzurueck ergebnis` |
| `brechet` | `break` | `brechet` |
| `fahrefort` | `continue` | `fahrefort` |
| `bestehe` | `pass` | `bestehe` |
| `probiert` | `try` | `probiert:` |
| `ausser` | `except` | `ausser ValueError:` |
| `endlich` | `finally` | `endlich:` |
| `werfet` | `raise` | `werfet ValueError("Nein!")` |
| `alsfehler` | `as` | `ausser Exception alsfehler e:` |
| `Wahrlich` | `True` | `fertig = Wahrlich` |
| `Falschlich` | `False` | `aktiv = Falschlich` |
| `Nichts` | `None` | `gibzurueck Nichts` |
| `verkuendet` | `print` | `verkuendet("Hallo!")` |

See [dictionary.md](dictionary.md) for the complete reference including built-in function aliases.

## Spotify Integration

### Parse Your Listening History

```bash
schlange run tools/tom2000.schl.py
```

Produces in `out/`:

- `tom2000_rangliste.csv` -- 2000 tracks ranked by play count
- `tom2000_playlist_seed.json` -- track+artist+URI pairs
- `tom2000_uris.json` -- Spotify URIs for playlist creation
- `tom2000_zusammenfassung.txt` -- text summary

### Publish the Playlist

```bash
# Set up Spotify API credentials
cp .env.example .env
# Edit .env with your SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET

schlange run tools/publish_tom2000.schl.py
```

> **Note**: Your Spotify app must have your email added in
> [Developer Dashboard > User Management](https://developer.spotify.com/dashboard)
> if the app is in Development mode.

## Video Pipeline

The video pipeline generates a script, subtitles, and placeholder video from `video/spec.yaml`:

```bash
schlange run tools/go.schl.py --skip-email
```

Uses a placeholder backend by default (creates stub files). Swap in a real video API by implementing the `VideoBackend` interface in `schlange/video/__init__.py`.

## Email Engine

Generates a tri-lingual (DE/EN/NL) bombastic HTML email with:

- CID inline images from extracted video frames
- Outlook-safe table-based layout
- All mandatory content: cow line, event date, closing line
- SMTP sending with dry-run support

```bash
# Generate email only (dry-run)
schlange run tools/go.schl.py --skip-video

# Actually send
schlange run tools/go.schl.py --send --skip-video
```

## Configuration

Copy `.env.example` to `.env` and configure:

| Variable | Purpose |
|----------|---------|
| `SPOTIPY_CLIENT_ID` | Spotify app client ID |
| `SPOTIPY_CLIENT_SECRET` | Spotify app client secret |
| `GOODBYE_DATE` | Event date (default: 2026-03-12) |
| `GOODBYE_LOCATION` | Event location (default: De Vierkant) |
| `EMAIL_FROM` | Sender email address |
| `SMTP_HOST` | SMTP server hostname |
| `RECIPIENTS` | Comma-separated recipient emails |

## Development

```bash
pip install -e ".[dev]"
pytest
schlange emit examples/loops.schl.py  # inspect transpiler output
```

## License

Apache 2.0
