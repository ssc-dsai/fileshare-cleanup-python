# spaCy PII logic
# Activate your environment first (if not already)
#conda activate FileShare-GPU

# Install the two small models we actually use
#python -m spacy download en_core_web_sm
#python -m spacy download fr_core_news_sm
# Classification/enrichers/pii_detector.py
"""
Classification/enrichers/pii_detector.py

Low-level PII detection using spaCy (en/fr) + targeted regex boosts.
Much stricter than before to avoid false positives.
"""

import logging
import re

import spacy

logger = logging.getLogger(__name__)

# Lazy-load spaCy models
nlp_en = None
nlp_fr = None
try:
    nlp_en = spacy.load("en_core_web_sm")
    nlp_fr = spacy.load("fr_core_news_sm")
except OSError as e:
    logger.warning(f"spaCy models not loaded: {e}. PII detection disabled.")
    logger.warning("Run: python -m spacy download en_core_web_sm   and   fr_core_news_sm")


def detect_pii(text: str) -> bool:
    """
    Detect presence of Personal Information.

    Returns True only for high-confidence signals:
    - PERSON entities with name-like structure
    - Explicit Canadian PII patterns (SIN, credit card, etc.)
    """
    if not text or len(text.strip()) < 30:
        return False

    text_sample = text[:25000]  # safe limit

    for nlp in [nlp_en, nlp_fr]:
        if nlp is None:
            continue

        try:
            doc = nlp(text_sample)

            for ent in doc.ents:
                ent_text = ent.text.strip()

                # Only PERSON with likely full name (first + last or similar)
                if ent.label_ == "PERSON":
                    words = ent_text.split()
                    if len(words) >= 2 and any(w[0].isupper() for w in words):
                        return True

                # Strong regex signals – always count as PII
                if re.search(r'\b\d{3}[- ]?\d{3}[- ]?\d{3}\b', ent_text):          # SIN
                    return True
                if re.search(r'\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b', ent_text):  # Credit card
                    return True
                # Add future patterns here (health card, passport, etc.)

        except Exception as e:
            logger.debug(f"spaCy processing failed: {e}")

    return False