"""Tri-lingual bombastic HTML email template generator.

Generates the goodbye email in DE -> EN -> NL with inline CSS,
table-based layout (Outlook safe), and CID image references.
"""

from __future__ import annotations

import os
from typing import Any


# ============================================================================
# Content blocks -- each language
# ============================================================================

CONTENT = {
    "de": {
        "lang_label": "DEUTSCH",
        "headline": "CHAOTIC ENGINEERING PROGRAM",
        "subheadline": "Eine Smutzige Hansi Produktion",
        "greeting": "Liebe Kolleginnen und Kollegen,",
        "intro": (
            "Ich gehe bald. Aber nicht ohne einen letzten Lacher. "
            "Nicht ohne ein chaotisches Abschiedsprogramm. "
            "Nicht ohne... <strong>SCHLANGE</strong>."
        ),
        "section_schlange_title": "Was ist Schlange?",
        "section_schlange": (
            "Schlange ist ein deutscher Python-Interpreter-Wrapper. "
            "Ein Preprocessor, der deutsche Schluesselwoerter in echtes Python uebersetzt. "
            "<code>verkuendet(\"Hallo Welt!\")</code> wird zu <code>print(\"Hallo Welt!\")</code>. "
            "Weil normale Programmierung zu langweilig war."
        ),
        "section_remix_title": "Was ist der Remix?",
        "section_remix": (
            "Ein KI-generiertes Abschiedsvideo mit Smutzige Hansi. "
            "Explosionen. Chaotisches Coding. Deutsche Python-Keywords. "
            "Die volle Dosis Over-Engineering."
        ),
        "section_playlist_title": "Was ist Tom 2000?",
        "section_playlist": (
            "2000 Tracks aus 6 Jahren Spotify-Geschichte -- automatisch gerankt und "
            "als Playlist generiert. Von Schlange. Fuer die Ewigkeit."
        ),
        "cow_line": (
            "Die KI hat entschieden: Wir mieten eine riesige aufblasbare Kuh, "
            "aus der man Bier melken kann."
        ),
        "faq_cow_title": "Warum die Kuh?",
        "faq_cow": "Weil es das einzige ist, was noch gefehlt hat.",
        "event_title": "DAS EVENT",
        "event_date": "Donnerstag, 12. Maerz 2026",
        "event_location": "De Vierkant",
        "closing": "Sei dabei -- oder sei ein Viereck.",
        "img_caption": "Smutzige Hansi beim letzten Commit.",
        "links_title": "Links",
        "footer": "Powered by Schlange -- Python auf Deutsch",
    },
    "en": {
        "lang_label": "ENGLISH",
        "headline": "CHAOTIC ENGINEERING PROGRAM",
        "subheadline": "A Smutzige Hansi Production",
        "greeting": "Dear colleagues,",
        "intro": (
            "I'm leaving soon. But not without one last laugh. "
            "Not without a chaotic farewell program. "
            "Not without... <strong>SCHLANGE</strong>."
        ),
        "section_schlange_title": "What is Schlange?",
        "section_schlange": (
            "Schlange is a Germanized Python interpreter wrapper. "
            "A preprocessor that translates German keywords into real Python. "
            "<code>verkuendet(\"Hallo Welt!\")</code> becomes <code>print(\"Hallo Welt!\")</code>. "
            "Because normal programming was too boring."
        ),
        "section_remix_title": "What is the Remix?",
        "section_remix": (
            "An AI-generated farewell video featuring Smutzige Hansi. "
            "Explosions. Chaotic coding. German Python keywords. "
            "Full-dose over-engineering."
        ),
        "section_playlist_title": "What is Tom 2000?",
        "section_playlist": (
            "2000 tracks from 6 years of Spotify history -- automatically ranked and "
            "generated as a playlist. By Schlange. For eternity."
        ),
        "cow_line": (
            "The AI has decided: We're renting a giant inflatable cow "
            "that dispenses beer."
        ),
        "faq_cow_title": "Why the cow?",
        "faq_cow": "Because it was the only thing still missing.",
        "event_title": "THE EVENT",
        "event_date": "Thursday, 12 March 2026",
        "event_location": "De Vierkant",
        "closing": "Be there -- or be square.",
        "img_caption": "Smutzige Hansi making the final commit.",
        "links_title": "Links",
        "footer": "Powered by Schlange -- Python auf Deutsch",
    },
    "nl": {
        "lang_label": "NEDERLANDS",
        "headline": "CHAOTIC ENGINEERING PROGRAM",
        "subheadline": "Een Smutzige Hansi Productie",
        "greeting": "Beste collega's,",
        "intro": (
            "Ik ga binnenkort weg. Maar niet zonder een laatste lach. "
            "Niet zonder een chaotisch afscheidsprogramma. "
            "Niet zonder... <strong>SCHLANGE</strong>."
        ),
        "section_schlange_title": "Wat is Schlange?",
        "section_schlange": (
            "Schlange is een Duitse Python-interpreter-wrapper. "
            "Een preprocessor die Duitse sleutelwoorden vertaalt naar echt Python. "
            "<code>verkuendet(\"Hallo Welt!\")</code> wordt <code>print(\"Hallo Welt!\")</code>. "
            "Omdat normaal programmeren te saai was."
        ),
        "section_remix_title": "Wat is de Remix?",
        "section_remix": (
            "Een AI-gegenereerde afscheidsvideo met Smutzige Hansi. "
            "Explosies. Chaotisch coderen. Duitse Python-keywords. "
            "De volle dosis over-engineering."
        ),
        "section_playlist_title": "Wat is Tom 2000?",
        "section_playlist": (
            "2000 nummers uit 6 jaar Spotify-geschiedenis -- automatisch gerankt en "
            "als playlist gegenereerd. Door Schlange. Voor de eeuwigheid."
        ),
        "cow_line": (
            "De AI heeft besloten: We huren een gigantische opblaasbare koe "
            "waar je bier uit kunt melken."
        ),
        "faq_cow_title": "Waarom de koe?",
        "faq_cow": "Omdat het het enige was dat nog ontbrak.",
        "event_title": "HET EVENT",
        "event_date": "Donderdag 12 maart 2026",
        "event_location": "De Vierkant",
        "closing": "Wees erbij -- of wees een vierkant.",
        "img_caption": "Smutzige Hansi bij zijn laatste commit.",
        "links_title": "Links",
        "footer": "Powered by Schlange -- Python auf Deutsch",
    },
}


