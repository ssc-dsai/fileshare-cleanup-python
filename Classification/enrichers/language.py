# Classification/enrichers/language.py
"""
Detects primary language(s) of the document text.
Uses lightweight heuristic tuned for English/French bilingual Government of Canada documents.
"""

from ..utils_Classification import detect_language


def enrich_language(text: str) -> dict:
    """
    Enrich metadata with detected language.

    Returns:
        {"language_detected": "English / Anglais" | "French / Français" | "Bil" | "und"}
    """
    if len(text.strip()) < 50:
        return {"language_detected": "und"}

    lang = detect_language(text)
    return {"language_detected": lang}