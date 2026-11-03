"""Amazon JP Associates CTA for OKPy (book search by blog category)."""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import quote

AMAZON_TAG = os.getenv("AMAZON_JP_TAG", "starful06-22")

# category -> Amazon search keyword
CATEGORY_AMAZON_KEYWORDS: dict[str, str] = {
    "python": "Python 本",
    "cloud": "AWS 本",
    "terraform": "Terraform 本",
    "career": "IT 転職 本",
}
DEFAULT_AMAZON_KEYWORD = "プログラミング 本"

_TRUE = ("1", "true", "yes", "on")


def amazon_keyword(category: str = "") -> str:
    return CATEGORY_AMAZON_KEYWORDS.get(
        (category or "").strip().lower(), DEFAULT_AMAZON_KEYWORD
    )


def amazon_search_url(keyword: str) -> str:
    return f"https://www.amazon.co.jp/s?k={quote(keyword)}&tag={AMAZON_TAG}"


def amazon_banner_context(category: str = "") -> dict[str, Any]:
    """Template context for ``_amazon_cta.html``."""
    raw = os.getenv("AFFILIATE_OKPY_ENABLED") or os.getenv("A8_OKPY_ENABLED") or "1"
    if raw.strip().lower() not in _TRUE:
        return {"show_amazon_cta": False, "amazon_cta": None}
    kw = amazon_keyword(category)
    return {
        "show_amazon_cta": True,
        "amazon_cta": {
            "id": "amazon",
            "keyword": kw,
            "click_url": amazon_search_url(kw),
            "label": "Amazon で探す",
            "desc": f"「{kw}」をAmazon.co.jpで検索",
            "title": "おすすめ書籍（アフィリエイト）",
            "note": "アフィリエイト広告 · 新しいタブで開きます",
        },
    }
