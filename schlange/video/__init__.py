"""Video generation pipeline -- provider-agnostic scene generation and stitching.

This module defines the interface and a placeholder backend.
Swap in a real video model API (Runway, Pika, Sora, etc.) when available.
"""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Scene:
    """A single scene in the video storyboard."""

    scene_id: str
    prompt: str
    duration_seconds: float
    image_refs: list[str]
    subtitle: str = ""


@dataclass
class VideoClip:
    """A generated video clip."""

    scene_id: str
    file_path: str
    duration_seconds: float


class VideoBackend(ABC):
    """Abstract interface for video generation backends."""

    @abstractmethod
    def generate_scene(self, scene: Scene) -> VideoClip:
        """Generate a video clip from a scene definition.

        Args:
            scene: The scene to render.

        Returns:
            A VideoClip with the path to the generated file.
        """

    @abstractmethod
    def stitch(self, clips: list[VideoClip], audio_track: str | None = None, output_path: str = "final.mp4") -> str:
        """Combine clips (and optional audio) into a final video.

        Args:
            clips: Ordered list of video clips.
            audio_track: Optional path to audio file.
            output_path: Where to write the final video.

        Returns:
            Path to the final video file.
        """


class PlaceholderBackend(VideoBackend):
    """A placeholder backend that creates stub files for development.

    This backend does NOT generate real video -- it creates text files
    describing what each scene would contain. Use it for end-to-end testing
    of the pipeline without an API key.
    """

    def __init__(self, output_dir: str = "out/video") -> None:
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_scene(self, scene: Scene) -> VideoClip:
        """Create a stub file representing the scene."""
        clip_path = os.path.join(self.output_dir, f"{scene.scene_id}.stub.txt")
        with open(clip_path, "w", encoding="utf-8") as fh:
            fh.write(f"SCENE: {scene.scene_id}\n")
            fh.write(f"PROMPT: {scene.prompt}\n")
            fh.write(f"DURATION: {scene.duration_seconds}s\n")
            fh.write(f"IMAGE REFS: {', '.join(scene.image_refs)}\n")
            fh.write(f"SUBTITLE: {scene.subtitle}\n")
        print(f"  [placeholder] Generated stub for scene '{scene.scene_id}'")
        return VideoClip(scene_id=scene.scene_id, file_path=clip_path, duration_seconds=scene.duration_seconds)

    def stitch(self, clips: list[VideoClip], audio_track: str | None = None, output_path: str = "final.mp4") -> str:
        """Create a stub manifest representing the final video."""
        manifest_path = os.path.join(self.output_dir, output_path.replace(".mp4", ".manifest.json"))
        manifest = {
            "scenes": [
                {"scene_id": c.scene_id, "file": c.file_path, "duration": c.duration_seconds} for c in clips
            ],
            "audio_track": audio_track,
            "total_duration": sum(c.duration_seconds for c in clips),
        }
        with open(manifest_path, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2)
        print(f"  [placeholder] Stitched {len(clips)} scenes -> {manifest_path}")
        return manifest_path


def load_storyboard(assets_json_path: str) -> list[Scene]:
    """Load a storyboard from an assets.json file.

    Expected format:
    {
        "scenes": [
            {
                "scene_id": "intro",
                "prompt": "Smutsahansi enters the office in Lederhosen",
                "duration_seconds": 4.0,
                "image_refs": ["assets/smutsahansi_01.jpg"],
                "subtitle": "SCHLANGE PRESENTIERT"
            }
        ]
    }
    """
    with open(assets_json_path, encoding="utf-8") as fh:
        data = json.load(fh)

    scenes = []
    for s in data.get("scenes", []):
        scenes.append(
            Scene(
                scene_id=s["scene_id"],
                prompt=s["prompt"],
                duration_seconds=s.get("duration_seconds", 4.0),
                image_refs=s.get("image_refs", []),
                subtitle=s.get("subtitle", ""),
            )
        )
    return scenes


def render_video(
    assets_json_path: str,
    backend: VideoBackend | None = None,
    audio_track: str | None = None,
    output_path: str = "final.mp4",
) -> str:
    """Full pipeline: load storyboard, generate scenes, stitch.

    Args:
        assets_json_path: Path to the storyboard JSON.
        backend: Video generation backend (defaults to PlaceholderBackend).
        audio_track: Optional audio file to mix in.
        output_path: Output video filename.

    Returns:
        Path to the final video (or manifest in placeholder mode).
    """
    if backend is None:
        backend = PlaceholderBackend()

    scenes = load_storyboard(assets_json_path)
    print(f"Loaded {len(scenes)} scenes from {assets_json_path}")

    clips = []
    for scene in scenes:
        clip = backend.generate_scene(scene)
        clips.append(clip)

    final = backend.stitch(clips, audio_track=audio_track, output_path=output_path)
    print(f"Video pipeline complete: {final}")
    return final
