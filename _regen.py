"""Temporary script to re-generate video clips and stitch."""

import os
import json
from dotenv import load_dotenv

load_dotenv()
os.environ["VIDEO_BACKEND"] = "veo3"

from schlange.video import Scene, get_backend, VideoClip

backend = get_backend(output_dir="out/video")

with open("assets/assets.json") as f:
    data = json.load(f)

audio_track = data.get("audio_track")

# Generate remaining scenes (skip existing)
for s in data["scenes"]:
    clip_path = os.path.join("out/video", f"{s['scene_id']}.mp4")
    if os.path.exists(clip_path):
        print(f"SKIP: {s['scene_id']} already exists")
        continue
    scene = Scene(
        scene_id=s["scene_id"],
        prompt=s["prompt"],
        duration_seconds=s.get("duration_seconds", 4.0),
        image_refs=s.get("image_refs", []),
        subtitle=s.get("subtitle", ""),
    )
    clip = backend.generate_scene(scene)
    print(f"  OK: {clip.file_path}")

print("All clips done!")

# Stitch all 9 in order
all_clips = []
for s in data["scenes"]:
    cp = os.path.join("out/video", f"{s['scene_id']}.mp4")
    dur = s.get("duration_seconds", 4.0)
    all_clips.append(VideoClip(scene_id=s["scene_id"], file_path=cp, duration_seconds=dur))

final = backend.stitch(all_clips, audio_track=audio_track, output_path="final.mp4")
print(f"RESULT: {final}")
