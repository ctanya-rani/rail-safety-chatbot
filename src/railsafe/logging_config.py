"""Logging configuration for the rail safety chatbot."""

import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    """Configure logging with a sensible format.

    Args:
        level: Logging level (default: INFO).
    """
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)
