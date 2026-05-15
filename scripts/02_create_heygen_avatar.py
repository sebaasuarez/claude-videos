#!/usr/bin/env python3
"""
Step 2: Upload Sofi's reference image to HeyGen and create a Photo Avatar.
Run once after generating the reference image.
Requires: HEYGEN_API_KEY environment variable.

HeyGen Photo Avatar IV creates a consistent talking-head avatar from a still image.
This avatar_id is then used for ALL future video generations.
"""

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"
HEYGEN_API = "https://api.heygen.com"

def get_headers():
    return {
        "X-Api-Key": os.environ["HEYGEN_API_KEY"],
        "Content-Type": "application/json",
    }

def upload_image(image_path: str) -> str:
    """Upload image to HeyGen and return asset_id."""
    print(f"Uploading image: {image_path}")

    with open(image_path, "rb") as f:
        image_data = f.read()

    upload_url = f"{HEYGEN_API}/v1/asset"
    response = requests.post(
        upload_url,
        headers={
            "X-Api-Key": os.environ["HEYGEN_API_KEY"],
            "Content-Type": "image/png",
        },
        data=image_data,
    )
    response.raise_for_status()
    result = response.json()
    asset_id = result["data"]["id"]
    print(f"  Image uploaded. Asset ID: {asset_id}")
    return asset_id

def create_photo_avatar(asset_id: str) -> str:
    """Create a Photo Avatar from an uploaded image asset."""
    print("Creating HeyGen Photo Avatar (Sofi)...")

    url = f"{HEYGEN_API}/v2/photo_avatar"
    payload = {
        "image_asset_id": asset_id,
        "name": "Sofi - Pedacito de Tranquilidad",
        "circle_image_asset_id": asset_id,
    }

    response = requests.post(url, headers=get_headers(), json=payload)
    response.raise_for_status()
    result = response.json()

    avatar_id = result["data"]["photo_avatar_id"]
    print(f"  Photo Avatar created! Avatar ID: {avatar_id}")
    return avatar_id

def save_avatar_id(avatar_id: str):
    """Save avatar_id to config for future use."""
    config_path = CONFIG_DIR / "heygen_config.json"
    config = {}
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)

    config["sofi_avatar_id"] = avatar_id
    config["created_at"] = time.strftime("%Y-%m-%d %Human:%M:%S")

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"  Avatar ID saved to {config_path}")

def main():
    parser = argparse.ArgumentParser(description="Create HeyGen avatar for Sofi")
    parser.add_argument("--image", required=True, help="Path to Sofi reference image")
    args = parser.parse_args()

    if not os.path.exists(args.image):
        print(f"Error: Image not found: {args.image}")
        sys.exit(1)

    asset_id = upload_image(args.image)
    avatar_id = create_photo_avatar(asset_id)
    save_avatar_id(avatar_id)

    print(f"\nSofi's avatar is ready!")
    print(f"Avatar ID: {avatar_id}")
    print("Next step: Generate videos using:")
    print("  python scripts/03_generate_video.py --episode ep001")

if __name__ == "__main__":
    main()
