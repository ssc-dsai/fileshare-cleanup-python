# Classification/enrichers/embedding_classifier.py
"""
Staged hierarchical semantic classification using full descriptions.
Adds smart excerpts. Document Type is protected from being overwritten.
"""

import logging
import re

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from ..config_Classification import HIERARCHY_COLUMNS

logger = logging.getLogger(__name__)


def _smart_excerpt(full_text: str, document_text: str, max_chars: int = 1000) -> str:
    if not full_text.strip():
        return ""

    sentences = re.split(r'(?<=[.!?])\s+', full_text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return full_text[:max_chars]

    doc_words = set(re.findall(r'\w+', document_text.lower()))
    scored = []
    for sent in sentences:
        sent_words = set(re.findall(r'\w+', sent.lower()))
        overlap = len(sent_words & doc_words)
        scored.append((overlap, sent))

    scored.sort(reverse=True, key=lambda x: x[0])

    excerpt_parts = []
    current_len = 0
    for _, sent in scored:
        if current_len + len(sent) + 1 > max_chars and excerpt_parts:
            break
        excerpt_parts.append(sent)
        current_len += len(sent) + 1

    excerpt = " ".join(excerpt_parts).strip()
    return excerpt[:max_chars] if len(excerpt) > max_chars else excerpt


def semantic_match_with_embedding(
    text: str,
    hierarchy_df: pd.DataFrame,
    embedder,
    min_confidence: float = 0.22,
    high_threshold: float = 0.55,
    medium_threshold: float = 0.35,
    max_text_chars: int = 1200,
    excerpt_length: int = 1000
) -> dict:
    """
    Staged hierarchical classification.
    Document Type is explicitly protected and never overwritten.
    """
    if hierarchy_df.empty or embedder is None:
        logger.warning("Hierarchy empty or no embedder → unknown classification")
        return _fallback_unknown()

    text_to_embed = text.strip()[:max_text_chars]
    if len(text_to_embed) < 40:
        logger.info("Text too short for meaningful embedding → unknown")
        return _fallback_unknown()

    doc_emb = embedder.encode(text_to_embed, normalize_embeddings=True).reshape(1, -1)

    # Stage 1: Function
    func_col = "Function_Desc_EN"
    descriptions = hierarchy_df[func_col].fillna("").astype(str)
    valid_mask = descriptions.str.strip().astype(bool)
    valid_descs = descriptions[valid_mask].tolist()

    if not valid_descs:
        return _fallback_unknown()

    hier_embs = embedder.encode(valid_descs, normalize_embeddings=True, batch_size=32)
    sims = cosine_similarity(doc_emb, hier_embs)[0]
    best_idx = np.argmax(sims)
    conf = float(sims[best_idx])

    if conf < min_confidence:
        return _fallback_unknown()

    original_idx = np.where(valid_mask)[0][best_idx]
    best_row = hierarchy_df.iloc[original_idx].copy()

    func_excerpt = _smart_excerpt(best_row[func_col], text, excerpt_length)

    # Stage 2: Sub-Function
    sub_col = "Sub-Function_Desc_EN"
    sub_mask = (hierarchy_df["Function_EN"] == best_row["Function_EN"]) & hierarchy_df[sub_col].notna()
    sub_df = hierarchy_df[sub_mask]

    sub_excerpt = ""
    if not sub_df.empty:
        sub_descs = sub_df[sub_col].fillna("").astype(str).tolist()
        sub_embs = embedder.encode(sub_descs, normalize_embeddings=True, batch_size=32)
        sub_sims = cosine_similarity(doc_emb, sub_embs)[0]
        sub_best_idx = np.argmax(sub_sims)
        sub_conf = float(sub_sims[sub_best_idx])

        if sub_conf >= min_confidence:
            sub_row = sub_df.iloc[sub_best_idx]
            sub_excerpt = _smart_excerpt(sub_row[sub_col], text, excerpt_length)
            best_row.update(sub_row)
        else:
            sub_excerpt = "[Low confidence sub-function match]"

    # Stage 3: Records excerpt
    records_col = "Records"
    records_text = best_row[records_col] if pd.notna(best_row[records_col]) else ""
    records_excerpt = _smart_excerpt(records_text, text, excerpt_length)

    # Build result — ONLY hierarchy columns + excerpts.
    # Do NOT include or touch "Document Type / Type de document"
    result = {}
    for col in HIERARCHY_COLUMNS:
        if col in best_row and pd.notna(best_row[col]):
            result[col] = str(best_row[col]).strip()

    result.update({
        "Function_Match_Excerpt": func_excerpt,
        "Sub_Function_Match_Excerpt": sub_excerpt,
        "Records_Match_Excerpt": records_excerpt,
        "overall_confidence": round(conf, 3),
        "confidence_category": "High" if conf >= high_threshold else "Medium" if conf >= medium_threshold else "Low",
        "needs_review": "No" if conf >= medium_threshold else "Yes"
    })

    logger.info(f"Staged classification | conf={conf:.3f} | Function={result.get('Function_EN', 'Unknown')} | review={result['needs_review']}")
    return result


def _fallback_unknown() -> dict:
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