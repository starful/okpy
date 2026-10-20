"""Shared helpers for reading JSON data files used across app modules."""
from __future__ import annotations

import json
import os
from typing import Any


def load_json_dict(path: str) -> dict[str, Any]:
    """Read a JSON object from `path`; return {} if missing, unreadable, or not an object."""
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}
