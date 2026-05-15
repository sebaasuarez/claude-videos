#!/usr/bin/env python3
"""
Step 2: Generate the Google Flow prompt for a given episode.
Prints the exact prompt to paste into https://labs.google/flow

Google Flow is FREE — 50 credits/day for any Google account.
No API needed, just your browser.

Usage:
  python scripts/02_flow_prompt.py --episode ep001
"""

import json
import argparse
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"


def load_episode(episode_id: str) -> dict:
    with open(CONFIG_DIR / "episodes.json") as f:
        data = json.load(f)
    for ep in data["episodes"]:
        if ep["id"] == episode_id:
            return ep
    raise ValueError(f"Episode {episode_id} not found")


def load_character() -> dict:
    with open(CONFIG_DIR / "sofi_character.json") as f:
        return json.load(f)


def build_flow_prompt(episode: dict, character: dict) -> str:
    v = character["visual_style"]
    s = character["setting"]
    a = character["appearance"]
    o = character["outfit"]

    prompt = f"""Cinematic 9:16 vertical video, 5 seconds.

Character: Young Latin woman ~30 years old, light warm brown skin, oval face, dark brown almond eyes, natural eyebrows, delicate nose, rosy medium lips, soft serene smile. Dark brown straight shoulder-length hair with natural movement, center part. Very subtle natural makeup, luminous skin.

Outfit: Soft lilac knit V-neck cardigan, basic beige blouse underneath, light beige pants. Small gold hoop earrings, thin minimalist necklace.

Scene: {episode['scene_description']}

Setting: Minimalist cozy warm living room. Beige armchair. Soft natural light from left side window. Cream, beige, warm white tones with lilac accents. Green plants in background. Wooden desk. Lilac painting on wall. Intimate warm atmosphere.

Camera: Medium close-up, stable with very subtle push-in forward movement, soft depth of field, warm natural cinematic lighting.

Movement: {episode['movement']}

Style: Realistic, cinematic, premium, emotional and relaxing mood. No text overlays."""

    return prompt


def main():
    parser = argparse.ArgumentParser(description="Generate Google Flow prompt for an episode")
    parser.add_argument("--episode", required=True, help="Episode ID (e.g. ep001)")
    args = parser.parse_args()

    episode = load_episode(args.episode)
    character = load_character()
    prompt = build_flow_prompt(episode, character)

    print("=" * 60)
    print(f"GOOGLE FLOW PROMPT — {args.episode}: {episode['title']}")
    print("=" * 60)
    print()
    print(prompt)
    print()
    print("=" * 60)
    print("INSTRUCTIONS:")
    print("  1. Go to: https://labs.google/flow")
    print("  2. Click 'Generate video'")
    print("  3. Paste the prompt above")
    if (CONFIG_DIR.parent / "characters" / "sofi_ref_01.png").exists():
        print("  4. Click the image icon → Upload characters/sofi_ref_01.png as ingredient")
        print("     (this locks Sofi's appearance for ALL future videos)")
    print("  5. Select Veo 3.1 model, 9:16 aspect ratio")
    print("  6. Generate (costs ~4 free daily credits)")
    print("  7. Download the video as MP4")
    print(f"  8. Save it to: videos/{args.episode}_raw.mp4")
    print()
    print("Then run:")
    print(f"  python scripts/03_generate_voice.py --episode {args.episode}")


if __name__ == "__main__":
    main()
