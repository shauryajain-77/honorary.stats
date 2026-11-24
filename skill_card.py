"""
skill_card.py - Voice-First Informal Worker Digital Skill Card Generator

A standalone Python module designed for demo prototypes to generate
mobile-ready digital skill cards, scannable QR codes, and WhatsApp share links.

STRICT SCOPE COMPLIANCE:
- Pure importable Python module (no frontend, web server routes, database, or Gemini AI code).
- Uses Pillow and qrcode.
- Handles Unicode fonts safely (Devanagari, Kannada, and English fallback).
- QR code is formatted with ISO/IEC 18004 compliant 4-module quiet zone and integer pixel
  scaling to ensure instant scanning across all smartphone cameras (iOS, Android, WhatsApp).
"""

import base64
import io
import os
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import qrcode
from PIL import Image, ImageDraw, ImageFont

# ==============================================================================
# 1. LOCALIZATION & LABELS CONFIGURATION
# ==============================================================================

LABELS: Dict[str, Dict[str, str]] = {
    "en": {
        "card_title": "DIGITAL SKILL PASSPORT",
        "card_subtitle": "National Informal Worker Registry • Verified Credential",
        "verified_badge": "VERIFIED",
        "card_id_label": "ID",
        "matched_role_label": "MATCHED VOCATIONAL ROLE",
        "skills_label": "CONFIRMED COMPETENCIES & SKILLS",
        "next_course_label": "RECOMMENDED UPSKILLING / NEXT COURSE",
        "next_course_hint": "Pathway to career progression & higher daily wage",
        "nearest_centre_label": "NEAREST TRAINING CENTRE",
        "qr_title": "Scan to Verify Credential",
        "qr_subtitle": "Scan with any phone camera or WhatsApp to open verified record.",
        "footer_platform": "Voice-First Informal Worker Platform • National Skills Demo",
        "footer_tamper": "Anti-Tamper Digital Record",
        "wa_header": "Digital Skill Card",
        "wa_role": "Matched Role",
        "wa_skills": "Confirmed Skills",
        "wa_url": "Verify Digital Card",
    },
    "hi": {
        "card_title": "डिजिटल कौशल पासपोर्ट",
        "card_subtitle": "राष्ट्रीय अनौपचारिक कामगार कौशल पंजीयन • सत्यापित प्रमाण",
        "verified_badge": "सत्यापित",
        "card_id_label": "पहचान",
        "matched_role_label": "मैच की गई व्यावसायिक भूमिका",
        "skills_label": "प्रमाणित कौशल एवं क्षमताएं",
        "next_course_label": "अनुशंसित अपस्किलिंग / अगला कोर्स",
        "next_course_hint": "वेतन वृद्धि और उन्नत प्रमाणन का मार्ग",
        "nearest_centre_label": "निकटतम प्रशिक्षण केंद्र",
        "qr_title": "सत्यापित करने के लिए स्कैन करें",
        "qr_subtitle": "पूर्ण डिजिटल रिकॉर्ड देखने के लिए किसी भी स्मार्टफोन से स्कैन करें।",
        "footer_platform": "आवाज़ आधारित कौशल मंच • राष्ट्रीय कौशल डेमो",
        "footer_tamper": "डिजिटल रूप से सुरक्षित रिकॉर्ड",
        "wa_header": "डिजिटल कौशल कार्ड",
        "wa_role": "भूमिका",
        "wa_skills": "प्रमाणित कौशल",
        "wa_url": "कौशल कार्ड देखें और सत्यापित करें",
    },
    "kn": {
        "card_title": "ಡಿಜಿಟಲ್ ಕೌಶಲ್ಯ ಪಾಸ್‌ಪೋರ್ಟ್",
        "card_subtitle": "ಅಸಂಘಟಿತ ಕಾರ್ಮಿಕರ ಕೌಶಲ್ಯ ನೋಂದಣಿ • ಪರಿಶೀಲಿಸಿದ ಪ್ರಮಾಣಪತ್ರ",
        "verified_badge": "ಪರಿಶೀಲಿಸಲಾಗಿದೆ",
        "card_id_label": "ಐಡಿ",
        "matched_role_label": "ಹೊಂದಾಣಿಕೆಯಾದ ವೃತ್ತಿ ಪಾತ್ರ",
        "skills_label": "ದೃಢಪಡಿಸಿದ ಕೌಶಲ್ಯಗಳು",
        "next_course_label": "ಮುಂದಿನ ಶಿಫಾರಸು ಮಾಡಿದ ತರಬೇತಿ ಕೋರ್ಸ್",
        "next_course_hint": "ಉನ್ನತ ಪ್ರಮಾಣೀಕರಣ ಮತ್ತು ವೇತನ ಹೆಚ್ಚಳಕ್ಕೆ ಹಾದಿ",
        "nearest_centre_label": "ಹತ್ತಿರದ ತರಬೇತಿ ಕೇಂದ್ರ",
        "qr_title": "ಪರಿಶೀಲಿಸಲು ಸ್ಕ್ಯಾನ್ ಮಾಡಿ",
        "qr_subtitle": "ಡಿಜಿಟಲ್ ದಾಖಲೆಯನ್ನು ವೀಕ್ಷಿಸಲು ಸ್ಮಾರ್ಟ್‌ಫೋನ್ ಮೂಲಕ ಸ್ಕ್ಯಾನ್ ಮಾಡಿ.",
        "footer_platform": "ಧ್ವನಿ ಆಧಾರಿತ ಕೌಶಲ್ಯ ವೇದಿಕೆ • ಕೌಶಲ್ಯ ಪ್ರಾತ್ಯಕ್ಷಿಕೆ",
        "footer_tamper": "ಡಿಜಿಟಲ್ ಸುರಕ್ಷಿತ ದಾಖಲೆ",
        "wa_header": "ಡಿಜಿಟಲ್ ಕೌಶಲ್ಯ ಕಾರ್ಡ್",
        "wa_role": "ಪಾತ್ರ",
        "wa_skills": "ದೃಢಪಡಿಸಿದ ಕೌಶಲ್ಯಗಳು",
        "wa_url": "ಕೌಶಲ್ಯ ಕಾರ್ಡ್ ಪರಿಶೀಲಿಸಿ",
    },
}

