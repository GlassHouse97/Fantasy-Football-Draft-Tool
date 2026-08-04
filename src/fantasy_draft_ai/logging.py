"""Consistent console logging for CLI and UI services."""

import logging
import os


def configure_logging() -> None:
    """Configure the root logger once using an environment override."""

    level_name = os.getenv("FANTASY_DRAFT_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
