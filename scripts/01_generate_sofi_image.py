#!/usr/bin/env python3
"""
Step 1: Generate reference images of Sofi using Google Gemini (Imagen 3).
Uses the Gemini API free tier — no OpenAI API key needed.
Requires: GEMINI_API_KEY environment variable.

Get your free key at: https://aistudio.google.com/apikey
The free tier includes Imagen 3 image generation.
"""

import os
import json
import base64
from pathlib import Path
import google.generativeai as genai

CHARACTERS_DIR = Path(__file__).parent.parent / "characters"
CONFIG_DIR = Path(__file__).parent.parent / "config"


def load_character_config():
    with open(CONFIG_DIR / "sofi_character.json") as f:
        return json.load(f)


def generate_sofi_images(n_images: int = 3):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    config = load_character_config()
    prompt = config["dall_e_prompt"]

    CHARACTERS_DIR.mkdir(exist_ok=True)
    saved = []

    # Imagen 3 via Gemini API
    image_model = genai.ImageGenerationModel("imagen-3.0-generate-002")

    for i in range(n_images):
        print(f"Generating Sofi reference image {i+1}/{n_images} with Imagen 3...")
        response = image_model.generate_images(
            prompt=prompt,
            number_of_images=1,
            aspect_ratio="9:16",
            safety_filter_level="block_only_high",
            person_generation="allow_adult",
        )

        output_path = CHARACTERS_DIR / f"sofi_ref_{i+1:02d}.png"
        response.images[0].save(str(output_path))
        print(f"  Saved: {output_path}")
        saved.append(str(output_path))

    print(f"\nDone! {len(saved)} reference images in {CHARACTERS_DIR}")
    print("\nNext step:")
    print("  1. Open https://labs.google/flow")
    print("  2. Upload the best image as an 'ingredient' (character reference)")
    print("  3. Tag it as @sofi for reuse in all future videos")
    print("  4. Generate the 5-second video with the scene prompt")
    print("  5. Download the video, then run:")
    print("     python scripts/03_generate_voice.py --episode ep001")
    return saved


if __name__ == "__main__":
    generate_sofi_images(n_images=3)
