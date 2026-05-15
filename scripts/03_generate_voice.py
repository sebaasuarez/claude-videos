#!/usr/bin/env python3
"""
Step 3: Generate the Spanish voiceover using ElevenLabs.
Creates a warm, calm, intimate female voice in neutral Latin American Spanish.
Requires: ELEVENLABS_API_KEY environment variable.

Recommended voice: "Valentina" or "Sofia" (ElevenLabs Latin American Spanish).
If not found, falls back to best available Spanish voice.
"""

import os
import json
import time
import argparse
import requests
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"
AUDIO_DIR = Path(__file__).parent.parent / "audio"
ELEVENLABS_API = "https://api.elevenlabs.io/v1"

# Preferred voice IDs for warm, calm Latin American Spanish female voice
# These are stable ElevenLabs voice IDs — calm, empathetic tone
PREFERRED_VOICE_IDS = [
    "21m00Tcm4TlvDq8ikWAM",  # Rachel - calm, warm (English base but multilingual)
    "AZnzlk1XvdvUeBnXmlld",  # Domi - calm female
    "EXAVITQu4vr4xnSDxMaL",  # Bella - soft female
]

# ElevenLabs voice settings for calm, warm, intimate delivery
VOICE_SETTINGS = {
    "stability": 0.85,       # High stability = consistent, calm delivery
    "similarity_boost": 0.75,
    "style": 0.15,           # Low style = natural, not dramatic
    "use_speaker_boost": True,
}

def load_episode(episode_id: str) -> dict:
    with open(CONFIG_DIR / "episodes.json") as f:
        data = json.load(f)
    for ep in data["episodes"]:
        if ep["id"] == episode_id:
            return ep
    raise ValueError(f"Episode {episode_id} not found")

def find_best_spanish_voice() -> str:
    """Find the best available calm female Spanish voice."""
    headers = {"xi-api-key": os.environ["ELEVENLABS_API_KEY"]}
    response = requests.get(f"{ELEVENLABS_API}/voices", headers=headers)
    response.raise_for_status()

    voices = response.json()["voices"]
    spanish_voices = [
        v for v in voices
        if any(
            label in str(v.get("labels", {})).lower()
            for label in ["spanish", "español", "latina", "latin"]
        )
    ]

    if spanish_voices:
        # Prefer calm/soft female voices
        for v in spanish_voices:
            labels = str(v.get("labels", {})).lower()
            if any(w in labels for w in ["calm", "soft", "warm", "female"]):
                print(f"  Selected voice: {v['name']} (ID: {v['voice_id']})")
                return v["voice_id"]
        print(f"  Selected voice: {spanish_voices[0]['name']}")
        return spanish_voices[0]["voice_id"]

    # Fallback to preferred voice IDs
    print("  No explicit Spanish voice found, using multilingual model with preferred voice")
    return PREFERRED_VOICE_IDS[0]

def generate_audio(episode: dict, voice_id: str) -> str:
    """Generate audio from script using ElevenLabs TTS."""
    AUDIO_DIR.mkdir(exist_ok=True)

    script = episode["script"]
    episode_id = episode["id"]
    output_path = AUDIO_DIR / f"{episode_id}_voice.mp3"

    print(f"Generating audio for: {episode_id}")
    print(f"  Script: {script!r}")
    print(f"  Voice ID: {voice_id}")

    headers = {
        "xi-api-key": os.environ["ELEVENLABS_API_KEY"],
        "Content-Type": "application/json",
    }

    payload = {
        "text": script,
        "model_id": "eleven_multilingual_v2",  # Best multilingual model for Spanish
        "voice_settings": VOICE_SETTINGS,
        "language_code": "es",  # Force Spanish
    }

    response = requests.post(
        f"{ELEVENLABS_API}/text-to-speech/{voice_id}",
        headers=headers,
        json=payload,
    )
    response.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(response.content)

    print(f"  Audio saved: {output_path} ({os.path.getsize(output_path):,} bytes)")
    return str(output_path)

def update_episode_audio(episode_id: str, audio_path: str):
    """Update episodes.json with the audio file path."""
    config_path = CONFIG_DIR / "episodes.json"
    with open(config_path) as f:
        data = json.load(f)

    for ep in data["episodes"]:
        if ep["id"] == episode_id:
            ep["elevenlabs_audio_path"] = audio_path
            break

    with open(config_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    parser = argparse.ArgumentParser(description="Generate voiceover for an episode")
    parser.add_argument("--episode", required=True, help="Episode ID (e.g. ep001)")
    parser.add_argument("--voice-id", help="Override ElevenLabs voice ID")
    args = parser.parse_args()

    episode = load_episode(args.episode)

    voice_id = args.voice_id
    if not voice_id:
        print("Finding best Spanish voice...")
        voice_id = find_best_spanish_voice()

    audio_path = generate_audio(episode, voice_id)
    update_episode_audio(args.episode, audio_path)

    print(f"\nVoiceover ready: {audio_path}")
    print("Next step: Generate the video with lip-sync:")
    print(f"  python scripts/04_generate_video_heygen.py --episode {args.episode}")

if __name__ == "__main__":
    main()
