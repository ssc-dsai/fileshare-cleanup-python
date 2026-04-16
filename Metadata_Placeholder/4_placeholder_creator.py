# Metadata_Placeholder/4_placeholder_creator.py
# Run with: python -m Metadata_Placeholder.4_placeholder_creator --excel "classification_results.xlsx"

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(PROJECT_ROOT))

from project_config import (
    BASE_DIR,
    PLACEHOLDERS_DIR,
    CLASSIFICATION_RESULTS_DIR
)

LOG_FILE = BASE_DIR / "Injected_Metadata" / f"placeholder_creator_{datetime.now().strftime('%Y%m%d_%H%M')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

logger.info("=== Metadata Placeholder Creator Started ===")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--excel", default="classification_results.xlsx",
                        help="Name of the classification Excel (default: classification_results.xlsx)")
    args = parser.parse_args()

    excel_path = CLASSIFICATION_RESULTS_DIR / args.excel
    if not excel_path.exists():
        logger.error(f"Excel file not found: {excel_path}")
        return

    logger.info(f"Reading classification results: {excel_path}")

    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        logger.error(f"Failed to read Excel: {e}")
        return

    logger.info(f"Found {len(df)} documents in classification_results.xlsx")

    created_count = 0
    for _, row in df.iterrows():
        original_path = Path(row.get("original_path", ""))
        if not original_path.exists():
            logger.warning(f"Original file not found, skipping: {original_path}")
            continue

        # Build side-car filename
        sidecar_name = original_path.name + ".metadata.json"
        sidecar_path = PLACEHOLDERS_DIR / sidecar_name

        # Extract all metadata using the new column names
        metadata = {
            "text_length": int(row.get("text_length", 0)),
            "language_detected": str(row.get("language_detected", "")),
            "Title | Titre": str(row.get("Title | Titre", "")),
            "Document Type / Type de document": str(row.get("Document Type / Type de document", "")),
            "Sensitivity": str(row.get("Sensitivity", "")),
            "Sensibilité": str(row.get("Sensibilité", "")),
            "IMCC File No": str(row.get("IMCC File No", "")),
            "Function_EN": str(row.get("Function_EN", "")),
            "Function_FR": str(row.get("Function_FR", "")),
            "Function_Desc_Sum_EN": str(row.get("Function_Desc_Sum_EN", "")),
            "File Class No - Level1": str(row.get("File Class No - Level1", "")),
            "Sub-Function_EN": str(row.get("Sub-Function_EN", "")),
            "Sub-Function_FR": str(row.get("Sub-Function_FR", "")),
            "Sub-Function_Desc_Summ_EN": str(row.get("Sub-Function_Desc_Summ_EN", "")),
            "File Class No - Level2": str(row.get("File Class No - Level2", "")),
            "Business_Process_EN": str(row.get("Business_Process_EN", "")),
            "File Class No - Level3": str(row.get("File Class No - Level3", "")),
            "Retention Period": str(row.get("Retention Period", "")),
            "Retention Trigger": str(row.get("Retention Trigger", "")),
            "Full_File_Class_No": str(row.get("Full_File_Class_No", "")),
            "Disposition Authorization / Autorisation de disposition": str(row.get("Disposition Authorization / Autorisation de disposition", "")),
            "Technical Environment | Environnement technique": str(row.get("Technical Environment | Environnement technique", "")),
            "Litigation_hold": str(row.get("Litigation_hold", "")),
            "Archival_value": str(row.get("Archival_value", "")),
            "critical_business_content": str(row.get("critical_business_content", "")),
            "personal_information": str(row.get("personal_information", "")),
            "needs_review": str(row.get("needs_review", "")),
            "overall_confidence": float(row.get("overall_confidence", 0.0)),
            "confidence_category": str(row.get("confidence_category", "")),
            "original_filename": original_path.name,
            "original_path": str(original_path),
            "timestamp_created": datetime.now().isoformat()
        }

        try:
            with open(sidecar_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            logger.info(f"Created placeholder: {sidecar_path.name}")
            created_count += 1
        except Exception as e:
            logger.error(f"Failed to create placeholder for {original_path.name}: {e}")

    logger.info(f"Placeholder creation finished | Side-car JSON files created: {created_count}")
    logger.info(f"All placeholders saved in: {PLACEHOLDERS_DIR}")
    print(f"\n✅ Phase 4 complete! {created_count} placeholder JSON files created in {PLACEHOLDERS_DIR}")

if __name__ == "__main__":
    main()