def _render_language_block(lang: str, links: dict[str, str], img_cid: str | None = None) -> str:
    """Render a single language block as HTML table rows."""
    c = CONTENT[lang]
    img_html = ""
    if img_cid:
        img_html = f"""
        <tr>
            <td style="padding:20px 30px;text-align:center;">
                <img src="cid:{img_cid}" alt="{c['img_caption']}" style="max-width:100%;border-radius:8px;border:3px solid #FFBF00;" />
                <p style="color:#999;font-size:13px;margin-top:8px;font-style:italic;">{c['img_caption']}</p>
            </td>
        </tr>"""

    links_html = ""
    if links:
        link_items = []
        for label, url in links.items():
            if url:
                link_items.append(f'<a href="{url}" style="color:#FFBF00;text-decoration:underline;">{label}</a>')
        if link_items:
            links_html = f"""
        <tr>
            <td style="padding:15px 30px;">
                <h3 style="color:#FFBF00;font-size:16px;margin:0 0 10px;">{c['links_title']}</h3>
                <p style="font-size:14px;line-height:2;">{' &nbsp;|&nbsp; '.join(link_items)}</p>
            </td>
        </tr>"""

    return f"""
    <!-- === {c['lang_label']} === -->
    <tr>
        <td style="background:linear-gradient(90deg,#F04923,#FFBF00);padding:12px 30px;">
            <h2 style="margin:0;color:#000;font-size:20px;letter-spacing:3px;">=== {c['lang_label']} ===</h2>
        </td>
    </tr>
    <tr>
        <td style="padding:25px 30px;">
            <p style="font-size:16px;margin:0 0 15px;">{c['greeting']}</p>
            <p style="font-size:15px;line-height:1.6;">{c['intro']}</p>
        </td>
    </tr>
    {img_html}
    <tr>
        <td style="padding:15px 30px;">
            <h3 style="color:#F04923;font-size:18px;margin:0 0 8px;">&#128013; {c['section_schlange_title']}</h3>
            <p style="font-size:14px;line-height:1.6;">{c['section_schlange']}</p>
        </td>
    </tr>
    <tr>
        <td style="padding:15px 30px;">
            <h3 style="color:#F04923;font-size:18px;margin:0 0 8px;">&#127909; {c['section_remix_title']}</h3>
            <p style="font-size:14px;line-height:1.6;">{c['section_remix']}</p>
        </td>
    </tr>
    <tr>
        <td style="padding:15px 30px;">
            <h3 style="color:#F04923;font-size:18px;margin:0 0 8px;">&#127925; {c['section_playlist_title']}</h3>
            <p style="font-size:14px;line-height:1.6;">{c['section_playlist']}</p>
        </td>
    </tr>
    {links_html}
    <tr>
        <td style="padding:20px 30px;background:#1a1a1a;border-left:4px solid #FFBF00;">
            <p style="font-size:16px;font-weight:bold;margin:0;">&#128004; {c['cow_line']}</p>
            <p style="font-size:13px;color:#999;margin:8px 0 0;"><em>{c['faq_cow_title']}</em> {c['faq_cow']}</p>
        </td>
    </tr>
    <tr>
        <td style="padding:25px 30px;text-align:center;background:#111;">
            <h2 style="color:#F04923;font-size:22px;margin:0 0 10px;">&#128165; {c['event_title']}</h2>
            <p style="font-size:24px;font-weight:bold;color:#FFBF00;margin:0;">{c['event_date']}</p>
            <p style="font-size:18px;color:#fff;margin:5px 0 0;">{c['event_location']}</p>
        </td>
    </tr>
    <tr>
        <td style="padding:20px 30px;text-align:center;">
            <p style="font-size:20px;font-weight:bold;font-style:italic;color:#FFBF00;margin:0;">{c['closing']}</p>
        </td>
    </tr>
    <tr><td style="padding:0;"><hr style="border:none;border-top:2px dashed #333;margin:0;" /></td></tr>
    """


