"""Tri-lingual farewell email template generator.

Generates the farewell party email in DE -> EN -> NL with inline CSS,
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
        "headline": "DIE LETSTE PARTY MIT SMUTZIGE HANSIE",
        "greeting": "Liebe Kolleginnen und Kollegen,",
        "body": (
            "Smutzige Hansie verlaesst YoungOnes. "
            "Aber nicht ohne ein letztes Fest."
        ),
        "video_line": "Schau dir das Abschiedsvideo im Anhang an.",
        "event_title": "DAS EVENT",
        "event_date": "Donnerstag, 12. Maerz 2026",
        "event_location": "YoungOnes Office",
        "closing": "Sei dabei.",
        "img_caption": "Smutzige Hansie.",
        "footer": "Powered by Schlange",
    },
    "en": {
        "lang_label": "ENGLISH",
        "headline": "DIE LETSTE PARTY MIT SMUTZIGE HANSIE",
        "greeting": "Dear colleagues,",
        "body": (
            "Smutzige Hansie is leaving YoungOnes. "
            "But not without one last party."
        ),
        "video_line": "Watch the farewell video attached to this email.",
        "event_title": "THE EVENT",
        "event_date": "Thursday, 12 March 2026",
        "event_location": "YoungOnes Office",
        "closing": "Be there.",
        "img_caption": "Smutzige Hansie.",
        "footer": "Powered by Schlange",
    },
    "nl": {
        "lang_label": "NEDERLANDS",
        "headline": "DIE LETSTE PARTY MIT SMUTZIGE HANSIE",
        "greeting": "Beste collega's,",
        "body": (
            "Smutzige Hansie verlaat YoungOnes. "
            "Maar niet zonder een laatste feest."
        ),
        "video_line": "Bekijk de afscheidsvideo in de bijlage.",
        "event_title": "HET EVENT",
        "event_date": "Donderdag 12 maart 2026",
        "event_location": "YoungOnes Office",
        "closing": "Wees erbij.",
        "img_caption": "Smutzige Hansie.",
        "footer": "Powered by Schlange",
    },
}


def _render_language_block(lang: str, img_cid: str | None = None) -> str:
    """Render a single language block as HTML table rows."""
    c = CONTENT[lang]
    img_html = ""
    if img_cid:
        img_html = f"""
        <tr>
            <td style="padding:20px 30px;text-align:center;">
                <img src="cid:{img_cid}" alt="{c['img_caption']}" style="max-width:100%;border-radius:8px;border:3px solid #FFBF00;" />
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
            <p style="font-size:16px;line-height:1.6;">{c['body']}</p>
            <p style="font-size:15px;line-height:1.6;color:#FFBF00;font-weight:bold;margin-top:15px;">&#127909; {c['video_line']}</p>
        </td>
    </tr>
    {img_html}
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
    video_cid: str | None = None,
    output_path: str = "out/email/email_trilingual.html",
) -> str:
    """Generate the tri-lingual farewell email.

    Args:
        links: Dict of label->URL for links section (unused, kept for compat).
        img_cid: Content-ID for the inline image. None to skip image.
        video_cid: Content-ID for the embedded video (unused, kept for compat).
        output_path: Where to write the HTML file.

    Returns:
        The HTML string.
    """
    lang_blocks = ""
    for lang in ["de", "en", "nl"]:
        lang_blocks += _render_language_block(lang, img_cid)

    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>DIE LETSTE PARTY MIT SMUTZIGE HANSIE</title>
</head>
<body style="margin:0;padding:0;background:#000;color:#fff;font-family:Arial,Helvetica,sans-serif;">

<!-- Outlook wrapper -->
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
            <h1 style="margin:0;font-size:28px;color:#F04923;letter-spacing:4px;">&#128165; DIE LETSTE PARTY MIT SMUTZIGE HANSIE &#128165;</h1>
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
        <td style="padding:15px 30px;text-align:center;background:#000;">
            <p style="font-size:12px;color:#666;margin:0;">Powered by Schlange</p>
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
