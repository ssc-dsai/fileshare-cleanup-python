# fileshare-cleanup-python

**Document Classification & Litigation Pipeline** for SSC DSAI

A complete end-to-end Python pipeline for ingesting, deduplicating, classifying, enriching with metadata, and generating litigation-ready reports for government documents (English/French bilingual support).

---

## Repository

- **GitHub**: https://github.com/ssc-dsai/fileshare-cleanup-python
- **Name**: `fileshare-cleanup-python`

---

## Key Features

- **Phase 0**: Intelligent deduplication with semantic similarity + trivial content detection
- **Phase 1**: Robust document ingestion (PDF, DOCX, PPTX, images, etc.) with optional title generation
- **Phase 2**: Advanced classification using embeddings + RegEx + sensitivity + PII detection
- **Phase 3 & 4**: Metadata placeholder creation and native Office metadata injection
- **Phase 5**: Full **Litigation Pipeline** — ingestion of litigation packages + tombstone extraction + professional reporting
- Bilingual (EN/FR) support using Canadian government terminology (`fcp_CSV-UTF.csv`)
- Vision model support for scanned/image-heavy documents
- Centralized configuration via `project_config.py`

---

## Important – Central Configuration

> **`project_config.py` is the single source of truth** for all directory paths and settings.

All scripts import paths from this file.  
**Never hard-code paths** in individual scripts.

**Key directories defined here:**
- `SOURCE_DOCS_DIR` → `C:\JAY_DOCS\Synthetic_Docs`
- `LITIGATION_PACKAGES_DIR` → Input folder for official litigation documents
- `LITIGATION_REPORTS_DIR` → Output folder for summaries and reports
- `CLASSIFICATION_RESULTS_DIR`, `EXTRACTED_TEXTS_DIR`, etc.

To verify directories are ready:
```bash
python -c "from project_config import ensure_directories; print('All folders ready!')"

Requirements & Installation
Two requirements files are provided:

requirements.txt → Clean & curated list recommended for team installation
requirements-generated.txt → Full pip freeze output (useful for vulnerability scanning, auditing, and environment debugging)

Install using the curated file:
Bashpip install -r requirements.txt
After installing spaCy models (run once):
Bashpython -m spacy download en_core_web_sm
python -m spacy download fr_core_news_sm
For security / vulnerability checks, use the generated file:
Bashpip-audit -r requirements-generated.txt

Quick Start – Script Launches
1. Start Ollama (required before any classification)
Bashpython start_ollama.py
2. Full Pipeline (Recommended)
Bashpython run_full_pipeline.py
3. Litigation Pipeline
Step A: Ingest litigation documents
Bashpython -m Litigation.litigation_ingest --input_folder "C:\JAY_DOCS\Litigation_Packages"
Step B: Generate Litigation Reports & Summaries
Bashpython -m Litigation.6_litigation_report_generator
Individual Phase Commands
Bash# Phase 0 - Deduplication
python -m DeDuplication.0_dedup_analysis
python -m DeDuplication.dedup_delete --excel "deduplication_review_....xlsx" --dry-run   # review first
python -m DeDuplication.dedup_delete --excel "deduplication_review_....xlsx"

# Phase 1 - Ingestion
python -m Ingestion.1_Ingestion

# Phase 2 - Classification
python -m Classification.2_Classification

# Phase 4 - Create placeholders
python -m Metadata_Placeholder.4_placeholder_creator --excel "C:\JAY_DOCS\classification_results\classification_results.xlsx"

# Phase 5 - Inject metadata into originals
python -m Metadata_Injector.5_metadata_injector

# Litigation only
python -m Litigation.litigation_ingest --input_folder "C:\JAY_DOCS\Litigation_Packages"
python -m Litigation.6_litigation_report_generator

Project Structure
textfileshare-cleanup-python/
├── project_config.py                 # ← SINGLE SOURCE OF TRUTH (very important)
├── run_full_pipeline.py
├── start_ollama.py
├── .gitignore
├── README.md
├── requirements.txt                  # Clean version for team
├── requirements-generated.txt        # Full pip freeze (for auditing)
│
├── Classification/                   # Phase 2
├── Ingestion/                        # Phase 1
├── DeDuplication/                    # Phase 0
├── Metadata_Placeholder/             # Phase 4
├── Metadata_Injector/                # Phase 5
├── Litigation/                       # Litigation pipeline
│   ├── litigation_ingest.py
│   ├── 6_litigation_report_generator.py
│   └── utils/
├── Resources-Sources/                # fcp_CSV-UTF.csv, RegEx-db.csv, etc.
└── C:\JAY_DOCS\                      # Data folders (not in repo)
    ├── Synthetic_Docs/
    ├── Litigation_Packages/
    └── Litigation_Reports/

Team Usage Notes

Always run python -c "from project_config import ensure_directories" after cloning.
Update paths only in project_config.py (never in individual scripts).
Classification results (classification_results.xlsx) enrich litigation reports with Function, Document Type, Sensitivity, etc.


Technologies

Python 3.11+
Ollama (qwen2.5 + qwen2.5vl)
Sentence-Transformers (bilingual embedding)
PyMuPDF, python-docx, python-pptx, pytesseract
pandas, openpyxl, scikit-learn
win32com (Windows metadata injection)