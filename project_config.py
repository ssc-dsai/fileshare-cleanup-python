# project_config.py
"""
CENTRALIZED PROJECT CONFIGURATION - SINGLE SOURCE OF TRUTH
All scripts now import paths and settings from here.
"""

from pathlib import Path
import os
import sys

# ── USER-CHANGEABLE DATA ROOT ─────────────────────────────────────
# Change here, or set environment variable JAY_DOCS_BASE_DIR
BASE_DIR = Path(os.getenv("JAY_DOCS_BASE_DIR", r"C:/JAY_DOCS")).resolve()

# ── CORE DIRECTORIES ───────────────────────────────────────────────
SOURCE_DOCS_DIR = BASE_DIR / "Synthetic_Docs"  # Single source folder for all documents
EXTRACTED_TEXTS_DIR = BASE_DIR / "extracted_texts"
CLASSIFICATION_RESULTS_DIR = BASE_DIR / "classification_results"
DEDUPS_DIR = BASE_DIR / "Dedups"
INJECTED_METADATA_DIR = BASE_DIR / "Injected_Metadata"
PLACEHOLDERS_DIR = INJECTED_METADATA_DIR / "placeholders"

# ── LITIGATION PIPELINE DIRECTORIES ───────────────────────────────
LITIGATION_PACKAGES_DIR = BASE_DIR / "Litigation_Packages"  # Permanent combined litigation .txt files
LITIGATION_REPORTS_DIR = BASE_DIR / "Litigation_Reports"  # Excel search reports
LITIGATION_SEARCH_ROOT = BASE_DIR / "Synthetic_Docs"  # Default folder to search recursively
LITIGATION_CONFIDENCE_THRESHOLD = 0.65  # Default minimum confidence for semantic search

# ── RESOURCE FILES (shipped with the project) ─────────────────────
PROJECT_ROOT = Path(__file__).parent.resolve()
RESOURCES_DIR = PROJECT_ROOT / "Resources-Sources"

HIERARCHY_CSV = RESOURCES_DIR / "fcp_CSV-UTF.csv"
DOC_TYPE_DICT = RESOURCES_DIR / "Doc_Type_Dictionary.txt"
REGEX_DB_PATH = RESOURCES_DIR / "RegEx-db.csv"
TRIVIAL_SUBJECTS = RESOURCES_DIR / "trivial_subjects.txt"

# ── OLLAMA MODELS ─────────────────────────────────────────────────
TEXT_MODEL = "qwen2.5:7b"
VISION_MODEL = "qwen2.5vl:7b"


def ensure_directories():
    """Create all required folders automatically."""
    dirs = [
        SOURCE_DOCS_DIR,
        EXTRACTED_TEXTS_DIR,
        CLASSIFICATION_RESULTS_DIR,
        DEDUPS_DIR,
        INJECTED_METADATA_DIR,
        PLACEHOLDERS_DIR,
        LITIGATION_PACKAGES_DIR,
        LITIGATION_REPORTS_DIR,
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    print(f"✅ Project directories ready")
    print(f"   • Source documents       : {SOURCE_DOCS_DIR}")
    print(f"   • Extracted texts        : {EXTRACTED_TEXTS_DIR}")
    print(f"   • Classification results : {CLASSIFICATION_RESULTS_DIR}")
    print(f"   • Deduplication          : {DEDUPS_DIR}")
    print(f"   • Injected metadata      : {INJECTED_METADATA_DIR}")
    print(f"   • Litigation Packages    : {LITIGATION_PACKAGES_DIR}")
    print(f"   • Litigation Reports     : {LITIGATION_REPORTS_DIR}")


# Auto-run when imported
ensure_directories()

print(f"🚀 Central config loaded | BASE_DIR = {BASE_DIR}")