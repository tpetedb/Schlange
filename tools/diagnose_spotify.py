"""Spotify 403 Diagnostic -- tests auth + add tracks step by step."""

from dotenv import load_dotenv

load_dotenv()

import os
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth

SCOPES = "playlist-modify-private playlist-modify-public"
TEST_URI = "spotify:track:4cOdK2wGLETKBW3PvgPWqT"  # Never Gonna Give You Up


def main() -> None:
    print("\n=== SPOTIFY 403 DIAGNOSTIC ===\n")

    # Step 1: Check env vars
    print("[1] Environment check")
    cid = os.getenv("SPOTIPY_CLIENT_ID", "")
    ruri = os.getenv("SPOTIPY_REDIRECT_URI", "")
    print(f"    Client ID: {cid[:8]}...{cid[-4:]}" if len(cid) > 12 else f"    Client ID: {cid}")
    print(f"    Redirect URI: {ruri}")
    print(f"    Scopes: {SCOPES}")

    # Step 2: Fresh auth (no cache)
    print("\n[2] Authentication (fresh -- no cache)")
    print("    Copy the URL below, open in browser, authorize, paste the redirect URL back.\n")
    auth = SpotifyOAuth(scope=SCOPES, open_browser=False)
    sp = spotipy.Spotify(auth_manager=auth)
    me = sp.current_user()
    uid = me["id"]
    print(f"\n    Authenticated as: {uid}")
    print(f"    Display name: {me.get('display_name', 'n/a')}")

    # Step 3: Check token
    print("\n[3] Token check")
    token_info = auth.get_cached_token()
    print(f"    Scopes in token: {token_info.get('scope', 'NONE')}")
    token = token_info["access_token"]

    # Step 4: Create playlist via /me/playlists
    print("\n[4] Create test playlist via /me/playlists")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.post(
        "https://api.spotify.com/v1/me/playlists",
        headers=headers,
        json={"name": "Schlange Diagnostic", "description": "Can delete", "public": False},
        timeout=30,
    )
    print(f"    Status: {resp.status_code}")
    if resp.status_code != 201:
        print(f"    FAILED: {resp.text[:200]}")
        return

    pl = resp.json()
    pid = pl["id"]
    print(f"    Playlist ID: {pid}")

    # Step 5: Add 1 track via direct API
    print(f"\n[5] Add 1 track to playlist ({TEST_URI})")
    resp2 = requests.post(
        f"https://api.spotify.com/v1/playlists/{pid}/tracks",
        headers=headers,
        json={"uris": [TEST_URI]},
        timeout=30,
    )
    print(f"    Status: {resp2.status_code}")
    if resp2.status_code in (200, 201):
        print("    SUCCESS! Track added.")
        print("\n    >>> The 403 issue is RESOLVED. You can run publish_tom2000 now.")
    else:
        print(f"    FAILED: {resp2.text[:300]}")
        print("\n    >>> Still 403. Checklist:")
        print("    1. Go to https://developer.spotify.com/dashboard")
        print("    2. Open your app (Client ID starts with 1c019fb0)")
        print("    3. Click 'Settings'")
        print("    4. Check 'Redirect URIs' includes: http://127.0.0.1:8888/callback")
        print("    5. Scroll to 'User Management'")
        print("    6. Verify your Spotify email is listed (the email you log in with)")
        print("    7. If not, add it and SAVE")
        print("    8. Important: the email must match your Spotify account exactly")
        print(f"    9. Your Spotify user ID is: {uid}")
        print("   10. Try requesting 'Extended Quota Mode' if User Management is correct")

    # Step 6: Try via spotipy method too
    print(f"\n[6] Also trying via spotipy.playlist_add_items...")
    try:
        sp.playlist_add_items(pid, [TEST_URI])
        print("    SUCCESS via spotipy!")
    except Exception as e:
        print(f"    FAILED: {e}")

    # Cleanup note
    print(f"\n[7] Cleanup: delete 'Schlange Diagnostic' playlist from your Spotify library")
    print("    (Also delete any 'Tom 2000' / 'Test Schlange' empty playlists)")
    print("\n=== END DIAGNOSTIC ===\n")


if __name__ == "__main__":
    main()
