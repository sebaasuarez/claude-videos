#!/usr/bin/env python3
"""
Master pipeline for "Pedacito de Tranquilidad" video generation.

100% FREE stack (using what you already have):
  - Google Flow (free 50 credits/day)  → cinematic video of Sofi
  - ElevenLabs free tier               → Spanish warm voice
  - Magic Hour free tier               → lip-sync (ranked #1 in 2026)

Usage:
  # First time: generate Sofi's reference images
  python scripts/pipeline.py setup

  # Get the prompt to paste in Google Flow
  python scripts/pipeline.py prompt --episode ep001

  # Generate Spanish voiceover
  python scripts/pipeline.py voice --episode ep001

  # Apply lip-sync (API or web fallback instructions)
  python scripts/pipeline.py lipsync --episode ep001

  # Add new episodes
  python scripts/pipeline.py add --title "Respira" --script "Respira. Solo eso."
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
SCRIPTS_DIR = BASE_DIR / "scripts"


def check_env():
    """Warn about missing optional keys (nothing is strictly required)."""
    keys = {
        "GEMINI_API_KEY": "Generate Sofi's image (free tier at aistudio.google.com)",
        "ELEVENLABS_API_KEY": "Generate Spanish voice (free tier at elevenlabs.io)",
        "MAGICHOUR_API_KEY": "Automate lip-sync (free tier at magichour.ai)",
    }
    missing = [f"  {k}: {v}" for k, v in keys.items() if not os.environ.get(k)]
    if missing:
        print("Optional API keys not set (all have free tiers):")
        for m in missing:
            print(m)
        print()


def run(script: str, args: list = None):
    cmd = [sys.executable, str(SCRIPTS_DIR / script)] + (args or [])
    print(f"\nRunning: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(result.returncode)


def setup():
    """Generate Sofi's reference images using Gemini / Imagen 3."""
    print("=== SETUP: Generating Sofi's reference images ===\n")
    if not os.environ.get("GEMINI_API_KEY"):
        print("GEMINI_API_KEY not set.")
        print("Get a free key at: https://aistudio.google.com/apikey")
        print("\nAlternative: Generate manually in Google Flow or Gemini:")
        print("  1. Open https://gemini.google.com")
        print("  2. Ask: 'Generate a portrait image of Sofi' using the prompt in config/sofi_character.json")
        print("  3. Save the best image to characters/sofi_ref_01.png")
        sys.exit(0)

    run("01_generate_sofi_image.py")

    images = sorted((BASE_DIR / "characters").glob("sofi_ref_*.png"))
    print(f"\n{len(images)} reference images generated.")
    print("Review them and use the best one in Google Flow as @sofi ingredient.")
    print("\nNext: python scripts/pipeline.py prompt --episode ep001")


def prompt_step(episode_id: str = None, all_episodes: bool = False):
    """Print the Google Flow prompt for a given episode or all episodes."""
    if all_episodes:
        run("02_flow_prompt.py", ["--all"])
    else:
        run("02_flow_prompt.py", ["--episode", episode_id])


def voice_step(episode_id: str = None, all_episodes: bool = False, series: bool = False):
    """Generate Spanish voiceover with ElevenLabs."""
    if all_episodes:
        run("03_generate_voice.py", ["--all"])
    elif series:
        run("03_generate_voice.py", ["--series"])
    else:
        run("03_generate_voice.py", ["--episode", episode_id])


def lipsync_step(episode_id: str):
    """Apply lip-sync using Magic Hour."""
    run("04_lipsync_magichour.py", ["--episode", episode_id])


def add_episode(title: str, script: str, duration: int = 5):
    """Add a new episode to the queue."""
    config_path = CONFIG_DIR / "episodes.json"
    with open(config_path) as f:
        data = json.load(f)

    next_num = len(data["episodes"]) + 1
    ep_id = f"ep{next_num:03d}"

    data["episodes"].append({
        "id": ep_id,
        "title": title,
        "status": "pending",
        "duration_seconds": duration,
        "script": script,
        "scene_description": "Sofi is seated in the beige armchair, looking directly at camera. Empathetic and calm expression.",
        "movement": "Warm gaze, slow breathing, slight head tilt",
        "voice_notes": "Warm, calm, intimate female voice. Neutral Latin American Spanish.",
        "heygen_video_id": None,
        "elevenlabs_audio_path": None,
        "output_file": None,
    })

    with open(config_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Episode added: {ep_id} — {title}")
    print(f'Script: "{script}"')
    print(f"\nWorkflow:")
    print(f"  python scripts/pipeline.py prompt   --episode {ep_id}  # Get Flow prompt")
    print(f"  python scripts/pipeline.py voice    --episode {ep_id}  # Generate voice")
    print(f"  python scripts/pipeline.py lipsync  --episode {ep_id}  # Apply lip-sync")
    return ep_id


def list_episodes():
    with open(CONFIG_DIR / "episodes.json") as f:
        data = json.load(f)

    print(f"\n{'ID':<8} {'Status':<12} {'Title'}")
    print("-" * 55)
    for ep in data["episodes"]:
        output = "✓" if ep.get("output_file") else " "
        print(f"{ep['id']:<8} {ep['status']:<12} {output} {ep['title']}")


def main():
    parser = argparse.ArgumentParser(
        description="Pedacito de Tranquilidad — Free Video Pipeline"
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("setup", help="Generate Sofi reference images (one-time)")

    p = sub.add_parser("prompt", help="Print Google Flow prompt for an episode")
    pgrp = p.add_mutually_exclusive_group(required=True)
    pgrp.add_argument("--episode", help="Episode ID (e.g. ep001)")
    pgrp.add_argument("--all", action="store_true", help="Print all 4 prompts")

    v = sub.add_parser("voice", help="Generate Spanish voiceover")
    vgrp = v.add_mutually_exclusive_group(required=True)
    vgrp.add_argument("--episode", help="Episode ID")
    vgrp.add_argument("--all", action="store_true", help="Generate all 4 episodes")
    vgrp.add_argument("--series", action="store_true", help="Generate full series in one take")

    ls = sub.add_parser("lipsync", help="Apply lip-sync (Magic Hour)")
    ls.add_argument("--episode", required=True)

    a = sub.add_parser("add", help="Add a new episode")
    a.add_argument("--title", required=True)
    a.add_argument("--script", required=True)
    a.add_argument("--duration", type=int, default=5)

    sub.add_parser("list", help="List all episodes and status")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    check_env()

    if args.command == "setup":
        setup()
    elif args.command == "prompt":
        prompt_step(args.episode, getattr(args, "all", False))
    elif args.command == "voice":
        voice_step(args.episode, getattr(args, "all", False), getattr(args, "series", False))
    elif args.command == "lipsync":
        lipsync_step(args.episode)
    elif args.command == "add":
        add_episode(args.title, args.script, args.duration)
    elif args.command == "list":
        list_episodes()


if __name__ == "__main__":
    main()
