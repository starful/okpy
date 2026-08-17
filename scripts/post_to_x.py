#!/usr/bin/env python3
"""Post one random okpy article to X (@X_okpy).

Used by .github/workflows/post_to_x.yml (08:00 and 14:00 JST).
"""

from __future__ import annotations

import json
import os
import random
import re
import sys
from pathlib import Path

import frontmatter
import tweepy
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
POSTS_DIR = BASE_DIR / "app" / "content" / "posts"
HISTORY_PATH = BASE_DIR / "data" / "posted_to_x.json"
SITE_URL = os.getenv("SITE_URL", "https://okpy.net").rstrip("/")
HISTORY_KEEP = 60
TWEET_WEIGHTED_LIMIT = 280
URL_WEIGHTED_LENGTH = 23

CATEGORY_TAGS = {
    "python": ["#Python"],
    "cloud": ["#Cloud"],
    "terraform": ["#Terraform"],
    "ai-models": ["#AI", "#LLM"],
    "data-analysis": ["#DataAnalysis"],
    "data-model": ["#DataModel"],
    "dev-method": ["#開発"],
    "pmbok": ["#PMBOK"],
    "agile-scrum": ["#Agile", "#Scrum"],
    "fit-journey": ["#Startup"],
    "eng-comms": ["#エンジニア"],
}


def weighted_len(text: str) -> int:
    """Approximate X weighted length (CJK/emoji ≈ 2, ASCII ≈ 1)."""
    n = 0
    for ch in text:
        n += 2 if ord(ch) > 0x7F else 1
    return n


def trim_weighted(text: str, limit: int) -> str:
    if weighted_len(text) <= limit:
        return text
    out = []
    used = 0
    for ch in text:
        w = 2 if ord(ch) > 0x7F else 1
        if used + w > limit:
            break
        out.append(ch)
        used += w
    return "".join(out).rstrip()


def load_history() -> list[str]:
    if not HISTORY_PATH.exists():
        return []
    try:
        data = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    slugs = data.get("slugs") if isinstance(data, dict) else data
    if not isinstance(slugs, list):
        return []
    return [str(s) for s in slugs]


def save_history(slugs: list[str]) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(
        json.dumps({"slugs": slugs[-HISTORY_KEEP:]}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )


def load_posts() -> list[dict]:
    posts = []
    for path in POSTS_DIR.rglob("*.md"):
        try:
            post = frontmatter.load(path)
        except Exception as exc:
            print(f"skip {path}: {exc}", file=sys.stderr)
            continue
        slug = str(post.get("slug") or path.stem).strip()
        title = str(post.get("title") or slug).strip()
        if not slug or not title:
            continue
        summary = str(post.get("summary") or "").strip()
        if not summary:
            body = re.sub(r"!\[.*?\]\(.*?\)", "", post.content or "")
            body = re.sub(r"[#*`>_-]", " ", body)
            body = re.sub(r"\s+", " ", body).strip()
            summary = body[:180]
        posts.append(
            {
                "slug": slug,
                "title": title,
                "summary": summary,
                "category": str(post.get("category") or "").strip().lower(),
            }
        )
    if not posts:
        raise FileNotFoundError(f"No markdown posts under {POSTS_DIR}")
    return posts


def pick_post(posts: list[dict], recent: list[str]) -> dict:
    recent_set = set(recent)
    candidates = [p for p in posts if p["slug"] not in recent_set] or posts
    return random.choice(candidates)


def build_tweet(post: dict) -> str:
    url = f"{SITE_URL}/blog/{post['slug']}"
    tags = CATEGORY_TAGS.get(post["category"], [])
    tag_line = " ".join(tags + ["#okpy"])
    title = post["title"].replace("\n", " ").strip()
    summary = re.sub(r"\s+", " ", post["summary"]).strip()

    header = "今日の技術メモ"
    # URL is counted as a fixed t.co length; keep a placeholder while budgeting.
    fixed = f"{header}\n\n\n\n{url}\n\n{tag_line}"
    budget = TWEET_WEIGHTED_LIMIT - weighted_len(fixed) - URL_WEIGHTED_LENGTH + weighted_len(url)

    title_limit = max(40, min(weighted_len(title), budget // 2))
    title = trim_weighted(title, title_limit)
    leftover = budget - weighted_len(title)
    if leftover < 8:
        summary = ""
    else:
        summary = trim_weighted(summary, leftover)

    parts = [header, "", title]
    if summary:
        parts.extend(["", summary])
    parts.extend(["", url, "", tag_line])
    tweet = "\n".join(parts)

    # Final safety trim if over (drop summary first).
    if weighted_len(tweet) - weighted_len(url) + URL_WEIGHTED_LENGTH > TWEET_WEIGHTED_LIMIT:
        parts = [header, "", title, "", url, "", tag_line]
        tweet = "\n".join(parts)
    return tweet


def client() -> tweepy.Client:
    key = os.getenv("X_API_KEY")
    secret = os.getenv("X_API_SECRET")
    token = os.getenv("X_ACCESS_TOKEN")
    token_secret = os.getenv("X_ACCESS_SECRET")
    missing = [
        name
        for name, val in [
            ("X_API_KEY", key),
            ("X_API_SECRET", secret),
            ("X_ACCESS_TOKEN", token),
            ("X_ACCESS_SECRET", token_secret),
        ]
        if not val
    ]
    if missing:
        raise SystemExit(f"Missing env: {', '.join(missing)}")
    return tweepy.Client(
        consumer_key=key,
        consumer_secret=secret,
        access_token=token,
        access_token_secret=token_secret,
    )


def main() -> None:
    dry_run = os.getenv("DRY_RUN", "").lower() in {"1", "true", "yes"}
    posts = load_posts()
    recent = load_history()
    chosen = pick_post(posts, recent)
    tweet = build_tweet(chosen)
    print(f"slug={chosen['slug']}")
    print("--- tweet ---")
    print(tweet)
    print("-------------")

    if dry_run:
        print("DRY_RUN=1 — not posting")
        return

    api = client()
    try:
        api.create_tweet(text=tweet)
    except tweepy.TweepyException as exc:
        raise SystemExit(f"X API error: {exc}") from exc

    recent.append(chosen["slug"])
    save_history(recent)
    print(f"posted: {chosen['title']}")


if __name__ == "__main__":
    main()
