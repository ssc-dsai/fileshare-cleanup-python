# Metadata_Injector/5_metadata_injector.py
# Run with: python -m Metadata_Injector.5_metadata_injector

import argparse
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path

# Win32com for native Office metadata injection (Windows only)
try:
    import win32com.client as win32

    WIN32COM_AVAILABLE = True
except ImportError:
    WIN32COM_AVAILABLE = False
    print("WARNING: win32com not installed. Install with: pip install pywin32")

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
import sys

sys.path.insert(0, str(PROJECT_ROOT))

from project_config import (
    BASE_DIR,
    INJECTED_METADATA_DIR as INJECTED_DIR,
    PLACEHOLDERS_DIR
)

LOG_FILE = INJECTED_DIR / f"injector_{datetime.now().strftime('%Y%m%d_%H%M')}.log"

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

logger.info("=== Metadata Injector Started ===")
logger.info(f"Injected folder: {INJECTED_DIR}")
logger.info(f"Placeholders folder: {PLACEHOLDERS_DIR}")
logger.info(f"win32com available: {WIN32COM_AVAILABLE}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--placeholders", default=str(PLACEHOLDERS_DIR),
                        help="Path to placeholders folder")
    args = parser.parse_args()

    placeholders_dir = Path(args.placeholders)
    if not placeholders_dir.exists():
        logger.error(f"Placeholders folder not found: {placeholders_dir}")
        return

    json_files = list(placeholders_dir.glob("*.metadata.json"))
    logger.info(f"Found {len(json_files)} placeholder JSON files")

    if len(json_files) == 0:
        logger.warning("No placeholder JSON files found.")
        return

    success_count = 0
    for json_file in json_files:
        original_name = json_file.stem.replace(".metadata", "")

        # Find original file in Synthetic_Docs
        original_candidates = list((BASE_DIR / "Synthetic_Docs").rglob(original_name))
        if not original_candidates:
            logger.warning(f"Original file not found for placeholder: {json_file.name}")
            continue

        original_path = original_candidates[0]
        relative = original_path.relative_to(BASE_DIR / "Synthetic_Docs")
        target_path = INJECTED_DIR / relative

        target_path.parent.mkdir(parents=True, exist_ok=True)

        if inject_metadata(original_path, json_file, target_path):
            success_count += 1

    logger.info(f"Injection finished | Successfully processed: {success_count} / {len(json_files)}")
    print(f"\n✅ Phase 5 complete! {success_count} documents processed into {INJECTED_DIR}")


def inject_metadata(original_path: Path, sidecar_path: Path, target_path: Path) -> bool:
    """Inject metadata using win32com for Office files + JSON side-car fallback."""
    try:
        # 1. Create exact clone
        shutil.copy2(original_path, target_path)
        logger.info(f"Created exact clone: {target_path.name}")

        # 2. Load side-car metadata
        with open(sidecar_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        suffix = target_path.suffix.lower()
        injected = False

        # Try native injection with win32com for Office files
        if WIN32COM_AVAILABLE and suffix in (".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt"):
            try:
                if suffix in (".docx", ".doc"):
                    app = win32.Dispatch("Word.Application")
                    app.Visible = False
                    doc = app.Documents.Open(str(target_path))

                    # Core properties
                    doc.BuiltInDocumentProperties("Title").Value = metadata.get("Title | Titre", "")
                    doc.BuiltInDocumentProperties("Subject").Value = metadata.get("Document Type / Type de document",
                                                                                  "")
                    doc.BuiltInDocumentProperties(
                        "Keywords").Value = f"Function:{metadata.get('Function_EN', '')} Sensitivity:{metadata.get('Sensitivity', '')}"

                    # Custom properties
                    for key, value in metadata.items():
                        if value and str(value).strip():
                            try:
                                doc.CustomDocumentProperties(key).Value = str(value)
                            except:
                                # If property doesn't exist, add it
                                doc.CustomDocumentProperties.Add(key, False, 4, str(value))  # 4 = text
                    doc.Save()
                    doc.Close()
                    app.Quit()
                    logger.info(f"Injected native metadata into Word document: {target_path.name}")
                    injected = True

                elif suffix in (".xlsx", ".xls"):
                    app = win32.Dispatch("Excel.Application")
                    app.Visible = False
                    wb = app.Workbooks.Open(str(target_path))
                    wb.BuiltinDocumentProperties("Title").Value = metadata.get("Title | Titre", "")
                    wb.BuiltinDocumentProperties("Subject").Value = metadata.get("Document Type / Type de document", "")
                    # Custom properties in Excel are a bit trickier, fallback to side-car for now
                    wb.Save()
                    wb.Close()
                    app.Quit()
                    logger.info(f"Injected basic metadata into Excel: {target_path.name}")
                    injected = True

            except Exception as com_err:
                logger.warning(f"win32com injection failed for {target_path.name}: {com_err}. Using side-car fallback.")

        # Fallback: always create JSON side-car
        if not injected:
            sidecar_copy = target_path.with_suffix(target_path.suffix + ".metadata.json")
            shutil.copy2(sidecar_path, sidecar_copy)
            logger.info(f"Created clone + side-car JSON for {target_path.name}")

        return True

    except Exception as e:
        logger.error(f"Failed to process {original_path.name}: {e}")
        return False


if __name__ == "__main__":
    main()