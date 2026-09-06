"""MBTI type → IT career mapping (nested under /category/career/mbti)."""
from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Any

MBTI_DATA_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "static", "json", "mbti_careers.json"
)
CAREER_MBTI_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "static", "json", "career_mbti.json"
)
MBTI_TYPE_ORDER: tuple[str, ...] = (
    "INTJ",
    "INTP",
    "ENTJ",
    "ENTP",
    "INFJ",
    "INFP",
    "ENFJ",
    "ENFP",
    "ISTJ",
    "ISFJ",
    "ESTJ",
    "ESFJ",
    "ISTP",
    "ISFP",
    "ESTP",
    "ESFP",
)
VALID_TYPES = frozenset(MBTI_TYPE_ORDER)


@lru_cache(maxsize=1)
def _load_raw() -> dict[str, Any]:
    if not os.path.isfile(MBTI_DATA_FILE):
        return {"types": {}}
    with open(MBTI_DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _load_career_mbti() -> dict[str, Any]:
    if not os.path.isfile(CAREER_MBTI_FILE):
        return {"careers": {}}
    with open(CAREER_MBTI_FILE, encoding="utf-8") as f:
        return json.load(f)


def normalize_mbti_type(raw: str) -> str | None:
    code = (raw or "").strip().upper()
    return code if code in VALID_TYPES else None


def list_mbti_types() -> list[dict[str, Any]]:
    data = _load_raw().get("types", {})
    items = []
    for code in MBTI_TYPE_ORDER:
        entry = data.get(code) or {}
        items.append(
            {
                "code": code,
                "label": entry.get("label", ""),
                "summary": entry.get("summary", ""),
            }
        )
    return items


def _posts_by_slug(career_posts: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {p.get("slug"): p for p in career_posts if p.get("slug")}


def get_mbti_type(
    code: str, career_posts: list[dict[str, Any]] | None = None
) -> dict[str, Any] | None:
    normalized = normalize_mbti_type(code)
    if not normalized:
        return None

    entry = (_load_raw().get("types") or {}).get(normalized)
    if not entry:
        return None

    jobs_by_id = _posts_by_slug(career_posts or [])
    careers = []
    for c in entry.get("careers") or []:
        jid = c.get("id", "")
        job = jobs_by_id.get(jid) or {}
        careers.append(
            {
                "id": jid,
                "name": c.get("name") or job.get("title", jid),
                "reason": c.get("reason", ""),
                "detail": c.get("detail", ""),
                "title": job.get("title", ""),
                "summary": job.get("summary", ""),
                "cover": job.get("cover", ""),
                "link": f"/blog/{jid}" if jid else "",
            }
        )

    related = []
    for rel in entry.get("related") or []:
        rel_code = normalize_mbti_type(rel)
        if not rel_code:
            continue
        rel_entry = (_load_raw().get("types") or {}).get(rel_code) or {}
        related.append({"code": rel_code, "label": rel_entry.get("label", "")})

    faqs = [
        {"question": f.get("q", ""), "answer": f.get("a", "")}
        for f in (entry.get("faqs") or [])
        if f.get("q") and f.get("a")
    ]

    return {
        "code": normalized,
        "label": entry.get("label", ""),
        "summary": entry.get("summary", ""),
        "intro": entry.get("intro", ""),
        "work_style": entry.get("work_style", ""),
        "avoid_env": entry.get("avoid_env", ""),
        "closing": entry.get("closing", ""),
        "strengths": list(entry.get("strengths") or []),
        "watchouts": list(entry.get("watchouts") or []),
        "careers": careers,
        "related": related,
        "faqs": faqs,
    }


def types_for_career(career_id: str, *, limit: int = 3) -> list[dict[str, str]]:
    if not career_id:
        return []

    type_meta = _load_raw().get("types") or {}
    career_map = (_load_career_mbti().get("careers") or {}).get(career_id) or []
    out: list[dict[str, str]] = []
    for item in career_map:
        code = normalize_mbti_type(item.get("code", ""))
        if not code:
            continue
        label = (type_meta.get(code) or {}).get("label", "")
        out.append(
            {
                "code": code,
                "label": label,
                "reason": (item.get("reason") or "").strip(),
            }
        )
        if len(out) >= limit:
            break

    if out:
        return out

    for code in MBTI_TYPE_ORDER:
        entry = type_meta.get(code) or {}
        ids = {c.get("id") for c in (entry.get("careers") or [])}
        if career_id in ids:
            out.append({"code": code, "label": entry.get("label", ""), "reason": ""})
            if len(out) >= limit:
                break
    return out


def all_mbti_type_codes() -> list[str]:
    return list(MBTI_TYPE_ORDER)
