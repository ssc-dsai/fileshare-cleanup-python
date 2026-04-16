# Classification/vision_utils.py
"""
Simple utilities for vision-related decisions in the classification pipeline:
- Check if vision processing is flagged in extracted text
- Find original source file from .txt stem in originals directory
"""

from pathlib import Path


VISION_FLAG_MARKER = "[VISION_FLAG: Yes]"


def is_vision_flagged(text: str) -> bool:
    """
    Check if the extracted text contains the vision processing flag.
    Indicates that the document has image content needing vision model analysis.
    """
    return VISION_FLAG_MARKER in text


def find_original_file(txt_stem: str, originals_dir: Path) -> Path | None:
    """
    Locate the original source file that produced the given .txt extraction.

    Tries common document extensions in the originals directory.

    Args:
        txt_stem: File stem of the .txt file (without extension)
        originals_dir: Directory containing original source documents

    Returns:
        Path to matching original file, or None if not found
    """
    extensions = [
        ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".tif", ".tiff",
        ".doc", ".docx", ".ppt", ".pptx", ".txt", ".rtf", ".odt"
    ]

    for ext in extensions:
        candidate = originals_dir / f"{txt_stem}{ext}"
        if candidate.is_file():
            return candidate

    return None