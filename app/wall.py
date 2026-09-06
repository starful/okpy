"""OKPy wall — one-line memos, shipped URLs, GitHub repos.

Approved cards are read from data/wall_approved.json.
New posts append to data/wall_queue.json and wait for review (local preview).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
APPROVED_JSON = os.environ.get("WALL_APPROVED_JSON") or os.path.join(DATA_DIR, "wall_approved.json")
QUEUE_JSON = os.environ.get("WALL_QUEUE_JSON") or os.path.join(DATA_DIR, "wall_queue.json")

HOME_WALL_LIMIT = 3
TEXT_MIN = 8
TEXT_MAX = 140
NAME_MAX = 24
QUEUE_CAP = 200
RATE_PER_DAY = 8

TYPES = ("memo", "ship", "github")
TYPE_LABELS = {
    "memo": "ひとこと",
    "ship": "つくったもの",
    "github": "GitHub",
}

_GITHUB_RE = re.compile(
    r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?$"
)
_SPAM_HOSTS = frozenset({"bit.ly", "t.co", "tinyurl.com", "goo.gl"})


def type_label(kind: str) -> str:
    return TYPE_LABELS.get(kind, kind)


def _read_json(path: str) -> dict[str, Any]:
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_json(path: str, payload: dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def _clean_text(raw: Any, *, limit: int = TEXT_MAX) -> str:
    text = re.sub(r"\s+", " ", str(raw or "")).strip()
    return text[:limit]


def _normalize_url(raw: str) -> str:
    url = str(raw or "").strip()
    if not url:
        return ""
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        return ""
    host = parsed.netloc.lower()
    if host in _SPAM_HOSTS or host.endswith(".bit.ly"):
        return ""
    path = parsed.path.rstrip("/")
    return f"https://{host}{path}"


def _github_url(raw: str) -> str:
    url = _normalize_url(raw)
    if not url:
        return ""
    if _GITHUB_RE.match(url) or _GITHUB_RE.match(url + "/"):
        return url.rstrip("/")
    return ""


def public_item(raw: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    kind = str(raw.get("type") or "").strip()
    if kind not in TYPES:
        return None
    text = _clean_text(raw.get("text"))
    if len(text) < TEXT_MIN:
        return None
    url = str(raw.get("url") or "").strip()
    if kind == "github":
        url = _github_url(url)
        if not url:
            return None
    elif kind == "ship":
        url = _normalize_url(url)
        if not url:
            return None
    else:
        url = _normalize_url(url) if url else ""
    name = _clean_text(raw.get("name"), limit=NAME_MAX) or "indie"
    at = str(raw.get("at") or "")[:10]
    return {
        "id": str(raw.get("id") or "")[:40],
        "type": kind,
        "label": TYPE_LABELS[kind],
        "text": text,
        "url": url,
        "name": name,
        "at": at,
    }


def load_approved(*, limit: int | None = None) -> list[dict[str, Any]]:
    items = []
    for raw in _read_json(APPROVED_JSON).get("items") or []:
        got = public_item(raw)
        if got:
            items.append(got)
    items.sort(key=lambda r: r.get("at") or "", reverse=True)
    if limit is not None:
        return items[:limit]
    return items


def load_home_wall() -> list[dict[str, Any]]:
    return load_approved(limit=HOME_WALL_LIMIT)


def _ip_hash(ip: str) -> str:
    return hashlib.sha256((ip or "local").encode("utf-8")).hexdigest()[:16]


def _queue_items() -> list[dict[str, Any]]:
    raw = _read_json(QUEUE_JSON).get("items") or []
    return [x for x in raw if isinstance(x, dict)]


def _rate_ok(ip_hash: str, now: datetime) -> bool:
    day = now.date().isoformat()
    n = 0
    for item in _queue_items():
        if item.get("ip") != ip_hash:
            continue
        at = str(item.get("at") or "")
        if at.startswith(day):
            n += 1
    return n < RATE_PER_DAY


def validate_submission(
    *,
    kind: str,
    text: str,
    url: str,
    name: str,
    honeypot: str,
) -> tuple[dict[str, Any] | None, str]:
    if str(honeypot or "").strip():
        return None, "送信できませんでした"
    kind = str(kind or "").strip()
    if kind not in TYPES:
        return None, "種別を選んでください"
    text = _clean_text(text)
    if len(text) < TEXT_MIN:
        return None, f"{TEXT_MIN}文字以上で書いてください"
    if len(text) > TEXT_MAX:
        return None, f"{TEXT_MAX}文字以内にしてください"
    name = _clean_text(name, limit=NAME_MAX)
    url = str(url or "").strip()
    if kind == "github":
        url = _github_url(url)
        if not url:
            return None, "GitHub は https://github.com/user/repo の形で"
    elif kind == "ship":
        url = _normalize_url(url)
        if not url:
            return None, "https:// で始まる URL を入れてください"
    else:
        url = _normalize_url(url) if url else ""
    return {
        "type": kind,
        "text": text,
        "url": url,
        "name": name,
    }, ""


def enqueue_submission(fields: dict[str, Any], *, ip: str = "") -> tuple[bool, str]:
    now = datetime.now(timezone.utc)
    iph = _ip_hash(ip)
    if not _rate_ok(iph, now):
        return False, "今日の投稿上限です。明日またどうぞ"
    items = _queue_items()
    entry = {
        "id": uuid.uuid4().hex[:12],
        "type": fields["type"],
        "text": fields["text"],
        "url": fields.get("url") or "",
        "name": fields.get("name") or "",
        "at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ip": iph,
        "status": "pending",
    }
    items.append(entry)
    if len(items) > QUEUE_CAP:
        items = items[-QUEUE_CAP:]
    try:
        _write_json(QUEUE_JSON, {"items": items})
    except OSError:
        return False, "保存できませんでした（ローカル data フォルダを確認）"
    return True, ""
