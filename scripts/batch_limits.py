"""Per-run batch caps from okadmin pipeline env."""
from __future__ import annotations

import os


def _non_negative_int(raw: str | None, default: int) -> int:
    if raw is None or str(raw).strip() == "":
        return default
    try:
        return max(0, int(str(raw).strip()))
    except ValueError:
        return default


def content_limit() -> int:
    return _non_negative_int(os.getenv("CONTENT_LIMIT"), 3)


def python_limit() -> int:
    raw = os.getenv("PYTHON_LIMIT")
    if raw is not None and str(raw).strip() != "":
        return _non_negative_int(raw, 3)
    return content_limit()


def cloud_limit() -> int:
    raw = os.getenv("CLOUD_LIMIT")
    if raw is not None and str(raw).strip() != "":
        return _non_negative_int(raw, 3)
    return content_limit()


def terraform_limit() -> int:
    raw = os.getenv("TERRAFORM_LIMIT")
    if raw is not None and str(raw).strip() != "":
        return _non_negative_int(raw, 3)
    return content_limit()
