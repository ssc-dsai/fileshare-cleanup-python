# Classification/enrichers/sensitivity.py
"""
Detects security classification markings (watermarks, headers, footers).
Uses rule-based matching against official Canadian Government labels.
"""

import logging
from pathlib import Path

from .sensitivity_classifier import detect_sensitivity

logger = logging.getLogger(__name__)


def enrich_sensitivity(
    text: str,
    image_path: Path | str | None = None
) -> dict:
    """
    Enrich metadata with detected sensitivity classification.

    Returns:
        {
            "Sensitivity": "Top Secret" | "Confidential" | ... | "Unclassified",
            "Sensibilité": "Très Secret" | "Confidentiel" | ... | "Non classifié"
        }
    """
    try:
        en, fr = detect_sensitivity(text)
        return {
            "Sensitivity": en,
            "Sensibilité": fr
        }
    except Exception as e:
        logger.warning(f"Sensitivity detection failed: {type(e).__name__} - {str(e)}")
        return {
            "Sensitivity": "Unclassified",
            "Sensibilité": "Non classifié"
        }