"""Map GSC page URLs to okpy blog post slugs."""

from __future__ import annotations

import json
import os
import urllib.parse

GSC_POPULAR_JSON = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "gsc_popular.json"
)
IT_TRENDS_JSON = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "it_trends.json"
)
HOME_LIMIT = 6
HOME_LATEST_LIMIT = 4
HOME_CAT_LIMIT = 3
HOME_SECTION_LEAD = ("eng-comms", "data-analysis")
GSC_SITE_URL = os.getenv("GSC_SITE_URL", "sc-domain:okpy.net")


def _path_from_url(page_url: str) -> str:
    path = urllib.parse.urlparse(page_url).path or ""
    return path if path.startswith("/") else "/" + path


def _slug_from_new_url(new_url: str) -> str:
    if "/blog/" not in new_url:
        return ""
    return new_url.split("/blog/", 1)[1].split("?")[0].split("#")[0].strip("/")


def path_to_slug(path: str, redirect_map: dict) -> str:
    path = path.rstrip("/") or path
    if path in redirect_map:
        return _slug_from_new_url(redirect_map[path])
    if not path.endswith("/"):
        alt = path + "/"
        if alt in redirect_map:
            return _slug_from_new_url(redirect_map[alt])
    if path.startswith("/blog/"):
        return path[len("/blog/") :].strip("/")
    return ""


