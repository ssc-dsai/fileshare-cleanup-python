# Classification/title_generator.py
"""
Title generation using Ollama qwen2.5 model.
Compatible with current ingestion call signature.
"""

import logging
from pathlib import Path

from project_config import TEXT_MODEL

logger = logging.getLogger(__name__)


def generate_title(text: str, image_path: Path | str | None = None, filename_hint: str | None = None) -> str:
    """
    Generate a clean, meaningful title (maximum 12 words).
    Uses filename_hint as strong fallback when text is short or LLM fails.
    """
    # Strong early fallback for very short or empty text
    if not text or len(text.strip()) < 80:
        if filename_hint:
            base_name = Path(filename_hint).stem.replace("_", " ").replace("-", " ").strip()
            return base_name.title()[:80]  # Title Case
        return "Untitled Document"

    # Use filename_hint for extremely short content as a good default
    if filename_hint and len(text.strip()) < 150:
        base_name = Path(filename_hint).stem.replace("_", " ").replace("-", " ").strip()
        return base_name.title()[:80]

    # Use a reasonable prefix of text for title generation
    short_text = text[:1400] if len(text) > 1400 else text

    prompt = f"""Generate a short, professional, and descriptive title (maximum 12 words) for this document.
Use Title Case (capitalize the first letter of each major word).
Do not use generic words like "Untitled", "Document", "File", or "Page".
Return ONLY the title as plain text — no quotes, no JSON, no explanations.

Text: {short_text}
"""

    try:
        from Classification.ollama_client import classify

        result = classify(
            question=prompt,
            image_path=str(image_path) if image_path else None,
            model=TEXT_MODEL,
            temperature=0.25,
            max_tokens=80,
            force_json_mode=False
        )

        # Robust extraction
        parsed = result.get("parsed", {}) or {}
        raw = result.get("raw", "").strip()

        title_candidates = [
            parsed.get("title"),
            parsed.get("response"),
            raw,
            result.get("response", "")
        ]

        for candidate in title_candidates:
            if candidate and isinstance(candidate, str):
                title = candidate.strip()
                if title and len(title) < 120 and title.lower() not in {"untitled", "document", "file", "page"}:
                    logger.debug(f"Generated title: {title}")
                    return title

        logger.warning(f"Title generation returned empty/invalid result for {filename_hint or 'unknown file'}")

    except Exception as e:
        logger.warning(f"Title generation failed for {filename_hint or 'unknown'}: {type(e).__name__} - {e}")

    # Final fallback — clean filename_hint if available (Title Case)
    if filename_hint:
        clean_title = Path(filename_hint).stem.replace("_", " ").replace("-", " ").strip()
        return clean_title.title()[:80]

    return "Untitled Document"