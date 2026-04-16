# Litigation/litigation_ingest.py
# Run with: python -m Litigation.litigation_ingest --input_folder "C:\JAY_DOCS\Litigation_Packages"

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from project_config import (
    LITIGATION_PACKAGES_DIR,  # Where permanent combined .txt files are saved
)

# Local imports (we will create these utils in the next steps)
from .utils.litigation_extractors import extract_from_file
from .utils.tombstone_extractor import extract_tombstone_data
from .utils.vision_processor import process_images_in_text

logger = logging.getLogger(__name__)


def setup_logger():
    log_dir = Path("Litigation/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        handlers=[
            logging.FileHandler(log_dir / f"litigation_ingest_{datetime.now().strftime('%Y%m%d_%H%M')}.log",
                                encoding="utf-8"),
            logging.StreamHandler()
        ]
    )


def main():
    setup_logger()
    parser = argparse.ArgumentParser(description="Litigation Document Ingestion")
    parser.add_argument("--input_folder", required=True, help="Path to folder containing litigation documents")
    parser.add_argument("--output_name", default=None, help="Optional custom name for the output package")
    args = parser.parse_args()

    input_folder = Path(args.input_folder)
    if not input_folder.is_dir():
        logger.error(f"Input folder not found: {input_folder}")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    package_name = args.output_name or f"Litigation_Package_{timestamp}"
    output_txt = LITIGATION_PACKAGES_DIR / f"{package_name}.txt"

    logger.info(f"Starting litigation ingestion from: {input_folder}")
    logger.info(f"Output package will be saved as: {output_txt}")

    all_text = []
    tombstone_data = {}

    # Supported file types for litigation ingestion
    supported_ext = {".pdf", ".docx", ".doc", ".ppt", ".pptx", ".txt"}
    files = [f for f in input_folder.rglob("*.*") if f.suffix.lower() in supported_ext]

    logger.info(f"Found {len(files)} documents to process")

    for file_path in files:
        logger.info(f"Processing: {file_path.name}")
        try:
            text, images = extract_from_file(file_path)

            # Extract structured tombstone / key facts first
            doc_tombstone = extract_tombstone_data(text, file_path)
            tombstone_data.update(doc_tombstone)  # merge (later documents can override)

            # Process any images with vision model
            if images:
                vision_desc = process_images_in_text(images, file_path)
                text += "\n\n[VISUAL CONTENT]\n" + vision_desc

            all_text.append(f"\n\n=== DOCUMENT: {file_path.name} ===\n{text}")

        except Exception as e:
            logger.error(f"Failed to process {file_path.name}: {e}")

    # Build final package with tombstone at the top
    final_content = f"""LITIGATION PACKAGE - {timestamp}
Source Folder: {input_folder}
Generated: {datetime.now()}

=== TOMBSTONE / KEY FACTS ===
"""
    for key, value in tombstone_data.items():
        final_content += f"{key}: {value}\n"

    final_content += "\n=== FULL EXTRACTED CONTENT ===\n"
    final_content += "\n".join(all_text)

    # Save permanent package
    output_txt.write_text(final_content, encoding="utf-8")
    logger.info(f"✅ Litigation package saved: {output_txt}")

    print(f"\n🎉 Litigation ingestion complete!")
    print(f"   Package saved to: {output_txt}")
    print(f"   Documents processed: {len(files)}")


if __name__ == "__main__":
    main()