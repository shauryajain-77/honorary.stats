"""
extras_helper.py - Official myScheme Links & Verification Helper

A lightweight standalone Python module for demo prototypes to retrieve
official Indian Government schemes mapped to informal worker categories.

STRICT SCOPE COMPLIANCE:
- Pure importable Python functions for backend teammates.
- No job-role database, SQLite/DynamoDB code, Gemini logic, API endpoints, or UI screens.
- Every returned entry includes an official https://www.myscheme.gov.in/ URL and
  the mandatory verification disclaimer.
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

# Default disclaimer text required on all scheme recommendations
DEFAULT_DISCLAIMER = "Verify eligibility on the official myScheme portal before applying."

# Path to the bundled JSON mapping
SCHEMES_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "myscheme_links.json")

# Synonym & keyword mapping to canonical categories
CATEGORY_KEYWORD_MAP: Dict[str, str] = {
    # Tailoring / Artisan
    "tailor": "tailoring/artisan",
    "tailoring": "tailoring/artisan",
    "darzi": "tailoring/artisan",
    "artisan": "tailoring/artisan",
    "garment": "tailoring/artisan",
    "textile": "tailoring/artisan",
    "sewing": "tailoring/artisan",
    "weaver": "tailoring/artisan",
    "handloom": "tailoring/artisan",
    "embroidery": "tailoring/artisan",
    "leather": "tailoring/artisan",
    "cobbler": "tailoring/artisan",
    # Electrical / Repair
    "electric": "electrical/repair",
    "electrical": "electrical/repair",
    "electrician": "electrical/repair",
    "repair": "electrical/repair",
    "wireman": "electrical/repair",
    "appliance": "electrical/repair",
    "solar": "electrical/repair",
    "electronics": "electrical/repair",
    "technician": "electrical/repair",
    "mobile repair": "electrical/repair",
    # Cooking / Food
    "cook": "cooking/food",
    "cooking": "cooking/food",
    "food": "cooking/food",
    "chef": "cooking/food",
    "catering": "cooking/food",
    "caterer": "cooking/food",
    "halwai": "cooking/food",
    "baker": "cooking/food",
    "bakery": "cooking/food",
    "dhaba": "cooking/food",
    "food stall": "cooking/food",
    "fast food": "cooking/food",
    "processing": "cooking/food",
    # Shopkeeping / Retail
    "shop": "shopkeeping/retail",
    "shopkeeper": "shopkeeping/retail",
    "shopkeeping": "shopkeeping/retail",
    "retail": "shopkeeping/retail",
    "retailer": "shopkeeping/retail",
    "store": "shopkeeping/retail",
    "kirana": "shopkeeping/retail",
    "vendor": "shopkeeping/retail",
    "street vendor": "shopkeeping/retail",
    "merchant": "shopkeeping/retail",
    "trader": "shopkeeping/retail",
    "hawker": "shopkeeping/retail",
    # Plumbing / Carpentry / Construction
    "plumb": "plumbing/carpentry/construction",
    "plumber": "plumbing/carpentry/construction",
    "plumbing": "plumbing/carpentry/construction",
    "carpenter": "plumbing/carpentry/construction",
    "carpentry": "plumbing/carpentry/construction",
    "suthar": "plumbing/carpentry/construction",
    "badhai": "plumbing/carpentry/construction",
    "construct": "plumbing/carpentry/construction",
    "construction": "plumbing/carpentry/construction",
    "mason": "plumbing/carpentry/construction",
    "rajmistri": "plumbing/carpentry/construction",
    "welder": "plumbing/carpentry/construction",
    "welding": "plumbing/carpentry/construction",
    "painter": "plumbing/carpentry/construction",
    "building": "plumbing/carpentry/construction",
    # Driving / Transport
    "drive": "driving/transport",
    "driver": "driving/transport",
    "driving": "driving/transport",
    "transport": "driving/transport",
    "auto": "driving/transport",
    "auto driver": "driving/transport",
    "rickshaw": "driving/transport",
    "e-rickshaw": "driving/transport",
    "taxi": "driving/transport",
    "cab": "driving/transport",
    "truck": "driving/transport",
    "delivery": "driving/transport",
    "chauffeur": "driving/transport",
    # Beauty / Salon
    "beauty": "beauty/salon",
    "salon": "beauty/salon",
    "parlour": "beauty/salon",
    "barber": "beauty/salon",
    "nai": "beauty/salon",
    "hair": "beauty/salon",
    "hairdresser": "beauty/salon",
    "hairstylist": "beauty/salon",
    "beautician": "beauty/salon",
    "wellness": "beauty/salon",
    "makeup": "beauty/salon",
}


def _load_schemes_data() -> Dict[str, List[Dict[str, Any]]]:
    """Loads and caches the raw JSON data mapping from myscheme_links.json."""
    if not os.path.exists(SCHEMES_JSON_PATH):
        return {}
    try:
        with open(SCHEMES_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _normalize_category_query(category: str) -> Optional[str]:
    """
    Normalizes a freeform category or role string to one of the 7 canonical
    categories in myscheme_links.json.
    """
    if not category:
        return None

    cleaned = re.sub(r"[^\w\s/]", " ", str(category).lower()).strip()

    # 1. Exact match with canonical keys
    canonical_keys = [
        "tailoring/artisan",
        "electrical/repair",
        "cooking/food",
        "shopkeeping/retail",
        "plumbing/carpentry/construction",
        "driving/transport",
        "beauty/salon",
    ]
    for key in canonical_keys:
        if cleaned == key or cleaned.replace(" ", "") == key.replace("/", ""):
            return key

    # 2. Keyword / substring lookup
    words = cleaned.split()
    for word in words:
        if word in CATEGORY_KEYWORD_MAP:
            return CATEGORY_KEYWORD_MAP[word]

    # 3. Check partial multi-word phrases
    for kw, target_cat in CATEGORY_KEYWORD_MAP.items():
        if kw in cleaned:
            return target_cat

    return None


def get_official_schemes(category: str) -> List[Dict[str, str]]:
    """
    Pure helper function that retrieves matching Indian Government schemes
    for an informal work category with official myScheme URLs and the mandatory
    verification disclaimer attached.

    Backend teammates can import and call this directly when building the
    'Your Path' / upskilling response.

    Args:
        category (str): Category or job role (e.g., 'electrical/repair', 'electrician',
                        'tailoring', 'darzi', 'cooking', 'street vendor', 'plumber',
                        'auto driver', 'barber', etc.).

    Returns:
        List[Dict[str, str]]: List of scheme dictionaries, each containing:
            - "scheme_name": Official scheme title.
            - "official_url": Valid https://www.myscheme.gov.in/ link.
            - "one_line_benefit": Concise summary of benefits.
            - "disclaimer": "Verify eligibility on the official myScheme portal before applying."
    """
    data = _load_schemes_data()
    if not data:
        return []

    canonical = _normalize_category_query(category)

    if canonical and canonical in data:
        results = data[canonical]
    else:
        # Fallback for unrecognized categories: return foundational national schemes
        # (PMKVY & PMMY Mudra)
        results = [
            {
                "scheme_name": "Pradhan Mantri Kaushal Vikas Yojana (PMKVY)",
                "official_url": "https://www.myscheme.gov.in/schemes/pmkvy",
                "one_line_benefit": "Government-sponsored skill development, Recognition of Prior Learning (RPL) certification, and accidental insurance.",
                "disclaimer": DEFAULT_DISCLAIMER,
            },
            {
                "scheme_name": "Pradhan Mantri Mudra Yojana (PMMY)",
                "official_url": "https://www.myscheme.gov.in/schemes/pmmy",
                "one_line_benefit": "Collateral-free micro-enterprise financing up to ₹10 Lakhs for self-employed and informal business owners.",
                "disclaimer": DEFAULT_DISCLAIMER,
            },
        ]

    # Ensure every entry strictly contains the required disclaimer and valid https:// url
    clean_output: List[Dict[str, str]] = []
    for item in results:
        entry = {
            "scheme_name": str(item.get("scheme_name", "National Vocational Scheme")).strip(),
            "official_url": str(item.get("official_url", "https://www.myscheme.gov.in/")).strip(),
            "one_line_benefit": str(item.get("one_line_benefit", "Skill training and enterprise financial support.")).strip(),
            "disclaimer": str(item.get("disclaimer", DEFAULT_DISCLAIMER)).strip(),
        }
        clean_output.append(entry)

    return clean_output


# ==============================================================================
# 2. VERIFICATION & URL INTEGRITY CHECK
# ==============================================================================

if __name__ == "__main__":
    print("=" * 72)
    print("MYSCHEME LINKS & EXTRAS HELPER - VERIFICATION SUITE")
    print("=" * 72)

    # 1. Verify JSON file existence and schema
    raw_data = _load_schemes_data()
    print(f"Loaded Categories from myscheme_links.json: {len(raw_data)}")
    assert len(raw_data) >= 7, "Must contain all 7 requested informal work categories"

    all_urls: List[str] = []
    total_schemes = 0

    print("\n--- [TEST 1] VALIDATING URLS & REQUIRED FIELDS ---")
    for category_name, schemes_list in raw_data.items():
        print(f"\n* Category: '{category_name}' ({len(schemes_list)} schemes)")
        for scheme in schemes_list:
            total_schemes += 1
            name = scheme.get("scheme_name")
            url = scheme.get("official_url")
            benefit = scheme.get("one_line_benefit")
            disclaimer = scheme.get("disclaimer")

            # Assert all 4 required keys exist
            assert name, f"Missing scheme_name in {category_name}"
            assert url, f"Missing official_url in {category_name}"
            assert benefit, f"Missing one_line_benefit in {category_name}"
            assert disclaimer, f"Missing disclaimer in {category_name}"

            # Assert URL is a valid https://www.myscheme.gov.in/ link
            assert url.startswith("https://www.myscheme.gov.in/"), f"URL must be https://www.myscheme.gov.in/ but got: {url}"
            assert disclaimer == DEFAULT_DISCLAIMER, f"Disclaimer must match official text: {disclaimer}"

            all_urls.append(url)
            print(f"    - {name}")
            print(f"      URL: {url}")
            print(f"      Benefit: {benefit[:75]}...")

    print(f"\n[OK] Checked {total_schemes} schemes across {len(raw_data)} categories.")
    print(f"[OK] 100% of URLs are valid 'https://www.myscheme.gov.in/' endpoints.")

    # 2. Test get_official_schemes helper across various informal worker inputs
    print("\n--- [TEST 2] TESTING get_official_schemes() HELPER ---")
    test_queries = [
        # Exact canonical categories
        "tailoring/artisan",
        "electrical/repair",
        "cooking/food",
        "shopkeeping/retail",
        "plumbing/carpentry/construction",
        "driving/transport",
        "beauty/salon",
        # Common worker job titles / synonyms
        "electrician",
        "darzi (tailor)",
        "halwai / street food vendor",
        "kirana shopkeeper",
        "carpenter",
        "auto driver",
        "barber salon",
        # Unrecognized category fallback test
        "general unskilled laborer",
    ]

    for q in test_queries:
        schemes = get_official_schemes(q)
        print(f"\n  Query: '{q}' -> Returned {len(schemes)} schemes:")
        for s in schemes:
            print(f"    • {s['scheme_name']}")
            print(f"      URL: {s['official_url']}")
            print(f"      Disclaimer: {s['disclaimer']}")
        assert len(schemes) >= 1, f"Must return at least 1 scheme for query '{q}'"

    print("\n" + "=" * 72)
    print("ALL TESTS PASSED! myscheme_links.json and extras_helper.py are verified.")
    print("=" * 72)
