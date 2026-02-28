"""Spotify export JSON parser.

Handles multiple Spotify export formats:
- StreamingHistory*.json  (basic: track, artist, ms_played, endTime)
- endsong_*.json          (extended: track, artist, ms_played, ts, album, etc.)
- Spotify "Account data" messages format

Normalizes all formats to a consistent DataFrame-like structure for ranking.
"""

from __future__ import annotations

import csv
import json
import os
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PlayRecord:
    """A single normalized play record."""

    played_at: str
    track_name: str
    artist_name: str
    ms_played: int = 0
    spotify_uri: str = ""
    album_name: str = ""


@dataclass
class RankedTrack:
    """A track with its ranking data."""

    rank: int
    track_name: str
    artist_name: str
    play_count: int
    total_ms: int
    spotify_uri: str = ""
    album_name: str = ""


def detect_format(data: list[dict[str, Any]]) -> str:
    """Detect which Spotify export format a list of records belongs to.

    Returns:
        One of: "streaming_history", "extended_history", "unknown"
    """
    if not data:
        return "unknown"

    sample = data[0]
    keys = set(sample.keys())

    if "master_metadata_track_name" in keys or "ts" in keys:
        return "extended_history"
    if "trackName" in keys or "artistName" in keys:
        return "streaming_history"
    return "unknown"


def parse_streaming_history(records: list[dict[str, Any]]) -> list[PlayRecord]:
    """Parse basic StreamingHistory*.json format."""
    plays = []
    for rec in records:
        track = rec.get("trackName") or rec.get("master_metadata_track_name") or ""
        artist = rec.get("artistName") or rec.get("master_metadata_album_artist_name") or ""
        ms = rec.get("msPlayed", 0) or rec.get("ms_played", 0)
        played_at = rec.get("endTime") or rec.get("ts") or ""
        if track and artist:
            plays.append(PlayRecord(played_at=played_at, track_name=track, artist_name=artist, ms_played=ms))
    return plays


def parse_extended_history(
    records: list[dict[str, Any]], min_ms: int = 30000
) -> list[PlayRecord]:
    """Parse extended endsong_*.json format.

    Args:
        records: Raw JSON records from the export.
        min_ms: Minimum ms_played to count as a real play (default 30s).
              Filters out skips and accidental plays.
    """
    plays = []
    for rec in records:
        track = rec.get("master_metadata_track_name") or ""
        artist = rec.get("master_metadata_album_artist_name") or ""
        ms = rec.get("ms_played", 0) or 0
        played_at = rec.get("ts") or ""
        uri = rec.get("spotify_track_uri") or ""
        album = rec.get("master_metadata_album_album_name") or ""
        if track and artist and ms >= min_ms:
            plays.append(PlayRecord(
                played_at=played_at,
                track_name=track,
                artist_name=artist,
                ms_played=ms,
                spotify_uri=uri,
                album_name=album,
            ))
    return plays


def load_export(path: str) -> list[PlayRecord]:
    """Load a Spotify export file or directory of JSON files.

    Args:
        path: Path to a single JSON file or a directory containing multiple.

    Returns:
        List of normalized PlayRecord objects.
    """
    p = Path(path)
    files: list[Path] = []

    if p.is_file():
        files = [p]
    elif p.is_dir():
        files = sorted(p.glob("*.json"))
    else:
        raise FileNotFoundError(f"Path not found: {path}")

    all_plays: list[PlayRecord] = []

    for f in files:
        with open(f, encoding="utf-8") as fh:
            data = json.load(fh)

        if not isinstance(data, list):
            continue

        fmt = detect_format(data)
        if fmt == "extended_history":
            all_plays.extend(parse_extended_history(data))
        elif fmt == "streaming_history":
            all_plays.extend(parse_streaming_history(data))
        # Skip unknown formats silently

    return all_plays


def rank_tracks(plays: list[PlayRecord], top_n: int = 2000) -> list[RankedTrack]:
    """Rank tracks by play count (tie-break by total ms_played).

    Args:
        plays: List of play records.
        top_n: Number of top tracks to return.

    Returns:
        Sorted list of RankedTrack objects.
    """
    # Count plays and total ms per (track, artist) pair
    play_counts: Counter[tuple[str, str]] = Counter()
    total_ms: dict[tuple[str, str], int] = {}
    track_uris: dict[tuple[str, str], str] = {}
    track_albums: dict[tuple[str, str], str] = {}

    for p in plays:
        key = (p.track_name, p.artist_name)
        play_counts[key] += 1
        total_ms[key] = total_ms.get(key, 0) + p.ms_played
        # Keep the most recent non-empty URI and album
        if p.spotify_uri:
            track_uris[key] = p.spotify_uri
        if p.album_name:
            track_albums[key] = p.album_name

    # Sort by play count desc, then total ms desc
    sorted_tracks = sorted(
        play_counts.keys(),
        key=lambda k: (play_counts[k], total_ms.get(k, 0)),
        reverse=True,
    )

    ranked: list[RankedTrack] = []
    for i, key in enumerate(sorted_tracks[:top_n], start=1):
        track_name, artist_name = key
        ranked.append(
            RankedTrack(
                rank=i,
                track_name=track_name,
                artist_name=artist_name,
                play_count=play_counts[key],
                total_ms=total_ms.get(key, 0),
                spotify_uri=track_uris.get(key, ""),
                album_name=track_albums.get(key, ""),
            )
        )

    return ranked


def export_csv(ranked: list[RankedTrack], output_path: str) -> None:
    """Write ranked tracks to a CSV file."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["rank", "track_name", "artist_name", "album_name", "play_count", "total_ms", "total_hours", "spotify_uri"])
        for t in ranked:
            hours = round(t.total_ms / 3_600_000, 2)
            writer.writerow([t.rank, t.track_name, t.artist_name, t.album_name, t.play_count, t.total_ms, hours, t.spotify_uri])


def export_playlist_seed(ranked: list[RankedTrack], output_path: str) -> None:
    """Write a JSON file with track+artist pairs for playlist building."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    seed = [
        {
            "track_name": t.track_name,
            "artist_name": t.artist_name,
            "spotify_uri": t.spotify_uri,
        }
        for t in ranked
    ]
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(seed, fh, indent=2, ensure_ascii=False)


def print_stats(plays: list[PlayRecord], ranked: list[RankedTrack]) -> None:
    """Print summary statistics about the listening history."""
    total_ms = sum(p.ms_played for p in plays)
    total_hours = total_ms / 3_600_000
    unique_tracks = len({(p.track_name, p.artist_name) for p in plays})
    unique_artists = len({p.artist_name for p in plays})
    date_range = sorted({p.played_at[:10] for p in plays if p.played_at})
    with_uri = sum(1 for t in ranked if t.spotify_uri)

    print(f"\n{'=' * 50}")
    print(f"  SMUTZIGE HANSIE'S LISTENING STATS")
    print(f"{'=' * 50}")
    print(f"  Total plays (>30s):    {len(plays):,}")
    print(f"  Total listening time:  {total_hours:,.1f} hours ({total_hours / 24:.0f} days)")
    print(f"  Unique tracks:         {unique_tracks:,}")
    print(f"  Unique artists:        {unique_artists:,}")
    if date_range:
        print(f"  Date range:            {date_range[0]} to {date_range[-1]}")
    print(f"  Top {len(ranked)} with Spotify URI: {with_uri}/{len(ranked)} ({100 * with_uri / len(ranked):.1f}%)")
    print(f"{'=' * 50}")
