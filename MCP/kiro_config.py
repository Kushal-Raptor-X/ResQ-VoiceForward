"""Load Layer 4/5 settings from `.kiro/config/ethical_longitudinal.json`."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path


def _mcp_dir() -> Path:
    return Path(__file__).resolve().parent


def _repo_root() -> Path:
    return _mcp_dir().parent


@lru_cache
def load_ethical_config() -> dict:
    path = _repo_root() / ".kiro" / "config" / "ethical_longitudinal.json"
    if not path.is_file():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def clear_ethical_config_cache() -> None:
    load_ethical_config.cache_clear()
