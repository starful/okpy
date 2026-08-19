#!/usr/bin/env python3
"""Post one random okpy article to X (@X_okpy).

Used by .github/workflows/post_to_x.yml (08:00 JST).
Alternates daily between eng-comms and data-analysis.
"""

from __future__ import annotations

import json
import os
import random
import re
import sys
import tempfile
import urllib.request
from pathlib import Path

import frontmatter
import tweepy
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
POSTS_DIR = BASE_DIR / "app" / "content" / "posts"
HISTORY_PATH = BASE_DIR / "data" / "posted_to_x.json"
SITE_URL = os.getenv("SITE_URL", "https://okpy.net").rstrip("/")
GCS_IMAGE_BASE = os.getenv(
    "GCS_IMAGE_BASE",
    "https://storage.googleapis.com/ok-project-assets/okpy",
).rstrip("/")
HISTORY_KEEP = 60
TWEET_WEIGHTED_LIMIT = 280
URL_WEIGHTED_LENGTH = 23
MAX_IMAGE_BYTES = 4_800_000
ALLOWED_CATEGORIES = ("eng-comms", "data-analysis")

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


def load_history() -> tuple[list[str], str]:
    if not HISTORY_PATH.exists():
        return [], ""
    try:
        data = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return [], ""
    if isinstance(data, list):
        return [str(s) for s in data], ""
    if not isinstance(data, dict):
        return [], ""
    slugs = data.get("slugs") or []
    if not isinstance(slugs, list):
        slugs = []
    last = str(data.get("last_category") or "").strip().lower()
    if last not in ALLOWED_CATEGORIES:
        last = ""
    return [str(s) for s in slugs], last


def save_history(slugs: list[str], last_category: str) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(
        json.dumps(
            {
                "last_category": last_category,
                "slugs": slugs[-HISTORY_KEEP:],
            },
            ensure_ascii=False,
            indent=2,
        )
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
        body = post.content or ""
        if not summary:
            plain = re.sub(r"!\[.*?\]\(.*?\)", "", body)
            plain = re.sub(r"[#*`>_-]", " ", plain)
            plain = re.sub(r"\s+", " ", plain).strip()
            summary = plain[:180]
        category = str(post.get("category") or "").strip().lower()
        if category not in ALLOWED_CATEGORIES:
            continue
        posts.append(
            {
                "slug": slug,
                "title": title,
                "summary": summary,
                "category": category,
                "cover": resolve_cover(post.get("cover"), body),
            }
        )
    if not posts:
        raise FileNotFoundError(
            f"No markdown posts in {', '.join(ALLOWED_CATEGORIES)} under {POSTS_DIR}"
        )
    return posts


def resolve_cover(cover, body: str) -> str:
    url = str(cover or "").strip()
    if not url:
        match = re.search(r"!\[[^\]]*\]\(([^)]+)\)", body or "")
        url = match.group(1).strip() if match else ""
    if not url:
        return ""
    for prefix in ("/static/images/posts/", "static/images/posts/"):
        if url.startswith(prefix):
            return f"{GCS_IMAGE_BASE}/{url[len(prefix):]}"
    return url


def next_category(last: str) -> str:
    if last == "eng-comms":
        return "data-analysis"
    if last == "data-analysis":
        return "eng-comms"
    return "eng-comms"


def pick_post(posts: list[dict], recent: list[str], last_category: str) -> dict:
    recent_set = set(recent)
    target = next_category(last_category)

    def pool_for(cat: str) -> list[dict]:
        cands = [p for p in posts if p["category"] == cat]
        unused = [p for p in cands if p["slug"] not in recent_set]
        base = unused or cands
        with_cover = [p for p in base if p.get("cover")]
        return with_cover or base

    pool = pool_for(target)
    if not pool:
        other = "data-analysis" if target == "eng-comms" else "eng-comms"
        pool = pool_for(other)
        target = other
    if not pool:
        raise SystemExit("No posts in eng-comms or data-analysis")
    chosen = random.choice(pool)
    print(f"category={chosen['category']} (target={target})")
    return chosen


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


def credentials() -> tuple[str, str, str, str]:
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
    return key, secret, token, token_secret


def v2_client() -> tweepy.Client:
    key, secret, token, token_secret = credentials()
    return tweepy.Client(
        consumer_key=key,
        consumer_secret=secret,
        access_token=token,
        access_token_secret=token_secret,
    )


def v1_api() -> tweepy.API:
    key, secret, token, token_secret = credentials()
    auth = tweepy.OAuth1UserHandler(key, secret, token, token_secret)
    return tweepy.API(auth)


def download_cover(url: str) -> Path | None:
    if not url.startswith(("http://", "https://")):
        return None
    suffix = Path(url.split("?", 1)[0]).suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        suffix = ".jpg"
    tmp = tempfile.NamedTemporaryFile(prefix="okpy-x-", suffix=suffix, delete=False)
    tmp.close()
    dest = Path(tmp.name)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "okpy-x-poster/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read(MAX_IMAGE_BYTES + 1)
        if not data or len(data) > MAX_IMAGE_BYTES:
            dest.unlink(missing_ok=True)
            return None
        dest.write_bytes(data)
        return dest
    except Exception as exc:
        print(f"cover download failed: {exc}", file=sys.stderr)
        dest.unlink(missing_ok=True)
        return None


def upload_cover(url: str) -> str | None:
    path = download_cover(url)
    if not path:
        return None
    try:
        media = v1_api().media_upload(filename=str(path))
        return str(media.media_id)
    except tweepy.TweepyException as exc:
        print(f"cover upload failed: {exc}", file=sys.stderr)
        return None
    finally:
        path.unlink(missing_ok=True)


def main() -> None:
    dry_run = os.getenv("DRY_RUN", "").lower() in {"1", "true", "yes"}
    posts = load_posts()
    recent, last_category = load_history()
    chosen = pick_post(posts, recent, last_category)
    tweet = build_tweet(chosen)
    print(f"slug={chosen['slug']}")
    print(f"cover={chosen.get('cover') or '(none)'}")
    print("--- tweet ---")
    print(tweet)
    print("-------------")

    if dry_run:
        print("DRY_RUN=1 — not posting")
        return

    media_ids = None
    if chosen.get("cover"):
        media_id = upload_cover(chosen["cover"])
        if media_id:
            media_ids = [media_id]
            print(f"attached media_id={media_id}")
        else:
            print("posting without image")

    api = v2_client()
    try:
        kwargs = {"text": tweet}
        if media_ids:
            kwargs["media_ids"] = media_ids
        api.create_tweet(**kwargs)
    except tweepy.TweepyException as exc:
        raise SystemExit(f"X API error: {exc}") from exc

    recent.append(chosen["slug"])
    save_history(recent, chosen["category"])
    print(f"posted: {chosen['title']}")


if __name__ == "__main__":
    main()
