#!/usr/bin/env python3
"""Sanity-check related_posts.py's ranking against a known high-traffic post (bokeh).

Loads real posts from app/content and prints what related_posts() picks for
the bokeh article, so category/tag/view-count weighting changes can be
eyeballed before deploying.
"""

import glob
import importlib.util
import os

import frontmatter

OKPY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(OKPY_ROOT, "app", "content", "posts")
TARGET_TITLE_HINT = "bokeh"


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_posts() -> list:
    posts = []
    for fpath in glob.glob(os.path.join(POSTS_DIR, "**", "*.md"), recursive=True):
        with open(fpath, "r", encoding="utf-8") as f:
            post = frontmatter.loads(f.read())
        basename = os.path.basename(fpath).replace(".md", "")
        posts.append(
            {
                "slug": str(post.get("slug") or basename).strip(),
                "title": str(post.get("title") or basename),
                "category": str(post.get("category") or "python").strip().lower(),
                "date": str(post.get("date") or "2026-01-01"),
            }
        )
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def main():
    # app/related_posts.py is imported standalone (its own ImportError fallback
    # picks up blog_categories/json_utils as top-level modules from app/).
    import sys

    sys.path.insert(0, os.path.join(OKPY_ROOT, "app"))
    related_posts_mod = _load_module("related_posts", os.path.join(OKPY_ROOT, "app", "related_posts.py"))

    posts = load_posts()
    target = next((p for p in posts if TARGET_TITLE_HINT in p["title"].lower()), None)
    if not target:
        print(f"❌ No post with '{TARGET_TITLE_HINT}' in the title found under {POSTS_DIR}")
        return

    print(f"🎯 Target: {target['title']} ({target['slug']}, category={target['category']})")
    print()

    results = related_posts_mod.related_posts(target, posts)
    for rank, candidate in enumerate(results, start=1):
        score = related_posts_mod._score(
            target["category"], related_posts_mod._tags_for(target["title"]), candidate
        )
        views = related_posts_mod._VIEW_COUNTS.get(candidate["slug"], 0)
        same_cat = "✓" if candidate["category"] == target["category"] else " "
        print(
            f"{rank}. [{score:2d}pt] cat={same_cat} views={views:<4} "
            f"{candidate['category']:<14} {candidate['title']}"
        )


if __name__ == "__main__":
    main()
