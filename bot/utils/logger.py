from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(level: str, file_path: str) -> logging.Logger:
    logger = logging.getLogger("bot")
    logger.setLevel(level.upper())
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(file_path, maxBytes=5_000_000, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.propagate = False
    return logger
