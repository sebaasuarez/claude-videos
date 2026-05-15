#!/usr/bin/env python3
"""
Step 3: Generate the Spanish voiceover using ElevenLabs.
Creates a warm, calm, intimate female voice in neutral Latin American Spanish.
Requires: ELEVENLABS_API_KEY environment variable (free tier at elevenlabs.io).

Modes:
  --episode ep001          Generate voice for a single episode
  --all                    Generate all 4 episodes individually
  --series                 Generate one continuous audio for the full series
                           (then split manually per clip using --split)
  --voice-id <id>          Override voice (find IDs at elevenlabs.io/voice-library)

Best voices for this style (warm, calm, Spanish Latina):
  - Search "Spanish" + "calm" in https://elevenlabs.io/voice-library
  - Or use the auto-detection below
"""

import os
import json
import argparse
import requests
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"
AUDIO_DIR = Path(__file__).parent.parent / "audio"
ELEVENLABS_API = "https://api.elevenlabs.io/v1"

# Voice settings tuned to the user's spec:
# "cálida, pausada, íntima, velocidad lenta, sin dramatismo"
VOICE_SETTINGS = {
    "stability": 0.88,        # High = consistent, calm, no variation
    "similarity_boost": 0.78,
    "style": 0.10,            # Near zero = natural, NOT dramatic/motivational
    "use_speaker_boost": True,
}

# Fallback voice IDs (multilingual, warm female)
FALLBACK_VOICE_IDS = [
    "21m00Tcm4TlvDq8ikWAM",  # Rachel — multilingual, calm
    "EXAVITQu4vr4xnSDxMaL",  # Bella — soft female
    "AZnzlk1XvdvUeBnXmlld",  # Domi — calm
]


def load_config() -> dict:
    with open(CONFIG_DIR / "episodes.json") as f:
        return json.load(f)


def load_episode(episode_id: str) -> dict:
    data = load_config()
    for ep in data["episodes"]:
        if ep["id"] == episode_id:
            return ep
    raise ValueError(f"Episode {episode_id} not found")


def find_best_spanish_voice() -> str:
    """Auto-detect the best available calm female Spanish voice."""
    print("Searching for best Spanish voice in your ElevenLabs library...")
    headers = {"xi-api-key": os.environ["ELEVENLABS_API_KEY"]}
    response = requests.get(f"{ELEVENLABS_API}/voices", headers=headers)
    response.raise_for_status()

    voices = response.json()["voices"]
    spanish_voices = [
        v for v in voices
        if any(
            kw in str(v.get("labels", {})).lower()
            for kw in ["spanish", "español", "latina", "latin", "hispana"]
        )
    ]

    for v in spanish_voices:
        labels = str(v.get("labels", {})).lower()
        if any(w in labels for w in ["calm", "soft", "warm", "gentle", "female", "mujer"]):
            print(f"  Best match: {v['name']} (ID: {v['voice_id']})")
            return v["voice_id"]

    if spanish_voices:
        print(f"  Using: {spanish_voices[0]['name']} (ID: {spanish_voices[0]['voice_id']})")
        return spanish_voices[0]["voice_id"]

    print("  No Spanish voice found — using multilingual fallback.")
    print("  Tip: Search 'Spanish calm female' in https://elevenlabs.io/voice-library")
    return FALLBACK_VOICE_IDS[0]


def generate_tts(text: str, voice_id: str, output_path: Path, label: str = ""):
    """Call ElevenLabs TTS and save the MP3."""
    AUDIO_DIR.mkdir(exist_ok=True)

    headers = {
        "xi-api-key": os.environ["ELEVENLABS_API_KEY"],
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": VOICE_SETTINGS,
        "language_code": "es",
    }

    print(f"  Generating{' ' + label if label else ''}: {text[:60].strip()!r}...")
    response = requests.post(
        f"{ELEVENLABS_API}/text-to-speech/{voice_id}",
        headers=headers,
        json=payload,
    )
    response.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(response.content)
    print(f"  Saved: {output_path} ({output_path.stat().st_size:,} bytes)")
    return str(output_path)


def update_episode_audio(episode_id: str, audio_path: str):
    config_path = CONFIG_DIR / "episodes.json"
    with open(config_path) as f:
        data = json.load(f)
    for ep in data["episodes"]:
        if ep["id"] == episode_id:
            ep["elevenlabs_audio_path"] = audio_path
            break
    with open(config_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def cmd_single(episode_id: str, voice_id: str):
    """Generate voice for one episode."""
    episode = load_episode(episode_id)
    out = AUDIO_DIR / f"{episode_id}_voice.mp3"
    generate_tts(episode["script"], voice_id, out, label=episode_id)
    update_episode_audio(episode_id, str(out))
    print(f"\nDone. Next:")
    print(f"  python scripts/pipeline.py lipsync --episode {episode_id}")


def cmd_all(voice_id: str):
    """Generate voice for all episodes individually."""
    data = load_config()
    for ep in data["episodes"]:
        out = AUDIO_DIR / f"{ep['id']}_voice.mp3"
        generate_tts(ep["script"], voice_id, out, label=ep["id"])
        update_episode_audio(ep["id"], str(out))
    print("\nAll voices generated. Apply lip-sync per clip:")
    for ep in data["episodes"]:
        print(f"  python scripts/pipeline.py lipsync --episode {ep['id']}")


def cmd_series(voice_id: str):
    """Generate one continuous audio file with the full series script."""
    data = load_config()
    series_script = data.get("series_voice_prompt", "")
    if not series_script:
        print("No series_voice_prompt found in episodes.json")
        return

    out = AUDIO_DIR / "series_full_voice.mp3"
    print("Generating full series audio (all 4 clips in one take)...")
    print(f"Script:\n{series_script}\n")
    generate_tts(series_script, voice_id, out, label="series")
    print(f"\nFull series audio: {out}")
    print("Split per clip manually, or use --all to generate individual clips.")


def main():
    parser = argparse.ArgumentParser(description="Generate ElevenLabs voiceover")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--episode", help="Episode ID (e.g. ep001)")
    group.add_argument("--all", action="store_true", help="Generate all episodes")
    group.add_argument("--series", action="store_true",
                       help="Generate one continuous audio for full series")
    parser.add_argument("--voice-id", help="Override ElevenLabs voice ID")
    args = parser.parse_args()

    if not os.environ.get("ELEVENLABS_API_KEY"):
        print("ELEVENLABS_API_KEY not set.")
        print("Get a free key at: https://elevenlabs.io (free tier: 10K chars/month)")
        print("\nManual alternative:")
        print("  1. Go to https://elevenlabs.io/text-to-speech")
        print("  2. Paste the script from config/episodes.json")
        print("  3. Choose a warm Spanish female voice")
        print("  4. Download and save to audio/ep00X_voice.mp3")
        return

    voice_id = args.voice_id or find_best_spanish_voice()

    if args.episode:
        cmd_single(args.episode, voice_id)
    elif args.all:
        cmd_all(voice_id)
    elif args.series:
        cmd_series(voice_id)


if __name__ == "__main__":
    main()