def generate_email_html(
    links: dict[str, str] | None = None,
    img_cid: str | None = "frame_coding",
    output_path: str = "out/email/email_trilingual.html",
) -> str:
    """Generate the complete tri-lingual bombastic HTML email.

    Args:
        links: Dict of label->URL for links section (GitHub, Spotify, Website).
        img_cid: Content-ID for the inline image. None to skip image.
        output_path: Where to write the HTML file.

    Returns:
        The HTML string.
    """
    if links is None:
        links = {}

    lang_blocks = ""
    for lang in ["de", "en", "nl"]:
        lang_blocks += _render_language_block(lang, links, img_cid)

    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>CHAOTIC ENGINEERING PROGRAM</title>
</head>
<body style="margin:0;padding:0;background:#000;color:#fff;font-family:Arial,Helvetica,sans-serif;">

<!-- Outlook wrapper -->
<!--[if mso]>
<table role="presentation" width="700" align="center" cellpadding="0" cellspacing="0"><tr><td>
<![endif]-->

<table role="presentation" cellpadding="0" cellspacing="0" style="max-width:700px;margin:0 auto;width:100%;background:#0a0a0a;border:2px solid #F04923;">

    <!-- HEADER: Hazard Banner -->
    <tr>
        <td style="background:repeating-linear-gradient(45deg,#000,#000 10px,#FFBF00 10px,#FFBF00 20px);padding:5px 0;">
        </td>
    </tr>
    <tr>
        <td style="background:#000;padding:30px;text-align:center;">
            <h1 style="margin:0;font-size:32px;color:#F04923;letter-spacing:5px;">&#128165; CHAOTIC ENGINEERING PROGRAM &#128165;</h1>
            <p style="margin:10px 0 0;font-size:14px;color:#FFBF00;letter-spacing:2px;">Eine Smutzige Hansi Produktion</p>
        </td>
    </tr>
    <tr>
        <td style="background:repeating-linear-gradient(45deg,#000,#000 10px,#FFBF00 10px,#FFBF00 20px);padding:5px 0;">
        </td>
    </tr>

    {lang_blocks}

    <!-- FOOTER -->
    <tr>
        <td style="background:repeating-linear-gradient(45deg,#000,#000 10px,#F04923 10px,#F04923 20px);padding:5px 0;">
        </td>
    </tr>
    <tr>
        <td style="padding:20px 30px;text-align:center;background:#000;">
            <p style="font-size:12px;color:#666;margin:0;">&#128013; Powered by Schlange -- Python auf Deutsch</p>
            <p style="font-size:11px;color:#444;margin:5px 0 0;">PROBIERT * AUSSER * ENDLICH</p>
        </td>
    </tr>

</table>

<!--[if mso]>
</td></tr></table>
<![endif]-->

</body>
</html>"""

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(html)

    return html
