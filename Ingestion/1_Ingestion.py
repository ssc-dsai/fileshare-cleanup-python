# Ingestion/1_Ingestion.py
# Run with: python -m Ingestion.1_Ingestion

import gc
import os
import sys
from pathlib import Path

# ── Add project root to Python path (fixes relative import issues with python -m) ─────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ── Import from central config (single source of truth) ─────────────────
from project_config import (
    SOURCE_DOCS_DIR as SOURCE_DIR,          # All documents come from here
    EXTRACTED_TEXTS_DIR as OUTPUT_PATH,     # .txt files go here
)

# ── Ingestion-specific settings ─────────────────
LOGS_PATH = OUTPUT_PATH / "logs"
SUPPORTED_EXTENSIONS = {
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".tif", ".tiff",
    ".doc", ".docx", ".ppt", ".pptx", ".txt", ".rtf", ".odt"
}
EXCLUDED_EXTENSIONS = {".tmp", ".bak", ".log", ".DS_Store", ".thumbs.db"}
EXCLUDED_DIRS = {"logs", "extracted_texts", "classification_results", "__pycache__"}
CREATE_PER_DOC_LOGS = False

# Optional title generation (from Classification)
try:
    from Classification.title_generator import generate_title
    TITLE_GENERATION_AVAILABLE = True
    print("✅ Title generation module loaded successfully")
except ImportError as e:
    TITLE_GENERATION_AVAILABLE = False
    print(f"WARNING: Title generation unavailable — skipping title prepending. ({e})")

gc.collect()


def process_directory():
    if not SOURCE_DIR.is_dir():
        print(f"ERROR: SOURCE_DIR not found or inaccessible: {SOURCE_DIR}")
        return

    logger = setup_summary_logger(LOGS_PATH)
    logger.info(f"Ingestion started | SOURCE_DIR: {SOURCE_DIR.resolve()}")

    processed = 0
    errors = 0
    vision_flagged = []

    for root, dirs, files in os.walk(SOURCE_DIR, topdown=True):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        current_root = Path(root)

        for file_name in files:
            full_path = current_root / file_name
            ext = full_path.suffix.lower()

            if ext in EXCLUDED_EXTENSIONS or ext not in SUPPORTED_EXTENSIONS:
                continue

            if OUTPUT_PATH in full_path.parents or LOGS_PATH in full_path.parents:
                continue

            try:
                text = extract_text_from_file(full_path)

                vision_flag = "[VISION_FLAG: Yes]" in text
                image_path = full_path if vision_flag else None

                title = "Untitled Document"
                if TITLE_GENERATION_AVAILABLE:
                    use_image = vision_flag and full_path.suffix.lower() != ".pdf"
                    title_image_path = full_path if use_image else None

                    # Clean filename hint
                    filename_hint = full_path.stem.replace("_", " ").replace("-", " ").strip()
                    if len(filename_hint) < 5:  # avoid generic names like "test"
                        filename_hint = None

                    title = generate_title(
                        text=text,
                        image_path=title_image_path,
                        filename_hint=filename_hint
                    )

                full_text = f"[Generated Title] {title}\n\n" + text
                full_text = normalize_text(full_text, preserve_paragraphs=True)

                txt_path = get_safe_txt_path(OUTPUT_PATH, full_path)
                save_text_to_file(full_text, txt_path)

                text_len = len(full_text)
                logger.info(f"Success | {text_len:,} chars | {txt_path.name} | title={title[:60]}...")

                if vision_flag:
                    logger.info(f"Vision flagged: {full_path.name}")
                    vision_flagged.append(full_path.name)

                processed += 1

            except Exception as e:
                logger.error(f"Error on {full_path.name}: {type(e).__name__} - {str(e)}")
                errors += 1

    logger.info(f"Ingestion complete | Processed: {processed} | Errors: {errors} | Vision-flagged: {len(vision_flagged)}")

    if vision_flagged:
        logger.info("VISION-FLAGGED FILES:")
        for f in vision_flagged:
            logger.info(f"- {f}")

    print("\n" + "=" * 70)
    print(f"Done | Processed: {processed} | Errors: {errors}")
    print(f"Summary log: {LOGS_PATH / 'zz_extraction_summary.log'}")
    print("=" * 70)


# ── Import local modules AFTER path setup ─────────────────
from .logging_setup import setup_summary_logger
from .utils_Ingestion import get_safe_txt_path, save_text_to_file, normalize_text
from .extractors import extract_text_from_file


if __name__ == "__main__":
    process_directory()