#!/usr/bin/env python3
"""
Step 2: Generate the Google Flow prompt for a given episode.
Prints the exact prompt to paste into https://labs.google/flow

Google Flow is FREE — 50 credits/day for any Google account.
No API needed, just your browser.

Usage:
  python scripts/02_flow_prompt.py --episode ep001
  python scripts/02_flow_prompt.py --all        # print all 4 clips at once
"""

import json
import argparse
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"

# Sofi's character block — identical in every clip to enforce consistency
CHARACTER_BLOCK = """Personaje (mantener idéntico en todos los clips):
Mujer adulta joven de aproximadamente 30 años, apariencia latina, piel trigueña clara con subtono cálido, rostro ovalado ligeramente alargado, facciones suaves, ojos café oscuro almendrados, cejas naturales de grosor medio, nariz delicada y proporcional, labios medianos de tono rosado natural, sonrisa suave y serena, mirada cálida, empática y tranquila. Cabello castaño oscuro, liso con movimiento natural, largo hasta los hombros, raya en el centro. Maquillaje natural muy sutil, piel luminosa y saludable."""

OUTFIT_BLOCK = """Vestimenta (mantener idéntica en todos los clips):
Cardigan tejido color lila suave con escote en V, blusa básica beige debajo, pantalón beige claro. Aretes pequeños de argolla dorada, collar fino minimalista."""

SETTING_BLOCK = """Entorno (mantener idéntico en todos los clips):
Sala minimalista, acogedora y cálida. Sillón beige. Luz natural suave entrando por ventana lateral izquierda. Tonos crema, beige, blanco cálido y detalles lila. Plantas verdes, escritorio de madera, cuadro lila en la pared. Ambiente íntimo y tranquilo."""

STYLE_BLOCK = """Estilo visual:
Realista, cinematográfico, premium. Plano medio cercano. Cámara estable con movimiento muy sutil hacia adelante. Profundidad de campo suave. Iluminación cálida natural. Ambiente emocional y relajante. 9:16 vertical."""

RULES_BLOCK = """Importante:
- No agregar texto en pantalla.
- No cortar el audio al final.
- Un solo plano continuo, sin cortes.
- Mantener siempre la misma apariencia facial, edad, tono de piel, color de ojos, cabello, ropa lila y entorno."""


def load_episodes() -> list:
    with open(CONFIG_DIR / "episodes.json") as f:
        return json.load(f)


def load_episode(episode_id: str) -> dict:
    data = load_episodes()
    for ep in data["episodes"]:
        if ep["id"] == episode_id:
            return ep
    raise ValueError(f"Episode {episode_id} not found")


def build_flow_prompt(episode: dict) -> str:
    has_image = (CONFIG_DIR.parent / "characters" / "sofi_ref_01.png").exists()
    ingredient_note = (
        "\n[IMPORTANTE: Sube characters/sofi_ref_01.png como ingrediente de personaje "
        "para bloquear la apariencia de Sofi en todos los clips]"
        if has_image else ""
    )

    prompt = f"""Video vertical 9:16, {episode['duration_seconds']} segundos, realista y cinematográfico.
Cuenta: "Pedacito de Tranquilidad"
{ingredient_note}

{CHARACTER_BLOCK}

{OUTFIT_BLOCK}

{SETTING_BLOCK}

Escena (Clip {episode['clip_number']} de 4):
{episode['scene_description']}

Movimiento:
{episode['movement']}

{STYLE_BLOCK}

{RULES_BLOCK}"""

    return prompt.strip()


def print_episode_prompt(episode: dict):
    prompt = build_flow_prompt(episode)
    clip_num = episode['clip_number']
    total = 4

    print(f"\n{'═' * 65}")
    print(f"  GOOGLE FLOW — Clip {clip_num}/{total}: {episode['title']}  [{episode['id']}]")
    print(f"{'═' * 65}")
    print()
    print(prompt)
    print()
    print(f"{'─' * 65}")
    print("INSTRUCCIONES:")
    print("  1. Ve a: https://labs.google/flow")
    print("  2. Haz clic en 'Generate video'")
    print("  3. Pega el prompt de arriba")
    if (CONFIG_DIR.parent / "characters" / "sofi_ref_01.png").exists():
        print("  4. Sube characters/sofi_ref_01.png como ingrediente de personaje")
    print("  5. Selecciona Veo 3.1, formato 9:16")
    print("  6. Genera (~4 créditos gratuitos)")
    print(f"  7. Descarga como: videos/{episode['id']}_raw.mp4")
    print()
    print(f"Luego genera la voz:")
    print(f"  python scripts/pipeline.py voice --episode {episode['id']}")


def main():
    parser = argparse.ArgumentParser(description="Generate Google Flow prompt for an episode")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--episode", help="Episode ID (e.g. ep001)")
    group.add_argument("--all", action="store_true", help="Print prompts for all episodes")
    args = parser.parse_args()

    if args.all:
        data = load_episodes()
        for ep in data["episodes"]:
            print_episode_prompt(ep)
            print()
    else:
        episode = load_episode(args.episode)
        print_episode_prompt(episode)


if __name__ == "__main__":
    main()
