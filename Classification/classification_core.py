# Classification/classification_core.py
"""
Thin wrapper around semantic_classify.
Forwards all parameters, including image_path for multimodal support.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from Classification.semantic.semantic_core import semantic_classify


def staged_classify(
    text: str,
    hierarchy_df: Any = None,                    # pd.DataFrame | None
    original_path: Optional[Path | str] = None,
    image_path: Optional[Path | str] = None,
) -> Dict[str, Any]:
    """
    Main entry point for document classification.
    Delegates directly to semantic_classify while maintaining forward compatibility.
    """
    return semantic_classify(
        text=text,
        hierarchy_df=hierarchy_df,
        original_path=original_path,
        image_path=image_path
    )