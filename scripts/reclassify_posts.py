#!/usr/bin/env python3
"""Reclassify exported posts into category subfolders using Hatena tags."""

import glob
import os
import re
import sys

import frontmatter
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

import importlib.util

OKPY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HATENA_DIR = "/opt/work/hatena"
POSTS_DIR = os.path.join(OKPY_ROOT, "app", "content", "posts")

load_dotenv(os.path.join(HATENA_DIR, ".env"))


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


okpy_config = _load_module("okpy_config", os.path.join(OKPY_ROOT, "app", "config.py"))
hatena_config = _load_module("hatena_config", os.path.join(HATENA_DIR, "config.py"))
blog_categories = _load_module(
    "blog_categories", os.path.join(OKPY_ROOT, "app", "blog_categories.py")
)

SITE_CONFIG = okpy_config.SITE_CONFIG
detect_category = blog_categories.detect_category

HATENA_USERNAME = os.getenv("HATENA_USERNAME")
hatena_tasks = hatena_config.TASKS["py"]
HATENA_BLOG_ID = os.getenv(hatena_tasks["hatena_blog_id_env"])
HATENA_API_KEY = os.getenv(hatena_tasks["hatena_api_key_env"])
NS = {"atom": "http://www.w3.org/2005/Atom", "app": "http://www.w3.org/2007/app"}


def entry_path(alternate_url: str) -> str:
    import urllib.parse
    if not alternate_url:
        return ""
    path = urllib.parse.urlparse(alternate_url).path
    return path if path.startswith("/") else "/" + path


def fetch_path_tags() -> dict:
    """Return {old_path: (tags_list, title)} for all published entries."""
    feed_url = f"https://blog.hatena.ne.jp/{HATENA_USERNAME}/{HATENA_BLOG_ID}/atom/entry"
    mapping = {}
    next_url = feed_url
    seen = set()

    while next_url:
        if next_url in seen:
            break
        seen.add(next_url)
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
            tags = []
            for cat in entry.findall("atom:category", NS):
                term = (cat.attrib.get("term") or "").strip()
                if term:
                    tags.append(term)

            alt = None
            for link in entry.findall("atom:link", NS):
                if link.attrib.get("rel") == "alternate":
                    alt = link.attrib.get("href")
                    break

            old_path = entry_path(alt)
            if old_path:
                mapping[old_path] = (tags, title)

        next_url = None
        for link in root.findall("atom:link", NS):
            if link.attrib.get("rel") == "next":
                next_url = link.attrib.get("href")
                break

    return mapping


def main():
    for cat in SITE_CONFIG["blog_categories"]:
        os.makedirs(os.path.join(POSTS_DIR, cat), exist_ok=True)

    print("📚 Fetching Hatena tags...", flush=True)
    path_tags = fetch_path_tags()
    print(f"✅ {len(path_tags)} paths loaded", flush=True)

    moved = 0
    unchanged = 0
    unknown = 0
    counts = {k: 0 for k in SITE_CONFIG["blog_categories"]}

    for fpath in glob.glob(os.path.join(POSTS_DIR, "**", "*.md"), recursive=True):
        with open(fpath, "r", encoding="utf-8") as f:
            post = frontmatter.loads(f.read())

        old_path = post.get("hatena_path") or ""
        tags, title = path_tags.get(old_path, ([], post.get("title", "")))
        if not tags and old_path:
            unknown += 1

        category = detect_category(tags, title or "")
        if category not in SITE_CONFIG["blog_categories"]:
            category = "python"

        post["category"] = category
        fname = os.path.basename(fpath)
        dest = os.path.join(POSTS_DIR, category, fname)

        content = frontmatter.dumps(post)
        if fpath != dest:
            with open(dest, "w", encoding="utf-8") as f:
                f.write(content)
            os.remove(fpath)
            moved += 1
        else:
            if post.get("category") != category:
                with open(dest, "w", encoding="utf-8") as f:
                    f.write(frontmatter.dumps(post))
            unchanged += 1

        counts[category] += 1

    print("\n✅ Reclassification done")
    print(f"   moved: {moved}, in-place: {unchanged}, unknown tags: {unknown}")
    for cat, n in counts.items():
        meta = SITE_CONFIG["blog_categories"][cat]
        print(f"   {meta['emoji']} {meta['label']}: {n}")


if __name__ == "__main__":
    main()
