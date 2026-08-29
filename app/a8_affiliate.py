"""A8.net affiliate banners for OKPy (approved programs only)."""

from __future__ import annotations

import os
from typing import Any

# Category → program key (提携済 only)
CATEGORY_A8_PROGRAM: dict[str, str] = {
    "data-analysis": "neuro_dive",
    "ai-models": "neuro_dive",
    "data-model": "neuro_dive",
    "eng-comms": "pro_jin",
    "fit-journey": "pro_jin",
}

NEURO_DIVE_PROGRAM_ID = "s00000019630003"
PRO_JIN_PROGRAM_ID = "s00000020853002"

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

_PROGRAMS = {
    "neuro_dive": NEURO_DIVE_A8,
    "pro_jin": PRO_JIN_A8,
}


def a8_banner_context(category: str = "") -> dict[str, Any]:
    """Template vars for one A8 banner based on blog category."""
    enabled = os.getenv("A8_OKPY_ENABLED", "1").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    if not enabled:
        return {"show_a8_banner": False}

    cat = (category or "").strip().lower()
    program_key = CATEGORY_A8_PROGRAM.get(cat)
    if not program_key:
        return {"show_a8_banner": False}

    src = _PROGRAMS[program_key]
    if not (src.get("click_url") or "").strip():
        return {"show_a8_banner": False}

    banner = {
        "id": src["id"],
        "click_url": src["click_url"],
        "image_url": src["image_url"],
        "pixel_url": src["pixel_url"],
        "alt": src["alt"],
        "label": src["label"],
        "desc": src["desc"],
    }
    return {
        "show_a8_banner": True,
        "a8_banner": banner,
        "a8_banner_title": src["title"],
        "a8_banner_note": "アフィリエイト広告 · 新しいタブで開きます",
    }
