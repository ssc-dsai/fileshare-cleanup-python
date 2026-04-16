# Classification/utils/document_type_mapper.py
"""
Single source of truth for file-extension → Document Type mapping.
Now uses the central project_config (no more hard-coded paths).
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Import the correct path from central config
from project_config import DOC_TYPE_DICT

def load_document_type_map() -> dict[str, str]:
    """Load Doc_Type_Dictionary.txt once."""
    doc_type_map: dict[str, str] = {}

    if not DOC_TYPE_DICT.is_file():
        logger.error(f"❌ Document type dictionary not found: {DOC_TYPE_DICT}")
        logger.error("   Expected location: Resources-Sources/Doc_Type_Dictionary.txt")
        return doc_type_map

    try:
        with open(DOC_TYPE_DICT, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    ext_part, label_part = line.split("=", 1)
                    ext = ext_part.strip().lower()
                    label = label_part.strip()
                    if ext.startswith("."):
                        doc_type_map[ext] = label
                    else:
                        logger.debug(f"Skipping invalid extension on line {line_num}: {ext}")
                except ValueError:
                    logger.debug(f"Skipping malformed line {line_num}: {line}")

        logger.info(f"✅ Loaded {len(doc_type_map)} document type mappings from {DOC_TYPE_DICT.name}")
        if len(doc_type_map) == 0:
            logger.warning("Dictionary loaded but is empty!")

    except Exception as e:
        logger.error(f"Failed to load document type dictionary: {e}")

    return doc_type_map


def get_document_type(
    original_path: Path | str | None = None,
    txt_path: Path | str | None = None,
    type_map: dict[str, str] | None = None
) -> str:
    """Return human-readable Document Type based on original file extension."""
    if type_map is None:
        type_map = load_document_type_map()

    file_ext = ""

    # 1. Prefer original document (has the real extension)
    if original_path:
        try:
            path_obj = Path(str(original_path))
            if path_obj.suffix:
                file_ext = path_obj.suffix.lower()
                logger.debug(f"Extracted extension from original: '{file_ext}' → {path_obj.name}")
        except Exception as e:
            logger.debug(f"Failed to extract from original_path: {e}")

    # 2. Fallback to .txt extraction file
    if not file_ext and txt_path:
        try:
            path_obj = Path(str(txt_path))
            if path_obj.suffix:
                file_ext = path_obj.suffix.lower()
        except Exception:
            pass

    if not file_ext:
        logger.warning("No file extension could be extracted → Unknown / Inconnu")
        return "Unknown / Inconnu"

    result = type_map.get(file_ext, "Unknown / Inconnu")

    if result == "Unknown / Inconnu":
        logger.warning(f"No mapping found for extension '{file_ext}' → Unknown / Inconnu")
    else:
        logger.info(f"✅ Mapped '{file_ext}' → {result}")

    return result