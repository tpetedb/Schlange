"""Email sender -- SMTP with CID inline images.

Sends the tri-lingual bombastic email with embedded screenshots.
Supports dry-run mode, recipient CSV, and environment variable config.
"""

from __future__ import annotations

import csv
import email.encoders
import email.mime.base
import email.mime.image
import email.mime.multipart
import email.mime.text
import os
import smtplib
from typing import Any


def load_recipients(
    csv_path: str = "data/recipients.csv",
    env_fallback: str = "RECIPIENTS",
) -> list[str]:
    """Load recipient email addresses.

    Tries CSV file first, falls back to RECIPIENTS env variable.

    Args:
        csv_path: Path to recipients CSV (one email per line, or 'email' column).
        env_fallback: Environment variable name for comma-separated emails.

    Returns:
        List of email addresses.
    """
    recipients: list[str] = []

    if os.path.exists(csv_path):
        with open(csv_path, encoding="utf-8") as fh:
            reader = csv.reader(fh)
            header = next(reader, None)
            # Find email column
            email_col = 0
            if header:
                for i, col in enumerate(header):
                    if "email" in col.lower() or "@" in col:
                        email_col = i
                        break
                # If header looks like an email, include it
                if "@" in (header[email_col] if header else ""):
                    recipients.append(header[email_col].strip())

            for row in reader:
                if row and len(row) > email_col:
                    addr = row[email_col].strip()
                    if "@" in addr:
                        recipients.append(addr)

    if not recipients:
        env_val = os.getenv(env_fallback, "")
        if env_val:
            recipients = [a.strip() for a in env_val.split(",") if "@" in a.strip()]

    return recipients


def send_email(
    html_body: str,
    recipients: list[str],
    subject: str = "DIE LETSTE PARTY MIT SMUTZIGE HANSIE -- Donnerstag, 12. Maerz 2026",
    from_addr: str | None = None,
    smtp_host: str | None = None,
    smtp_port: int = 587,
    smtp_user: str | None = None,
    smtp_pass: str | None = None,
    image_paths: list[str] | None = None,
    image_cids: list[str] | None = None,
    attachments: list[str] | None = None,
    dry_run: bool = True,
    **kwargs: Any,
) -> dict[str, Any]:
    """Send the email with optional CID inline images and file attachments.

    Args:
        html_body: The HTML email body.
        recipients: List of recipient email addresses.
        subject: Email subject line.
        from_addr: Sender address (or EMAIL_FROM env var).
        smtp_host: SMTP server (or SMTP_HOST env var).
        smtp_port: SMTP port (default 587 for TLS).
        smtp_user: SMTP username (or SMTP_USER env var).
        smtp_pass: SMTP password (or SMTP_PASS env var).
        image_paths: List of image file paths to embed.
        image_cids: List of Content-IDs for each image.
        attachments: List of file paths to attach (e.g. video files).
        dry_run: If True, don't actually send -- just validate and log.

    Returns:
        Report dict with send status.
    """
    from_addr = from_addr or os.getenv("EMAIL_FROM", "")
    smtp_host = smtp_host or os.getenv("SMTP_HOST", "")
    smtp_user = smtp_user or os.getenv("SMTP_USER", "")
    smtp_pass = smtp_pass or os.getenv("SMTP_PASS", "")

    report: dict[str, Any] = {
        "recipients": recipients,
        "subject": subject,
        "from": from_addr,
        "image_count": len(image_paths) if image_paths else 0,
        "attachment_count": len(attachments) if attachments else 0,
        "dry_run": dry_run,
        "sent": False,
        "errors": [],
    }

    if not recipients:
        report["errors"].append("No recipients specified")
        return report

    if not dry_run and not from_addr:
        report["errors"].append("EMAIL_FROM not set")
    if not dry_run and not smtp_host:
        report["errors"].append("SMTP_HOST not set")

    if report["errors"]:
        return report

    # Build MIME message: mixed (for attachments) wrapping related (for inline images)
    msg = email.mime.multipart.MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = ", ".join(recipients)

    # Related part for HTML + inline images
    related = email.mime.multipart.MIMEMultipart("related")
    html_part = email.mime.text.MIMEText(html_body, "html", "utf-8")
    related.attach(html_part)

    # Attach inline images to related part
    if image_paths and image_cids:
        for img_path, cid in zip(image_paths, image_cids):
            if os.path.exists(img_path):
                with open(img_path, "rb") as fh:
                    img_data = fh.read()
                mime_img = email.mime.image.MIMEImage(img_data, _subtype="jpeg")
                mime_img.add_header("Content-ID", f"<{cid}>")
                mime_img.add_header("Content-Disposition", "inline", filename=os.path.basename(img_path))
                related.attach(mime_img)

    msg.attach(related)

    # Attach files (e.g. video)
    if attachments:
        for filepath in attachments:
            if not os.path.exists(filepath):
                print(f"  WARNUNG: Attachment nicht gefunden: {filepath}")
                continue
            with open(filepath, "rb") as fh:
                file_data = fh.read()
            part = email.mime.base.MIMEBase("application", "octet-stream")
            part.set_payload(file_data)
            email.encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition", "attachment",
                filename=os.path.basename(filepath),
            )
            msg.attach(part)
            size_mb = len(file_data) / (1024 * 1024)
            print(f"  Attachment: {os.path.basename(filepath)} ({size_mb:.1f} MB)")

    if dry_run:
        print(f"  [DRY RUN] Would send to {len(recipients)} recipients:")
        for r in recipients:
            print(f"    - {r}")
        print(f"  [DRY RUN] Subject: {subject}")
        print(f"  [DRY RUN] From: {from_addr or '(not set)'}")
        print(f"  [DRY RUN] Images: {len(image_paths) if image_paths else 0}")
        print(f"  [DRY RUN] Attachments: {len(attachments) if attachments else 0}")
        report["sent"] = False
        return report

    # Actually send
    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=120) as server:
            server.starttls()
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.sendmail(from_addr, recipients, msg.as_string())
        report["sent"] = True
        print(f"  Email sent to {len(recipients)} recipients!")
    except Exception as exc:
        report["errors"].append(str(exc))
        print(f"  Email send FAILED: {exc}")

    return report
