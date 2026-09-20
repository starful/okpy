"""A8.net affiliate banners for OKPy (career + お名前.com)."""

from __future__ import annotations

import os
from typing import Any

# Career / 就労・転職 — Neuro Dive + @PRO人 (career + MBTI only)
CAREER_CATEGORIES: frozenset[str] = frozenset({"career"})

# Tech howto — お名前.com (domain / rental server)
ONAMAE_CATEGORIES: frozenset[str] = frozenset(
    {
        "python",
        "cloud",
        "terraform",
    }
)

A8_CATEGORIES: frozenset[str] = CAREER_CATEGORIES | ONAMAE_CATEGORIES

# Back-compat alias used by tests / older call sites
CATEGORY_A8_PROGRAM: dict[str, str] = {
    "career": "pro_jin",
    "python": "onamae",
    "cloud": "onamae",
    "terraform": "onamae",
}

NEURO_DIVE_PROGRAM_ID = "s00000019630003"
PRO_JIN_PROGRAM_ID = "s00000020853002"
ONAMAE_PROGRAM_ID = "s00000000018015"

NEURO_DIVE_A8 = {
    "id": "neuro_dive",
    "program_id": NEURO_DIVE_PROGRAM_ID,
    "click_url": os.getenv(
        "A8_NEURO_DIVE_CLICK_URL",
        "https://px.a8.net/svt/ejp?a8mat=4BACLI+2KVOOY+47GS+HVNAP",
    ),
    "image_url": os.getenv(
        "A8_NEURO_DIVE_BANNER_URL",
        "https://www27.a8.net/svt/bgt?aid=260823366156&wid=003&eno=01&mid=s00000019630003003000&mc=1",
    ),
    "pixel_url": os.getenv(
        "A8_NEURO_DIVE_PIXEL_URL",
        "https://www12.a8.net/0.gif?a8mat=4BACLI+2KVOOY+47GS+HVNAP",
    ),
    "label": "Neuro Dive — IT特化型 就労移行支援",
    "desc": "AI・データサイエンスを学べる就労移行支援（パーソルダイバース）",
    "alt": "Neuro Dive 就労移行支援 — アフィリエイト",
    "title": "就労移行支援（IT・データサイエンス）",
}

PRO_JIN_A8 = {
    "id": "pro_jin",
    "program_id": PRO_JIN_PROGRAM_ID,
    "click_url": os.getenv(
        "A8_PRO_JIN_CLICK_URL",
        "https://px.a8.net/svt/ejp?a8mat=4BACLI+2IHY9U+4GWI+BZVU9",
    ),
    "image_url": os.getenv(
        "A8_PRO_JIN_BANNER_URL",
        "https://www24.a8.net/svt/bgt?aid=260823366152&wid=003&eno=01&mid=s00000020853002015000&mc=1",
    ),
    "pixel_url": os.getenv(
        "A8_PRO_JIN_PIXEL_URL",
        "https://www13.a8.net/0.gif?a8mat=4BACLI+2IHY9U+4GWI+BZVU9",
    ),
    "label": "IT転職エージェント @PRO人",
    "desc": "IT職種・業界特化。キャリア相談の質にこだわった転職エージェント",
    "alt": "IT転職エージェント @PRO人 — アフィリエイト",
    "title": "IT転職エージェント",
}

ONAMAE_A8 = {
    "id": "onamae",
    "program_id": ONAMAE_PROGRAM_ID,
    "click_url": os.getenv(
        "A8_ONAMAE_CLICK_URL",
        "https://px.a8.net/svt/ejp?a8mat=4BACLH+2TT6RM+50+2HHVNM",
    ),
    "image_url": os.getenv("A8_ONAMAE_BANNER_URL", ""),
    "pixel_url": os.getenv(
        "A8_ONAMAE_PIXEL_URL",
        "https://www18.a8.net/0.gif?a8mat=4BACLH+2TT6RM+50+2HHVNM",
    ),
    "label": "お名前.com — ドメイン・レンタルサーバー",
    "desc": "検証用ドメインや個人プロジェクトの独自ドメイン取得",
    "alt": "お名前.com — アフィリエイト",
    "title": "ドメイン・レンタルサーバー",
}


def _banner_dict(src: dict[str, str]) -> dict[str, str]:
    return {
        "id": src["id"],
        "click_url": src["click_url"],
        "image_url": src["image_url"],
        "pixel_url": src["pixel_url"],
        "alt": src["alt"],
        "label": src["label"],
        "desc": src["desc"],
    }


def a8_banner_context(category: str = "") -> dict[str, Any]:
    """Career banners or お名前.com on matching blog categories."""
    enabled = os.getenv("A8_OKPY_ENABLED", "1").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    if not enabled:
        return {
            "show_a8_banner": False,
            "show_a8_banners": False,
            "a8_banners": [],
        }

    cat = (category or "").strip().lower()
    if cat not in A8_CATEGORIES:
        return {
            "show_a8_banner": False,
            "show_a8_banners": False,
            "a8_banners": [],
        }

    if cat in ONAMAE_CATEGORIES:
        banners = [_banner_dict(ONAMAE_A8)]
        title = "ドメイン・サーバー（アフィリエイト）"
    else:
        banners = [_banner_dict(NEURO_DIVE_A8), _banner_dict(PRO_JIN_A8)]
        title = "キャリア支援（アフィリエイト）"

    first = banners[0]
    note = "アフィリエイト広告 · 新しいタブで開きます"
    return {
        "show_a8_banner": True,
        "a8_banner": first,
        "a8_banner_title": title,
        "a8_banner_note": note,
        "show_a8_banners": True,
        "a8_banners": banners,
        "a8_banners_title": title,
        "a8_banners_note": note,
    }
