# Classification/combined_decision.py
"""
Combines OCR-extracted text with visual understanding from images (if flagged).
Produces a single normalized text string for downstream classification.
"""

from pathlib import Path
import logging

from project_config import VISION_MODEL
from Classification.ollama_client import classify
from Classification.utils_Classification import normalize_text

logger = logging.getLogger(__name__)

# Separator used between OCR text and visual summary
VISUAL_SEPARATOR = "\n\n" + "─" * 50 + "\n[VISUAL LAYOUT & CONTENT SUMMARY]\n"


VISION_PROMPT = """\
You are an expert analyst of Canadian federal/provincial government, administrative, financial, legal and business documents (English and French bilingual possible).

Carefully examine this document image. Focus ONLY on what is **visually readable**:

- Document type: invoice, receipt, letter, memo, form, contract, report, table, chart, ID, application, statement…
- Layout: portrait/landscape, columns, sections, headers/footers, logos, seals, stamps, signatures
- Key visible elements: title/heading, field labels (Name/Nom, Date, Amount, SIN/NAS, File No, Account #…), dates, numbers, monetary values, tables, checkboxes
- Language(s): English, French, bilingual
- Official indicators: department name, crown logo, watermark, redaction marks

Produce a concise factual summary (200–400 words max) describing ONLY what is visible — no hallucination.
Be precise with numbers, dates, identifiers when readable.
Write in clear English (note if French-dominant).

Return **ONLY** valid JSON:
{"visual_summary": "Your description here"}
""".strip()


def get_visual_description(image_path: Path | str) -> str:
    """
    Get visual layout/content summary using vision model.
    Returns description string or error placeholder.
    """
    image_path = Path(image_path)
    if not image_path.is_file():
        logger.warning(f"Image not found: {image_path}")
        return "[VISION: Image file missing]"

    try:
        result = classify(
            question=VISION_PROMPT,
            image_path=str(image_path.resolve()),
            temperature=0.1,
            max_tokens=600,
            model=VISION_MODEL
        )

        parsed = result.get("parsed", {})
        if "visual_summary" in parsed and isinstance(parsed["visual_summary"], str):
            desc = normalize_text(parsed["visual_summary"], preserve_paragraphs=False).strip()
            logger.debug(f"Visual description generated | length={len(desc)} chars")
            return desc

        logger.warning(f"Invalid vision response format | raw: {result.get('raw', '')[:200]}…")
        return "[VISION: Invalid model response]"

    except Exception as e:
        logger.exception(f"Vision processing failed for {image_path.name}")
        return f"[VISION ERROR: {type(e).__name__} – {str(e)}]"


def fuse_text_and_vision(
    ocr_text: str,
    image_path: Path | str | None = None,
    separator: str = VISUAL_SEPARATOR
) -> str:
    """
    Combine OCR text with visual summary (if image available).
    Returns single normalized string ready for classification.
    """
    ocr_clean = normalize_text(ocr_text, preserve_paragraphs=True).strip()

    if not image_path:
        return ocr_clean

    visual_summary = get_visual_description(image_path)

    if visual_summary.startswith("[VISION"):
        # Degraded mode: append error note
        combined = ocr_clean + "\n\n" + visual_summary
    else:
        combined = ocr_clean + separator + visual_summary

    final_text = normalize_text(combined, preserve_paragraphs=True)

    logger.info(
        f"Fused text | ocr_len={len(ocr_clean)} | visual_len={len(visual_summary)} | "
        f"final_len={len(final_text)} | has_vision={bool(image_path)}"
    )

    return final_text