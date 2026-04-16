# Classification/utils_Classification.py
"""
Shared low-level utilities for the classification pipeline.
Focus: text normalization, language detection heuristics, path helpers, JSON repair.
"""

import json
import logging
import re
from pathlib import Path

from json_repair import repair_json

logger = logging.getLogger(__name__)


def normalize_text(text: str, preserve_paragraphs: bool = True) -> str:
    """
    Normalize text while optionally preserving paragraph structure.
    Used in multiple places (ingestion + classification).
    """
    if not text or not text.strip():
        return text.strip()

    if preserve_paragraphs:
        # Keep paragraph breaks, collapse only within lines
        lines = [re.sub(r'\s+', ' ', line.strip()) for line in text.splitlines()]
        cleaned_lines = [line for line in lines if line]
        return '\n'.join(cleaned_lines)
    else:
        # Aggressive single-block normalization
        return re.sub(r'\s+', ' ', text).strip()


def detect_language(text: str) -> str:
    """
    Very lightweight bilingual (EN/FR) language detector tuned for Government of Canada documents.
    Returns: "English / Anglais", "French / Français", "Bil", "und"
    """
    if not text or len(text) < 50:
        return "und"

    sample = text[:3000].lower()

    # Common French function words + accents
    fr_indicators = len(re.findall(
        r'\b(les?|la|le|des?|du|de|et|pour|dans|sur|avec|est|sont|que|qui|ce|cette|ces|être|avoir|faire)\b',
        sample
    )) + len(re.findall(r'[éèêëàâäôöûüç]', sample))

    # Common English function words
    en_indicators = len(re.findall(
        r'\b(the|and|or|to|of|in|for|on|with|is|are|this|that|these|those|be|have|do|will|can)\b',
        sample
    ))

    if fr_indicators + fr_indicators > 8 and en_indicators > 8:
        return "Bil"
    elif fr_indicators + fr_indicators > en_indicators * 1.8:
        return "French / Français"
    elif en_indicators > (fr_indicators + fr_indicators) * 1.8:
        return "English / Anglais"
    else:
        return "Bil" if fr_indicators + en_indicators > 5 else "und"


def parse_llm_json(raw_output: str) -> dict:
    """
    Robust parsing of LLM JSON output.
    Handles markdown fences, extra text, broken JSON → uses json_repair as fallback.
    """
    if not raw_output.strip():
        return {}

    # Step 1: try clean json.loads
    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        pass

    # Step 2: aggressive cleaning
    cleaned = re.sub(r'^.*?\{', '{', raw_output, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r'\}.*?$', '}', cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r'```json\s*|\s*```', '', cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip()

    # Step 3: direct parse again
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Step 4: json_repair fallback
    try:
        repaired = repair_json(cleaned, return_string=False)
        if isinstance(repaired, dict):
            return repaired
    except Exception as e:
        logger.warning(f"JSON repair failed: {e} — raw preview: {raw_output[:180]}...")

    return {}


def get_safe_filename(original: Path | str) -> str:
    """
    Create filesystem-safe filename from original path stem.
    """
    path = Path(original)
    stem = path.stem
    safe = "".join(c for c in stem if c.isprintable() and c not in r'<>:"/\|?*')
    return f"{safe}{path.suffix}"