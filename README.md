# Pedacito de Tranquilidad — Video Pipeline

Pipeline automatizado para generar videos con el personaje **Sofi**, avatar recurrente de la cuenta.

## Stack técnico

| Herramienta | Propósito | Costo |
|---|---|---|
| **DALL-E 3** (OpenAI) | Generar imagen de referencia de Sofi | Ya pagado |
| **HeyGen** | Avatar con lip-sync, video final | Desde $29/mes |
| **ElevenLabs** | Voz española latina premium | $5/mes (Starter) |

## Cuentas necesarias

1. **OpenAI** → ya tienes cuenta. Obtén API key en: https://platform.openai.com/api-keys
2. **HeyGen** → Crea cuenta en: https://www.heygen.com → Settings → API → Get API Key
3. **ElevenLabs** → Crea cuenta en: https://elevenlabs.io (plan gratuito sirve para empezar)

## Setup inicial (una sola vez)

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
export OPENAI_API_KEY=sk-...
export HEYGEN_API_KEY=...
export ELEVENLABS_API_KEY=...   # Opcional, usa HeyGen TTS si no está

# Crear a Sofi (genera imagen + avatar en HeyGen)
python scripts/pipeline.py setup
```

## Generar un video

```bash
# Ver episodios disponibles
python scripts/pipeline.py list

# Generar el primer episodio (ep001)
python scripts/pipeline.py generate --episode ep001
```

## Agregar nuevos episodios

```bash
python scripts/pipeline.py add \
  --title "Respira" \
  --script "Cuando todo se acumule... respira. Solo eso." \
  --duration 5

# Luego generar:
python scripts/pipeline.py generate --episode ep002
```

## Estructura del proyecto

```
claude-videos/
├── config/
│   ├── sofi_character.json    # Descripción completa del personaje
│   ├── episodes.json          # Lista de todos los episodios
│   └── heygen_config.json     # Avatar ID de Sofi (generado en setup)
├── characters/
│   └── sofi_ref_01.png        # Imagen de referencia de Sofi
├── audio/
│   └── ep001_voice.mp3        # Audio de cada episodio
├── videos/
│   └── ep001_final.mp4        # Videos finales listos para publicar
└── scripts/
    ├── 01_generate_sofi_image.py
    ├── 02_create_heygen_avatar.py
    ├── 03_generate_voice.py
    ├── 04_generate_video_heygen.py
    └── pipeline.py            # Orquestador principal
```

## Costo estimado por video (5 segundos)

- ElevenLabs: ~$0 (texto muy corto, entra en plan gratuito)
- HeyGen Avatar IV: ~$0.33 por video a 1080p
- **En plan Creator ($29/mes): ~90 videos cortos por mes**

## Personaje: Sofi

Descripción completa en `config/sofi_character.json`.

Características clave:
- Mujer latina ~30 años, piel trigueña clara
- Cabello castaño oscuro, raya al centro
- Cardigan lila, blusa beige
- Sala minimalista cálida, sillón beige
- Voz calmada, empática, español latino neutro