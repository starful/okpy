#!/usr/bin/env python3
"""Export all published Hatena posts to okpy markdown + redirects.csv."""

import csv
import importlib.util
import os
import re
import sys
import time
import unicodedata
import urllib.parse

import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

HATENA_DIR = "/opt/work/hatena"
OKPY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import importlib.util

blog_categories = importlib.util.spec_from_file_location(
    "blog_categories", os.path.join(OKPY_ROOT, "app", "blog_categories.py")
)
_bc_mod = importlib.util.module_from_spec(blog_categories)
blog_categories.loader.exec_module(_bc_mod)
detect_category = _bc_mod.detect_category

POSTS_DIR = os.path.join(OKPY_ROOT, "app", "content", "posts")
REDIRECTS_CSV = os.path.join(OKPY_ROOT, "data", "redirects.csv")
SITE_URL = os.getenv("SITE_URL", "https://okpy.net")

load_dotenv(os.path.join(HATENA_DIR, ".env"))
sys.path.insert(0, HATENA_DIR)
from config import TASKS  # noqa: E402

HATENA_USERNAME = os.getenv("HATENA_USERNAME")
config = TASKS["py"]
HATENA_BLOG_ID = os.getenv(config["hatena_blog_id_env"])
HATENA_API_KEY = os.getenv(config["hatena_api_key_env"])
NS = {"atom": "http://www.w3.org/2005/Atom", "app": "http://www.w3.org/2007/app"}


def slugify(title: str, max_len: int = 55) -> str:
    s = unicodedata.normalize("NFKC", title)
    s = re.sub(r"[【】\[\]（）()｜|：:、，.!?！？「」『』\s]+", "-", s)
    s = re.sub(r"[^a-zA-Z0-9\u3040-\u30ff\u4e00-\u9fff-]+", "", s)
    s = re.sub(r"-+", "-", s).strip("-").lower()
    if len(s) > max_len:
        s = s[:max_len].rstrip("-")
    return s or "post"


def entry_path(alternate_url: str) -> str:
    if not alternate_url:
        return ""
    path = urllib.parse.urlparse(alternate_url).path
    return path if path.startswith("/") else "/" + path


def path_slug_suffix(old_path: str) -> str:
    """e.g. /entry/2026/03/09/090000_1 -> 20260309-090000-1"""
    parts = old_path.rstrip("/").split("/")
    if len(parts) >= 3 and parts[1] == "entry":
        date_parts = parts[2:5] if len(parts) >= 5 else []
        entry_id = parts[-1] if parts else "post"
        date_slug = "".join(date_parts)
        entry_slug = entry_id.replace("_", "-")
        if date_slug:
            return f"{date_slug}-{entry_slug}"
    return re.sub(r"[^a-z0-9-]+", "-", old_path.lower()).strip("-")


def extract_summary(content: str, title: str) -> str:
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("```"):
            continue
        line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
        line = re.sub(r"[*_`#>]", "", line).strip()
        if len(line) > 20:
            return line[:160] + ("…" if len(line) > 160 else "")
    return title[:120]


def fetch_all_entries():
    feed_url = f"https://blog.hatena.ne.jp/{HATENA_USERNAME}/{HATENA_BLOG_ID}/atom/entry"
    items = []
    next_url = feed_url
    seen_pages = set()

    while next_url:
        if next_url in seen_pages:
            break
        seen_pages.add(next_url)
        resp = requests.get(
            next_url,
            auth=(HATENA_USERNAME, HATENA_API_KEY),
            headers={"Accept": "application/atom+xml"},
            timeout=30,
        )
        resp.raise_for_status()
        root = ET.fromstring(resp.text)

        for entry in root.findall("atom:entry", NS):
            draft_el = entry.find("app:control/app:draft", NS)
            draft = (draft_el.text or "yes").strip() if draft_el is not None else "yes"
            if draft != "no":
                continue

            title = (entry.find("atom:title", NS).text or "").strip()
            published = (entry.find("atom:published", NS).text or "")[:10]
            if not published:
                published = (entry.find("atom:updated", NS).text or "")[:10]

            edit_url = alt = None
            for link in entry.findall("atom:link", NS):
                if link.attrib.get("rel") == "edit":
                    edit_url = link.attrib.get("href")
                if link.attrib.get("rel") == "alternate":
                    alt = link.attrib.get("href")

            items.append(
                {
                    "title": title,
                    "date": published,
                    "edit_url": edit_url,
                    "alternate_url": alt,
                    "old_path": entry_path(alt),
                }
            )

        next_url = None
        for link in root.findall("atom:link", NS):
            if link.attrib.get("rel") == "next":
                next_url = link.attrib.get("href")
                break

        print(f"  listed {len(items)} entries ({len(seen_pages)} pages)...", flush=True)

    return items


