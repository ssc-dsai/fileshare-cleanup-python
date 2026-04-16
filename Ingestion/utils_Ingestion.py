# Ingestion/utils_Ingestion.py
"""
Low-level shared utilities for the ingestion pipeline:
- Safe .txt path generation
- Normalized text saving
- Text normalization (preserve paragraphs or flatten)
"""

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)


def get_safe_txt_path(output_dir: Path, original_path: Path) -> Path:
    """
    Generate a safe, unique .txt path in output_dir based on original file.

    Replaces invalid filename characters and ensures no overwrite conflicts.
    Appends numeric suffix if needed (e.g. document_1.txt, document_2.txt).

    Args:
        output_dir: Directory where .txt files are saved
        original_path: Original source file path

    Returns:
        Path to the target .txt file
    """
    stem = "".join(c for c in original_path.stem if c.isprintable() and c not in r'<>:"/\|?*')
    base_name = stem or "unnamed_document"

    txt_path = output_dir / f"{base_name}.txt"
    counter = 1

    while txt_path.exists():
        txt_path = output_dir / f"{base_name}_{counter}.txt"
        counter += 1

    return txt_path


def save_text_to_file(text: str, txt_path: Path) -> None:
    """
    Save extracted text to .txt file with UTF-8 encoding.

    Creates parent directories if missing.
    Logs errors but does not raise.
    """
    txt_path.parent.mkdir(exist_ok=True, parents=True)

    try:
        txt_path.write_text(text, encoding="utf-8")
    except Exception as e:
        logger.error(f"Failed to save text to {txt_path}: {type(e).__name__} - {str(e)}")


def normalize_text(text: str, preserve_paragraphs: bool = True) -> str:
    """
    Normalize whitespace in extracted text.

    Args:
        text: Raw extracted text
        preserve_paragraphs: Keep line breaks between paragraphs (default True)

    Returns:
        Cleaned text string
    """
    if not text.strip():
        return ""

    if preserve_paragraphs:
        # Collapse multiple spaces/tabs within lines, keep paragraph breaks
        lines = [re.sub(r'\s+', ' ', line.strip()) for line in text.splitlines()]
        cleaned_lines = [line for line in lines if line]
        return "\n".join(cleaned_lines)
    else:
        # Single-block aggressive normalization
        return re.sub(r'\s+', ' ', text).strip()