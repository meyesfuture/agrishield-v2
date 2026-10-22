"""
Structured logging module for Punjab GrainWatch Backend.
Ensures clean, secret-free logging across all application components.
"""

import logging
import re
import sys
from typing import Any, Dict


# Regex pattern to catch common credential strings
SENSITIVE_PATTERNS = [
    re.compile(r"(token|secret|password|api[_-]?key|auth|bearer)\s*[:=]\s*['\"]?([^'\"\s&]+)", re.IGNORECASE),
    re.compile(r"(Bearer\s+)([A-Za-z0-9_\-\.]+)", re.IGNORECASE),
]


class SecretSanitizingFormatter(logging.Formatter):
    """Custom logging formatter that scrubs passwords, tokens, and secrets."""

    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record)
        for pattern in SENSITIVE_PATTERNS:
            msg = pattern.sub(r"\1: [REDACTED]", msg)
        return msg


def setup_logger(name: str = "grainwatch") -> logging.Logger:
    """Configure and return the application logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            SecretSanitizingFormatter(
                "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


logger = setup_logger()
