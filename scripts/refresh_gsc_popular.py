#!/usr/bin/env python3
"""Refresh data/gsc_popular.json from Search Console (top pages by clicks)."""

import csv
import json
import os
import sys
import urllib.parse
from datetime import datetime, timezone

OKPY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OKADMIN_ROOT = "/opt/work/okadmin"
GSC_SITE_URL = os.getenv("GSC_SITE_URL", "sc-domain:okpy.net")
LIMIT = 6
DAYS = int(os.getenv("GSC_DAYS", "28"))

sys.path.insert(0, OKADMIN_ROOT)
from analytics_api import fetch_gsc_pages  # noqa: E402

REDIRECTS_CSV = os.path.join(OKPY_ROOT, "data", "redirects.csv")
OUT_JSON = os.path.join(OKPY_ROOT, "data", "gsc_popular.json")


def load_redirect_map():
    mapping = {}
    if not os.path.isfile(REDIRECTS_CSV):
        return mapping
    with open(REDIRECTS_CSV, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            old = (row.get("old_path") or "").strip()
            new = (row.get("new_url") or "").strip()
            if old and new:
                mapping[old] = new
    return mapping


def path_from_url(page_url: str) -> str:
    path = urllib.parse.urlparse(page_url).path or ""
    return path if path.startswith("/") else "/" + path


def slug_from_new_url(new_url: str) -> str:
    if "/blog/" not in new_url:
        return ""
    return new_url.split("/blog/", 1)[1].split("?")[0].split("#")[0].strip("/")


def path_to_slug(path: str, redirect_map: dict) -> str:
    if path in redirect_map:
        return slug_from_new_url(redirect_map[path])
    if not path.endswith("/"):
        alt = path + "/"
        if alt in redirect_map:
            return slug_from_new_url(redirect_map[alt])
    if path.startswith("/blog/"):
        return path[len("/blog/") :].strip("/")
    return ""


def main():
    print(f"📊 Fetching GSC pages for {GSC_SITE_URL} ({DAYS} days)...", flush=True)
    raw = fetch_gsc_pages(GSC_SITE_URL, days=DAYS)
    if raw.get("error"):
        print(f"❌ {raw['error']}", flush=True)
        sys.exit(1)

    rows = sorted(raw.get("rows") or [], key=lambda r: (-int(r.get("clicks") or 0), -(r.get("impressions") or 0)))
    redirect_map = load_redirect_map()
    entries = []
    seen_slugs = set()

    for row in rows:
        page = row.get("page") or ""
        path = path_from_url(page)
        slug = path_to_slug(path, redirect_map)
        if not slug or slug in seen_slugs:
            continue
        seen_slugs.add(slug)
        entries.append(
            {
                "page": page,
                "path": path,
                "slug": slug,
                "clicks": int(row.get("clicks") or 0),
                "impressions": int(row.get("impressions") or 0),
                "ctr": float(row.get("ctr") or 0),
                "position": float(row.get("position") or 0),
            }
        )
        if len(entries) >= LIMIT:
            break

    payload = {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "gsc_site_url": GSC_SITE_URL,
        "gsc_range": {"start": raw.get("start"), "end": raw.get("end"), "days": DAYS},
        "entries": entries,
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"✅ Wrote {len(entries)} popular entries → {OUT_JSON}")
    for e in entries:
        print(f"   {e['clicks']:3d} clicks | {e['slug'][:50]}")


if __name__ == "__main__":
    main()
