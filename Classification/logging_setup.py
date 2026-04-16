# Ingestion/logging_setup.py
"""
Configures logging for the ingestion pipeline.
Everything goes to one single file + console.
"""

import logging
from datetime import datetime
from pathlib import Path


def setup_summary_logger(logs_path: Path, log_name: str = "zz_extraction_summary.log") -> logging.Logger:
    """
    Set up the single summary logger for all ingestion activity.
    Returns the 'ingestion' logger.
    """
    log_path = logs_path / log_name
    logs_path.mkdir(exist_ok=True, parents=True)

    logger = logging.getLogger("classification")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(name)-12s | %(levelname)-7s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.info("=" * 80)
    logger.info(f"NEW CLASSIFICATION RUN STARTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Log file: {log_path.resolve()}")
    logger.info(f"Logging levels → File: DEBUG, Console: INFO")
    logger.info("=" * 80)

    logger.debug("DEBUG logging active in file")
    logger.info("Ingestion logging setup complete")

    return logger