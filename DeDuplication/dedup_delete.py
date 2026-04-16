# dedup_delete.py
# Run with: python -m DeDuplication.dedup_delete --excel "deduplication_review_20260416_1339.xlsx" --dry-run
# Run with: python -m DeDuplication.dedup_delete --excel "deduplication_review_20260416_1339.xlsx"
import argparse
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# Add project root to path for central config
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from project_config import (
    BASE_DIR,
    DEDUPS_DIR,
    SOURCE_DOCS_DIR as SOURCE_DIR,   # for safety check
)

LOG_FILE = DEDUPS_DIR / f"dedup_deletion_{datetime.now().strftime('%Y%m%d_%H%M')}.log"

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

logger.info("=== Metadata Deletion Tool Started ===")
logger.info(f"BASE_DIR: {BASE_DIR}")
logger.info(f"Dedups folder: {DEDUPS_DIR}")


def main():
    parser = argparse.ArgumentParser(description="Safe deletion of deduplicated files")
    parser.add_argument("--excel", required=True, help="Name or full path to the reviewed deduplication Excel")
    parser.add_argument("--dry-run", action="store_true", help="Do not delete, only log and backup")
    args = parser.parse_args()

    # Resolve Excel path
    excel_path = Path(args.excel)
    if not excel_path.is_absolute():
        excel_path = DEDUPS_DIR / excel_path

    if not excel_path.exists():
        logger.error(f"Excel file not found: {excel_path}")
        logger.error(f"Make sure the file is in: {DEDUPS_DIR}")
        return

    logger.info(f"Starting deletion process | Excel: {excel_path} | Dry-run: {args.dry_run}")

    try:
        df = pd.read_excel(excel_path, sheet_name="Duplicate_Clusters")
    except Exception as e:
        logger.error(f"Failed to read Excel file: {e}")
        return

    logger.info(f"Loaded {len(df)} rows from classification Excel")

    # Create backup folder
    backup_dir = DEDUPS_DIR / f"_dedup_backup_{datetime.now().strftime('%Y%m%d_%H%M')}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Backup folder created: {backup_dir}")

    deleted_count = 0
    skipped_count = 0

    for idx, row in df.iterrows():
        filename = row.get("filename", "unknown")
        original_path_str = row.get("original_path", "")
        if not original_path_str:
            logger.warning(f"Row {idx}: No original_path found, skipping")
            skipped_count += 1
            continue

        file_path = Path(original_path_str)

        # Safety: only delete files that are actually inside our SOURCE_DOCS_DIR
        try:
            file_path.relative_to(SOURCE_DIR)
        except ValueError:
            logger.warning(f"Row {idx}: File outside allowed source directory, skipping → {file_path}")
            skipped_count += 1
            continue

        confirmed = str(row.get("User_Confirmed_Delete", "")).strip().lower() == "yes"
        recommended_delete = str(row.get("Recommended_Action", "")).strip() == "Delete"

        # Only delete if user explicitly confirmed OR it's a clear duplicate to delete
        if confirmed or (recommended_delete and not row.get("Is_Master", False)):
            if file_path.exists():
                try:
                    # Always backup first
                    backup_path = backup_dir / file_path.relative_to(BASE_DIR)
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, backup_path)

                    if not args.dry_run:
                        file_path.unlink()
                        logger.info(f"DELETED: {file_path}")
                    else:
                        logger.info(f"DRY-RUN: Would delete {file_path}")
                    deleted_count += 1

                except Exception as e:
                    logger.error(f"Failed to process {file_path}: {type(e).__name__} - {e}")
            else:
                logger.warning(f"File not found (already deleted?): {file_path}")
        else:
            logger.debug(f"Skipped (not marked for deletion): {filename}")

    logger.info(f"Deletion process finished | Files deleted: {deleted_count} | Skipped: {skipped_count} | Backup: {backup_dir}")
    print(f"\n✅ Deletion process complete!")
    print(f"   Deleted: {deleted_count} files")
    print(f"   Backup folder: {backup_dir}")
    print(f"   Log: {LOG_FILE}")


if __name__ == "__main__":
    main()