# Ingestion/logging_setup.py
"""
Configures logging for the ingestion pipeline.
- File: DEBUG+ (detailed output for troubleshooting)
- Console: INFO+ (progress & important messages only)
"""
import logging
from datetime import datetime
from pathlib import Path

from .config_Ingestion import CREATE_PER_DOC_LOGS


def setup_summary_logger(logs_path: Path, log_name: str = "zz_extraction_summary.log") -> logging.Logger:
    """
    Set up the main summary logger for ingestion runs.
    Returns the 'ingestion' logger.
    """
    log_path = logs_path / log_name
    logs_path.mkdir(exist_ok=True, parents=True)

    logger = logging.getLogger("ingestion")
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers
    if logger.handlers:
        logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(name)-12s | %(levelname)-7s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler: DEBUG+
    file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler: INFO+
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Run marker
    logger.info("=" * 80)
    logger.info(f"NEW INGESTION RUN STARTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Log file: {log_path.resolve()}")
    logger.info(f"Logging levels → File: DEBUG, Console: INFO")
    logger.info("=" * 80)

    logger.debug("DEBUG logging active in file")
    logger.info("Ingestion logging setup complete")

    return logger


def setup_document_logger(file_path: str, logs_path: Path) -> logging.Logger | None:
    """
    Optional per-document logger (if CREATE_PER_DOC_LOGS = True).
    Returns a dedicated logger or None if disabled.
    """
    if not CREATE_PER_DOC_LOGS:
        return None

    logs_path.mkdir(exist_ok=True, parents=True)

    safe_name = Path(file_path).stem[:50].replace(" ", "_")  # truncate + safe chars
    log_name = f"doc_{safe_name}.log"
    log_path = logs_path / log_name

    logger = logging.getLogger(f"ingestion.doc.{safe_name}")
    logger.setLevel(logging.DEBUG)

    # Prevent duplicates
    if logger.handlers:
        logger.handlers.clear()

    handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")  # overwrite per run
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s"))
    logger.addHandler(handler)

    logger.info(f"Per-document log started for: {Path(file_path).name}")
    return logger