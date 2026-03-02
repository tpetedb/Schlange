"""Veo 3.1 video generation backend via the Gemini API.

Generates 8-second video clips from text prompts using Google's Veo 3.1
model, then stitches them into a final video using ffmpeg.

Requires:
    - google-genai SDK: pip install google-genai
    - GOOGLE_API_KEY in .env (paid tier with video generation access)
    - ffmpeg on PATH (for stitching)

Pricing (Veo 3.1 Standard):
    - 720p/1080p: $0.40 per clip
    - 4k: $0.60 per clip
"""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path

from schlange.video import Scene, VideoBackend, VideoClip

# Valid Veo durations -- generation only supports these exact values
VALID_DURATIONS = (4, 6, 8)

# Model variants
MODELS = {
    "veo3.1": "veo-3.1-generate-preview",
    "veo3.1-fast": "veo-3.1-fast-generate-preview",
    "veo3": "veo-3.0-generate-001",
    "veo3-fast": "veo-3.0-fast-generate-001",
    "veo2": "veo-2.0-generate-001",
}

DEFAULT_MODEL = "veo3.1"


def _snap_duration(seconds: float) -> int:
    """Snap a duration to the nearest valid Veo duration (4, 6, or 8)."""
    if seconds <= 4:
        return 4
    if seconds <= 6:
        return 6
    return 8


