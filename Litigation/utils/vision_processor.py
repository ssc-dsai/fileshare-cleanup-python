# Litigation/utils/vision_processor.py
"""
Uses qwen2.5vl:7b to describe images, tables, diagrams extracted from litigation documents.
"""

import logging
from pathlib import Path

from Classification.ollama_client import classify  # reuse existing client

logger = logging.getLogger(__name__)

VISION_PROMPT = """\
You are analyzing a document image from a litigation matter.
Describe ONLY what is visible: layout, tables, charts, signatures, stamps, handwritten notes, key numbers, names, dates.
Be factual and concise. Focus on information that could be relevant to a legal case.
Return only the description, no explanations.
"""

def process_images_in_text(image_paths: list, file_path: Path) -> str:
    """Process extracted images with vision model."""
    if not image_paths:
        return ""

    descriptions = []
    for img_path in image_paths:
        try:
            result = classify(
                question=VISION_PROMPT,
                image_path=str(img_path),
                model="qwen2.5vl:7b",
                temperature=0.1,
                max_tokens=400
            )
            desc = result.get("parsed", {}).get("visual_summary", "No description available")
            descriptions.append(f"Image from {img_path.name}: {desc}")
        except Exception as e:
            logger.warning(f"Vision failed for {img_path.name}: {e}")
            descriptions.append(f"Image from {img_path.name}: [Vision processing failed]")

    return "\n".join(descriptions)