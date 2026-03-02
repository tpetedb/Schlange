"""Reminder email for DIE LETSTE PARTY MIT SMUTZIGE HANSIE.

Sends a tri-lingual reminder that also explains the Schlange project,
shares the GitHub repo and the Tom 2000 Spotify playlist.

Usage:
    source .venv/bin/activate
    python tools/reminder.py              # dry-run
    python tools/reminder.py --send       # actually send
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schlange.email.sender import load_recipients, send_email

load_dotenv()

REPO_URL = "https://github.com/tpetedb/Schlange"
GAME_URL = "https://tpetedb.github.io/Schlange/game/schlange.html"
PLAYLIST_URL = os.getenv(
    "SPOTIFY_PLAYLIST_URL",
    "https://open.spotify.com/playlist/5krqck3JrIb2OyUEUPpufq?si=503fa213af9249d0",
)

SUBJECT = "REMINDER: DIE LETSTE PARTY MIT SMUTZIGE HANSIE -- Donnerstag, 12. Maerz 2026"


def build_reminder_html() -> str:
    """Build the tri-lingual reminder email HTML."""

    blocks = {
        "de": {
            "lang_label": "DEUTSCH",
            "greeting": "Liebe Kolleginnen und Kollegen,",
            "reminder": "Dies ist eine freundliche Erinnerung:",
            "party_line": (
                "<strong>Smutzige Hansie verlasst YoungOnes</strong> -- " "und seine letzte Party ist naechste Woche!"
            ),
            "event_title": "DAS EVENT",
            "event_date": "Donnerstag, 12. Maerz 2026",
            "event_location": "YoungOnes Office",
            "project_title": "WAS IST SCHLANGE?",
            "project_desc": (
                "Schlange ist ein Python-Pr&auml;prozessor mit deutschen Schl&uuml;sselw&ouml;rtern. "
                "Statt <code>print</code> schreibst du <code>verkuendet</code>. "
                "Statt <code>return</code> schreibst du <code>gibzurueck</code>. "
                "Statt <code>if/else</code> schreibst du <code>sofern/sonst</code>. "
                "35 Schl&uuml;sselw&ouml;rter. 25 Built-ins. Alles auf Deutsch. "
                "Alles unn&ouml;tig. Alles wundersch&ouml;n."
            ),
            "project_extras": (
                "Es kann auch deine Spotify-H&ouml;rgeschichte der letzten 6 Jahre parsen, "
                "KI-Videos mit Google Veo generieren, und dreisprachige E-Mails versenden. "
                "Zum Beispiel diese hier."
            ),
            "repo_label": "Den Code anschauen",
            "playlist_title": "TOM 2000 PLAYLIST",
            "playlist_desc": (
                "6 Jahre Spotify-H&ouml;rgeschichte, gerankt zu 2000 Tracks. "
                "Von Marconi Union bis Goldband. Perfekt f&uuml;r die Party."
            ),
            "playlist_label": "Playlist auf Spotify &ouml;ffnen",
            "game_title": "SCHLANGE SPIELEN -- GEWINNE DIE KUH!",
            "game_desc": (
                "Auf der Party steht eine <strong>3,5 Meter hohe Bierkuh</strong>. "
                "Wer den h&ouml;chsten Score in Schlange hat, darf als Erster die Kuh melken! "
                "Spiel jetzt, schick deinen Score, und sichere dir den ersten Schluck."
            ),
            "game_label": "Jetzt spielen",
            "closing": "Sei dabei -- oder sei ein Viereck.",
        },
        "en": {
            "lang_label": "ENGLISH",
            "greeting": "Dear colleagues,",
            "reminder": "This is a friendly reminder:",
            "party_line": (
                "<strong>Smutzige Hansie is leaving YoungOnes</strong> -- " "and his last party is next week!"
            ),
            "event_title": "THE EVENT",
            "event_date": "Thursday, 12 March 2026",
            "event_location": "YoungOnes Office",
            "project_title": "WHAT IS SCHLANGE?",
            "project_desc": (
                "Schlange is a Python preprocessor with German keywords. "
                "Instead of <code>print</code> you write <code>verkuendet</code>. "
                "Instead of <code>return</code> you write <code>gibzurueck</code>. "
                "Instead of <code>if/else</code> you write <code>sofern/sonst</code>. "
                "35 keywords. 25 built-ins. All in German. "
                "All unnecessary. All beautiful."
            ),
            "project_extras": (
                "It can also parse 6 years of your Spotify listening history, "
                "generate AI videos with Google Veo, and send tri-lingual emails. "
                "Like this one, for example."
            ),
            "repo_label": "Check out the code",
            "playlist_title": "TOM 2000 PLAYLIST",
            "playlist_desc": (
                "6 years of Spotify listening history, ranked into 2000 tracks. "
                "From Marconi Union to Goldband. Perfect party soundtrack."
            ),
            "playlist_label": "Open playlist on Spotify",
            "game_title": "PLAY SCHLANGE -- WIN THE COW!",
            "game_desc": (
                "At the party there will be a <strong>3.5 meter tall beer cow</strong>. "
                "Whoever has the highest Schlange score gets to milk the cow first! "
                "Play now, submit your score, and secure the first sip."
            ),
            "game_label": "Play now",
            "closing": "Be there -- or be a square.",
        },
        "nl": {
            "lang_label": "NEDERLANDS",
            "greeting": "Beste collega's,",
            "reminder": "Dit is een vriendelijke herinnering:",
            "party_line": (
                "<strong>Smutzige Hansie verlaat YoungOnes</strong> -- " "en zijn laatste feest is volgende week!"
            ),
            "event_title": "HET EVENT",
            "event_date": "Donderdag 12 maart 2026",
            "event_location": "YoungOnes Office",
            "project_title": "WAT IS SCHLANGE?",
            "project_desc": (
                "Schlange is een Python-preprocessor met Duitse trefwoorden. "
                "In plaats van <code>print</code> schrijf je <code>verkuendet</code>. "
                "In plaats van <code>return</code> schrijf je <code>gibzurueck</code>. "
                "In plaats van <code>if/else</code> schrijf je <code>sofern/sonst</code>. "
                "35 trefwoorden. 25 ingebouwde functies. Alles in het Duits. "
                "Alles onnodig. Alles prachtig."
            ),
            "project_extras": (
                "Het kan ook je Spotify-luistergeschiedenis van de afgelopen 6 jaar parsen, "
                "AI-video's genereren met Google Veo, en drietalige e-mails versturen. "
                "Zoals deze, bijvoorbeeld."
            ),
            "repo_label": "Bekijk de code",
            "playlist_title": "TOM 2000 PLAYLIST",
            "playlist_desc": (
                "6 jaar Spotify-luistergeschiedenis, gerankt in 2000 nummers. "
                "Van Marconi Union tot Goldband. Perfecte party-soundtrack."
            ),
            "playlist_label": "Open playlist op Spotify",
            "game_title": "SPEEL SCHLANGE -- WIN DE KOE!",
            "game_desc": (
                "Op het feest staat een <strong>3,5 meter hoge bierkoe</strong>. "
                "Wie de hoogste Schlange-score heeft, mag als eerste de koe melken! "
                "Speel nu, stuur je score, en verzeker je van de eerste slok."
            ),
            "game_label": "Nu spelen",
            "closing": "Wees erbij -- of wees een vierkant.",
        },
    }

    lang_html = ""
    for lang in ["de", "en", "nl"]:
        c = blocks[lang]
        lang_html += f"""
    <!-- === {c['lang_label']} === -->
    <tr>
        <td style="background:linear-gradient(90deg,#F04923,#FFBF00);padding:12px 30px;">
            <h2 style="margin:0;color:#000;font-size:20px;letter-spacing:3px;">=== {c['lang_label']} ===</h2>
        </td>
    </tr>
    <tr>
        <td style="padding:25px 30px;">
            <p style="font-size:16px;margin:0 0 10px;">{c['greeting']}</p>
            <p style="font-size:18px;font-weight:bold;color:#FFBF00;margin:0 0 10px;">&#128227; {c['reminder']}</p>
            <p style="font-size:16px;line-height:1.6;">{c['party_line']}</p>
        </td>
    </tr>

    <!-- Event block -->
    <tr>
        <td style="padding:25px 30px;text-align:center;background:#111;">
            <h2 style="color:#F04923;font-size:22px;margin:0 0 10px;">&#128165; {c['event_title']}</h2>
            <p style="font-size:24px;font-weight:bold;color:#FFBF00;margin:0;">{c['event_date']}</p>
            <p style="font-size:18px;color:#fff;margin:5px 0 0;">{c['event_location']}</p>
        </td>
    </tr>

    <!-- Schlange project -->
    <tr>
        <td style="padding:25px 30px;">
            <h3 style="color:#00A86B;font-size:18px;margin:0 0 10px;">&#128013; {c['project_title']}</h3>
            <p style="font-size:15px;line-height:1.6;color:#ccc;">{c['project_desc']}</p>
            <p style="font-size:15px;line-height:1.6;color:#ccc;margin-top:10px;">{c['project_extras']}</p>
            <p style="margin-top:15px;">
                <a href="{REPO_URL}" style="display:inline-block;background:#0067A5;color:#fff;padding:10px 20px;text-decoration:none;border-radius:4px;font-weight:bold;">&#128187; {c['repo_label']}</a>
            </p>
        </td>
    </tr>

    <!-- Spotify playlist -->
    <tr>
        <td style="padding:25px 30px;background:#111;">
            <h3 style="color:#1DB954;font-size:18px;margin:0 0 10px;">&#127925; {c['playlist_title']}</h3>
            <p style="font-size:15px;line-height:1.6;color:#ccc;">{c['playlist_desc']}</p>
            <p style="margin-top:15px;">
                <a href="{PLAYLIST_URL}" style="display:inline-block;background:#1DB954;color:#fff;padding:10px 20px;text-decoration:none;border-radius:20px;font-weight:bold;">&#9654; {c['playlist_label']}</a>
            </p>
        </td>
    </tr>

    <!-- Game -->
    <tr>
        <td style="padding:25px 30px;">
            <h3 style="color:#F04923;font-size:18px;margin:0 0 10px;">&#127918; {c['game_title']}</h3>
            <p style="font-size:15px;line-height:1.6;color:#ccc;">{c['game_desc']}</p>
            <p style="margin-top:15px;">
                <a href="{GAME_URL}" style="display:inline-block;background:#F04923;color:#fff;padding:10px 20px;text-decoration:none;border-radius:4px;font-weight:bold;">&#128013; {c['game_label']}</a>
            </p>
        </td>
    </tr>

    <!-- Closing -->
    <tr>
        <td style="padding:20px 30px;text-align:center;">
            <p style="font-size:20px;font-weight:bold;font-style:italic;color:#FFBF00;margin:0;">{c['closing']}</p>
        </td>
    </tr>
    <tr><td style="padding:0;"><hr style="border:none;border-top:2px dashed #333;margin:0;" /></td></tr>
    """

    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>REMINDER -- DIE LETSTE PARTY MIT SMUTZIGE HANSIE</title>
</head>
<body style="margin:0;padding:0;background:#000;color:#fff;font-family:Arial,Helvetica,sans-serif;">

<!--[if mso]>
<table role="presentation" width="700" align="center" cellpadding="0" cellspacing="0"><tr><td>
<![endif]-->

<table role="presentation" cellpadding="0" cellspacing="0" style="max-width:700px;margin:0 auto;width:100%;background:#0a0a0a;border:2px solid #F04923;">

    <!-- HEADER -->
    <tr>
        <td style="background:repeating-linear-gradient(45deg,#000,#000 10px,#FFBF00 10px,#FFBF00 20px);padding:5px 0;">
        </td>
    </tr>
    <tr>
        <td style="background:#000;padding:30px;text-align:center;">
            <h1 style="margin:0;font-size:26px;color:#F04923;letter-spacing:4px;">&#128276; REMINDER &#128276;</h1>
            <h1 style="margin:10px 0 0;font-size:24px;color:#FFBF00;letter-spacing:3px;">DIE LETSTE PARTY MIT SMUTZIGE HANSIE</h1>
        </td>
    </tr>
    <tr>
        <td style="background:repeating-linear-gradient(45deg,#000,#000 10px,#FFBF00 10px,#FFBF00 20px);padding:5px 0;">
        </td>
    </tr>

    {lang_html}

    <!-- FOOTER -->
    <tr>
        <td style="background:repeating-linear-gradient(45deg,#000,#000 10px,#F04923 10px,#F04923 20px);padding:5px 0;">
        </td>
    </tr>
    <tr>
        <td style="padding:15px 30px;text-align:center;background:#000;">
            <p style="font-size:12px;color:#666;margin:0;">Powered by Schlange -- <a href="{REPO_URL}" style="color:#666;">github.com/tpetedb/Schlange</a></p>
        </td>
    </tr>

</table>

<!--[if mso]>
</td></tr></table>
<![endif]-->

</body>
</html>"""
    return html


def main() -> None:
    senden = "--send" in sys.argv

    print()
    print("  ===================================================")
    print("  =        REMINDER EMAIL -- SMUTZIGE HANSIE        =")
    print("  ===================================================")
    print()
    print(f"  Modus: {'SENDEN (LIVE!)' if senden else 'DRY-RUN'}")
    print(f"  Repo:  {REPO_URL}")
    print(f"  Game:  {GAME_URL}")
    print(f"  Playlist: {PLAYLIST_URL}")
    print()

    html = build_reminder_html()

    # Save HTML preview
    os.makedirs("out/email", exist_ok=True)
    preview_path = "out/email/reminder.html"
    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  HTML preview: {preview_path}")

    recipients = load_recipients()
    if not recipients:
        print("  Keine Empfaenger gefunden!")
        print("  Erstelle data/recipients.csv oder setze RECIPIENTS in .env")
        return

    print(f"  Empfaenger: {len(recipients)}")

    result = send_email(
        html_body=html,
        recipients=recipients,
        subject=SUBJECT,
        dry_run=not senden,
    )

    if result.get("errors"):
        print("  Fehler:")
        for err in result["errors"]:
            print(f"    - {err}")

    print()


if __name__ == "__main__":
    main()