def fetch_entry_details(edit_url: str):
    resp = requests.get(
        edit_url,
        auth=(HATENA_USERNAME, HATENA_API_KEY),
        headers={"Accept": "application/atom+xml"},
        timeout=30,
    )
    resp.raise_for_status()
    root = ET.fromstring(resp.text)
    title = (root.find("atom:title", NS).text or "").strip()
    content = (root.find("atom:content", NS).text or "").strip()
    cats = [(c.attrib.get("term") or "").strip() for c in root.findall("atom:category", NS)]
    return title, content, [c for c in cats if c]


def unique_slug(title: str, old_path: str, used: set) -> str:
    base = slugify(title)
    slug = base
    if slug in used:
        slug = f"{base}-{path_slug_suffix(old_path)}"
    if slug in used:
        slug = path_slug_suffix(old_path)
    n = 2
    while slug in used:
        slug = f"{base}-{n}"
        n += 1
    used.add(slug)
    return slug


def strip_duplicate_h1(body: str, title: str) -> str:
    lines = body.splitlines()
    if lines and lines[0].startswith("# "):
        h1 = lines[0][2:].strip()
        if h1 == title or title in h1 or h1 in title:
            return "\n".join(lines[1:]).lstrip()
    return body


def main():
    if not all([HATENA_USERNAME, HATENA_BLOG_ID, HATENA_API_KEY]):
        print("❌ Missing Hatena env vars")
        sys.exit(1)

    _spec = importlib.util.spec_from_file_location(
        "okpy_config", os.path.join(OKPY_ROOT, "app", "config.py")
    )
    okpy_config = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(okpy_config)
    SITE_CONFIG = okpy_config.SITE_CONFIG

    for cat in SITE_CONFIG["blog_categories"]:
        os.makedirs(os.path.join(POSTS_DIR, cat), exist_ok=True)

    # Remove flat .md files from previous layout
    for fname in os.listdir(POSTS_DIR):
        fpath = os.path.join(POSTS_DIR, fname)
        if fname.endswith(".md") and os.path.isfile(fpath):
            os.remove(fpath)

    print("📚 Fetching entry list...", flush=True)
    entries = fetch_all_entries()
    print(f"✅ Found {len(entries)} published entries", flush=True)

    used_slugs = set()
    redirects = []
    exported = 0
    errors = 0

    for i, entry in enumerate(entries, 1):
        try:
            title, content, cats = fetch_entry_details(entry["edit_url"])
            if not content:
                print(f"⚠️  [{i}] empty body, skip: {title[:50]}", flush=True)
                errors += 1
                continue

            category = detect_category(cats, title)
            old_path = entry["old_path"]
            slug = unique_slug(title, old_path, used_slugs)
            summary = extract_summary(content, title)
            body = strip_duplicate_h1(content, title)

            md = f"""---
title: {title!r}
date: {entry['date']}
category: {category}
slug: {slug}
summary: {summary!r}
hatena_path: {old_path!r}
---

# {title}

{body}
"""
            out_path = os.path.join(POSTS_DIR, category, f"{slug}.md")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(md)

            if old_path:
                new_url = f"{SITE_URL.rstrip('/')}/blog/{slug}"
                redirects.append({"old_path": old_path, "new_url": new_url})

            exported += 1
            if i % 25 == 0 or i == len(entries):
                print(f"  [{i}/{len(entries)}] exported {exported} ({category}/{slug}.md)", flush=True)

            time.sleep(0.12)
        except Exception as e:
            print(f"❌ [{i}] {entry.get('title', '')[:40]}: {e}", flush=True)
            errors += 1

    os.makedirs(os.path.dirname(REDIRECTS_CSV), exist_ok=True)
    with open(REDIRECTS_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["old_path", "new_url"])
        writer.writeheader()
        writer.writerows(redirects)

    py_count = len(os.listdir(os.path.join(POSTS_DIR, "python")))
    cloud_count = len(os.listdir(os.path.join(POSTS_DIR, "cloud")))
    print(f"\n✅ Done: {exported} md files (python={py_count}, cloud={cloud_count})")
    print(f"✅ redirects.csv: {len(redirects)} rows")
    if errors:
        print(f"⚠️  errors: {errors}")


if __name__ == "__main__":
    main()
