# Classification/enrichers/title.py
"""
Title enrichment using Ollama qwen2.5 model.
Falls back gracefully if title generation is unavailable.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Import from central config
from project_config import TEXT_MODEL

try:
    from Classification.title_generator import generate_title
except ImportError as e:
    logger.warning(f"Title generation unavailable — skipping title prepending. ({e})")
    generate_title = None


def enrich_title(text: str, image_path: Path | str | None = None) -> dict:
    """
    Enrich document with a generated title.
    Returns a dict with 'Title | Titre' key.
    """
    metadata = {"Title | Titre": "Untitled Document"}

    if not generate_title:
        return metadata

    try:
        title = generate_title(
            text=text,
            image_path=image_path,
            model=TEXT_MODEL
        )
        if title and title.strip():
            metadata["Title | Titre"] = title.strip()
            logger.debug(f"Generated title: {title[:80]}...")
        else:
            logger.debug("Title generation returned empty result, using default")
    except Exception as e:
        logger.warning(f"Title generation failed: {e}. Using default title.")

    return metadata