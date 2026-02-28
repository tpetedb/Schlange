# Schlange

**Write Python in Old German. Run it for real.**

Schlange is a Germanized Python preprocessor that lets you write Python using archaic German keywords. It uses token-based rewriting (not naive text replacement) so keywords inside strings and comments are never touched.

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

## Features

- **Token-based transpiler** -- uses Python's `tokenize` module; strings and comments are never rewritten
- **CLI with subcommands** -- `run`, `emit`, `repl`, `woerterbuch`
- **Interactive REPL** -- `schlange repl` for live experimentation
- **Spotify integration** -- parse your listening history, rank tracks, build playlists
- **Video pipeline** -- provider-agnostic scene generation with placeholder backend

## Project Structure

```
Schlange/
  schlange/              # Core package
    __init__.py
    cli.py               # Click CLI entrypoint
    keywords.py          # German -> Python keyword dictionary
    transpile.py         # Token-based transpiler
    spotify/             # Spotify integration (B1 + B2)
      parser.py          # Export JSON parser + ranking
      playlist.py        # Spotify API search + playlist builder
    video/               # Video pipeline (C1-C3)
      __init__.py        # Provider-agnostic pipeline + placeholder backend
  examples/              # Demo scripts in Schlange
    hello.schl.py        # Hello World
    loops.schl.py        # Loops, conditionals, functions
    fehler.schl.py       # Try/except with custom errors
    spotify_parse.schl.py  # Spotify export parser
  tools/                 # Utility scripts
    make_playlist.schl.py  # Spotify playlist builder
    make_video.schl.py     # Video generation pipeline
  assets/                # Video storyboard + media
    assets.json          # Scene definitions
  tests/                 # pytest test suite
    test_transpile.py    # Transpiler tests
    test_cli.py          # CLI integration tests
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

### B1: Parse Your Listening History

```bash
schlange run examples/spotify_parse.schl.py --input ~/spotify_export/ --out out/
```

Produces:

- `out/top_tracks.csv` -- ranked by play count
- `out/playlist_seed.json` -- track+artist pairs for the playlist builder

### B2: Build the Tom 2000 Playlist

```bash
# Set up Spotify API credentials
cp .env.example .env
# Edit .env with your SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI

schlange run tools/make_playlist.schl.py --top 2000 --public false
```

Produces:

- A Spotify playlist named "Tom 2000"
- `out/resolution_report.txt` with match statistics

## Video Pipeline

```bash
# Edit assets/assets.json with your storyboard
schlange run tools/make_video.schl.py
```

Uses a placeholder backend by default (creates stub files). Swap in a real video API by implementing the `VideoBackend` interface.

## Development

```bash
pip install -e ".[dev]"
pytest
schlange emit examples/loops.schl.py  # inspect transpiler output
```

## License

Apache 2.0