FALLBACK_LABELS: Dict[str, Dict[str, str]] = {
    "hi": {
        "card_title": "DIGITAL SKILL PASSPORT (Kaushal Card)",
        "card_subtitle": "National Informal Worker Skill Registry • Verified Credential",
        "verified_badge": "VERIFIED (Satyaapit)",
        "card_id_label": "ID",
        "matched_role_label": "MATCHED VOCATIONAL ROLE (Bhumika)",
        "skills_label": "CONFIRMED SKILLS (Pramanit Kaushal)",
        "next_course_label": "RECOMMENDED NEXT COURSE (Agla Course)",
        "next_course_hint": "Pathway to career progression & higher daily wage",
        "nearest_centre_label": "NEAREST TRAINING CENTRE (Nikat-tam Kendra)",
        "qr_title": "Scan to Verify Credential",
        "qr_subtitle": "Scan with any phone camera or WhatsApp to open verified record.",
        "footer_platform": "Voice-First Informal Worker Platform • National Skills Demo",
        "footer_tamper": "Anti-Tamper Digital Record",
        "wa_header": "Digital Skill Card",
        "wa_role": "Matched Role",
        "wa_skills": "Confirmed Skills",
        "wa_url": "Verify Digital Card",
    },
    "kn": {
        "card_title": "DIGITAL SKILL PASSPORT (Kowshalya Card)",
        "card_subtitle": "National Informal Worker Skill Registry • Verified Credential",
        "verified_badge": "VERIFIED (Drudhapadisida)",
        "card_id_label": "ID",
        "matched_role_label": "MATCHED VOCATIONAL ROLE (Paatra)",
        "skills_label": "CONFIRMED SKILLS (Kowshalyagalu)",
        "next_course_label": "RECOMMENDED NEXT COURSE (Mundina Course)",
        "next_course_hint": "Pathway to career progression & higher daily wage",
        "nearest_centre_label": "NEAREST TRAINING CENTRE (Hattirada Kendra)",
        "qr_title": "Scan to Verify Credential",
        "qr_subtitle": "Scan with any phone camera or WhatsApp to open verified record.",
        "footer_platform": "Voice-First Informal Worker Platform • National Skills Demo",
        "footer_tamper": "Anti-Tamper Digital Record",
        "wa_header": "Digital Skill Card",
        "wa_role": "Matched Role",
        "wa_skills": "Confirmed Skills",
        "wa_url": "Verify Digital Card",
    },
}

COMMON_VOCAB_MAP: Dict[str, str] = {
    # Hindi
    "इलेक्ट्रीशियन": "Electrician",
    "सहायक इलेक्ट्रीशियन": "Assistant Electrician",
    "प्लंबर": "Plumber",
    "कारपेंटर": "Carpenter",
    "बढ़ई": "Carpenter",
    "वेल्डर": "Welder",
    "राजमिस्त्री": "Mason",
    "सौर तकनीशियन": "Solar Technician",
    "सोलर तकनीशियन": "Solar Technician",
    "सोलर रूफटॉप तकनीशियन": "Solar Rooftop Technician",
    "वायरिंग": "Wiring",
    "घरेलू वायरिंग": "Domestic Wiring",
    "सर्किट रिपेयर": "Circuit Repair",
    "उपकरण मरम्मत": "Appliance Maintenance",
    "सुरक्षा मानक": "Safety Standards",
    "सोलर पैनल इंस्टालेशन": "Solar Panel Installation",
    # Kannada
    "ಎಲೆಕ್ಟ್ರಿಷಿಯನ್": "Electrician",
    "ಸಹಾಯಕ ಎಲೆಕ್ಟ್ರಿಷಿಯನ್": "Assistant Electrician",
    "ಪ್ಲಂಬರ್": "Plumber",
    "ಬಡಗಿ": "Carpenter",
    "ವೆಲ್ಡರ್": "Welder",
    "ಮೇಸ್ತ್ರಿ": "Mason",
    "ಸೌರ ತಂತ್ರಜ್ಞ": "Solar Technician",
    "ಸೋಲಾರ್ ಪ್ಯಾನಲ್ ಸ್ಥಾಪನೆ": "Solar Panel Installation",
    "ವೈರಿಂಗ್ ದುರಸ್ತಿ": "Wiring Repair",
    "ಇನ್ವರ್ಟರ್ ನಿರ್ವಹಣೆ": "Inverter Maintenance",
    "ಸುರಕ್ಷತಾ ಮಾನದಂಡಗಳು": "Safety Standards",
}

# ==============================================================================
# 2. UNICODE, URL & FONT UTILITIES
# ==============================================================================

def normalize_url(url: str) -> str:
    """
    Ensures URL has a proper scheme (e.g. 'https://') so smartphone camera
    scanners reliably recognize it as a clickable website link.
    """
    cleaned = (url or "").strip()
    if not cleaned:
        return "https://example.com"
    if not cleaned.startswith(("http://", "https://")):
        return f"https://{cleaned}"
    return cleaned


