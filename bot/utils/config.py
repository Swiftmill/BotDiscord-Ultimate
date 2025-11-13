from __future__ import annotations

import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class Config:
    bot: Dict[str, Any]
    license: Dict[str, Any]
    security: Dict[str, Any]
    music: Dict[str, Any]
    logging: Dict[str, Any]
    web: Dict[str, Any]


def load_config(path: str | Path) -> Config:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return Config(**data)
