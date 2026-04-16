# Classification/2_Classification.py
import sys
from pathlib import Path

import pandas as pd
from tqdm import tqdm

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from project_config import (
    SOURCE_DOCS_DIR as SOURCE_ORIGINALS,
    EXTRACTED_TEXTS_DIR as SOURCE_EXTRACTED,
    CLASSIFICATION_RESULTS_DIR as OUTPUT_DIR,
)

from .config_Classification import COLUMNS_ORDER

from .classification_core import staged_classify
from .logging_setup import setup_summary_logger
from .utils.vision_utils import is_vision_flagged, find_original_file
from Classification.semantic.combined_decision import fuse_text_and_vision
from .utils.document_type_mapper import load_document_type_map
from .utils.excel_formatter import format_classification_excel


def run_classification():
    log_dir = OUTPUT_DIR / "logs"
    log_dir.mkdir(exist_ok=True, parents=True)
    logger = setup_summary_logger(log_dir)

    logger.info(f"Starting classification run – looking in {SOURCE_EXTRACTED}")

    txt_files = sorted(SOURCE_EXTRACTED.glob("*.txt"))
    if not txt_files:
        logger.warning("No .txt files found → nothing to classify")
        print("No documents to classify.")
        return

    logger.info(f"Found {len(txt_files)} documents to classify")
    doc_type_map = load_document_type_map()

    results = []

    for txt_path in tqdm(txt_files, desc="Classifying", unit="doc"):
        try:
            logger.info(f"Processing: {txt_path.name}")

            text = txt_path.read_text(encoding="utf-8", errors="replace").strip()

            # === ONLY use the prepended title from ingestion ===
            title = "Untitled Document"
            lines = text.splitlines()
            if lines and lines[0].startswith("[Generated Title] "):
                title = lines[0].replace("[Generated Title] ", "", 1).strip()
                text = "\n".join(lines[1:]).strip()
                logger.info(f"✅ Extracted prepended title → {title}")
            else:
                logger.warning(f"No [Generated Title] found in {txt_path.name}")

            vision_detected = is_vision_flagged(text)
            original_path = find_original_file(txt_path.stem, SOURCE_ORIGINALS)
            image_path = original_path if vision_detected and original_path else None

            fused_text = fuse_text_and_vision(ocr_text=text, image_path=image_path)

            logger.debug(f"  - Fused text | len={len(fused_text):,} | vision_detected={vision_detected}")

            metadata = staged_classify(
                text=fused_text,
                hierarchy_df=None,
                original_path=original_path,
                image_path=image_path
            )

            # Build row — Title from ingestion is authoritative
            row = {
                "filename": txt_path.name,
                "original_path": str(original_path) if original_path else "",
                "text_length": len(text),
                "language_detected": metadata.get("language_detected", ""),
                "Title | Titre": title,   # ← from ingestion
                **metadata
            }

            # <<< CRITICAL LINE — Protects the ingested title >>>
            row["Title | Titre"] = title

            for col in COLUMNS_ORDER:
                row.setdefault(col, "")

            logger.info(
                f"  - Classified | title={row['Title | Titre'][:80]}... | "
                f"function={row.get('Function_EN', 'Unknown')} | "
                f"doc_type={row.get('Document Type / Type de document', 'Unknown')} | "
                f"conf={row.get('overall_confidence', 'N/A')} | "
                f"review={row.get('needs_review', 'N/A')}"
            )

            results.append(row)

        except Exception as e:
            logger.error(f"Failed {txt_path.name}: {type(e).__name__} - {str(e)}", exc_info=True)

    if not results:
        logger.warning("No successful classifications")
        return

    df = pd.DataFrame(results)
    df = df.reindex(columns=COLUMNS_ORDER, fill_value="")

    csv_path = OUTPUT_DIR / "classification_results.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    logger.info(f"CSV saved: {csv_path}")

    excel_path = OUTPUT_DIR / "classification_results.xlsx"
    df.to_excel(excel_path, index=False, engine="openpyxl")
    logger.info(f"Excel created: {excel_path}")

    format_classification_excel(excel_path)

    print(f"\nLog file:     {log_dir / 'classification_summary.log'}")
    print(f"Results CSV:  {csv_path}")
    print(f"Results Excel: {excel_path}")


if __name__ == "__main__":
    run_classification()