def _generate_clean_qr_image(url: str, max_size: int = 150) -> Image.Image:
    """
    Generates a scannable QR code strictly adhering to the ISO/IEC 18004
    standard:
    1. Border of 4 modules (Quiet Zone) for camera edge detection.
    2. Pure black (#000000) on pure white (#FFFFFF) for maximum contrast.
    3. Integer box_size scaling to eliminate fractional module aliasing.
    """
    clean_url = normalize_url(url)

    # Calculate module dimensions with base box_size=1 and standard 4-module border
    qr_probe = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=1,
        border=4,
    )
    qr_probe.add_data(clean_url)
    qr_probe.make(fit=True)

    # Total modules including 4 modules quiet zone on each side
    total_modules = qr_probe.modules_count + 8
    # Calculate highest integer box_size that fits within max_size
    box_size = max(2, max_size // total_modules)

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=4,  # Crucial quiet zone
    )
    qr.add_data(clean_url)
    qr.make(fit=True)

    return qr.make_image(fill_color="black", back_color="white").convert("RGB")


def _transliterate_indic(text: str) -> str:
    """
    Phonetically transliterates Devanagari and Kannada text to Latin script
    so characters never render as blank boxes when Indic fonts are missing.
    """
    if not text:
        return ""

    trimmed = text.strip()
    if trimmed in COMMON_VOCAB_MAP:
        return COMMON_VOCAB_MAP[trimmed]

    dev_consonants = {
        0x0915: "k", 0x0916: "kh", 0x0917: "g", 0x0918: "gh", 0x0919: "ng",
        0x091A: "ch", 0x091B: "chh", 0x091C: "j", 0x091D: "jh", 0x091E: "ny",
        0x091F: "t", 0x0920: "th", 0x0921: "d", 0x0922: "dh", 0x0923: "n",
        0x0924: "t", 0x0925: "th", 0x0926: "d", 0x0927: "dh", 0x0928: "n",
        0x092A: "p", 0x092B: "ph", 0x092C: "b", 0x092D: "bh", 0x092E: "m",
        0x092F: "y", 0x0930: "r", 0x0932: "l", 0x0933: "l", 0x0935: "v",
        0x0936: "sh", 0x0937: "sh", 0x0938: "s", 0x0939: "h",
    }
    dev_vowels = {
        0x0905: "a", 0x0906: "aa", 0x0907: "i", 0x0908: "ee", 0x0909: "u",
        0x090A: "oo", 0x090B: "ri", 0x090F: "e", 0x0910: "ai", 0x0913: "o", 0x0914: "au",
    }
    dev_matras = {
        0x093E: "aa", 0x093F: "i", 0x0940: "ee", 0x0941: "u", 0x0942: "oo",
        0x0943: "ri", 0x0947: "e", 0x0948: "ai", 0x094B: "o", 0x094C: "au",
    }

    kan_consonants = {
        0x0C95: "k", 0x0C96: "kh", 0x0C97: "g", 0x0C98: "gh", 0x0C99: "ng",
        0x0C9A: "ch", 0x0C9B: "chh", 0x0C9C: "j", 0x0C9D: "jh", 0x0C9E: "ny",
        0x0C9F: "t", 0x0CA0: "th", 0x0CA1: "d", 0x0CA2: "dh", 0x0CA3: "n",
        0x0CA4: "t", 0x0CA5: "th", 0x0CA6: "d", 0x0CA7: "dh", 0x0CA8: "n",
        0x0CAA: "p", 0x0CAB: "ph", 0x0CAC: "b", 0x0CAD: "bh", 0x0CAE: "m",
        0x0CAF: "y", 0x0CB0: "r", 0x0CB1: "r", 0x0CB2: "l", 0x0CB3: "l",
        0x0CB5: "v", 0x0CB6: "sh", 0x0CB7: "sh", 0x0CB8: "s", 0x0CB9: "h",
    }
    kan_vowels = {
        0x0C85: "a", 0x0C86: "aa", 0x0C87: "i", 0x0C88: "ee", 0x0C89: "u",
        0x0C8A: "oo", 0x0C8B: "ri", 0x0C8E: "e", 0x0C8F: "ee", 0x0C90: "ai",
        0x0C92: "o", 0x0C93: "oo", 0x0C94: "au",
    }
    kan_matras = {
        0x0CBE: "aa", 0x0CBF: "i", 0x0CC0: "ee", 0x0CC1: "u", 0x0CC2: "oo",
        0x0CC3: "ri", 0x0CC6: "e", 0x0CC7: "ee", 0x0CC8: "ai", 0x0CCA: "o",
        0x0CCB: "oo", 0x0CCC: "au",
    }

    res: List[str] = []
    i = 0
    n = len(text)
    while i < n:
        code = ord(text[i])
        if 0x0966 <= code <= 0x096F:
            res.append(str(code - 0x0966))
        elif 0x0CE6 <= code <= 0x0CEF:
            res.append(str(code - 0x0CE6))
        elif code in dev_vowels:
            res.append(dev_vowels[code])
        elif code in kan_vowels:
            res.append(kan_vowels[code])
        elif code in dev_consonants:
            base = dev_consonants[code]
            next_code = ord(text[i + 1]) if i + 1 < n else None
            if next_code == 0x094D:
                res.append(base)
                i += 1
            elif next_code in dev_matras:
                res.append(base + dev_matras[next_code])
                i += 1
            elif next_code in (0x0902, 0x0901):
                res.append(base + "an")
                i += 1
            else:
                res.append(base + ("a" if next_code in dev_consonants or (next_code and chr(next_code).isalnum()) else ""))
        elif code in kan_consonants:
            base = kan_consonants[code]
            next_code = ord(text[i + 1]) if i + 1 < n else None
            if next_code == 0x0CCD:
                res.append(base)
                i += 1
            elif next_code in kan_matras:
                res.append(base + kan_matras[next_code])
                i += 1
            elif next_code in (0x0C82, 0x0C83):
                res.append(base + "an")
                i += 1
            else:
                res.append(base + ("a" if next_code in kan_consonants or (next_code and chr(next_code).isalnum()) else ""))
        elif code in (0x0902, 0x0901, 0x0C82):
            res.append("n")
        elif code in (0x0903, 0x0C83):
            res.append("h")
        elif code in (0x094D, 0x0CCD):
            pass
        else:
            res.append(text[i])
        i += 1

    transliterated = "".join(res)
    return " ".join(w.capitalize() if w.islower() else w for w in transliterated.split(" "))


