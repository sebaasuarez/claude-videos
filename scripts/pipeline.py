#!/usr/bin/env python3
"""
Master pipeline for "Pedacito de Tranquilidad" video generation.
Orchestrates the full workflow: image → avatar → voice → video.

Usage:
  # First time setup (generate Sofi's avatar):
  python scripts/pipeline.py setup

  # Generate a specific episode:
  python scripts/pipeline.py generate --episode ep001

  # Add a new episode and generate it:
  python scripts/pipeline.py add --script "Tu cuerpo te habla. Apréndelo a escuchar." --title "Escucha tu cuerpo"
  python scripts/pipeline.py generate --episode ep002
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
SCRIPTS_DIR = BASE_DIR / "scripts"


def check_env():
    missing = []
    required = {
        "OPENAI_API_KEY": "Generate Sofi's reference image with DALL-E 3",
        "HEYGEN_API_KEY": "Create avatar and render videos",
        "ELEVENLABS_API_KEY": "Generate Spanish voiceover (optional, HeyGen TTS used if missing)",
    }
    for key, purpose in required.items():
        if not os.environ.get(key) and key != "ELEVENLABS_API_KEY":
            missing.append(f"  {key}: {purpose}")

    if missing:
        print("Missing required environment variables:")
        for m in missing:
            print(m)
        print("\nSet them with:")
        for key in required:
            if key != "ELEVENLABS_API_KEY":
                print(f"  export {key}=your_key_here")
        sys.exit(1)

    if not os.environ.get("ELEVENLABS_API_KEY"):
        print("Note: ELEVENLABS_API_KEY not set. Will use HeyGen built-in TTS.")


def run(script: str, args: list = None):
    cmd = [sys.executable, str(SCRIPTS_DIR / script)] + (args or [])
    print(f"\nRunning: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"Error running {script}")
        sys.exit(result.returncode)


def setup():
    """One-time setup: generate Sofi's image and create her HeyGen avatar."""
    print("=== SETUP: Creating Sofi's avatar ===\n")

    run("01_generate_sofi_image.py")

    # Find the first generated image
    characters_dir = BASE_DIR / "characters"
    images = sorted(characters_dir.glob("sofi_ref_*.png"))
    if not images:
        print("No reference images found. Check step 1.")
        sys.exit(1)

    print(f"\nReference images generated: {len(images)}")
    print("Review the images and choose the best one.")
    best = images[0]
    print(f"Using: {best} (change with --image if needed)")

    run("02_create_heygen_avatar.py", ["--image", str(best)])
    print("\n=== Setup complete! Sofi's avatar is ready. ===")
    print("Generate your first video with:")
    print("  python scripts/pipeline.py generate --episode ep001")


def generate(episode_id: str, use_tts: bool = False):
    """Generate a complete video for an episode."""
    print(f"=== GENERATING VIDEO: {episode_id} ===\n")

    if os.environ.get("ELEVENLABS_API_KEY") and not use_tts:
        run("03_generate_voice.py", ["--episode", episode_id])
        run("04_generate_video_heygen.py", ["--episode", episode_id])
    else:
        run("04_generate_video_heygen.py", ["--episode", episode_id, "--use-tts"])

    print(f"\n=== VIDEO READY: {episode_id} ===")
    print(f"Find it in: {BASE_DIR / 'videos'}")


def add_episode(title: str, script: str, duration: int = 5):
    """Add a new episode to the queue."""
    config_path = CONFIG_DIR / "episodes.json"
    with open(config_path) as f:
        data = json.load(f)

    # Generate next episode ID
    existing_ids = [ep["id"] for ep in data["episodes"]]
    next_num = len(existing_ids) + 1
    ep_id = f"ep{next_num:03d}"

    new_episode = {
        "id": ep_id,
        "title": title,
        "status": "pending",
        "duration_seconds": duration,
        "script": script,
        "scene_description": "Sofi is seated in the beige armchair, looking directly at camera. Empathetic and calm expression.",
        "movement": "Warm gaze, slow breathing, slight head tilt",
        "voice_notes": "Warm, calm, intimate female voice. Neutral Latin American Spanish.",
        "heygen_video_id": None,
        "elevenlabs_audio_id": None,
        "output_file": None,
    }

    data["episodes"].append(new_episode)
    with open(config_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Episode added: {ep_id} - {title}")
    print(f"Script: {script}")
    print(f"\nGenerate with:")
    print(f"  python scripts/pipeline.py generate --episode {ep_id}")
    return ep_id


def list_episodes():
    """Show all episodes and their status."""
    config_path = CONFIG_DIR / "episodes.json"
    with open(config_path) as f:
        data = json.load(f)

    print(f"\n{'ID':<8} {'Status':<12} {'Title'}")
    print("-" * 50)
    for ep in data["episodes"]:
        print(f"{ep['id']:<8} {ep['status']:<12} {ep['title']}")


def main():
    parser = argparse.ArgumentParser(
        description="Pedacito de Tranquilidad - Video Pipeline"
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("setup", help="First-time setup: generate Sofi's avatar")

    gen_parser = subparsers.add_parser("generate", help="Generate video for an episode")
    gen_parser.add_argument("--episode", required=True, help="Episode ID")
    gen_parser.add_argument("--use-tts", action="store_true",
                            help="Use HeyGen TTS instead of ElevenLabs")

    add_parser = subparsers.add_parser("add", help="Add a new episode")
    add_parser.add_argument("--title", required=True, help="Episode title")
    add_parser.add_argument("--script", required=True, help="Script text (what Sofi says)")
    add_parser.add_argument("--duration", type=int, default=5, help="Duration in seconds")

    subparsers.add_parser("list", help="List all episodes and their status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    check_env()

    if args.command == "setup":
        setup()
    elif args.command == "generate":
        generate(args.episode, getattr(args, "use_tts", False))
    elif args.command == "add":
        add_episode(args.title, args.script, args.duration)
    elif args.command == "list":
        list_episodes()


if __name__ == "__main__":
    main()
