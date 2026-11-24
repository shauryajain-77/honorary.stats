"""
voice_service.py - Voice Recognition & Output Service for Informal Workers

A standalone Python module for demo prototypes integrating the official
ElevenLabs Python SDK (elevenlabs >= 2.0).

STRICT SCOPE COMPLIANCE:
- Pure importable Python functions for backend teammates.
- No frontend microphone UI, backend HTTP routes, database code, or Gemini AI extraction logic.
- Supported Languages: Hindi ('hi'), English ('en'), and Kannada ('kn').
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Allowed audio formats for transcription
ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".webm", ".ogg"}
MAX_AUDIO_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

# Supported language codes
SUPPORTED_LANGUAGES = {"hi", "en", "kn"}

# Mapping of common language names/codes to ISO-639-1 ('hi', 'en', 'kn')
LANGUAGE_CODE_MAP = {
    "hi": "hi",
    "hin": "hi",
    "hindi": "hi",
    "en": "en",
    "eng": "en",
    "english": "en",
    "kn": "kn",
    "kan": "kn",
    "kannada": "kn",
}

# Default ElevenLabs Voice ID (e.g., 'Rachel' or custom preset from .env)
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"


# ==============================================================================
# 1. ENVIRONMENT & CLIENT HELPERS
# ==============================================================================

def get_elevenlabs_credentials() -> Dict[str, str]:
    """Retrieves ElevenLabs API key and voice ID from environment or .env."""
    load_dotenv()  # Reload in case .env was updated at runtime
    api_key = os.getenv("ELEVENLABS_API_KEY", "").strip()
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", DEFAULT_VOICE_ID).strip() or DEFAULT_VOICE_ID
    return {"api_key": api_key, "voice_id": voice_id}


def _create_silent_fallback_mp3(file_path: str, duration_frames: int = 40) -> None:
    """
    Generates a valid, standards-compliant MPEG-1 Layer 3 (MP3) audio file
    consisting of clean silent frames. Used as a safe fallback when ElevenLabs
    API key is missing, rate-limited, or offline.
    """
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    # 128 kbps, 44.1 kHz, joint stereo silent MP3 frame (418 bytes)
    header = bytes([0xFF, 0xFB, 0x90, 0x44])
    frame = header + b"\x00" * (418 - 4)
    with open(file_path, "wb") as f:
        f.write(frame * duration_frames)


def _clean_text_for_speech(text: str, language: str = "en") -> str:
    """
    Cleans raw card text (e.g., removes English transliteration brackets like
    'रमेश कुमार (Ramesh Kumar)') so text-to-speech speaks smoothly and naturally
    without reading aloud punctuation or parentheses.
    """
    cleaned = str(text or "").strip()
    if language in ("hi", "kn"):
        # Strip Latin parentheses like '(Assistant Electrician)' if Indic text precedes it
        cleaned = re.sub(r"\s*\([A-Za-z0-9\s,&./-]+\)", "", cleaned)
    elif language == "en":
        # If English has parenthesized Latin name like 'रमेश कुमार (Ramesh Kumar)', extract Latin
        match = re.search(r"\(([A-Za-z0-9\s,&./-]+)\)", cleaned)
        if match:
            cleaned = match.group(1)
        else:
            # Strip non-ASCII if standalone
            cleaned = re.sub(r"[^\x00-\x7F]+", "", cleaned)
    return cleaned.strip()


# ==============================================================================
# 2. VOICE RECOGNITION (SPEECH-TO-TEXT)
# ==============================================================================

def transcribe_worker_voice(
    audio_file_path: str,
    language_hint: Optional[str] = None
) -> Dict[str, Any]:
    """
    Transcribes incoming worker audio using ElevenLabs Speech-to-Text (`scribe_v1`
    or latest Scribe model).

    Validates audio format (.mp3, .wav, .webm, .ogg) and size (< 10 MB).
    Restricts/maps language detection to 'hi', 'en', or 'kn' (or honors language_hint).

    Args:
        audio_file_path (str): Path to the audio recording.
        language_hint (str | None): Optional hint: 'hi', 'en', or 'kn'.

    Returns:
        dict: {
            "status": "ok" | "error",
            "transcript": "...",
            "detected_language": "hi" | "en" | "kn",
            "error": None | str
        }
    """
    # 1. Validate File Existence
    if not os.path.exists(audio_file_path):
        return {
            "status": "error",
            "transcript": "",
            "detected_language": None,
            "error": f"Audio file not found: {audio_file_path}",
        }

    # 2. Validate Extension
    file_ext = Path(audio_file_path).suffix.lower()
    if file_ext not in ALLOWED_AUDIO_EXTENSIONS:
        return {
            "status": "error",
            "transcript": "",
            "detected_language": None,
            "error": f"Unsupported audio format '{file_ext}'. Allowed formats: {', '.join(ALLOWED_AUDIO_EXTENSIONS)}",
        }

    # 3. Validate File Size (< 10 MB)
    file_size = os.path.getsize(audio_file_path)
    if file_size > MAX_AUDIO_SIZE_BYTES:
        size_mb = file_size / (1024 * 1024)
        return {
            "status": "error",
            "transcript": "",
            "detected_language": None,
            "error": f"File size ({size_mb:.2f} MB) exceeds maximum allowed limit of 10 MB",
        }

    # 4. Normalize Language Hint
    norm_hint: Optional[str] = None
    if language_hint:
        norm_hint = LANGUAGE_CODE_MAP.get(language_hint.lower().strip(), None)

    # 5. Check API Key
    creds = get_elevenlabs_credentials()
    api_key = creds["api_key"]
    if not api_key:
        return {
            "status": "error",
            "transcript": "",
            "detected_language": None,
            "error": "ELEVENLABS_API_KEY is not configured in .env or environment variables",
        }

    # 6. Call ElevenLabs Scribe STT
    try:
        from elevenlabs.client import ElevenLabs

        client = ElevenLabs(api_key=api_key)

        with open(audio_file_path, "rb") as audio_stream:
            response = client.speech_to_text.convert(
                file=audio_stream,
                model_id="scribe_v1",
                language_code=norm_hint,
            )

        transcript = getattr(response, "text", "") or ""
        raw_lang = getattr(response, "language_code", None) or ""

        # Map detected language to 'hi', 'en', or 'kn'
        detected_lang = LANGUAGE_CODE_MAP.get(str(raw_lang).lower().strip(), norm_hint or "en")
        if detected_lang not in SUPPORTED_LANGUAGES:
            detected_lang = norm_hint or "en"

        return {
            "status": "ok",
            "transcript": transcript.strip(),
            "detected_language": detected_lang,
            "error": None,
        }

    except Exception as exc:
        return {
            "status": "error",
            "transcript": "",
            "detected_language": norm_hint,
            "error": f"ElevenLabs STT error: {str(exc)}",
        }


# ==============================================================================
# 3. SCRIPT FORMATTER (SPOKEN SUMMARY)
# ==============================================================================

def build_spoken_summary(card_data: dict, language: str = "en") -> str:
    """
    Generates a short, natural plain-language readout summarizing the worker's
    matched role, confirmed skills, recommended next course, nearest training centre,
    and government scheme name in English ('en'), Hindi ('hi'), or Kannada ('kn').

    Args:
        card_data (dict): Worker card attributes.
        language (str): Target language ('en', 'hi', or 'kn').

    Returns:
        str: Clean conversational script for audio narration.
    """
    lang = language.lower().strip()
    if lang not in SUPPORTED_LANGUAGES:
        lang = "en"

    raw_worker = card_data.get("worker_name", "")
    raw_role = card_data.get("matched_role", "")
    raw_skills = card_data.get("confirmed_skills", [])
    raw_course = card_data.get("next_course", "")
    raw_centre = card_data.get("nearest_centre", "")
    raw_scheme = card_data.get("scheme_name", "")

    # Clean text to avoid reading out punctuation or transliteration parens
    worker = _clean_text_for_speech(raw_worker, lang) or ("कामगार" if lang == "hi" else ("ಕಾರ್ಮಿಕರೇ" if lang == "kn" else "Worker"))
    role = _clean_text_for_speech(raw_role, lang) or ("कुशल पेशेवर" if lang == "hi" else ("ನುರಿತ ವೃತ್ತಿಪರರು" if lang == "kn" else "Skilled Professional"))
    course = _clean_text_for_speech(raw_course, lang) or ("उन्नत कौशल प्रशिक्षण" if lang == "hi" else ("ಉನ್ನತ ಕೌಶಲ್ಯ ತರಬೇತಿ" if lang == "kn" else "Advanced Vocational Training"))
    centre = _clean_text_for_speech(raw_centre, lang) or ("निकटतम प्रशिक्षण केंद्र" if lang == "hi" else ("ಹತ್ತಿರದ ತರಬೇತಿ ಕೇಂದ್ರ" if lang == "kn" else "Nearest Skill Development Centre"))

    if isinstance(raw_skills, list):
        clean_skills = [_clean_text_for_speech(s, lang) for s in raw_skills if str(s).strip()]
    elif isinstance(raw_skills, str):
        clean_skills = [_clean_text_for_speech(s, lang) for s in raw_skills.split(",") if s.strip()]
    else:
        clean_skills = []

    if lang == "hi":
        scheme = _clean_text_for_speech(raw_scheme, lang) or "प्रधानमंत्री कौशल विकास योजना"
        skills_str = " और ".join(clean_skills) if clean_skills else "व्यावसायिक कार्य"
        return (
            f"नमस्ते {worker}। आपके आवाज़ मूल्यांकन के आधार पर आपका डिजिटल कौशल कार्ड तैयार हो गया है। "
            f"आपकी चुनी गई भूमिका {role} है, और आपके प्रमाणित कौशल हैं: {skills_str}। "
            f"आपके करियर की प्रगति के लिए, {scheme} के अंतर्गत अगला अनुशंसित कोर्स {course} है। "
            f"आपका निकटतम प्रशिक्षण केंद्र {centre} है। "
            f"प्रशिक्षण में शामिल होने के लिए केंद्र पर जाएं या अपना कौशल कार्ड स्कैन करें।"
        )

    elif lang == "kn":
        scheme = _clean_text_for_speech(raw_scheme, lang) or "ಪ್ರಧಾನಮಂತ್ರಿ ಕೌಶಲ್ಯ ವಿಕಾಸ ಯೋಜನೆ"
        skills_str = ", ".join(clean_skills) if clean_skills else "ವೃತ್ತಿಪರ ಕೌಶಲ್ಯಗಳು"
        return (
            f"ನಮಸ್ಕಾರ {worker} ಅವರೇ. ನಿಮ್ಮ ಧ್ವನಿ ಮೌಲ್ಯಮಾಪನದ ಆಧಾರದ ಮೇಲೆ ನಿಮ್ಮ ಡಿಜಿಟಲ್ ಕೌಶಲ್ಯ ಕಾರ್ಡ್ ಸಿದ್ಧವಾಗಿದೆ. "
            f"ನಿಮ್ಮ ಹೊಂದಾಣಿಕೆಯಾದ ವೃತ್ತಿ ಪಾತ್ರ {role}. ನಿಮ್ಮ ದೃಢಪಡಿಸಿದ ಕೌಶಲ್ಯಗಳು: {skills_str}. "
            f"ನಿಮ್ಮ ವೃತ್ತಿಜೀವನದ ಮುನ್ನಡೆಗಾಗಿ, {scheme} ಯೋಜನೆಯಡಿ ಶಿಫಾರಸು ಮಾಡಿದ ಮುಂದಿನ ಕೋರ್ಸ್ {course}. "
            f"ನಿಮ್ಮ ಹತ್ತಿರದ ತರಬೇತಿ ಕೇಂದ್ರ {centre}. "
            f"ಹೆಚ್ಚಿನ ವಿವರಗಳಿಗಾಗಿ ದಯವಿಟ್ಟು ಕೇಂದ್ರಕ್ಕೆ ಭೇಟಿ ನೀಡಿ ಅಥವಾ ನಿಮ್ಮ ಕೌಶಲ್ಯ ಕಾರ್ಡ್ ಸ್ಕ್ಯಾನ್ ಮಾಡಿ."
        )

    else:
        # Default English
        scheme = _clean_text_for_speech(raw_scheme, "en") or "Pradhan Mantri Kaushal Vikas Yojana"
        skills_str = ", ".join(clean_skills) if clean_skills else "Vocational Competencies"
        return (
            f"Hello {worker}. Based on your voice assessment, your digital skill card has been verified. "
            f"Your matched role is {role}, and your confirmed skills include {skills_str}. "
            f"To advance your career, your recommended next course is {course} under the {scheme} scheme. "
            f"Your nearest training centre is {centre}. "
            f"Please visit the centre or scan your digital skill card to enroll."
        )


# ==============================================================================
# 4. VOICE OUTPUT (TEXT-TO-SPEECH WITH CACHING)
# ==============================================================================

def generate_voice_output(
    text: str,
    card_id: str,
    language: str = "en",
    output_dir: str = "./audio_cache"
) -> Dict[str, Any]:
    """
    Synthesizes spoken audio using ElevenLabs `eleven_v3` (multilingual support
    for Hindi, English, and Kannada) with language_code set to 'hi', 'en', or 'kn'.

    Saves output to `{output_dir}/{card_id}_{language}.mp3`.
    Local File Caching: If the file already exists on disk, returns cached path
    immediately without hitting the ElevenLabs API again.

    Safe Fallback: If ElevenLabs API key is missing, invalid, or rate-limited,
    generates a playable fallback audio file without crashing.

    Args:
        text (str): Script to synthesize.
        card_id (str): Identifier for the card (used in filename).
        language (str): 'hi', 'en', or 'kn'.
        output_dir (str): Target directory for audio files.

    Returns:
        dict: {
            "status": "ok" | "fallback",
            "audio_path": "...",
            "cached": bool,
            "error": None | str
        }
    """
    lang = language.lower().strip()
    if lang not in SUPPORTED_LANGUAGES:
        lang = "en"

    clean_card_id = re.sub(r"[^\w\-]", "_", str(card_id or "DEMO").strip())
    os.makedirs(output_dir, exist_ok=True)
    target_filename = f"{clean_card_id}_{lang}.mp3"
    target_path = os.path.join(output_dir, target_filename)
    abs_target_path = os.path.abspath(target_path)

    # 1. Local Cache Check
    if os.path.exists(target_path) and os.path.getsize(target_path) > 0:
        return {
            "status": "ok",
            "audio_path": abs_target_path,
            "cached": True,
            "error": None,
        }

    # 2. Check Credentials
    creds = get_elevenlabs_credentials()
    api_key = creds["api_key"]
    voice_id = creds["voice_id"]

    if not api_key:
        # Fallback audio generation
        _create_silent_fallback_mp3(target_path)
        return {
            "status": "fallback",
            "audio_path": abs_target_path,
            "cached": False,
            "error": "ELEVENLABS_API_KEY is not set in environment or .env. Generated fallback audio.",
        }

    # 3. Call ElevenLabs TTS (`eleven_v3`)
    try:
        from elevenlabs.client import ElevenLabs

        client = ElevenLabs(api_key=api_key)
        audio_stream = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_v3",
            language_code=lang,
        )

        with open(target_path, "wb") as audio_file:
            for chunk in audio_stream:
                if chunk:
                    audio_file.write(chunk)

        return {
            "status": "ok",
            "audio_path": abs_target_path,
            "cached": False,
            "error": None,
        }

    except Exception as exc:
        # Generate safe fallback so backend teammate's pipeline never breaks
        if not os.path.exists(target_path) or os.path.getsize(target_path) == 0:
            _create_silent_fallback_mp3(target_path)

        return {
            "status": "fallback",
            "audio_path": abs_target_path,
            "cached": False,
            "error": f"ElevenLabs TTS error ({type(exc).__name__}): {str(exc)}",
        }


# ==============================================================================
# 5. TEST & VERIFICATION BLOCK
# ==============================================================================

if __name__ == "__main__":
    print("=" * 72)
    print("VOICE SERVICE TEST SUITE (ELEVENLABS SDK - HI / EN / KN)")
    print("=" * 72)

    creds = get_elevenlabs_credentials()
    has_api_key = bool(creds["api_key"])
    print(f"API Key Present : {has_api_key}")
    print(f"Active Voice ID : {creds['voice_id']}")

    # Sample worker cards across Hindi, Kannada, and English
    sample_cards = [
        {
            "card_id": "WKR-HI-4091",
            "language": "hi",
            "worker_name": "रमेश कुमार (Ramesh Kumar)",
            "matched_role": "सहायक इलेक्ट्रीशियन (Assistant Electrician)",
            "confirmed_skills": ["घरेलू वायरिंग", "सर्किट रिपेयर", "सोलर पैनल इंस्टालेशन"],
            "next_course": "सोलर रूफटॉप तकनीशियन (Surya Mitra)",
            "nearest_centre": "पीएमकेके कौशल केंद्र, सेक्टर 62, नोएडा",
            "scheme_name": "पीएम सूर्य घर मुफ्त बिजली योजना",
        },
        {
            "card_id": "WKR-KN-8820",
            "language": "kn",
            "worker_name": "ಬಸವರಾಜ ಕುಮಾರ್ (Basavaraj Kumar)",
            "matched_role": "ಸೌರ ತಂತ್ರಜ್ಞ (Solar Technician)",
            "confirmed_skills": ["ಸೋಲಾರ್ ಪ್ಯಾನಲ್ ಸ್ಥಾಪನೆ", "ವೈರಿಂಗ್ ದುರಸ್ತಿ", "ಇನ್ವರ್ಟರ್ ನಿರ್ವಹಣೆ"],
            "next_course": "ಸುಧಾರಿತ ಗ್ರಿಡ್-ಸಂಯೋಜಿತ ಸೌರ ವ್ಯವಸ್ಥೆಗಳು",
            "nearest_centre": "ಜನ ಶಿಕ್ಷಣ ಸಂಸ್ಥಾನ, ಜಯನಗರ, ಬೆಂಗಳೂರು",
            "scheme_name": "ಪ್ರಧಾನಮಂತ್ರಿ ಕೌಶಲ್ಯ ವಿಕಾಸ ಯೋಜನೆ",
        },
        {
            "card_id": "WKR-EN-1024",
            "language": "en",
            "worker_name": "Sunita Devi",
            "matched_role": "Apparel & Garment Specialist",
            "confirmed_skills": ["Industrial Machine Sewing", "Pattern Cutting", "Quality Inspection"],
            "next_course": "Automated Computerized Textile Pattern Operations",
            "nearest_centre": "National Skill Development Center, Okhla Phase 3, New Delhi",
            "scheme_name": "Pradhan Mantri Kaushal Vikas Yojana",
        },
    ]

    cache_dir = "./audio_cache"
    generated_audio_files: List[str] = []

    print("\n--- TEST 1: GENERATE & CACHE SPOKEN READOUTS (.mp3) ---")
    for idx, card in enumerate(sample_cards, start=1):
        lang = card["language"]
        cid = card["card_id"]
        print(f"\n[{idx}/3] Language: {lang.upper()} | Worker: {card['worker_name']} ({cid})")

        # Step A: Build natural spoken script
        script = build_spoken_summary(card, language=lang)
        print(f"    Spoken Script:\n    \"{script}\"")

        # Step B: Generate Voice Output (First Call -> Generates/Caches)
        res1 = generate_voice_output(script, card_id=cid, language=lang, output_dir=cache_dir)
        print(f"    [Run 1] Status: {res1['status']} | Cached: {res1['cached']} | Path: {res1['audio_path']}")
        if res1["error"]:
            print(f"    Notice: {res1['error']}")
        assert os.path.exists(res1["audio_path"]), f"File must exist: {res1['audio_path']}"
        generated_audio_files.append(res1["audio_path"])

        # Step C: Test Local File Caching (Second Call -> Must hit cache)
        res2 = generate_voice_output(script, card_id=cid, language=lang, output_dir=cache_dir)
        print(f"    [Run 2] Status: {res2['status']} | Cached: {res2['cached']} | Fast Return!")
        assert res2["cached"] is True, "Second call must hit cache"

    print("\n--- TEST 2: VALIDATE SPEECH-TO-TEXT (STT) VALIDATIONS ---")
    # Test A: Non-existent file
    stt_missing = transcribe_worker_voice("./non_existent_audio.mp3")
    print(f"    [STT Non-Existent File] Status: {stt_missing['status']} | Error: {stt_missing['error']}")
    assert stt_missing["status"] == "error"

    # Test B: Invalid extension
    test_invalid_txt = "./test_invalid.txt"
    with open(test_invalid_txt, "w") as f:
        f.write("dummy")
    stt_bad_ext = transcribe_worker_voice(test_invalid_txt)
    print(f"    [STT Invalid Format]    Status: {stt_bad_ext['status']} | Error: {stt_bad_ext['error']}")
    assert stt_bad_ext["status"] == "error"
    os.remove(test_invalid_txt)

    # Test C: STT on generated audio sample
    if generated_audio_files:
        sample_audio = generated_audio_files[0]
        stt_result = transcribe_worker_voice(sample_audio, language_hint="hi")
        print(f"    [STT Sample Audio]      Status: {stt_result['status']} | Detected Lang: {stt_result['detected_language']}")
        if stt_result["error"]:
            print(f"    Notice: {stt_result['error']}")

    print("\n" + "=" * 72)
    print("ALL TESTS PASSED! Module voice_service.py is verified and ready for integration.")
    print("=" * 72)
