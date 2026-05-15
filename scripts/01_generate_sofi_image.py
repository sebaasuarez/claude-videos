#!/usr/bin/env python3
"""
Step 1: Generate reference images of Sofi using DALL-E 3.
Run this once to create the base character images used for HeyGen avatar creation.
Requires: OPENAI_API_KEY environment variable.
"""

import os
import json
import base64
import requests
from pathlib import Path
from openai import OpenAI

CHARACTERS_DIR = Path(__file__).parent.parent / "characters"
CONFIG_DIR = Path(__file__).parent.parent / "config"

def load_character_config():
    with open(CONFIG_DIR / "sofi_character.json") as f:
        return json.load(f)

def generate_sofi_images(n_images: int = 3):
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    config = load_character_config()
    prompt = config["dall_e_prompt"]

    CHARACTERS_DIR.mkdir(exist_ok=True)
    saved = []

    for i in range(n_images):
        print(f"Generating Sofi reference image {i+1}/{n_images}...")
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1792",  # Closest to 9:16 portrait
            quality="hd",
            n=1,
            response_format="b64_json",
        )

        image_data = response.data[0].b64_json
        revised_prompt = response.data[0].revised_prompt

        output_path = CHARACTERS_DIR / f"sofi_ref_{i+1:02d}.png"
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(image_data))

        print(f"  Saved: {output_path}")
        print(f"  DALL-E revised prompt: {revised_prompt[:100]}...")
        saved.append(str(output_path))

    print(f"\nDone! Generated {len(saved)} reference images in {CHARACTERS_DIR}")
    print("Next step: Upload the best image to HeyGen to create Sofi's avatar.")
    print("Run: python scripts/02_create_heygen_avatar.py --image characters/sofi_ref_XX.png")
    return saved

if __name__ == "__main__":
    generate_sofi_images(n_images=3)
