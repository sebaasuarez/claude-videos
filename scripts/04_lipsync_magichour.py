#!/usr/bin/env python3
"""
Step 4: Apply lip-sync to the video using Magic Hour API.
Combines the Google Flow video with the ElevenLabs voice audio.
Ranked #1 for lip-sync quality in 2026, better than HeyGen.

FREE tier: 3 lip-syncs/day, no account needed.
With free account: 100 credits/day + 400 bonus credits.

Requires: MAGICHOUR_API_KEY environment variable (optional — can use web UI instead).
Get free key at: https://magichour.ai (free signup)

Web alternative (no API key needed):
  1. Go to https://magichour.ai/create/lip-sync
  2. Upload the video from videos/ep001_raw.mp4
  3. Upload the audio from audio/ep001_voice.mp3
  4. Generate (3 free/day, no account required)
  5. Download to videos/ep001_final.mp4
"""

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"
VIDEOS_DIR = Path(__file__).parent.parent / "videos"
AUDIO_DIR = Path(__file__).parent.parent / "audio"
MAGICHOUR_API = "https://api.magichour.ai/api"


def load_episode(episode_id: str) -> dict:
    with open(CONFIG_DIR / "episodes.json") as f:
        data = json.load(f)
    for ep in data["episodes"]:
        if ep["id"] == episode_id:
            return ep
    raise ValueError(f"Episode {episode_id} not found")


def create_lipsync_job(video_path: str, audio_path: str) -> str:
    """Create a Magic Hour lip-sync job via API."""
    print(f"Creating lip-sync job...")
    print(f"  Video: {video_path}")
    print(f"  Audio: {audio_path}")

    headers = {
        "Authorization": f"Bearer {os.environ['MAGICHOUR_API_KEY']}",
    }

    with open(video_path, "rb") as vf, open(audio_path, "rb") as af:
        files = {
            "video": (os.path.basename(video_path), vf, "video/mp4"),
            "audio": (os.path.basename(audio_path), af, "audio/mpeg"),
        }
        response = requests.post(
            f"{MAGICHOUR_API}/v1/video-projects/lip-sync",
            headers=headers,
            files=files,
            data={
                "enhance_quality": "true",
                "output_format": "mp4",
            },
        )

    response.raise_for_status()
    result = response.json()
    project_id = result["id"]
    print(f"  Job created. Project ID: {project_id}")
    return project_id


def poll_job_status(project_id: str, max_wait: int = 300) -> str:
    """Poll until job is complete, return download URL."""
    headers = {"Authorization": f"Bearer {os.environ['MAGICHOUR_API_KEY']}"}
    start = time.time()
    interval = 5

    print(f"Waiting for lip-sync to complete...")

    while time.time() - start < max_wait:
        response = requests.get(
            f"{MAGICHOUR_API}/v1/video-projects/{project_id}",
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()
        status = data.get("status")
        elapsed = int(time.time() - start)
        print(f"  [{elapsed}s] Status: {status}")

        if status == "complete":
            return data["downloads"][0]["url"]
        elif status in ("error", "failed"):
            raise RuntimeError(f"Lip-sync failed: {data.get('error_message', 'unknown')}")

        time.sleep(interval)
        interval = min(interval * 1.5, 30)

    raise TimeoutError(f"Job not ready after {max_wait}s")


def download_video(url: str, output_path: str):
    print(f"Downloading final video...")
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    size = os.path.getsize(output_path)
    print(f"  Saved: {output_path} ({size:,} bytes)")


def update_episode_status(episode_id: str, output_path: str):
    config_path = CONFIG_DIR / "episodes.json"
    with open(config_path) as f:
        data = json.load(f)
    for ep in data["episodes"]:
        if ep["id"] == episode_id:
            ep["output_file"] = output_path
            ep["status"] = "completed"
            break
    with open(config_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="Apply lip-sync to episode video")
    parser.add_argument("--episode", required=True, help="Episode ID (e.g. ep001)")
    args = parser.parse_args()

    episode = load_episode(args.episode)
    episode_id = episode["id"]

    video_path = str(VIDEOS_DIR / f"{episode_id}_raw.mp4")
    audio_path = episode.get("elevenlabs_audio_path") or str(AUDIO_DIR / f"{episode_id}_voice.mp3")
    output_path = str(VIDEOS_DIR / f"{episode_id}_final.mp4")

    if not os.path.exists(video_path):
        print(f"Video not found: {video_path}")
        print("Generate it first in Google Flow:")
        print(f"  python scripts/02_flow_prompt.py --episode {episode_id}")
        sys.exit(1)

    if not os.path.exists(audio_path):
        print(f"Audio not found: {audio_path}")
        print("Generate it first:")
        print(f"  python scripts/03_generate_voice.py --episode {episode_id}")
        sys.exit(1)

    if not os.environ.get("MAGICHOUR_API_KEY"):
        print("No MAGICHOUR_API_KEY found.")
        print("Use the web interface instead (free, no account needed):")
        print("  1. Go to https://magichour.ai/create/lip-sync")
        print(f"  2. Upload video: {video_path}")
        print(f"  3. Upload audio: {audio_path}")
        print("  4. Download result and save as:")
        print(f"     {output_path}")
        sys.exit(0)

    project_id = create_lipsync_job(video_path, audio_path)
    download_url = poll_job_status(project_id)
    download_video(download_url, output_path)
    update_episode_status(episode_id, output_path)

    print(f"\nFinal video ready: {output_path}")
    print("Ready to upload to Instagram Reels, TikTok, YouTube Shorts!")


if __name__ == "__main__":
    main()
