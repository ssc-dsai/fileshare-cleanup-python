# Litigation/utils/tombstone_extractor.py
"""
Extracts key tombstone / structured data from litigation text.
Focuses on plaintiff, defendant, dates, amounts, case numbers, etc.
"""

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

def extract_tombstone_data(text: str, file_path: Path) -> dict:
    """Extract key facts from litigation document text."""
    data = {
        "Source_File": file_path.name,
        "Plaintiff_Name": "Not Found",
        "Defendant_Name": "Not Found",
        "Case_Number": "Not Found",
        "Date_of_Incident": "Not Found",
        "Claim_Amount": "Not Found",
        "Key_File_Reference": "Not Found",
        "Document_Type": file_path.suffix.upper().replace(".", ""),
    }

    text_lower = text.lower()

    # Simple regex patterns for common tombstone items
    plaintiff_match = re.search(r'(?i)(plaintiff|claimant|petitioner):\s*([^\n,]+)', text)
    if plaintiff_match:
        data["Plaintiff_Name"] = plaintiff_match.group(2).strip()

    defendant_match = re.search(r'(?i)(defendant|respondent):\s*([^\n,]+)', text)
    if defendant_match:
        data["Defendant_Name"] = defendant_match.group(2).strip()

    case_match = re.search(r'(?i)(case no|file no|court file|docket):\s*([^\n]+)', text)
    if case_match:
        data["Case_Number"] = case_match.group(2).strip()

    date_match = re.search(r'(?i)(date of incident|incident date|occurred on):\s*([^\n]+)', text)
    if date_match:
        data["Date_of_Incident"] = date_match.group(2).strip()

    amount_match = re.search(r'(?i)(claim amount|damages|value of claim|settlement):\s*\$?([\d,]+)', text)
    if amount_match:
        data["Claim_Amount"] = f"${amount_match.group(2).strip()}"

    file_ref_match = re.search(r'(?i)(file class|imcc|file no):\s*([^\n]+)', text)
    if file_ref_match:
        data["Key_File_Reference"] = file_ref_match.group(2).strip()

    logger.debug(f"Tombstone extracted for {file_path.name}: {data}")
    return data