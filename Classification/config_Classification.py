# Classification/config_Classification.py
"""
Central configuration – aligned to the new fcp_CSV-UTF.csv column names.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from project_config import (
    SOURCE_DOCS_DIR as SOURCE_ORIGINALS,
)

# ── NEW HIERARCHY COLUMNS (exact match to updated fcp_CSV-UTF.csv) ─────────────────
HIERARCHY_COLUMNS = [
    "IMCC File No",
    "Function_EN",
    "Function_FR",
    "Function_Desc_EN",
    "Function_Desc_FR",
    "Function_Desc_Sum_EN",
    "Function_Desc_Sum_FR",
    "File Class No - Level1",
    "Sub-Function_EN",
    "Sub-Function_FR",
    "Sub-Function_Desc_EN",
    "Sub-Function_Desc_FR",
    "Sub-Function_Desc_Summ_EN",
    "Sub-Function_Desc_Summ_FR",
    "File Class No - Level2",
    "Business_Process_EN",
    "Business_Process_FR",
    "File Class No - Level3",
    "Records",
    "Retention Period",
    "Retention Trigger",
    "Full_File_Class_No"
]

# Metadata columns (non-hierarchy)
METADATA_COLUMNS = [
    "filename",
    "original_path",
    "text_length",
    "language_detected",
    "Title | Titre",
    "Document Type / Type de document",
    "Sensitivity",
    "Sensibilité",
    "Disposition Authorization / Autorisation de disposition",
    "Technical Environment | Environnement technique",
    "Litigation_hold",
    "Archival_value",
    "critical_business_content",
    "personal_information",
    "needs_review",
    "overall_confidence",
    "confidence_category"
]

# Final output column order – hierarchy inserted in the middle
COLUMNS_ORDER = [
    "filename",
    "original_path",
    "text_length",
    "language_detected",
    "Title | Titre",
    "Document Type / Type de document",
    "Sensitivity",
    "Sensibilité",

    # Hierarchy section – exact new order
    "IMCC File No",
    "Function_EN",
    "Function_FR",
    "Function_Desc_EN",
    "Function_Desc_FR",
    "Function_Desc_Sum_EN",
    "Function_Desc_Sum_FR",
    "File Class No - Level1",
    "Sub-Function_EN",
    "Sub-Function_FR",
    "Sub-Function_Desc_EN",
    "Sub-Function_Desc_FR",
    "Sub-Function_Desc_Summ_EN",
    "Sub-Function_Desc_Summ_FR",
    "File Class No - Level2",
    "Business_Process_EN",
    "Business_Process_FR",
    "File Class No - Level3",
    "Records",
    "Retention Period",
    "Retention Trigger",
    "Full_File_Class_No",

    # Metadata end
    "Disposition Authorization / Autorisation de disposition",
    "Technical Environment | Environnement technique",
    "Litigation_hold",
    "Archival_value",
    "critical_business_content",
    "personal_information",
    "needs_review",
    "overall_confidence",
    "confidence_category"
]

print(f"✅ Classification config loaded with updated columns")