# Litigation/6_litigation_report_generator.py
# Run with: python -m Litigation.6_litigation_report_generator

import argparse
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime
import numpy as np

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(PROJECT_ROOT))

from project_config import (
    LITIGATION_PACKAGES_DIR,
    LITIGATION_REPORTS_DIR,
    CLASSIFICATION_RESULTS_DIR,
    TEXT_MODEL,
)

from Classification.ollama_client import classify

# Reuse the same embedder that Classification uses
try:
    from sentence_transformers import SentenceTransformer
    embedder = SentenceTransformer('Lajavaness/bilingual-embedding-small', trust_remote_code=True)
except Exception:
    embedder = None

logger = logging.getLogger(__name__)

def setup_logger():
    log_dir = LITIGATION_REPORTS_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        handlers=[
            logging.FileHandler(log_dir / f"litigation_report_{datetime.now():%Y%m%d_%H%M}.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

def load_classification_metadata():
    excel_path = CLASSIFICATION_RESULTS_DIR / "classification_results.xlsx"
    if not excel_path.exists():
        logger.warning("classification_results.xlsx not found")
        return pd.DataFrame(columns=["filename"])
    df = pd.read_excel(excel_path)
    if "filename" not in df.columns:
        logger.warning("No 'filename' column found")
        return pd.DataFrame(columns=["filename"])
    df = df.set_index("filename").fillna("")
    logger.info(f"Loaded classification metadata for {len(df)} documents")
    return df

def generate_summary_and_dates(package_text: str, package_name: str) -> dict:
    prompt = f"""You are a senior litigation paralegal. Return ONLY valid JSON.

{{
  "executive_summary": "One-paragraph professional summary (max 150 words)",
  "key_dates": ["2025-03-15: Incident date", "2025-04-01: Statement of claim filed", ...],
  "plaintiff": "Name of plaintiff or 'Not Found'",
  "defendant": "Name of defendant or 'Not Found'",
  "case_number": "Case/file number or 'Not Found'"
}}

Package: {package_name}
Text (first 13,000 chars):
{package_text[:13000]}
"""
    try:
        result = classify(
            question=prompt,
            model=TEXT_MODEL,
            temperature=0.1,
            max_tokens=900,
            force_json_mode=True
        )
        parsed = result.get("parsed", {})
        return parsed if isinstance(parsed, dict) else {}
    except Exception as e:
        logger.error(f"LLM failed for {package_name}: {e}")
        return {"executive_summary": "Summary unavailable", "key_dates": [], "plaintiff": "Not Found", "defendant": "Not Found", "case_number": "Not Found"}

def main():
    setup_logger()
    parser = argparse.ArgumentParser(description="Litigation Summary & Report Generator")
    parser.add_argument("--package", default=None, help="Process only one specific package (partial name match)")
    args = parser.parse_args()

    LITIGATION_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    meta_df = load_classification_metadata()

    packages = sorted(LITIGATION_PACKAGES_DIR.glob("*.txt"))
    if args.package:
        packages = [p for p in packages if args.package.lower() in p.name.lower()]

    logger.info(f"Found {len(packages)} litigation packages")
    if not packages:
        print("No packages found in Litigation_Packages/")
        return

    master_rows = []
    run_date = datetime.now().strftime("%Y-%m-%d")   # ← Clean date only for Excel & reports

    for pkg_path in packages:
        logger.info(f"Processing: {pkg_path.name}")
        full_text = pkg_path.read_text(encoding="utf-8", errors="replace")

        # Preserve raw tombstone block
        tombstone_block = ""
        if "=== TOMBSTONE / KEY FACTS ===" in full_text:
            parts = full_text.split("=== FULL EXTRACTED CONTENT ===", 1)
            tombstone_block = parts[0].strip() if len(parts) > 1 else ""

        summary_data = generate_summary_and_dates(full_text, pkg_path.name)

        # Safe metadata lookup
        classification_info = {}
        matched = meta_df[meta_df.index.str.contains(pkg_path.stem, case=False, na=False)]
        if not matched.empty:
            classification_info = matched.iloc[0].to_dict()

        # Semantic search for related classified documents
        related_docs = []
        if embedder is not None and not meta_df.empty:
            try:
                pkg_emb = embedder.encode(full_text[:3000], normalize_embeddings=True).reshape(1, -1)
                meta_texts = meta_df.index.astype(str).tolist()
                meta_embs = embedder.encode(meta_texts, normalize_embeddings=True, batch_size=32)
                sims = (pkg_emb @ meta_embs.T).flatten()
                top_idx = np.argsort(sims)[-3:][::-1]
                for i in top_idx:
                    fname = meta_df.index[i]
                    row = meta_df.iloc[i]
                    related_docs.append(
                        f"{fname} | Function: {row.get('Function_EN','')} | "
                        f"Type: {row.get('Document Type / Type de document','')} | Conf: {row.get('overall_confidence',''):.2f}"
                    )
            except Exception as e:
                logger.warning(f"Semantic search failed for {pkg_path.name}: {e}")

        report_row = {
            "Package_Name": pkg_path.name,
            "Generated_Date": run_date,                    # ← Now clean YYYY-MM-DD only
            "Executive_Summary": summary_data.get("executive_summary", ""),
            "Plaintiff": summary_data.get("plaintiff", "Not Found"),
            "Defendant": summary_data.get("defendant", "Not Found"),
            "Case_Number": summary_data.get("case_number", "Not Found"),
            "Key_Dates": "; ".join(summary_data.get("key_dates", [])),
            "Tombstone_Raw": tombstone_block[:2500] if tombstone_block else "",
            "Function_EN": classification_info.get("Function_EN", ""),
            "Document_Type": classification_info.get("Document Type / Type de document", ""),
            "Sensitivity": classification_info.get("Sensitivity", ""),
            "Related_Classified_Docs": " | ".join(related_docs) if related_docs else "None found",
        }
        master_rows.append(report_row)

        # Markdown Report with clean Timeline
        dates_list = summary_data.get("key_dates", [])
        timeline = "\n".join(sorted(dates_list)) if dates_list else "No dates found"

        md_path = LITIGATION_REPORTS_DIR / f"{pkg_path.stem}_REPORT_{run_date}.md"   # date-only in filename too
        md_content = f"""# Litigation Report – {pkg_path.name}
**Generated:** {run_date}

## Executive Summary
{summary_data.get('executive_summary', 'N/A')}

## Plaintiff / Defendant
**Plaintiff:** {report_row['Plaintiff']}  
**Defendant:** {report_row['Defendant']}  
**Case Number:** {report_row['Case_Number']}

## Timeline (Key Dates)
{timeline}

## Tombstone / Key Facts (preserved from ingestion)
{tombstone_block or 'No tombstone block found'}

## Classification & Related Documents
- Function (EN): {report_row['Function_EN']}
- Document Type: {report_row['Document_Type']}
- Sensitivity: {report_row['Sensitivity']}
- Related Classified Docs (Semantic Match): {report_row['Related_Classified_Docs']}

## Full Package Location
{pkg_path}
"""
        md_path.write_text(md_content, encoding="utf-8")
        logger.info(f"Created Markdown report: {md_path.name}")

    # Master Excel
    master_df = pd.DataFrame(master_rows)
    excel_out = LITIGATION_REPORTS_DIR / f"Litigation_Master_Summary_{run_date}.xlsx"
    master_df.to_excel(excel_out, index=False)

    logger.info(f"Master Excel saved: {excel_out}")
    print("\n🎉 Litigation reporting complete!")
    print(f"   Reports folder : {LITIGATION_REPORTS_DIR}")
    print(f"   Master Excel   : {excel_out}")
    print(f"   Markdown reports : {len(packages)} files created")

if __name__ == "__main__":
    main()