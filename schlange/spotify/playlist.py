"""Spotify API integration -- search, match, and playlist creation.

Uses spotipy for OAuth and API calls.
Requires SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI in .env.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
except ImportError:
    spotipy = None  # type: ignore[assignment]
    SpotifyOAuth = None  # type: ignore[assignment, misc]


@dataclass
class MatchResult:
    """Result of matching a track against Spotify's catalog."""

    track_name: str
    artist_name: str
    spotify_uri: str | None
    spotify_name: str | None
    spotify_artist: str | None
    score: float
    matched: bool


class PlaylistBuilder:
    """Build a Spotify playlist from a ranked track list.

    Usage:
        builder = PlaylistBuilder()
        builder.authenticate()
        results = builder.resolve_tracks(seed_path="out/playlist_seed.json")
        builder.create_playlist(results, name="Tom 2000")
    """

    SCOPES = "playlist-modify-private playlist-modify-public"
    BATCH_SIZE = 100  # Spotify max per add-tracks call

    def __init__(self, cache_path: str = ".spotify_cache.json") -> None:
        self._sp: Any = None
        self._user_id: str | None = None
        self._cache_path = cache_path
        self._resolution_cache: dict[str, MatchResult] = {}
        self._load_cache()

    def _load_cache(self) -> None:
        """Load previously resolved tracks from disk cache."""
        if os.path.exists(self._cache_path):
            with open(self._cache_path, encoding="utf-8") as fh:
                data = json.load(fh)
            for item in data:
                key = f"{item['track_name']}|||{item['artist_name']}"
                self._resolution_cache[key] = MatchResult(**item)

    def _save_cache(self) -> None:
        """Persist resolution cache to disk."""
        items = []
        for mr in self._resolution_cache.values():
            items.append({
                "track_name": mr.track_name,
                "artist_name": mr.artist_name,
                "spotify_uri": mr.spotify_uri,
                "spotify_name": mr.spotify_name,
                "spotify_artist": mr.spotify_artist,
                "score": mr.score,
                "matched": mr.matched,
            })
        with open(self._cache_path, "w", encoding="utf-8") as fh:
            json.dump(items, fh, indent=2, ensure_ascii=False)

    def authenticate(self) -> None:
        """Authenticate with Spotify using OAuth Authorization Code flow."""
        if spotipy is None:
            raise ImportError("spotipy is required: pip install spotipy")

        auth_manager = SpotifyOAuth(scope=self.SCOPES)
        self._sp = spotipy.Spotify(auth_manager=auth_manager)
        self._user_id = self._sp.current_user()["id"]

    def _create_playlist_via_me(self, name: str, description: str, public: bool) -> dict:
        """Create a playlist using the /me/playlists endpoint.

        This avoids the /users/{user_id}/playlists endpoint which can return 403
        for apps in Spotify's Development mode if the user hasn't been added
        to the app's User Management list.

        Falls back to the user-id approach if /me/ fails too.
        """
        import requests

        token = self._sp.auth_manager.get_access_token(as_dict=False)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {
            "name": name,
            "description": description,
            "public": public,
        }

        # Try /me/playlists first
        resp = requests.post(
            "https://api.spotify.com/v1/me/playlists",
            headers=headers,
            json=payload,
            timeout=30,
        )

        if resp.status_code == 201:
            return resp.json()

        # Fallback: try the user-id endpoint
        print(f"  /me/playlists returned {resp.status_code}, trying user-id endpoint...")
        resp2 = requests.post(
            f"https://api.spotify.com/v1/users/{self._user_id}/playlists",
            headers=headers,
            json=payload,
            timeout=30,
        )

        if resp2.status_code == 201:
            return resp2.json()

        # Both failed -- raise with details
        error_detail = resp.json() if resp.status_code != 201 else resp2.json()
        raise RuntimeError(
            f"Failed to create playlist (status {resp.status_code} / {resp2.status_code}). "
            f"Detail: {error_detail}. "
            f"If 403: go to https://developer.spotify.com/dashboard, open your app, "
            f"go to Settings > User Management, and add your Spotify email address."
        )

    def _add_tracks_via_api(self, playlist_id: str, uris: list[str]) -> None:
        """Add tracks to a playlist using direct API calls.

        Uses requests.post to /playlists/{id}/tracks instead of spotipy's
        playlist_add_items -- works around 403 in Spotify Development mode.
        """
        import requests

        token = self._sp.auth_manager.get_access_token(as_dict=False)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

        resp = requests.post(url, headers=headers, json={"uris": uris}, timeout=30)
        if resp.status_code not in (200, 201):
            raise RuntimeError(
                f"Failed to add tracks (HTTP {resp.status_code}): {resp.text}"
            )

    def _search_track(self, track_name: str, artist_name: str) -> MatchResult:
        """Search Spotify for a track and return the best match."""
        cache_key = f"{track_name}|||{artist_name}"
        if cache_key in self._resolution_cache:
            return self._resolution_cache[cache_key]

        query = f"track:{track_name} artist:{artist_name}"
        try:
            results = self._sp.search(q=query, type="track", limit=5)
        except Exception:
            # Rate limit or error -- return unmatched
            return MatchResult(
                track_name=track_name,
                artist_name=artist_name,
                spotify_uri=None,
                spotify_name=None,
                spotify_artist=None,
                score=0.0,
                matched=False,
            )

        tracks = results.get("tracks", {}).get("items", [])
        if not tracks:
            result = MatchResult(
                track_name=track_name,
                artist_name=artist_name,
                spotify_uri=None,
                spotify_name=None,
                spotify_artist=None,
                score=0.0,
                matched=False,
            )
            self._resolution_cache[cache_key] = result
            self._save_cache()
            return result

        # Score candidates
        best_score = 0.0
        best_track = tracks[0]

        for t in tracks:
            score = 0.0
            sp_name = t.get("name", "").lower()
            sp_artists = [a.get("name", "").lower() for a in t.get("artists", [])]

            # Track name similarity (simple)
            if track_name.lower() == sp_name:
                score += 1.0
            elif track_name.lower() in sp_name or sp_name in track_name.lower():
                score += 0.5

            # Artist match
            if artist_name.lower() in sp_artists:
                score += 1.0
            elif any(artist_name.lower() in a for a in sp_artists):
                score += 0.5

            if score > best_score:
                best_score = score
                best_track = t

        result = MatchResult(
            track_name=track_name,
            artist_name=artist_name,
            spotify_uri=best_track["uri"],
            spotify_name=best_track["name"],
            spotify_artist=", ".join(a["name"] for a in best_track.get("artists", [])),
            score=best_score,
            matched=best_score >= 0.5,
        )

        self._resolution_cache[cache_key] = result
        self._save_cache()
        return result

    def resolve_tracks(self, seed_path: str, delay: float = 0.1) -> list[MatchResult]:
        """Resolve a playlist seed JSON to Spotify track URIs.

        Args:
            seed_path: Path to the playlist_seed.json file.
            delay: Seconds between API calls (rate limit protection).

        Returns:
            List of MatchResult objects.
        """
        with open(seed_path, encoding="utf-8") as fh:
            seed = json.load(fh)

        results: list[MatchResult] = []
        for i, entry in enumerate(seed):
            track_name = entry["track_name"]
            artist_name = entry["artist_name"]
            result = self._search_track(track_name, artist_name)
            results.append(result)

            if i % 50 == 0 and i > 0:
                matched = sum(1 for r in results if r.matched)
                print(f"  Resolved {i}/{len(seed)} tracks ({matched} matched)")

            time.sleep(delay)

        return results

    def create_playlist(
        self,
        results: list[MatchResult],
        name: str = "Tom 2000",
        description: str = "Generated from my listening history via Schlange",
        public: bool = False,
    ) -> str:
        """Create a Spotify playlist and add matched tracks.

        Args:
            results: List of MatchResult from resolve_tracks.
            name: Playlist name.
            description: Playlist description.
            public: Whether the playlist is public.

        Returns:
            The Spotify playlist URL.
        """
        if not self._sp or not self._user_id:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        # Create playlist using /me/playlists (avoids user-id 403 in dev mode)
        playlist = self._create_playlist_via_me(name, description, public)
        playlist_id = playlist["id"]
        playlist_url = playlist["external_urls"]["spotify"]

        # Collect matched URIs
        uris = [r.spotify_uri for r in results if r.matched and r.spotify_uri]

        # Add in batches of 100 via direct API
        for i in range(0, len(uris), self.BATCH_SIZE):
            batch = uris[i : i + self.BATCH_SIZE]
            self._add_tracks_via_api(playlist_id, batch)

        return playlist_url

    def create_playlist_from_uris(
        self,
        uris: list[str],
        name: str = "Tom 2000",
        description: str = "Generated from my listening history via Schlange",
        public: bool = False,
    ) -> str:
        """Create a Spotify playlist directly from a list of track URIs.

        Skips the search/resolve step entirely -- use when URIs are already
        known (e.g. from the Spotify Extended Streaming History export).

        Args:
            uris: List of Spotify track URIs (spotify:track:...).
            name: Playlist name.
            description: Playlist description.
            public: Whether the playlist is public.

        Returns:
            The Spotify playlist URL.
        """
        if not self._sp or not self._user_id:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        # Filter out empty/invalid URIs
        valid_uris = [u for u in uris if u and u.startswith("spotify:track:")]
        print(f"  {len(valid_uris)} valid URIs out of {len(uris)} total")

        # Create playlist using /me/playlists (avoids user-id 403 in dev mode)
        playlist = self._create_playlist_via_me(name, description, public)
        playlist_id = playlist["id"]
        playlist_url = playlist["external_urls"]["spotify"]
        print(f"  Playlist created: {playlist_url}")

        # Add in batches of 100 via direct API
        total_batches = (len(valid_uris) + self.BATCH_SIZE - 1) // self.BATCH_SIZE
        for i in range(0, len(valid_uris), self.BATCH_SIZE):
            batch = valid_uris[i : i + self.BATCH_SIZE]
            batch_num = i // self.BATCH_SIZE + 1
            self._add_tracks_via_api(playlist_id, batch)
            print(f"  Batch {batch_num}/{total_batches}: added {len(batch)} tracks")

        print(f"  Total: {len(valid_uris)} tracks added to '{name}'")
        return playlist_url

    def generate_report(self, results: list[MatchResult], output_path: str | None = None) -> str:
        """Generate a resolution report.

        Returns:
            Report string with match statistics and unmatched tracks.
        """
        total = len(results)
        matched = sum(1 for r in results if r.matched)
        unmatched = [r for r in results if not r.matched]

        lines = [
            f"=== Track Resolution Report ===",
            f"Total tracks: {total}",
            f"Matched: {matched} ({100 * matched / total:.1f}%)" if total else "Matched: 0",
            f"Unmatched: {len(unmatched)}",
            "",
        ]

        if unmatched:
            lines.append("--- Unmatched Tracks ---")
            for r in unmatched:
                lines.append(f"  {r.artist_name} - {r.track_name}")

        report = "\n".join(lines)

        if output_path:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as fh:
                fh.write(report)

        return report