def load_gsc_popular_cache() -> dict:
    if not os.path.isfile(GSC_POPULAR_JSON):
        return {}
    try:
        with open(GSC_POPULAR_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def popular_posts_from_gsc(cached_posts: list, redirect_map: dict, limit: int = HOME_LIMIT) -> list:
    """Resolve top GSC pages to post dicts; fallback to newest if cache missing."""
    cache = load_gsc_popular_cache()
    entries = cache.get("entries") or []
    by_slug = {p["slug"]: p for p in cached_posts}
    seen = set()
    popular = []

    for entry in entries:
        slug = entry.get("slug") or path_to_slug(
            _path_from_url(entry.get("page", "")), redirect_map
        )
        if not slug or slug in seen:
            continue
        post = by_slug.get(slug)
        if post:
            popular.append({**post, "gsc_clicks": entry.get("clicks", 0)})
            seen.add(slug)
        if len(popular) >= limit:
            break

    if len(popular) < limit:
        for post in cached_posts:
            if post["slug"] in seen:
                continue
            popular.append(post)
            seen.add(post["slug"])
            if len(popular) >= limit:
                break

    return popular[:limit]


def ordered_home_categories(categories: dict) -> dict:
    """Homepage topic/section order: communication first, then config order."""
    lead = [k for k in HOME_SECTION_LEAD if k in categories]
    rest = [k for k in categories if k not in HOME_SECTION_LEAD]
    return {k: categories[k] for k in (*lead, *rest)}


def posts_by_category(cached_posts: list, categories: dict, limit: int = HOME_LIMIT) -> dict:
    """Pick recent posts per category, preferring ones that have cover images."""
    buckets = {cat: [] for cat in categories}
    leftovers = {cat: [] for cat in categories}

    for post in cached_posts:
        cat = post.get("category")
        if cat not in buckets:
            continue
        if post.get("cover"):
            if len(buckets[cat]) < limit:
                buckets[cat].append(post)
        else:
            leftovers[cat].append(post)

    for cat in buckets:
        if len(buckets[cat]) < limit:
            need = limit - len(buckets[cat])
            buckets[cat].extend(leftovers[cat][:need])
    return buckets


def category_thumbnails(cached_posts: list, categories: dict) -> dict:
    """Most recent cover image per category (for topic cards)."""
    thumbs: dict[str, str] = {}
    for post in cached_posts:
        cat = post.get("category")
        if cat not in categories or cat in thumbs:
            continue
        cover = str(post.get("cover") or "").strip()
        if cover:
            thumbs[cat] = cover
    return thumbs


def category_cover_pool(cached_posts: list, categories: dict, per_cat: int = 24) -> dict:
    """Collect recent unique covers per category for card fallbacks."""
    pools: dict[str, list[str]] = {cat: [] for cat in categories}
    seen: dict[str, set[str]] = {cat: set() for cat in categories}
    for post in cached_posts:
        cat = post.get("category")
        if cat not in pools or len(pools[cat]) >= per_cat:
            continue
        cover = str(post.get("cover") or "").strip()
        if not cover or cover in seen[cat]:
            continue
        seen[cat].add(cover)
        pools[cat].append(cover)
    return {cat: covers for cat, covers in pools.items() if covers}


def fallback_cover_for_post(post: dict, cover_pools: dict) -> str:
    """Stable per-slug fallback cover from the category pool."""
    cat = post.get("category")
    pool = cover_pools.get(cat) or []
    if not pool:
        return ""
    slug = str(post.get("slug") or "")
    idx = sum(ord(c) for c in slug) % len(pool)
    return pool[idx]


def apply_card_covers(posts: list, cover_pools: dict) -> list:
    """Ensure each post has card_cover for list/grid rendering."""
    enriched = []
    for post in posts:
        cover = str(post.get("cover") or "").strip()
        if not cover:
            cover = fallback_cover_for_post(post, cover_pools)
        enriched.append({**post, "card_cover": cover})
    return enriched


def diverse_latest_posts(posts: list, limit: int = HOME_LATEST_LIMIT) -> list:
    """Newest posts, at most one per category (avoids lookalike pairs)."""
    picked: list = []
    seen_cat: set[str] = set()
    seen_slug: set[str] = set()
    for post in posts:
        slug = str(post.get("slug") or "")
        cat = str(post.get("category") or "")
        if not slug or slug in seen_slug or cat in seen_cat:
            continue
        picked.append(post)
        seen_slug.add(slug)
        if cat:
            seen_cat.add(cat)
        if len(picked) >= limit:
            return picked
    for post in posts:
        slug = str(post.get("slug") or "")
        if not slug or slug in seen_slug:
            continue
        picked.append(post)
        seen_slug.add(slug)
        if len(picked) >= limit:
            break
    return picked


def load_it_trends() -> dict:
    """Homepage editorial boards from data/it_trends.json (okadmin 트렌드 갱신)."""
    if not os.path.isfile(IT_TRENDS_JSON):
        return {}
    try:
        with open(IT_TRENDS_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    boards_out = []
    for board in data.get("boards") or []:
        if not isinstance(board, dict):
            continue
        items_out = []
        for item in board.get("items") or []:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or "").strip()
            href = str(item.get("href") or "").strip()
            if not name:
                continue
            if href.startswith("https://okpy.net"):
                href = href[len("https://okpy.net") :] or "/"
            if not href.startswith("/"):
                href = ""
            try:
                score = max(0, min(100, int(item.get("score") or 0)))
            except (TypeError, ValueError):
                score = 0
            try:
                rank = int(item.get("rank") or len(items_out) + 1)
            except (TypeError, ValueError):
                rank = len(items_out) + 1
            delta = item.get("delta", 0)
            if delta != "new":
                try:
                    delta = int(delta)
                except (TypeError, ValueError):
                    delta = 0
            items_out.append(
                {
                    "rank": rank,
                    "name": name,
                    "score": score or max(28, 100 - (rank - 1) * 6),
                    "delta": delta,
                    "href": href,
                }
            )
            if len(items_out) >= 12:
                break
        if not items_out:
            continue
        boards_out.append(
            {
                "id": str(board.get("id") or ""),
                "title": str(board.get("title") or board.get("id") or "Trend"),
                "items": items_out,
            }
        )
        if len(boards_out) >= 3:
            break
    if not boards_out:
        return {}
    return {
        "updated": str(data.get("updated") or "").strip()[:10],
        "headline": str(data.get("headline") or "今月のITトレンド").strip()[:40],
        "note": str(
            data.get("note")
            or "公式ランキングではありません。OKPyの記事と検索傾向から編集部が整理しています。"
        ).strip()[:160],
        "boards": boards_out,
    }
