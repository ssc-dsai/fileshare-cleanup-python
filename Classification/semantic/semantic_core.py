"""
Classification/semantic/semantic_core.py

Main semantic classification coordinator.
TITLE IS NOW ONLY SOURCED FROM INGESTION (prepended [Generated Title]).
"""

import logging
from pathlib import Path
import pandas as pd

from project_config import HIERARCHY_CSV

from ..config_Classification import HIERARCHY_COLUMNS, COLUMNS_ORDER

from ..enrichers.language import enrich_language
from ..enrichers.pii import enrich_pii
from ..enrichers.sensitivity import enrich_sensitivity
from ..utils.document_type_mapper import get_document_type
from ..enrichers.embedding_classifier import semantic_match_with_embedding
from ..enrichers.regex_enricher import apply_regex_rules

logger = logging.getLogger(__name__)

# Global embedder – loaded once
embedder = None
try:
    from sentence_transformers import SentenceTransformer
    embedder = SentenceTransformer('Lajavaness/bilingual-embedding-small', trust_remote_code=True)
except Exception as e:
    logger.error(f"Failed to load embedder: {e}")
    embedder = None


def semantic_classify(
    text: str,
    hierarchy_df: pd.DataFrame | None = None,
    original_path: Path | str | None = None,
    image_path: Path | str | None = None,
) -> dict:
    if not text or not text.strip():
        return _minimal_unknown_row(original_path)

    filename = Path(original_path).name if original_path else "unknown"

    metadata = {
        "filename": filename,
        "original_path": str(original_path) if original_path else "",
        "text_length": len(text),
    }

    # Load hierarchy
    if hierarchy_df is None:
        try:
            hierarchy_df = pd.read_csv(HIERARCHY_CSV, encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to load hierarchy CSV: {e}")
            hierarchy_df = pd.DataFrame()

    # 1. RegEx layer (highest precedence)
    regex_overrides = apply_regex_rules(text, original_path=original_path)
    if regex_overrides:
        metadata.update(regex_overrides)

    # 2. Lightweight enrichers — TITLE IS NO LONGER GENERATED HERE
    metadata.update(enrich_language(text))
    metadata.update(enrich_sensitivity(text, image_path=image_path))

    # 3. Document Type
    doc_type_value = get_document_type(original_path=original_path)
    metadata["Document Type / Type de document"] = doc_type_value
    logger.info(f"✅ Document Type set to: '{doc_type_value}' for {filename}")

    # 4. PII
    if "personal_information" not in metadata:
        metadata.update(enrich_pii(text))

    # 5. Embedding classification
    if embedder is not None and not hierarchy_df.empty and len(text.strip()) > 50:
        try:
            classif_result = semantic_match_with_embedding(
                text=text,
                hierarchy_df=hierarchy_df,
                embedder=embedder,
            )
            classif_result.pop("Document Type / Type de document", None)  # protect it
            metadata.update(classif_result)
        except Exception as e:
            logger.error(f"Embedding classification failed: {e}")
            metadata.update(_fallback_unknown_classification())
    else:
        metadata.update(_fallback_unknown_classification())

    # Static defaults
    metadata.setdefault("Litigation_hold", "No")
    metadata.setdefault("Archival_value", "No")
    metadata.setdefault("critical_business_content", "No")

    final_row = {col: metadata.get(col, "") for col in COLUMNS_ORDER}

    return final_row


def _fallback_unknown_classification() -> dict:
    return {
        "Function_EN": "Unknown",
        "Function_FR": "Inconnu",
        "Sub-Function_EN": "Unknown",
        "Sub-Function_FR": "Inconnu",
        "Business_Process_EN": "Unknown",
        "Business_Process_FR": "Inconnu",
        "Function_Match_Excerpt": "",
        "Sub_Function_Match_Excerpt": "",
        "Records_Match_Excerpt": "",
        "overall_confidence": 0.0,
        "confidence_category": "Low",
        "needs_review": "Yes",
    }


def _minimal_unknown_row(original_path=None) -> dict:
    return {
        "filename": Path(original_path).name if original_path else "unknown_document",
        "original_path": str(original_path) if original_path else "",
        "text_length": 0,
        "language_detected": "und",
        "personal_information": "No",
        "Sensitivity": "Unclassified",
        "Sensibilité": "Non classifié",
        "Function_EN": "Unknown",
        "overall_confidence": 0.0,
        "confidence_category": "Low",
        "needs_review": "Yes",
    }