class Veo3Backend(VideoBackend):
    """Generate video clips using Google Veo 3.1 via the Gemini API.

    Configuration via environment variables:
        GOOGLE_API_KEY: Required. Gemini API key (paid tier).
        VEO_MODEL: Model variant (default: veo3.1).
                   Options: veo3.1, veo3.1-fast, veo3, veo3-fast, veo2
        VEO_RESOLUTION: Output resolution (default: 720p).
                        Options: 720p, 1080p, 4k (1080p/4k require 8s duration)
        VEO_ASPECT_RATIO: Aspect ratio (default: 16:9).
                          Options: 16:9, 9:16
        VEO_NEGATIVE_PROMPT: Elements to exclude from all scenes.
        VEO_PERSON_GENERATION: Person generation mode (default: allow_adult).
                               EU/UK/CH users must use allow_adult.
        VEO_POLL_INTERVAL: Seconds between status polls (default: 10).
        VEO_MAX_WAIT: Maximum seconds to wait per scene (default: 600).
    """

    def __init__(self, output_dir: str = "out/video") -> None:
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Lazy import -- only needed when actually generating
        try:
            from google import genai

            self._genai = genai
        except ImportError:
            raise ImportError("google-genai is required for Veo 3 backend: " "pip install google-genai")

        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("VIDEO_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY (or VIDEO_API_KEY) must be set in .env")

        self.client = genai.Client(api_key=api_key)

        # Configuration from environment
        model_key = os.getenv("VEO_MODEL", DEFAULT_MODEL)
        self.model = MODELS.get(model_key, model_key)
        self.resolution = os.getenv("VEO_RESOLUTION", "720p")
        self.aspect_ratio = os.getenv("VEO_ASPECT_RATIO", "16:9")
        self.negative_prompt = os.getenv("VEO_NEGATIVE_PROMPT", "")
        self.person_generation = os.getenv("VEO_PERSON_GENERATION", "allow_all")
        self.poll_interval = int(os.getenv("VEO_POLL_INTERVAL", "10"))
        self.max_wait = int(os.getenv("VEO_MAX_WAIT", "600"))

    def generate_scene(self, scene: Scene) -> VideoClip:
        """Generate a video clip from a scene prompt using Veo.

        If the scene has image_refs pointing to local image files, they are
        uploaded via the Files API and passed as reference images for character
        consistency.  Reference images require 8s duration and
        person_generation="allow_adult".
        """
        from google.genai import types

        duration = _snap_duration(scene.duration_seconds)

        # 1080p and 4k only work with 8s duration
        resolution = self.resolution
        if resolution in ("1080p", "4k") and duration != 8:
            print(f"  [{scene.scene_id}] {resolution} requires 8s duration, using 720p")
            resolution = "720p"

        print(f"  [{scene.scene_id}] Generating {duration}s clip at {resolution} " f"with {self.model}...")
        print(f"  [{scene.scene_id}] Prompt: {scene.prompt[:80]}...")

        if scene.image_refs:
            print(f"  [{scene.scene_id}] (skipping {len(scene.image_refs)} ref images -- SDK not yet supported)")

        config = types.GenerateVideosConfig(
            aspect_ratio=self.aspect_ratio,
            resolution=resolution,
            duration_seconds=duration,
            person_generation=self.person_generation,
            number_of_videos=1,
        )

        if self.negative_prompt:
            config.negative_prompt = self.negative_prompt

        # Start async generation
        operation = self.client.models.generate_videos(
            model=self.model,
            prompt=scene.prompt,
            config=config,
        )

        # Poll until done
        elapsed = 0
        while not operation.done:
            if elapsed >= self.max_wait:
                raise TimeoutError(f"Scene '{scene.scene_id}' timed out after {self.max_wait}s")
            time.sleep(self.poll_interval)
            elapsed += self.poll_interval
            operation = self.client.operations.get(operation)
            if elapsed % 30 == 0:
                print(f"  [{scene.scene_id}] Waiting... ({elapsed}s elapsed)")

        print(f"  [{scene.scene_id}] Generation complete ({elapsed}s)")

        # Check for errors
        if operation.response is None or not operation.response.generated_videos:
            error_msg = getattr(operation, "error", "Unknown error")
            raise RuntimeError(f"Scene '{scene.scene_id}' generation failed: {error_msg}")

        # Download the video
        generated_video = operation.response.generated_videos[0]
        clip_path = os.path.join(self.output_dir, f"{scene.scene_id}.mp4")

        self.client.files.download(file=generated_video.video)
        generated_video.video.save(clip_path)

        print(f"  [{scene.scene_id}] Saved to {clip_path}")

        return VideoClip(
            scene_id=scene.scene_id,
            file_path=clip_path,
            duration_seconds=duration,
        )

    def stitch(
        self,
        clips: list[VideoClip],
        audio_track: str | None = None,
        output_path: str = "final.mp4",
    ) -> str:
        """Concatenate clips using ffmpeg concat demuxer.

        Falls back to a simple copy if ffmpeg is not available.
        """
        final_path = os.path.join(self.output_dir, output_path)

        # Verify ffmpeg is available
        if not shutil.which("ffmpeg"):
            print("  WARNING: ffmpeg not found -- cannot stitch clips")
            print("  Individual scene clips are in out/video/")
            return self._write_concat_manifest(clips, final_path)

        # Write concat file list
        concat_file = os.path.join(self.output_dir, "concat_list.txt")
        with open(concat_file, "w", encoding="utf-8") as fh:
            for clip in clips:
                # ffmpeg concat requires absolute or properly escaped paths
                abs_path = os.path.abspath(clip.file_path)
                fh.write(f"file '{abs_path}'\n")

        # Build ffmpeg command
        cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            concat_file,
        ]

        if audio_track and os.path.exists(audio_track):
            # Mix in audio track, shortest wins
            cmd.extend(["-i", audio_track, "-shortest"])

        cmd.extend(
            [
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                final_path,
            ]
        )

        print(f"  Stitching {len(clips)} clips -> {final_path}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"  WARNING: ffmpeg failed: {result.stderr[:200]}")
            # Try re-encoding instead of copy (handles different codecs)
            cmd_reencode = [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                concat_file,
                "-c:v",
                "libx264",
                "-c:a",
                "aac",
                "-preset",
                "fast",
                final_path,
            ]
            result2 = subprocess.run(cmd_reencode, capture_output=True, text=True)
            if result2.returncode != 0:
                print(f"  ERROR: ffmpeg re-encode also failed: {result2.stderr[:200]}")
                return self._write_concat_manifest(clips, final_path)

        total_dur = sum(c.duration_seconds for c in clips)
        print(f"  Final video: {final_path} ({total_dur}s, {len(clips)} scenes)")
        return final_path

    def _write_concat_manifest(self, clips: list[VideoClip], final_path: str) -> str:
        """Write a JSON manifest when ffmpeg is not available."""
        import json

        manifest_path = final_path.replace(".mp4", ".manifest.json")
        manifest = {
            "scenes": [
                {
                    "scene_id": c.scene_id,
                    "file": c.file_path,
                    "duration": c.duration_seconds,
                }
                for c in clips
            ],
            "total_duration": sum(c.duration_seconds for c in clips),
            "note": "ffmpeg not available -- stitch manually or install ffmpeg",
        }
        with open(manifest_path, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2)
        print(f"  Wrote manifest: {manifest_path}")
        return manifest_path
