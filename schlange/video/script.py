"""Video script and subtitle generator.

Generates the German narration script and SRT subtitles from the video spec.
"""

from __future__ import annotations

import json
import os
from datetime import timedelta
from typing import Any


# The definitive narration script -- 8 scenes
SCRIPT_SCENES: list[dict[str, Any]] = [
    {
        "id": "explosion_intro",
        "duration": 4,
        "narration": "",
        "subtitle": "CHAOTIC ENGINEERING PROGRAM",
        "overlay": "Eine Smutzige Hansi Produktion",
    },
    {
        "id": "hansi_intro",
        "duration": 5,
        "narration": (
            "Ich gehe bald...\n"
            "Letzter Lacher fuer meine geliebten Kolleginnen und Kollegen."
        ),
        "subtitle": "Ich gehe bald...",
    },
    {
        "id": "coding_chaos",
        "duration": 8,
        "narration": (
            "Smutzige Hansi hat nicht einfach gekuendigt.\n"
            "Smutzige Hansi hat eine Programmiersprache gebaut.\n"
            "Und damit ein chaotisches Abschiedsprogramm gestartet."
        ),
        "subtitle": "PROBIERT * AUSSER * ENDLICH",
        "keywords": ["importiert", "probiert", "gibzurueck", "als"],
    },
    {
        "id": "schlange_reveal",
        "duration": 6,
        "narration": (
            "Schlange -- ein deutscher Python-Interpreter-Wrapper.\n"
            "Weil normale Programmierung zu langweilig war."
        ),
        "subtitle": "SCHLANGE -- Python auf Deutsch",
    },
    {
        "id": "playlist_reveal",
        "duration": 6,
        "narration": (
            "Tom 1000? Zu wenig.\n"
            "Tom 2000 -- featuring Schlange.\n"
            "Automatisch generiert aus 6 Jahren Spotify-Geschichte."
        ),
        "subtitle": "TOM 2000 -- 2000 Tracks. 5706 Stunden.",
    },
    {
        "id": "cow_announcement",
        "duration": 6,
        "narration": (
            "Die KI hat entschieden: Wir mieten eine riesige aufblasbare Kuh, "
            "aus der man Bier melken kann."
        ),
        "subtitle": "Die KI hat entschieden...",
    },
    {
        "id": "event_cta",
        "duration": 5,
        "narration": (
            "Donnerstag, 12. Maerz 2026.\n"
            "De Vierkant."
        ),
        "subtitle": "Donnerstag, 12. Maerz 2026 -- De Vierkant",
    },
    {
        "id": "closing",
        "duration": 5,
        "narration": "Sei dabei -- oder sei ein Viereck.",
        "subtitle": "Sei dabei -- oder sei ein Viereck.",
    },
]


def generate_script(output_path: str = "out/video/script_de.txt") -> str:
    """Generate the full German narration script.

    Returns:
        The script text.
    """
    lines: list[str] = []
    lines.append("=" * 60)
    lines.append("  CHAOTIC ENGINEERING PROGRAM")
    lines.append("  Video Script -- Smutzige Hansi Remix")
    lines.append("=" * 60)
    lines.append("")

    total_duration = 0
    for scene in SCRIPT_SCENES:
        total_duration += scene["duration"]
        lines.append(f"--- Scene: {scene['id']} ({scene['duration']}s) ---")
        lines.append(f"[SUBTITLE] {scene['subtitle']}")
        if scene.get("overlay"):
            lines.append(f"[OVERLAY]  {scene['overlay']}")
        if scene.get("keywords"):
            lines.append(f"[KEYWORDS] {', '.join(scene['keywords'])}")
        if scene["narration"]:
            lines.append("[NARRATION]")
            for line in scene["narration"].split("\n"):
                lines.append(f"  {line}")
        else:
            lines.append("[NO NARRATION -- visual only]")
        lines.append("")

    lines.append("=" * 60)
    lines.append(f"  Total duration: {total_duration}s")
    lines.append("=" * 60)

    script_text = "\n".join(lines)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(script_text)

    return script_text


def _format_srt_time(seconds: float) -> str:
    """Format seconds as SRT timestamp: HH:MM:SS,mmm"""
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_subtitles(output_path: str = "out/video/subtitles.srt") -> str:
    """Generate SRT subtitle file from the script scenes.

    Returns:
        The SRT content.
    """
    srt_lines: list[str] = []
    current_time = 0.0
    index = 1

    for scene in SCRIPT_SCENES:
        start = current_time
        end = current_time + scene["duration"]

        # Subtitle line
        srt_lines.append(str(index))
        srt_lines.append(f"{_format_srt_time(start)} --> {_format_srt_time(end)}")
        srt_lines.append(scene["subtitle"])
        srt_lines.append("")
        index += 1

        # If there's narration, add it as a separate subtitle block
        if scene["narration"]:
            narration_lines = [l.strip() for l in scene["narration"].split("\n") if l.strip()]
            if len(narration_lines) > 1:
                # Split narration across the scene duration
                chunk_duration = scene["duration"] / len(narration_lines)
                for j, line in enumerate(narration_lines):
                    n_start = start + j * chunk_duration
                    n_end = start + (j + 1) * chunk_duration
                    srt_lines.append(str(index))
                    srt_lines.append(f"{_format_srt_time(n_start)} --> {_format_srt_time(n_end)}")
                    srt_lines.append(line)
                    srt_lines.append("")
                    index += 1

        current_time = end

    srt_text = "\n".join(srt_lines)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(srt_text)

    return srt_text


def generate_metadata(output_path: str = "out/video/metadata.json") -> dict:
    """Generate video metadata JSON.

    Returns:
        Metadata dict.
    """
    total_duration = sum(s["duration"] for s in SCRIPT_SCENES)
    metadata = {
        "title": "CHAOTIC ENGINEERING PROGRAM -- Smutzige Hansi Remix",
        "duration_seconds": total_duration,
        "scenes": len(SCRIPT_SCENES),
        "event_date": "2026-03-12",
        "event_date_de": "Donnerstag, 12. Maerz 2026",
        "event_location": "De Vierkant",
        "language": "de",
        "reference_video": "data/smutzige_hansie_video.mp4",
        "scene_list": [
            {"id": s["id"], "duration": s["duration"], "subtitle": s["subtitle"]}
            for s in SCRIPT_SCENES
        ],
        "mandatory_checks": {
            "cow_line": True,
            "event_date": True,
            "coding_reference": True,
            "chaotic_engineering": True,
            "closing_line": True,
        },
    }

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(metadata, fh, indent=2, ensure_ascii=False)

    return metadata
