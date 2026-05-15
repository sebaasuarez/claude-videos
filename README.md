# Pedacito de Tranquilidad — Video Pipeline

Pipeline para generar videos con el personaje **Sofi**. **Costo adicional: $0** — usa herramientas 100% gratuitas o lo que ya pagas.

## Stack (todo gratis)

| Herramienta | Propósito | Costo |
|---|---|---|
| **Google Flow** | Video cinemático de Sofi con Veo 3.1 | **Gratis** (50 créditos/día) |
| **ElevenLabs** | Voz española latina cálida | **Gratis** (10K chars/mes) |
| **Magic Hour** | Lip-sync #1 ranked 2026 | **Gratis** (3/día sin cuenta) |
| Gemini API | Generar imagen de Sofi (opcional) | **Gratis** (free tier) |

## Cuentas necesarias (todas gratuitas)

1. **Google** → Ya tienes. Abre https://labs.google/flow (gratis con cualquier cuenta)
2. **ElevenLabs** → https://elevenlabs.io — plan gratis, no tarjeta
3. **Magic Hour** → https://magichour.ai — 3 lip-syncs/día sin ni crear cuenta

## Workflow por video (3 pasos)

```
Google Flow → ElevenLabs → Magic Hour
  (video)       (voz)       (lip-sync)
```

### Paso 1: Video en Google Flow (web)

```bash
# Genera el prompt exacto para pegar en Flow:
python scripts/pipeline.py prompt --episode ep001
```

Luego en https://labs.google/flow:
- Pega el prompt
- Sube `characters/sofi_ref_01.png` como ingrediente (bloquea la apariencia de Sofi)
- Genera con Veo 3.1, formato 9:16
- Descarga como `videos/ep001_raw.mp4`

### Paso 2: Voz en ElevenLabs

```bash
export ELEVENLABS_API_KEY=tu_clave_gratis
python scripts/pipeline.py voice --episode ep001
# → genera audio/ep001_voice.mp3
```

O manualmente en https://elevenlabs.io/text-to-speech (sin API key).

### Paso 3: Lip-sync en Magic Hour

```bash
# Con API key (gratis en magichour.ai):
export MAGICHOUR_API_KEY=tu_clave_gratis
python scripts/pipeline.py lipsync --episode ep001

# Sin API key: instrucciones en pantalla para la web
python scripts/pipeline.py lipsync --episode ep001
```

## Setup inicial (una sola vez)

```bash
pip install -r requirements.txt

# Generar imagen de referencia de Sofi (opcional, también puedes hacerlo en Gemini web):
export GEMINI_API_KEY=tu_clave_gratis  # aistudio.google.com/apikey
python scripts/pipeline.py setup
```

## Agregar nuevos episodios

```bash
python scripts/pipeline.py add \
  --title "Respira" \
  --script "Cuando todo se acumule... respira. Solo eso."

python scripts/pipeline.py prompt  --episode ep002
python scripts/pipeline.py voice   --episode ep002
python scripts/pipeline.py lipsync --episode ep002
```

## Ver todos los episodios

```bash
python scripts/pipeline.py list
```

## Estructura del proyecto

```
claude-videos/
├── config/
│   ├── sofi_character.json    # Descripción completa de Sofi
│   └── episodes.json          # Cola de episodios
├── characters/
│   └── sofi_ref_01.png        # Imagen de referencia (subir a Google Flow)
├── audio/
│   └── ep001_voice.mp3        # Voz generada por ElevenLabs
├── videos/
│   ├── ep001_raw.mp4          # Video de Google Flow (sin lip-sync)
│   └── ep001_final.mp4        # Video final con lip-sync
└── scripts/
    ├── 01_generate_sofi_image.py   # Imagen via Gemini API
    ├── 02_flow_prompt.py           # Prompt para Google Flow
    ├── 03_generate_voice.py        # Voz via ElevenLabs
    ├── 04_lipsync_magichour.py     # Lip-sync via Magic Hour
    └── pipeline.py                 # Orquestador
```

## Costo real por video

- Google Flow: **$0** (50 créditos gratis/día → ~12 videos/día con Veo 3.1 Lite)
- ElevenLabs: **$0** (texto muy corto, plan gratuito cubre docenas de clips)
- Magic Hour: **$0** (3 lip-syncs/día sin cuenta, 100/día con cuenta gratuita)
- **Total por video: $0**

## Personaje: Sofi

Ver `config/sofi_character.json` para la descripción completa.

- Mujer latina ~30 años, piel trigueña cálida
- Cabello castaño oscuro liso, raya al centro
- Cardigan lila suave, blusa beige
- Sala minimalista cálida, sillón beige
- Voz calmada, empática, español neutro latino