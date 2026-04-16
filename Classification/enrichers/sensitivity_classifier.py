# Classification/utils/sensitivity_classifier.py
"""
Rule-based detection of Canadian Government security classification markings.
Looks for headers, footers, watermarks, or prominent labels in text.
"""

import logging
import re

logger = logging.getLogger(__name__)

# Controlled vocabulary – ordered from most to least sensitive
CLASSIFICATIONS_EN = [
    "Top Secret",
    "Secret",
    "Confidential",
    "Protected C",
    "Protected B",
    "Protected A",
    "Unclassified",
]

CLASSIFICATIONS_FR = [
    "Très Secret",
    "Secret",
    "Confidentiel",
    "Protégé C",
    "Protégé B",
    "Protégé A",
    "Non classifié",
]

# English → French mapping for consistency
CLASSIF_MAP = dict(zip(CLASSIFICATIONS_EN, CLASSIFICATIONS_FR))

# All possible markers (lowercased for matching)
MARKERS = (
    [e.lower() for e in CLASSIFICATIONS_EN] +
    [f.lower() for f in CLASSIFICATIONS_FR] +
    ["top secret", "très secret", "protected a", "protégé a", "unclassified", "non classifié"]
)


def detect_sensitivity(text: str) -> tuple[str, str]:
    """
    Detect security classification label in document text.

    Args:
        text: Extracted document text (OCR or full content)

    Returns:
        (english_label, french_label)
        Defaults to ("Unclassified", "Non classifié")
    """
    if not text.strip():
        return "Unclassified", "Non classifié"

    # Focus on first ~4000 chars (headers/footers/watermarks usually early)
    head = text.lower()[:4000]

    for candidate in CLASSIFICATIONS_EN + CLASSIFICATIONS_FR:
        cand_lower = candidate.lower()

        # Strong match: whole word with boundaries
        if re.search(r'\b' + re.escape(cand_lower) + r'\b', head):
            if candidate in CLASSIFICATIONS_EN:
                return candidate, CLASSIF_MAP[candidate]
            else:
                # French match → map back to English
                en = next(k for k, v in CLASSIF_MAP.items() if v.lower() == cand_lower)
                return en, candidate

        # Relaxed substring match (for partial or formatted cases)
        if len(cand_lower) > 8 and cand_lower in head:
            if candidate in CLASSIFICATIONS_EN:
                return candidate, CLASSIF_MAP[candidate]
            else:
                en = next(k for k, v in CLASSIF_MAP.items() if v.lower() == cand_lower)
                return en, candidate

    # Default if no match
    return "Unclassified", "Non classifié"