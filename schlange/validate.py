"""Mandatory content validation for DIE LETSTE PARTY MIT SMUTZIGE HANSIE.

Checks that all required elements are present in:
- Video script
- Subtitles
- Email (all three languages)
- Metadata

Build fails if any mandatory element is missing.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """Result of a validation check."""

    check: str
    passed: bool
    details: str = ""


@dataclass
class ValidationReport:
    """Full validation report."""

    results: list[ValidationResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results)

    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    def add(self, check: str, passed: bool, details: str = "") -> None:
        self.results.append(ValidationResult(check=check, passed=passed, details=details))

    def summary(self) -> str:
        lines = []
        lines.append("=" * 60)
        lines.append("  VALIDATION REPORT")
        lines.append("=" * 60)
        for r in self.results:
            status = "PASS" if r.passed else "FAIL"
            icon = "  " if r.passed else "  "
            lines.append(f"  [{status}] {r.check}")
            if r.details and not r.passed:
                lines.append(f"         {r.details}")
        lines.append("")
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        lines.append(f"  {passed}/{total} checks passed")
        if self.passed:
            lines.append("  BUILD: PASSED")
        else:
            lines.append(f"  BUILD: FAILED ({self.failed_count} failures)")
        lines.append("=" * 60)
        return "\n".join(lines)


# Mandatory content strings
MANDATORY = {
    "event_date_iso": "2026-03-12",
    "event_date_de": "12. Maerz 2026",
    "event_date_en": "12 March 2026",
    "event_date_nl": "12 maart 2026",
    "event_location": "YoungOnes Office",
    "party_name": "DIE LETSTE PARTY MIT SMUTZIGE HANSIE",
    "hansie": "Smutzige Hansie",
}


def _check_string_in_file(filepath: str, search: str) -> bool:
    """Check if a string exists in a file."""
    if not os.path.exists(filepath):
        return False
    with open(filepath, encoding="utf-8") as fh:
        content = fh.read()
    return search.lower() in content.lower()


def validate_script(script_path: str = "out/video/script_de.txt") -> ValidationReport:
    """Validate the video script contains all mandatory content."""
    report = ValidationReport()

    report.add(
        "Script file exists",
        os.path.exists(script_path),
        f"Missing: {script_path}",
    )

    if os.path.exists(script_path):
        checks = {
            "Script: Cow reference": "aufblasbare Kuh",
            "Script: Beer reference": "Bier melken",
            "Script: Event date": "12. Maerz 2026",
            "Script: Location": "YoungOnes Office",
            "Script: Closing line": "Viereck",
            "Script: Coding - importiert": "importiert",
            "Script: Coding - probiert": "probiert",
            "Script: Coding - gibzurueck": "gibzurueck",
            "Script: Die Letste Party": "DIE LETSTE PARTY",
            "Script: Schlange mention": "Schlange",
            "Script: Programmiersprache": "Programmiersprache",
            "Script: Abschiedsprogramm": "Abschiedsprogramm",
        }
        for name, search in checks.items():
            report.add(name, _check_string_in_file(script_path, search), f"Missing: '{search}'")

    return report


def validate_subtitles(srt_path: str = "out/video/subtitles.srt") -> ValidationReport:
    """Validate subtitles contain key content."""
    report = ValidationReport()

    report.add("Subtitles file exists", os.path.exists(srt_path), f"Missing: {srt_path}")

    if os.path.exists(srt_path):
        checks = {
            "Subtitles: DIE LETSTE PARTY": "DIE LETSTE PARTY",
            "Subtitles: Event date": "12. Maerz 2026",
            "Subtitles: Closing": "Viereck",
            "Subtitles: Schlange": "Schlange",
        }
        for name, search in checks.items():
            report.add(name, _check_string_in_file(srt_path, search), f"Missing: '{search}'")

    return report


def validate_email(email_path: str = "out/email/email_trilingual.html") -> ValidationReport:
    """Validate the email contains all mandatory content in all languages."""
    report = ValidationReport()

    report.add("Email file exists", os.path.exists(email_path), f"Missing: {email_path}")

    if os.path.exists(email_path):
        checks = {
            # German
            "Email DE: Event date": "12. Maerz 2026",
            "Email DE: Location": "YoungOnes Office",
            "Email DE: Video line": "Abschiedsvideo",
            # English
            "Email EN: Event date": "12 March 2026",
            "Email EN: Video line": "farewell video",
            # Dutch
            "Email NL: Event date": "12 maart 2026",
            "Email NL: Video line": "afscheidsvideo",
            # Cross-language
            "Email: DIE LETSTE PARTY": "DIE LETSTE PARTY MIT SMUTZIGE HANSIE",
            "Email: Smutzige Hansie": "Smutzige Hansie",
        }
        for name, search in checks.items():
            report.add(name, _check_string_in_file(email_path, search), f"Missing: '{search}'")

    return report


def validate_metadata(metadata_path: str = "out/video/metadata.json") -> ValidationReport:
    """Validate video metadata."""
    report = ValidationReport()

    report.add("Metadata file exists", os.path.exists(metadata_path), f"Missing: {metadata_path}")

    if os.path.exists(metadata_path):
        with open(metadata_path, encoding="utf-8") as fh:
            data = json.load(fh)
        report.add("Metadata: event_date", data.get("event_date") == "2026-03-12", f"Got: {data.get('event_date')}")
        report.add(
            "Metadata: location", "Vierkant" in data.get("event_location", ""), f"Got: {data.get('event_location')}"
        )

    return report


def validate_frames(frame_dir: str = "out/email/img") -> ValidationReport:
    """Validate that frame images were extracted."""
    report = ValidationReport()

    report.add("Frame directory exists", os.path.isdir(frame_dir), f"Missing: {frame_dir}")

    if os.path.isdir(frame_dir):
        frames = [f for f in os.listdir(frame_dir) if f.startswith("frame_")]
        report.add(
            "Frames extracted (>= 2)",
            len(frames) >= 2,
            f"Found {len(frames)} frames (need >= 2)",
        )

    return report


def validate_all() -> ValidationReport:
    """Run all validation checks and return combined report."""
    report = ValidationReport()

    for sub_report in [
        validate_script(),
        validate_subtitles(),
        validate_email(),
        validate_metadata(),
        validate_frames(),
    ]:
        report.results.extend(sub_report.results)

    return report
