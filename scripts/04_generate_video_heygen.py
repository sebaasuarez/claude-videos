#!/usr/bin/env python3
"""
Step 4: Generate the final video with HeyGen - lip-synced avatar video.
Uses Sofi's saved avatar_id + ElevenLabs audio (or HeyGen built-in TTS).
Requires: HEYGEN_API_KEY environment variable.

Output: MP4 video in 9:16 (portrait) format with Sofi speaking the script.
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
HEYGEN_API = "https://api.heygen.com"

def get_headers():
    return {
        "X-Api-Key": os.environ["HEYGEN_API_KEY"],
        "Content-Type": "application/json",
    }

def load_config(filename: str) -> dict:
    path = CONFIG_DIR / filename
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)

def load_episode(episode_id: str) -> dict:
    data = load_config("episodes.json")
    for ep in data.get("episodes", []):
        if ep["id"] == episode_id:
            return ep
    raise ValueError(f"Episode {episode_id} not found")

def upload_audio_to_heygen(audio_path: str) -> str:
    """Upload ElevenLabs audio to HeyGen for use in video generation."""
    print(f"Uploading audio to HeyGen: {audio_path}")

    with open(audio_path, "rb") as f:
        audio_data = f.read()

    response = requests.post(
        f"{HEYGEN_API}/v1/asset",
        headers={
            "X-Api-Key": os.environ["HEYGEN_API_KEY"],
            "Content-Type": "audio/mpeg",
        },
        data=audio_data,
    )
    response.raise_for_status()
    asset_id = response.json()["data"]["id"]
    print(f"  Audio asset ID: {asset_id}")
    return asset_id

def create_video_with_audio(avatar_id: str, audio_asset_id: str, episode: dict) -> str:
    """Create a HeyGen video using the avatar + uploaded audio (lip-sync)."""
    print("Creating video with lip-sync...")

    # HeyGen v2 video generation with photo avatar + audio
    payload = {
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id,
                    "avatar_style": "normal",
                },
                "voice": {
                    "type": "audio",
                    "audio_asset_id": audio_asset_id,
                },
                "background": {
                    "type": "color",
                    "value": "#F5F0E8",  # Warm cream background fallback
                },
            }
        ],
        "dimension": {
            "width": 1080,
            "height": 1920,   # 9:16 portrait for social media
        },
        "aspect_ratio": "9:16",
        "test": False,        # Set True for free low-res test, False for full quality
    }

    response = requests.post(
        f"{HEYGEN_API}/v2/video/generate",
        headers=get_headers(),
        json=payload,
    )
    response.raise_for_status()
    result = response.json()
    video_id = result["data"]["video_id"]
    print(f"  Video generation started. Video ID: {video_id}")
    return video_id

def create_video_with_tts(avatar_id: str, episode: dict) -> str:
    """Fallback: Create video using HeyGen's built-in Spanish TTS (no ElevenLabs needed)."""
    print("Creating video with HeyGen built-in Spanish TTS...")

    payload = {
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id,
                    "avatar_style": "normal",
                },
                "voice": {
                    "type": "text",
                    "input_text": episode["script"],
                    "voice_id": "es-MX-DaliaNeural",   # Warm Mexican Spanish female
                    "speed": 0.85,                       # Slightly slower = calmer
                },
            }
        ],
        "dimension": {
            "width": 1080,
            "height": 1920,
        },
        "aspect_ratio": "9:16",
    }

    response = requests.post(
        f"{HEYGEN_API}/v2/video/generate",
        headers=get_headers(),
        json=payload,
    )
    response.raise_for_status()
    result = response.json()
    video_id = result["data"]["video_id"]
    print(f"  Video generation started (TTS). Video ID: {video_id}")
    return video_id

def poll_video_status(video_id: str, max_wait: int = 300) -> str:
    """Poll HeyGen until video is ready, return download URL."""
    print(f"Waiting for video to render (up to {max_wait}s)...")
    start = time.time()
    interval = 5

    while time.time() - start < max_wait:
        response = requests.get(
            f"{HEYGEN_API}/v1/video_status.get?video_id={video_id}",
            headers=get_headers(),
        )
        response.raise_for_status()
        data = response.json()["data"]
        status = data["status"]

        elapsed = int(time.time() - start)
        print(f"  [{elapsed}s] Status: {status}")

        if status == "completed":
            return data["video_url"]
        elif status == "failed":
            raise RuntimeError(f"Video generation failed: {data.get('error', 'unknown error')}")

        time.sleep(interval)
        interval = min(interval * 1.5, 30)  # Exponential backoff, max 30s

    raise TimeoutError(f"Video not ready after {max_wait}s")

def download_video(url: str, output_path: str):
    """Download the rendered video."""
    print(f"Downloading video...")
    response = requests.get(url, stream=True)
    response.raise_for_status()

    total = int(response.headers.get("Content-Length", 0))
    downloaded = 0

    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)

    print(f"  Saved: {output_path} ({downloaded:,} bytes)")

def update_episode_video(episode_id: str, video_id: str, video_path: str):
    config_path = CONFIG_DIR / "episodes.json"
    with open(config_path) as f:
        data = json.load(f)

    for ep in data["episodes"]:
        if ep["id"] == episode_id:
            ep["heygen_video_id"] = video_id
            ep["output_file"] = video_path
            ep["status"] = "completed"
            break

    with open(config_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    parser = argparse.ArgumentParser(description="Generate lip-sync video for an episode")
    parser.add_argument("--episode", required=True, help="Episode ID (e.g. ep001)")
    parser.add_argument("--use-tts", action="store_true",
                        help="Use HeyGen built-in TTS instead of ElevenLabs audio")
    args = parser.parse_args()

    episode = load_episode(args.episode)
    heygen_config = load_config("heygen_config.json")

    avatar_id = heygen_config.get("sofi_avatar_id")
    if not avatar_id:
        print("Error: No avatar_id found. Run step 2 first:")
        print("  python scripts/02_create_heygen_avatar.py --image characters/sofi_ref_01.png")
        sys.exit(1)

    VIDEOS_DIR.mkdir(exist_ok=True)

    if args.use_tts:
        video_id = create_video_with_tts(avatar_id, episode)
    else:
        audio_path = episode.get("elevenlabs_audio_path")
        if not audio_path or not os.path.exists(audio_path):
            print("No ElevenLabs audio found. Using HeyGen built-in TTS.")
            video_id = create_video_with_tts(avatar_id, episode)
        else:
            audio_asset_id = upload_audio_to_heygen(audio_path)
            video_id = create_video_with_audio(avatar_id, audio_asset_id, episode)

    video_url = poll_video_status(video_id)
    output_path = str(VIDEOS_DIR / f"{episode['id']}_final.mp4")
    download_video(video_url, output_path)
    update_episode_video(args.episode, video_id, output_path)

    print(f"\nVideo ready: {output_path}")
    print("Upload to Instagram Reels, TikTok, or YouTube Shorts!")

if __name__ == "__main__":
    main()
