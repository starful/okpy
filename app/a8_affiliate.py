"""A8.net affiliate banners for OKPy — retired.

Neuro Dive and お名前.com (px.a8.net) were removed; OKPy now uses Amazon JP only
(see ``amazon_affiliate.py``). This module is kept so ``a8_banner_context`` imports
keep working; it never shows an A8 banner.
"""

from __future__ import annotations

from typing import Any

A8_CATEGORIES: frozenset[str] = frozenset()


def a8_banner_context(category: str = "") -> dict[str, Any]:
    return {
        "show_a8_banner": False,
        "show_a8_banners": False,
        "a8_banners": [],
    }
