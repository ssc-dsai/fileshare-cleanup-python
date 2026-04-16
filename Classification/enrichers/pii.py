# Classification/enrichers/pii.py
"""
Detects presence of Personal Information (PII) / Renseignements personnels.
Uses spaCy entity recognition + lightweight regex boosts for Canadian context.
"""

import logging

from .pii_detector import detect_pii

logger = logging.getLogger(__name__)


def enrich_pii(text: str) -> dict:
    """
    Enrich metadata with PII detection result.

    Returns:
        {
            "personal_information": "Yes" | "No"
        }
    """
    try:
        has_pii = detect_pii(text)
        return {
            "personal_information": "Yes" if has_pii else "No"
        }
    except Exception as e:
        logger.warning(f"PII detection failed: {type(e).__name__} - {str(e)}")
        return {"personal_information": "No"}