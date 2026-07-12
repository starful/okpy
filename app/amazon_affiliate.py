"""Amazon Associates (JP) search-link helpers for OKPy blog."""

from __future__ import annotations

import os
import re
from typing import Any
from urllib.parse import quote_plus

# Tracking ID from Amazon Associates Central (override via env).
ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG", "starful06-22")

# Default search keyword per blog category key.
CATEGORY_KEYWORDS: dict[str, str] = {
    "python": "Python",
    "cloud": "AWS",  # overridden by _cloud_keyword() when possible
    "dev-method": "開発方法論",
    "data-model": "データモデル",
    "pmbok": "PMBOK",
    "agile-scrum": "スクラム",
    "fit-journey": "新規事業",
}

BUTTON_LABELS: dict[str, str] = {
    "python": "Amazonで Python 関連を探す",
    "cloud": "Amazonでクラウド関連を探す",
    "dev-method": "Amazonで開発方法論を探す",
    "data-model": "Amazonでデータモデルを探す",
    "pmbok": "Amazonで PMBOK を探す",
    "agile-scrum": "Amazonでスクラムを探す",
    "fit-journey": "Amazonで新規事業を探す",
}

# Rakuten Affiliate text links (search: 「{keyword} 本」). Same hgc ID for all.
_RAKUTEN_UT = "eyJwYWdlIjoidXJsIiwidHlwZSI6InRleHQiLCJjb2wiOjF9"
_RAKUTEN_HGC = "43cde6d2.98a376f7.43cde6d3.c7b92630"


def _rakuten_url(pc_path_encoded: str) -> str:
    """pc_path_encoded is the double-encoded mall path segment from Affiliate tool."""
    return (
        f"https://hb.afl.rakuten.co.jp/hgc/{_RAKUTEN_HGC}/"
        f"?pc=https%3A%2F%2Fsearch.rakuten.co.jp%2Fsearch%2Fmall%2F"
        f"{pc_path_encoded}%2F&link_type=text&ut={_RAKUTEN_UT}"
    )


# Keys match resolve_keyword() output.
RAKUTEN_URLS: dict[str, str] = {
    "Python": _rakuten_url("Python%2520%25E6%259C%25AC"),
    "AWS": _rakuten_url("AWS%2520%25E6%259C%25AC"),
    "GCP": _rakuten_url("GCP%2520%25E6%259C%25AC"),
    "Azure": _rakuten_url("Azure%2520%25E6%259C%25AC"),
    "開発方法論": _rakuten_url(
        "%25E9%2596%258B%25E7%2599%25BA%25E6%2596%25B9%25E6%25B3%2595%25E8%25AB%2596%2520%25E6%259C%25AC"
    ),
    "データモデル": _rakuten_url(
        "%25E3%2583%2587%25E3%2583%25BC%25E3%2582%25BF%25E3%2583%25A2%25E3%2583%2587%25E3%2583%25AB%2520%25E6%259C%25AC"
    ),
    "PMBOK": _rakuten_url("PMBOK%2520%25E6%259C%25AC"),
    "スクラム": _rakuten_url(
        "%25E3%2582%25B9%25E3%2582%25AF%25E3%2583%25A9%25E3%2583%25A0%2520%25E6%259C%25AC"
    ),
    "新規事業": _rakuten_url(
        "%25E6%2596%25B0%25E8%25A6%258F%25E4%25BA%258B%25E6%25A5%25AD%2520%25E6%259C%25AC"
    ),
}


def _cloud_keyword(title: str = "", slug: str = "", body: str = "") -> str:
    text = f"{title} {slug} {body[:3000]}".lower()
    if re.search(r"\bazure\b|microsoft azure", text):
        return "Azure"
    if re.search(r"\bgcp\b|google cloud", text):
        return "GCP"
    if re.search(r"\baws\b|amazon web services|アマゾン ウェブ", text):
        return "AWS"
    return "AWS"


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
    return CATEGORY_KEYWORDS.get(cat, "Python")


def search_url(keyword: str, *, tag: str | None = None) -> str:
    tag = tag or ASSOCIATE_TAG
    return (
        "https://www.amazon.co.jp/s?k="
        + quote_plus(keyword)
        + "&tag="
        + quote_plus(tag)
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
        label = f"Amazonで {keyword} 関連を探す"
        rakuten_label = f"楽天で {keyword} 本を探す"
    else:
        label = BUTTON_LABELS.get(cat, f"Amazonで {keyword} を探す")
        rakuten_label = f"楽天で {keyword} 本を探す"
    return {
        "amazon_keyword": keyword,
        "amazon_search_url": search_url(keyword),
        "amazon_button_label": label,
        "amazon_associate_tag": ASSOCIATE_TAG,
        "rakuten_search_url": RAKUTEN_URLS.get(keyword, RAKUTEN_URLS["Python"]),
        "rakuten_button_label": rakuten_label,
    }
