# Voice-First Informal Worker Digital Skill Card & Scheme Helper

Standalone Python modules for generating multilingual **Digital Skill Cards** (with scannable QR codes and WhatsApp share links), **Speech-to-Text / Text-to-Speech voice workflows** (Hindi, English, and Kannada via ElevenLabs), and **official myScheme government scheme lookups**.

---

## Features

- **Digital Skill Card Generator (`skill_card.py`)**
  - Renders `800×1120` mobile-ready PNG skill passports (`generated_cards/{card_id}.png`).
  - Embeds ISO/IEC 18004 compliant QR codes (4-module quiet zone, integer pixel scaling) and generates Base64 QR data URIs.
  - Creates localized WhatsApp share links (`https://wa.me/?text=...`).
  - Supports **English (`en`)**, **Hindi (`hi`)**, and **Kannada (`kn`)** with automatic font discovery and fallback transliteration if Indic fonts are unavailable.

- **Multilingual Voice Service (`voice_service.py`)**
  - **Speech-to-Text (STT):** `transcribe_worker_voice()` transcribes `.mp3`, `.wav`, `.webm`, and `.ogg` audio (< 10 MB) using ElevenLabs `scribe_v1`.
  - **Spoken Summary Formatter:** `build_spoken_summary()` generates natural plain-language narration scripts in `en`, `hi`, or `kn` while stripping parenthesized transliterations.
  - **Text-to-Speech (TTS) with Local Caching:** `generate_voice_output()` synthesizes MP3 audio using ElevenLabs `eleven_v3` and caches output at `audio_cache/{card_id}_{language}.mp3`. Falls back safely to a silent playable MP3 if `ELEVENLABS_API_KEY` is missing or unavailable.

- **Official myScheme Helper (`extras_helper.py` + `myscheme_links.json`)**
  - `get_official_schemes(category)` maps worker roles/keywords (e.g., `electrician`, `tailor`, `cook`, `shopkeeper`, `plumber`, `driver`, `barber`) across 7 vocational categories to curated `https://www.myscheme.gov.in/` scheme links with a verification disclaimer.

---

## Project Structure

```text
.
├── skill_card.py               # Digital skill card PNG, QR code, & WhatsApp link generator
├── voice_service.py            # ElevenLabs STT (scribe_v1), summary builder, & cached TTS (eleven_v3)
├── extras_helper.py            # Role/category matching for official myScheme portal links
├── myscheme_links.json         # Curated schemes across 7 informal worker categories
├── requirements_voice_card.txt # Python dependencies
├── .env.example                # Environment variable template
├── Dockerfile                  # Minimal Python 3.11 container with Devanagari & Kannada fonts
├── INTEGRATION.md              # Developer 1-pager with card_data schema and snippets
├── DEPLOY_AWS.md               # Deployment guide for AWS App Runner, EC2, Railway, and Render
├── generated_cards/            # Sample/output PNG skill cards
└── audio_cache/                # Cached MP3 voice outputs
```

---

## Setup & Installation

### 1. Install Dependencies

Python 3.11+ is recommended.

```bash
pip install -r requirements_voice_card.txt
```

Dependencies listed in `requirements_voice_card.txt`:
- `qrcode[pil]>=7.4.2`
- `pillow>=10.0.0`
- `elevenlabs>=2.0.0`
- `python-dotenv>=1.0.0`

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Key variables:
- `ELEVENLABS_API_KEY` — Required for live ElevenLabs STT & TTS (without it, TTS outputs a silent fallback MP3).
- `ELEVENLABS_VOICE_ID` — Optional voice preset ID (defaults to `21m00Tcm4TlvDq8ikWAM`).
- `PUBLIC_BASE_URL` / `SKILL_CARD_BASE_URL` — Base URL used for QR verification and share links.
- `GEMINI_API_KEY`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`, `AWS_S3_BUCKET_NAME` — Optional teammate integration keys defined in `.env.example`.

---

## Quick Usage

### Run Standalone Module Demos

Each module includes a `__main__` self-test/demo block:

```bash
python skill_card.py
python voice_service.py
python extras_helper.py
```

### Python Integration Example

```python
from skill_card import generate_skill_card_image, create_whatsapp_share_link, generate_qr_base64
from voice_service import build_spoken_summary, generate_voice_output
from extras_helper import get_official_schemes

card_data = {
    "card_id": "WKR-2024-HI01",
    "worker_name": "रमेश कुमार (Ramesh Kumar)",
    "language": "hi",  # "en" | "hi" | "kn"
    "matched_role": "सहायक इलेक्ट्रीशियन (Assistant Electrician)",
    "confirmed_skills": [
        "घरेलू वायरिंग (House Wiring)",
        "सर्किट रिपेयर (Circuit Repair)",
        "सोलर पैनल इंस्टालेशन",
    ],
    "next_course": "सोलर रूफटॉप तकनीशियन (Surya Mitra)",
    "nearest_centre": "पीएमकेके कौशल केंद्र, सेक्टर 62, नोएडा",
    "public_card_url": "https://your-domain.com/verify/WKR-2024-HI01",
    "scheme_name": "पीएम सूर्य घर मुफ्त बिजली योजना",
}

# Generate card PNG, WhatsApp share URL, and QR Base64 data URI
card_png_path = generate_skill_card_image(card_data, output_dir="./generated_cards")
whatsapp_link = create_whatsapp_share_link(card_data)
qr_data_uri = generate_qr_base64(card_data["public_card_url"])

# Build spoken summary & synthesize cached MP3
spoken_script = build_spoken_summary(card_data, language="hi")
tts_result = generate_voice_output(
    spoken_script,
    card_id=card_data["card_id"],
    language="hi",
    output_dir="./audio_cache",
)

# Retrieve official myScheme links
schemes = get_official_schemes("electrician")
```

For full integration snippets and STT usage (`transcribe_worker_voice`), see [INTEGRATION.md](INTEGRATION.md).

---

## Docker & Deployment

The included `Dockerfile` uses `python:3.11-slim` with `fonts-dejavu-core`, `fonts-lohit-deva` (Devanagari), and `fonts-lohit-knda` (Kannada) preinstalled:

```bash
docker build -t voice-skill-prototype .
docker run --rm --env-file .env voice-skill-prototype
```

See [DEPLOY_AWS.md](DEPLOY_AWS.md) for step-by-step instructions to deploy on **AWS App Runner**, **AWS EC2**, **Railway**, or **Render**.
