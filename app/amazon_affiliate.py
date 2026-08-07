"""Amazon Associates (JP) + Rakuten Ichiba search-link helpers for OKPy blog."""

from __future__ import annotations

import os
import re
from typing import Any
from urllib.parse import quote, quote_plus

# Tracking ID from Amazon Associates Central (override via env).
ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG", "starful06-22")
_RAKUTEN_UT = "eyJwYWdlIjoidXJsIiwidHlwZSI6InRleHQiLCJjb2wiOjF9"
_RAKUTEN_HGC = os.getenv(
    "RAKUTEN_ICHIBA_HGC", "43cde6d2.98a376f7.43cde6d3.c7b92630"
)

# Default search keyword per blog category key (book-weighted).
CATEGORY_KEYWORDS: dict[str, str] = {
    "python": "Python 本",
    "cloud": "AWS 本",  # overridden by _cloud_keyword() when possible
    "terraform": "Terraform 本",
    "dev-method": "開発方法論 本",
    "data-model": "データモデル 本",
    "data-analysis": "データ分析 本",
    "pmbok": "PMBOK 本",
    "agile-scrum": "スクラム 本",
    "fit-journey": "新規事業 本",
}

BUTTON_LABELS: dict[str, str] = {
    "python": "Amazonで Python 本を探す",
    "cloud": "Amazonでクラウド本を探す",
    "terraform": "Amazonで Terraform 本を探す",
    "dev-method": "Amazonで開発方法論の本を探す",
    "data-model": "Amazonでデータモデルの本を探す",
    "data-analysis": "Amazonでデータ分析の本を探す",
    "pmbok": "Amazonで PMBOK 本を探す",
    "agile-scrum": "Amazonでスクラム本を探す",
    "fit-journey": "Amazonで新規事業の本を探す",
}


def _cloud_keyword(title: str = "", slug: str = "", body: str = "") -> str:
    text = f"{title} {slug} {body[:3000]}".lower()
    if re.search(r"\bazure\b|microsoft azure", text):
        return "Azure 本"
    if re.search(r"\bgcp\b|google cloud", text):
        return "GCP 本"
    if re.search(r"\baws\b|amazon web services|アマゾン ウェブ", text):
        return "AWS 本"
    return "AWS 本"


def _python_keyword(title: str = "", slug: str = "", body: str = "") -> str:
    text = f"{title} {slug} {body[:2000]}".lower()
    if re.search(r"\bfastapi\b", text):
        return "FastAPI 本"
    if re.search(r"\bdjango\b", text):
        return "Django 本"
    if re.search(r"\bflask\b", text):
        return "Flask 本"
    if re.search(r"\bpandas\b", text):
        return "pandas 本"
    return "Python 本"


def resolve_keyword(
    category: str,
    *,
    title: str = "",
    slug: str = "",
    body: str = "",
) -> str:
    cat = (category or "python").strip().lower()
    if cat == "cloud":
        return _cloud_keyword(title=title, slug=slug, body=body)
    if cat == "python":
        return _python_keyword(title=title, slug=slug, body=body)
    return CATEGORY_KEYWORDS.get(cat, "Python 本")


def search_url(keyword: str, *, tag: str | None = None) -> str:
    tag = tag or ASSOCIATE_TAG
    return (
        "https://www.amazon.co.jp/s?k="
        + quote_plus(keyword)
        + "&tag="
        + quote_plus(tag)
    )


def rakuten_search_url(keyword: str) -> str:
    """Dynamic Ichiba search (same wrap style as campus sites)."""
    dest = f"https://search.rakuten.co.jp/search/mall/{quote(keyword, safe='')}/"
    pc = quote(dest, safe="")
    return (
        f"https://hb.afl.rakuten.co.jp/hgc/{_RAKUTEN_HGC}/"
        f"?pc={pc}&link_type=text&ut={_RAKUTEN_UT}"
    )


def affiliate_context(
    category: str,
    *,
    title: str = "",
    slug: str = "",
    body: str = "",
) -> dict[str, Any]:
    """Template vars for the Amazon + Rakuten CTA box."""
    cat = (category or "python").strip().lower()
    keyword = resolve_keyword(cat, title=title, slug=slug, body=body)
    if cat == "cloud":
        label = f"Amazonで {keyword} を探す"
        rakuten_label = f"楽天で {keyword} を探す"
    elif cat == "python":
        label = f"Amazonで {keyword} を探す"
        rakuten_label = f"楽天で {keyword} を探す"
    else:
        label = BUTTON_LABELS.get(cat, f"Amazonで {keyword} を探す")
        rakuten_label = f"楽天で {keyword} を探す"
    return {
        "amazon_keyword": keyword,
        "amazon_search_url": search_url(keyword),
        "amazon_button_label": label,
        "amazon_associate_tag": ASSOCIATE_TAG,
        "rakuten_search_url": rakuten_search_url(keyword),
        "rakuten_button_label": rakuten_label,
    }
