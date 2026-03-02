"""Frame extraction from reference video.

Extracts key frames from the Smutzige Hansi reference video for email embedding.
Uses Pillow for image handling. Falls back to placeholder frames if video
processing libraries are not available.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


def extract_frames_ffmpeg(
    video_path: str,
    output_dir: str = "out/email/img",
    num_frames: int = 4,
    prefix: str = "frame",
) -> list[str]:
    """Extract frames from a video using ffmpeg.

    Tries ffmpeg first (most reliable). Falls back to placeholder images.

    Args:
        video_path: Path to the video file.
        output_dir: Where to save extracted frames.
        num_frames: Number of frames to extract.
        prefix: Filename prefix for output frames.

    Returns:
        List of paths to extracted frame images.
    """
    os.makedirs(output_dir, exist_ok=True)
    frame_paths: list[str] = []

    # Get video duration using ffprobe
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_entries",
                "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
                video_path,
            ],
            capture_output=True, text=True, timeout=10,
        )
        duration = float(result.stdout.strip())
    except (subprocess.SubprocessError, ValueError, FileNotFoundError):
        print("  [frames] ffprobe not available, using placeholder frames")
        return create_placeholder_frames(output_dir, num_frames, prefix)

    # Extract evenly spaced frames
    interval = duration / (num_frames + 1)
    for i in range(1, num_frames + 1):
        timestamp = interval * i
        output_path = os.path.join(output_dir, f"{prefix}_{i:02d}.jpg")
        try:
            subprocess.run(
                [
                    "ffmpeg", "-y", "-ss", str(timestamp),
                    "-i", video_path, "-frames:v", "1",
                    "-q:v", "2", output_path,
                ],
                capture_output=True, timeout=30,
            )
            if os.path.exists(output_path):
                frame_paths.append(output_path)
                print(f"  [frames] Extracted frame {i} at {timestamp:.1f}s -> {output_path}")
        except (subprocess.SubprocessError, FileNotFoundError):
            print(f"  [frames] Failed to extract frame {i}")

    if not frame_paths:
        return create_placeholder_frames(output_dir, num_frames, prefix)

    return frame_paths


def create_placeholder_frames(
    output_dir: str = "out/email/img",
    num_frames: int = 4,
    prefix: str = "frame",
) -> list[str]:
    """Create placeholder frame images when video extraction is not available.

    Creates simple text-based placeholder images using Pillow, or plain text
    files if Pillow is not installed.

    Returns:
        List of paths to placeholder frames.
    """
    os.makedirs(output_dir, exist_ok=True)
    frame_paths: list[str] = []

    captions = [
        "Smutzige Hansi beim letzten Commit",
        "DIE LETSTE PARTY MIT SMUTZIGE HANSIE",
        "importiert * probiert * gibzurueck",
        "Sei dabei -- oder sei ein Viereck",
    ]

    try:
        from PIL import Image, ImageDraw, ImageFont

        for i in range(min(num_frames, len(captions))):
            img = Image.new("RGB", (1280, 720), color=(0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Try to use a reasonable font, fall back to default
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            except (IOError, OSError):
                font = ImageFont.load_default()
                font_small = font

            # Dark background with accent
            draw.rectangle([(0, 0), (1280, 80)], fill=(240, 73, 35))  # #F04923 header
            draw.text((40, 20), "DIE LETSTE PARTY MIT SMUTZIGE HANSIE", fill=(255, 255, 255), font=font)
            draw.text((640, 360), captions[i], fill=(255, 191, 0), font=font, anchor="mm")
            draw.text((640, 680), f"Frame {i + 1}/{num_frames}", fill=(100, 100, 100), font=font_small, anchor="mm")

            output_path = os.path.join(output_dir, f"{prefix}_{i + 1:02d}.jpg")
            img.save(output_path, "JPEG", quality=90)
            frame_paths.append(output_path)
            print(f"  [frames] Created placeholder frame {i + 1} -> {output_path}")

    except ImportError:
        # No Pillow -- create text stubs
        print("  [frames] Pillow not available, creating text placeholders")
        for i in range(min(num_frames, len(captions))):
            output_path = os.path.join(output_dir, f"{prefix}_{i + 1:02d}.txt")
            with open(output_path, "w") as fh:
                fh.write(f"PLACEHOLDER FRAME {i + 1}\n")
                fh.write(f"Caption: {captions[i]}\n")
                fh.write(f"Resolution: 1280x720\n")
            frame_paths.append(output_path)

    return frame_paths


def generate_assets_manifest(
    frame_paths: list[str],
    video_path: str = "data/smutzige_hansie_video.mp4",
    output_path: str = "assets_manifest.json",
) -> dict:
    """Generate an assets manifest JSON.

    Args:
        frame_paths: List of extracted frame image paths.
        video_path: Path to the reference video.
        output_path: Where to write the manifest.

    Returns:
        The manifest dict.
    """
    manifest = {
        "reference_video": video_path,
        "video_exists": os.path.exists(video_path),
        "video_size_mb": round(os.path.getsize(video_path) / 1_048_576, 1) if os.path.exists(video_path) else 0,
        "frames": [
            {
                "path": p,
                "exists": os.path.exists(p),
                "index": i + 1,
            }
            for i, p in enumerate(frame_paths)
        ],
        "frame_count": len(frame_paths),
    }

    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    return manifest
