# FileShare-CleanUp User Guide

**Document Classification & Litigation Pipeline**  
**Installation Path:** `C:\FileShare-Cleanup`  
**For SSC DSAI Team**  
**Last Updated:** April 2026

---

## 1. Initial Setup

### 1.1 Activate Environment
```bash
cd C:\FileShare-Cleanup
conda activate FileShare-GPU

# 1.2 Verify Project Folders
Bashpython -c "from project_config import ensure_directories; print('All folders ready!')"
1.3 Start Ollama (Required for Classification & Litigation)
Bashpython start_ollama.py

Phase 0: DeDuplication
Purpose: Detect duplicate files and trivial (non-business) content before processing.
How to Run
Bash# Step 1: Analyze
python -m DeDuplication.0_dedup_analysis

# Step 2: Review Excel report
# Location: C:\FileShare-Cleanup\Dedups\deduplication_review_YYYYMMDD_HHMM.xlsx

# Step 3: Delete (after review)
python -m DeDuplication.dedup_delete --excel "C:\FileShare-Cleanup\Dedups\deduplication_review_YYYYMMDD_HHMM.xlsx" --dry-run

# Actual deletion (remove --dry-run)
python -m DeDuplication.dedup_delete --excel "C:\FileShare-Cleanup\Dedups\deduplication_review_YYYYMMDD_HHMM.xlsx"
Expected Outcome: Duplicates moved to archive, trivial files flagged.

Phase 1: Ingestion
Purpose: Extract clean text from all document types (PDF, Word, PowerPoint, scanned images via OCR).
How to Run
Bashpython -m Ingestion.1_Ingestion
Expected Outcome:

Text files created in C:\FileShare-Cleanup\extracted_texts\
Each file starts with [VISION_FLAG: Yes/No]


Phase 2: Classification (Core AI Step)
Purpose: Assign official SSC classification using semantic AI + RegEx.
How to Run
Bashpython -m Classification.2_Classification
Expected Outcome:

C:\FileShare-Cleanup\classification_results\classification_results.xlsx
New columns with 500-character matching excerpts:
Function_Match_Excerpt
Sub_Function_Match_Excerpt
BProcess-Match_Excerpt

Static fields always present:
Disposition Authorization / Autorisation de disposition = 2021/005
Technical Environment | Environnement technique = Microsoft's Distributed File System (DFS)



Phase 4: Metadata Placeholder + Injector
Create Placeholders
Bashpython -m Metadata_Placeholder.4_placeholder_creator --excel "C:\FileShare-Cleanup\classification_results\classification_results.xlsx"
Inject Metadata into Original Files
Bashpython -m Metadata_Injector.5_metadata_injector

Phase 5: Litigation Pipeline
Step A: Ingest Litigation Packages
Bashpython -m Litigation.litigation_ingest --input_folder "C:\FileShare-Cleanup\Litigation_Packages"
Step B: Generate Reports
Bashpython -m Litigation.6_litigation_report_generator
Expected Outcome:

Master Excel summary with Plaintiff, Defendant, Timeline
Individual Markdown reports per package


Full Pipeline (One Command)
Bashpython run_full_pipeline.py

The Most Important File: project_config.py
project_config.py is the single source of truth for the entire project.
All paths are defined here.
Never hard-code paths in other scripts.
Key lines to edit if needed:
PythonBASE_DIR = Path(r"C:\FileShare-Cleanup")

SOURCE_DOCS_DIR = BASE_DIR / "Synthetic_Docs"
LITIGATION_PACKAGES_DIR = BASE_DIR / "Litigation_Packages"
LITIGATION_REPORTS_DIR = BASE_DIR / "Litigation_Reports"
Always verify after changes:
Bashpython -c "from project_config import ensure_directories; print('All folders ready!')"