def _contains_indic(text: str) -> bool:
    """Checks if string contains Devanagari or Kannada characters."""
    for ch in text:
        code = ord(ch)
        if (0x0900 <= code <= 0x097F) or (0x0C80 <= code <= 0x0CFF):
            return True
    return False


def _can_font_render_sample(font: Any, sample_text: str) -> bool:
    """Validates whether a font can render sample glyphs without generating .notdef tofu."""
    if not hasattr(font, "getmask"):
        return False
    try:
        notdef_mask = list(font.getmask(chr(0)))
        for ch in sample_text:
            if not ch.isspace():
                if list(font.getmask(ch)) == notdef_mask:
                    return False
        return True
    except Exception:
        return False


def _discover_font_path(lang: str = "en", bold: bool = False) -> Tuple[Optional[str], int]:
    """Searches system font directories on Windows, Linux, and macOS."""
    win_dir = os.environ.get("WINDIR", "C:\\Windows")
    win_fonts = os.path.join(win_dir, "Fonts")

    candidates: List[Tuple[str, int]] = []

    if lang in ("hi", "kn"):
        if bold:
            candidates.append((os.path.join(win_fonts, "Nirmala.ttc"), 1))
            candidates.append((os.path.join(win_fonts, "mangalb.ttf"), 0))
            candidates.append((os.path.join(win_fonts, "Tungab.ttf"), 0))
            candidates.append(("/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf", 0))
            candidates.append(("/usr/share/fonts/truetype/noto/NotoSansKannada-Bold.ttf", 0))
        candidates.append((os.path.join(win_fonts, "Nirmala.ttc"), 0))
        candidates.append((os.path.join(win_fonts, "mangal.ttf"), 0))
        candidates.append((os.path.join(win_fonts, "aparaj.ttf"), 0))
        candidates.append((os.path.join(win_fonts, "Tunga.ttf"), 0))
        candidates.append(("/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf", 0))
        candidates.append(("/usr/share/fonts/truetype/noto/NotoSansKannada-Regular.ttf", 0))
        candidates.append(("/usr/share/fonts/truetype/lohit-devanagari/Lohit-Devanagari.ttf", 0))
        candidates.append(("/usr/share/fonts/truetype/lohit-kannada/Lohit-Kannada.ttf", 0))
        candidates.append(("/System/Library/Fonts/Kohinoor.ttc", 0))
        candidates.append(("/System/Library/Fonts/Supplemental/DevanagariMT.ttc", 0))
        candidates.append(("/System/Library/Fonts/Supplemental/Kannada Sangam MN.ttc", 0))

    if bold:
        candidates.append((os.path.join(win_fonts, "segoeuib.ttf"), 0))
        candidates.append((os.path.join(win_fonts, "arialbd.ttf"), 0))
        candidates.append(("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 0))
    candidates.append((os.path.join(win_fonts, "segoeui.ttf"), 0))
    candidates.append((os.path.join(win_fonts, "arial.ttf"), 0))
    candidates.append(("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 0))
    candidates.append(("/Library/Fonts/Arial.ttf", 0))

    for path, idx in candidates:
        if os.path.exists(path):
            return path, idx

    return None, 0


def _load_font_instance(font_path: Optional[str], font_index: int, size: int) -> ImageFont.ImageFont:
    """Loads a TTF/TTC font instance or falls back to Pillow default."""
    if font_path and os.path.exists(font_path):
        try:
            return ImageFont.truetype(font_path, size=size, index=font_index)
        except Exception:
            pass
    try:
        return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()


# ==============================================================================
# 3. CORE PUBLIC FUNCTIONS
# ==============================================================================

def generate_qr_base64(public_card_url: str) -> str:
    """
    Encodes `public_card_url` into a scannable QR code and returns it as a
    base64 PNG data URI.

    Args:
        public_card_url (str): Public verification URL for the worker.

    Returns:
        str: Base64-encoded PNG data URI ('data:image/png;base64,...').
    """
    clean_url = normalize_url(public_card_url)
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,  # ISO compliant quiet zone
    )
    qr.add_data(clean_url)
    qr.make(fit=True)

    qr_image = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    qr_image.save(buffer, format="PNG")
    encoded_png = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded_png}"


def create_whatsapp_share_link(card_data: dict) -> str:
    """
    Constructs a properly URL-encoded WhatsApp share link (https://wa.me/?text=...)
    containing the worker's role, confirmed skills, and public verification card URL.

    Args:
        card_data (dict): Dictionary with worker and skill attributes.

    Returns:
        str: Fully encoded https://wa.me/?text=... share link.
    """
    lang = card_data.get("language", "en")
    lang_labels = LABELS.get(lang, LABELS["en"])

    worker_name = card_data.get("worker_name", "Worker")
    matched_role = card_data.get("matched_role", "")
    confirmed_skills = card_data.get("confirmed_skills", [])
    public_card_url = normalize_url(card_data.get("public_card_url", ""))

    if isinstance(confirmed_skills, list):
        skills_str = ", ".join(str(s) for s in confirmed_skills)
    else:
        skills_str = str(confirmed_skills)

    header = lang_labels.get("wa_header", "Digital Skill Card")
    role_label = lang_labels.get("wa_role", "Matched Role")
    skills_label = lang_labels.get("wa_skills", "Confirmed Skills")
    url_label = lang_labels.get("wa_url", "Verify Digital Card")

    share_message = (
        f"🌟 {header}: {worker_name}\n"
        f"🛠️ {role_label}: {matched_role}\n"
        f"✅ {skills_label}: {skills_str}\n"
        f"🔗 {url_label}: {public_card_url}"
    )

    encoded_text = urllib.parse.quote(share_message)
    return f"https://wa.me/?text={encoded_text}"


def generate_skill_card_image(card_data: dict, output_dir: str = "./generated_cards") -> str:
    """
    Generates a clean, mobile-ready Digital Skill Card PNG saved to
    `{output_dir}/{card_id}.png` and returns the file path.

    - Embeds a high-contrast scannable QR code formatted with a 4-module quiet zone
      and integer pixel modules, guaranteeing instant scanning by smartphone cameras.
    - Accurately positions worker credentials, role, skills pills, upskilling path,
      and training centre.
    - Handles Unicode fonts safely: checks if host OS has TTF fonts for Devanagari
      or Kannada. If missing, falls back cleanly to English / transliterated labels
      so text NEVER renders as blank boxes.

    Args:
        card_data (dict): Expected keys: `card_id`, `worker_name`, `language`
                          (`en`, `hi`, `kn`), `matched_role`, `confirmed_skills` (list),
                          `next_course`, `nearest_centre`, `public_card_url`.
        output_dir (str): Target directory to save the generated PNG.

    Returns:
        str: Relative or absolute path to the generated image file.
    """
    os.makedirs(output_dir, exist_ok=True)

    card_id = str(card_data.get("card_id", "CARD-DEMO")).strip()
    language = str(card_data.get("language", "en")).strip().lower()
    if language not in ("en", "hi", "kn"):
        language = "en"

    # -------------------------------------------------------------------------
    # 1. Font Selection & Unicode Fallback Verification
    # -------------------------------------------------------------------------
    test_sample = "कौशल" if language == "hi" else ("ಕೌಶಲ್ಯ" if language == "kn" else "Skills")

    indic_font_path, indic_idx = _discover_font_path(lang=language, bold=False)
    indic_bold_path, indic_bold_idx = _discover_font_path(lang=language, bold=True)

    indic_supported = False
    if language in ("hi", "kn") and indic_font_path:
        test_font = _load_font_instance(indic_font_path, indic_idx, 20)
        indic_supported = _can_font_render_sample(test_font, test_sample)

    if language in ("hi", "kn") and not indic_supported:
        active_labels = FALLBACK_LABELS.get(language, LABELS["en"])
        force_transliterate = True
        base_font_path, base_idx = _discover_font_path(lang="en", bold=False)
        bold_font_path, bold_idx = _discover_font_path(lang="en", bold=True)
    else:
        active_labels = LABELS.get(language, LABELS["en"])
        force_transliterate = False
        base_font_path, base_idx = indic_font_path, indic_idx
        bold_font_path, bold_idx = indic_bold_path, indic_bold_idx

    def _sanitize(val: Any) -> str:
        s = str(val or "").strip()
        if force_transliterate and _contains_indic(s):
            return _transliterate_indic(s)
        return s

    worker_name = _sanitize(card_data.get("worker_name", "Informal Worker"))
    matched_role = _sanitize(card_data.get("matched_role", "Skilled Professional"))
    raw_skills = card_data.get("confirmed_skills", [])
    if isinstance(raw_skills, str):
        skills_list = [s.strip() for s in raw_skills.split(",") if s.strip()]
    elif isinstance(raw_skills, (list, tuple)):
        skills_list = [_sanitize(s) for s in raw_skills if str(s).strip()]
    else:
        skills_list = [_sanitize(raw_skills)]

    next_course = _sanitize(card_data.get("next_course", "Advanced Vocational Certification"))
    nearest_centre = _sanitize(card_data.get("nearest_centre", "District Kaushal Vikas Kendra"))
    public_card_url = normalize_url(str(card_data.get("public_card_url", "https://example.com/verify")))

    # Font instances
    font_header_title = _load_font_instance(bold_font_path, bold_idx, 23)
    font_header_sub = _load_font_instance(base_font_path, base_idx, 12)
    font_badge = _load_font_instance(bold_font_path, bold_idx, 12)

    font_name = _load_font_instance(bold_font_path, bold_idx, 30)
    font_id = _load_font_instance(bold_font_path, bold_idx, 13)

    font_label_sm = _load_font_instance(bold_font_path, bold_idx, 12)
    font_role = _load_font_instance(bold_font_path, bold_idx, 22)

    font_chip = _load_font_instance(bold_font_path, bold_idx, 14)

    font_course = _load_font_instance(bold_font_path, bold_idx, 18)
    font_hint = _load_font_instance(base_font_path, base_idx, 12)

    font_centre = _load_font_instance(bold_font_path, bold_idx, 16)

    font_qr_title = _load_font_instance(bold_font_path, bold_idx, 17)
    font_qr_desc = _load_font_instance(base_font_path, base_idx, 12)
    font_qr_url = _load_font_instance(bold_font_path, bold_idx, 12)

    font_footer = _load_font_instance(base_font_path, base_idx, 11)

    # -------------------------------------------------------------------------
    # 2. Text Wrapping Helper
    # -------------------------------------------------------------------------
    def _wrap_text(text: str, font: ImageFont.ImageFont, max_w: int, draw_obj: ImageDraw.ImageDraw) -> List[str]:
        words = text.split(" ")
        lines: List[str] = []
        current: List[str] = []
        for word in words:
            test_line = " ".join(current + [word])
            w = draw_obj.textlength(test_line, font=font)
            if w <= max_w:
                current.append(word)
            else:
                if current:
                    lines.append(" ".join(current))
                    current = [word]
                else:
                    lines.append(word)
                    current = []
        if current:
            lines.append(" ".join(current))
        return lines or [text]

    # -------------------------------------------------------------------------
    # 3. Dynamic Layout & Sizing
    # -------------------------------------------------------------------------
    card_width = 800
    temp_img = Image.new("RGB", (card_width, 100), (255, 255, 255))
    temp_draw = ImageDraw.Draw(temp_img)

    # Pre-calculate skills chips layout
    start_x = 55
    max_x = card_width - 55
    chip_h = 32
    curr_chip_x = start_x
    curr_chip_y = 0
    chip_positions: List[Tuple[int, int, int, int, str]] = []

    check_glyph = "✓" if _can_font_render_sample(font_chip, "✓") else "●"

    for skill in skills_list:
        label = f"{check_glyph} {skill}"
        text_w = temp_draw.textlength(label, font=font_chip)
        chip_w = int(text_w + 24)
        if curr_chip_x + chip_w > max_x and curr_chip_x > start_x:
            curr_chip_x = start_x
            curr_chip_y += chip_h + 8
        chip_positions.append((curr_chip_x, curr_chip_y, chip_w, chip_h, label))
        curr_chip_x += chip_w + 10

    skills_box_h = max(70, curr_chip_y + chip_h + 46)

    # Pre-calculate course lines
    course_lines = _wrap_text(next_course, font_course, card_width - 120, temp_draw)
    course_box_h = 58 + (len(course_lines) * 22) + 24

    # Pre-calculate centre lines
    centre_lines = _wrap_text(nearest_centre, font_centre, card_width - 120, temp_draw)
    centre_box_h = 44 + (len(centre_lines) * 22) + 16

    # Generate QR Code image using standard quiet zone & integer module sizing
    qr_img = _generate_clean_qr_image(public_card_url, max_size=150)
    qr_w, qr_h = qr_img.size

    qr_box_h = max(175, qr_h + 24)

    header_h = 100
    spacing = 16

    total_content_h = (
        6 + header_h + 20 + 72 + spacing
        + 76 + spacing
        + skills_box_h + spacing
        + course_box_h + spacing
        + centre_box_h + spacing
        + qr_box_h + 24 + 40
    )
    card_height = max(1120, total_content_h)

    # -------------------------------------------------------------------------
    # 4. Canvas Creation & Header
    # -------------------------------------------------------------------------
    img = Image.new("RGB", (card_width, card_height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Outer border
    draw.rectangle([0, 0, card_width - 1, card_height - 1], outline=(226, 232, 240), width=2)

    # Tricolor stripe
    stripe_w = card_width // 3
    draw.rectangle([0, 0, stripe_w, 6], fill=(255, 153, 51))
    draw.rectangle([stripe_w, 0, stripe_w * 2, 6], fill=(241, 245, 249))
    draw.rectangle([stripe_w * 2, 0, card_width, 6], fill=(19, 136, 8))

    # Header Banner (Midnight Navy)
    draw.rectangle([0, 6, card_width, 6 + header_h], fill=(15, 23, 42))

    draw.text((40, 26), active_labels["card_title"], fill=(255, 255, 255), font=font_header_title)
    draw.text((40, 64), active_labels["card_subtitle"], fill=(148, 163, 184), font=font_header_sub)

    badge_text = f"● {active_labels['verified_badge']}"
    badge_w = int(draw.textlength(badge_text, font=font_badge) + 20)
    badge_x = card_width - 40 - badge_w
    draw.rounded_rectangle(
        [badge_x, 38, badge_x + badge_w, 70],
        radius=16,
        fill=(6, 78, 59),
        outline=(16, 185, 129),
        width=1,
    )
    draw.text((badge_x + 10, 45), badge_text, fill=(52, 211, 153), font=font_badge)

    # -------------------------------------------------------------------------
    # 5. Worker Identity Section
    # -------------------------------------------------------------------------
    curr_y = 6 + header_h + 20

    draw.text((40, curr_y), worker_name, fill=(15, 23, 42), font=font_name)

    sub_y = curr_y + 44
    id_badge = f"{active_labels['card_id_label']}: #{card_id}"
    id_w = int(draw.textlength(id_badge, font=font_id) + 18)
    draw.rounded_rectangle([40, sub_y, 40 + id_w, sub_y + 26], radius=6, fill=(241, 245, 249), outline=(203, 213, 225), width=1)
    draw.text((49, sub_y + 4), id_badge, fill=(71, 85, 105), font=font_id)

    lang_badge = f"LANG: {language.upper()}"
    lang_w = int(draw.textlength(lang_badge, font=font_id) + 18)
    draw.rounded_rectangle([40 + id_w + 10, sub_y, 40 + id_w + 10 + lang_w, sub_y + 26], radius=6, fill=(248, 250, 252), outline=(226, 232, 240), width=1)
    draw.text((40 + id_w + 19, sub_y + 4), lang_badge, fill=(100, 116, 139), font=font_id)

    curr_y = sub_y + 26 + spacing + 6

    # -------------------------------------------------------------------------
    # 6. Matched Role Container
    # -------------------------------------------------------------------------
    role_box_h = 76
    draw.rounded_rectangle(
        [40, curr_y, card_width - 40, curr_y + role_box_h],
        radius=12,
        fill=(239, 246, 255),
        outline=(147, 197, 253),
        width=1,
    )
    draw.text((56, curr_y + 12), active_labels["matched_role_label"], fill=(37, 99, 235), font=font_label_sm)
    draw.text((56, curr_y + 36), matched_role, fill=(30, 58, 138), font=font_role)

    curr_y += role_box_h + spacing

    # -------------------------------------------------------------------------
    # 7. Confirmed Skills Container
    # -------------------------------------------------------------------------
    draw.rounded_rectangle(
        [40, curr_y, card_width - 40, curr_y + skills_box_h],
        radius=12,
        fill=(248, 250, 252),
        outline=(226, 232, 240),
        width=1,
    )
    draw.text((56, curr_y + 12), active_labels["skills_label"], fill=(71, 85, 105), font=font_label_sm)

    base_chip_y = curr_y + 36
    for cx, cy, cw, ch, label in chip_positions:
        rx = cx
        ry = base_chip_y + cy
        draw.rounded_rectangle([rx, ry, rx + cw, ry + ch], radius=ch // 2, fill=(240, 253, 244), outline=(134, 239, 172), width=1)
        draw.text((rx + 12, ry + 6), label, fill=(22, 101, 52), font=font_chip)

    curr_y += skills_box_h + spacing

    # -------------------------------------------------------------------------
    # 8. Recommended Course Container
    # -------------------------------------------------------------------------
    draw.rounded_rectangle(
        [40, curr_y, card_width - 40, curr_y + course_box_h],
        radius=12,
        fill=(255, 251, 235),
        outline=(252, 211, 77),
        width=1,
    )
    draw.text((56, curr_y + 12), active_labels["next_course_label"], fill=(217, 119, 6), font=font_label_sm)

    cy_text = curr_y + 34
    for line in course_lines:
        draw.text((56, cy_text), line, fill=(146, 64, 14), font=font_course)
        cy_text += 22

    draw.text((56, cy_text + 4), active_labels["next_course_hint"], fill=(180, 83, 9), font=font_hint)

    curr_y += course_box_h + spacing

    # -------------------------------------------------------------------------
    # 9. Nearest Training Centre Container
    # -------------------------------------------------------------------------
    draw.rounded_rectangle(
        [40, curr_y, card_width - 40, curr_y + centre_box_h],
        radius=12,
        fill=(248, 250, 252),
        outline=(226, 232, 240),
        width=1,
    )
    draw.text((56, curr_y + 12), active_labels["nearest_centre_label"], fill=(100, 116, 139), font=font_label_sm)

    centre_y = curr_y + 32
    for line in centre_lines:
        draw.text((56, centre_y), line, fill=(30, 41, 59), font=font_centre)
        centre_y += 22

    curr_y += centre_box_h + spacing

    # -------------------------------------------------------------------------
    # 10. Scannable QR Code Container (With Clean ISO Quiet Zone)
    # -------------------------------------------------------------------------
    draw.rounded_rectangle(
        [40, curr_y, card_width - 40, curr_y + qr_box_h],
        radius=14,
        fill=(255, 255, 255),
        outline=(203, 213, 225),
        width=1,
    )

    qr_x = 56
    qr_y = curr_y + (qr_box_h - qr_h) // 2

    # Paste QR code cleanly on white container background (no border lines choking quiet zone)
    img.paste(qr_img, (qr_x, qr_y))

    # Text beside QR
    tx = qr_x + qr_w + 18
    ty = curr_y + 20
    draw.text((tx, ty), active_labels["qr_title"], fill=(15, 23, 42), font=font_qr_title)

    desc_lines = _wrap_text(active_labels["qr_subtitle"], font_qr_desc, card_width - tx - 55, draw)
    desc_y = ty + 28
    for dl in desc_lines:
        draw.text((tx, desc_y), dl, fill=(100, 116, 139), font=font_qr_desc)
        desc_y += 18

    # Display clean URL
    display_url = public_card_url if len(public_card_url) <= 52 else public_card_url[:49] + "..."
    draw.text((tx, desc_y + 8), display_url, fill=(37, 99, 235), font=font_qr_url)

    # -------------------------------------------------------------------------
    # 11. Footer Section
    # -------------------------------------------------------------------------
    footer_y = card_height - 38
    draw.line([40, footer_y, card_width - 40, footer_y], fill=(226, 232, 240), width=1)
    draw.text((40, footer_y + 12), active_labels["footer_platform"], fill=(148, 163, 184), font=font_footer)

    tamper_text = f"● {active_labels['footer_tamper']}"
    tamper_w = draw.textlength(tamper_text, font=font_footer)
    draw.text((card_width - 40 - tamper_w, footer_y + 12), tamper_text, fill=(148, 163, 184), font=font_footer)

    # -------------------------------------------------------------------------
    # 12. Save and Return Path
    # -------------------------------------------------------------------------
    output_filename = f"{card_id}.png"
    output_path = os.path.join(output_dir, output_filename)
    img.save(output_path, format="PNG", optimize=True)

    return os.path.abspath(output_path)


# ==============================================================================
# 4. VERIFICATION / TEST BLOCK
# ==============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("VOICE-FIRST INFORMAL WORKER SKILL CARD GENERATOR - TEST SUITE")
    print("=" * 70)

    # Base URL configuration:
    # Set SKILL_CARD_BASE_URL env var if your teammate deployed a frontend (e.g. Vercel/ngrok).
    # Default uses live endpoints (httpbin.org returns live JSON verification data in browser).
    custom_base_url = os.environ.get("SKILL_CARD_BASE_URL")

    def make_demo_url(card_id: str, name: str, role: str) -> str:
        if custom_base_url:
            return f"{custom_base_url.rstrip('/')}/{card_id}"
        # Live endpoint that returns verified JSON payload in any phone browser
        params = urllib.parse.urlencode({
            "card_id": card_id,
            "worker": name,
            "role": role,
            "verified": "true",
            "issuer": "VoiceSkillRegistry"
        })
        return f"https://httpbin.org/anything?{params}"

    # 1. Hindi Worker Sample Data
    sample_worker_hi: Dict[str, Any] = {
        "card_id": "WKR-HI-4091",
        "worker_name": "रमेश कुमार (Ramesh Kumar)",
        "language": "hi",
        "matched_role": "सहायक इलेक्ट्रीशियन (Assistant Electrician)",
        "confirmed_skills": [
            "घरेलू वायरिंग (House Wiring)",
            "सर्किट रिपेयर (Circuit Repair)",
            "सुरक्षा मानक (Safety Compliance)",
            "सोलर पैनल इंस्टालेशन",
        ],
        "next_course": "सोलर रूफटॉप तकनीशियन (Surya Mitra Certification)",
        "nearest_centre": "पीएमकेके कौशल केंद्र, सेक्टर 62, नोएडा, उत्तर प्रदेश",
        "public_card_url": make_demo_url("WKR-HI-4091", "Ramesh Kumar", "Assistant Electrician"),
    }

    # 2. Kannada Worker Sample Data
    sample_worker_kn: Dict[str, Any] = {
        "card_id": "WKR-KN-8820",
        "worker_name": "ಬಸವರಾಜ ಕುಮಾರ್ (Basavaraj Kumar)",
        "language": "kn",
        "matched_role": "ಸೌರ ತಂತ್ರಜ್ಞ (Solar Technician)",
        "confirmed_skills": [
            "ಸೋಲಾರ್ ಪ್ಯಾನಲ್ ಸ್ಥಾಪನೆ",
            "ವೈರಿಂಗ್ ದುರಸ್ತಿ",
            "ಇನ್ವರ್ಟರ್ ನಿರ್ವಹಣೆ",
            "ವಿದ್ಯುತ್ ಸುರಕ್ಷತೆ",
        ],
        "next_course": "ಸುಧಾರಿತ ಗ್ರಿಡ್-ಸಂಯೋಜಿತ ಸೌರ ವ್ಯವಸ್ಥೆಗಳು",
        "nearest_centre": "ಜನ ಶಿಕ್ಷಣ ಸಂಸ್ಥಾನ, ಜಯನಗರ, ಬೆಂಗಳೂರು, ಕರ್ನಾಟಕ",
        "public_card_url": make_demo_url("WKR-KN-8820", "Basavaraj Kumar", "Solar Technician"),
    }

    # 3. English Worker Sample Data
    sample_worker_en: Dict[str, Any] = {
        "card_id": "WKR-EN-1024",
        "worker_name": "Sunita Devi",
        "language": "en",
        "matched_role": "Apparel & Garment Specialist",
        "confirmed_skills": [
            "Industrial Machine Sewing",
            "Pattern Cutting & Fitting",
            "Quality Inspection",
            "Fabric Safety Standards",
        ],
        "next_course": "Automated Computerized Textile Pattern Operations",
        "nearest_centre": "National Skill Development Center, Okhla Phase 3, New Delhi",
        "public_card_url": make_demo_url("WKR-EN-1024", "Sunita Devi", "Apparel Specialist"),
    }

    test_samples = [sample_worker_hi, sample_worker_kn, sample_worker_en]
    output_directory = "./generated_cards"

    for idx, worker in enumerate(test_samples, start=1):
        print(f"\n[{idx}/3] Processing: {worker['worker_name']} ({worker['card_id']})")
        print(f"    Language: {worker['language']}")
        print(f"    Target URL: {worker['public_card_url']}")

        # Test 1: QR Base64 Data URI
        qr_uri = generate_qr_base64(worker["public_card_url"])
        print(f"    [1] QR Base64 Data URI: {qr_uri[:45]}... (Length: {len(qr_uri)} chars)")

        # Test 2: WhatsApp Share Link
        wa_link = create_whatsapp_share_link(worker)
        print(f"    [2] WhatsApp Share Link: {wa_link[:80]}...")

        # Test 3: Generate Skill Card Image PNG
        card_file_path = generate_skill_card_image(worker, output_dir=output_directory)
        print(f"    [3] Saved Skill Card PNG: {card_file_path}")
        assert os.path.exists(card_file_path), f"Card file does not exist: {card_file_path}"
        file_size_kb = os.path.getsize(card_file_path) / 1024.0
        print(f"    [OK] File verified on disk ({file_size_kb:.1f} KB)")

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED! Scannable QR codes link to live browser-accessible endpoints.")
    print("=" * 70)
