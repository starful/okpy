"""Related-post recommendations by category/tag/traffic similarity.

Posts carry no explicit tags field, so the Hatena tag/keyword hints in
blog_categories.py double as a lightweight tag vocabulary, combined with
title keyword overlap to tell apart posts within the same category.
Candidates that are already proven high-traffic (data/gsc_popular.json)
get a small boost so popular posts pick up more internal links. A handful of
slugs can also be manually curated via RELATED_POSTS_OVERRIDES, for posts that
should link out to other categories the scoring alone wouldn't surface.
"""

import os
import re

try:
    from .blog_categories import (
        CLOUD_TAGS,
        CLOUD_TITLE_KEYWORDS,
        HATENA_TAG_PRIORITY,
        TERRAFORM_TAGS,
        TERRAFORM_TITLE_KEYWORDS,
    )
    from .json_utils import load_json_dict
except ImportError:
    from blog_categories import (
        CLOUD_TAGS,
        CLOUD_TITLE_KEYWORDS,
        HATENA_TAG_PRIORITY,
        TERRAFORM_TAGS,
        TERRAFORM_TITLE_KEYWORDS,
    )
    from json_utils import load_json_dict

RELATED_POSTS_LIMIT = 3
CATEGORY_MATCH_WEIGHT = 10
VIEW_SCORE_CAP = 5
VIEW_SCORE_DIVISOR = 2

# Manual curation for specific high-traffic posts: slug -> ordered list of related
# slugs to pin ahead of the scored ranking below. Useful when a post should link to
# others outside its own category that the tag/keyword overlap can't find on its own.
RELATED_POSTS_OVERRIDES = {
    "pythonistaのためのbokehでパワフルなグラフを作ろう": [
        "nicegui",
        "python-pyarrow-大規模データの処理-まだ-遅い-と我慢していませんか",
        "データベース設計におけるpk-fk-インデックスの重要性",
    ],
}

GSC_POPULAR_JSON = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "gsc_popular.json"
)

# Pseudo-tag vocabulary derived from blog_categories.py's own tag/keyword hints.
_TAG_VOCAB = {t.lower() for t in CLOUD_TAGS | TERRAFORM_TAGS}
_TAG_VOCAB |= {k.lower() for k in CLOUD_TITLE_KEYWORDS + TERRAFORM_TITLE_KEYWORDS}
_TAG_VOCAB |= {tag.lower() for tag, _ in HATENA_TAG_PRIORITY}

_TOKEN_RE = re.compile(r"[A-Za-z0-9]+|[぀-ヿ一-鿿]+")
_STOPWORDS = {"の", "と", "を", "に", "は", "が", "で", "か", "も", "vs", "とは", "比較"}


def _tags_for(title: str) -> set:
    """Tag-like keywords for a post: blog_categories.py hints + title tokens."""
    title = title or ""
    hits = {kw for kw in _TAG_VOCAB if kw in title.lower()}
    tokens = {t for t in _TOKEN_RE.findall(title.lower()) if len(t) > 1 and t not in _STOPWORDS}
    return hits | tokens


def _load_view_counts() -> dict:
    """Slug -> GSC clicks (data/gsc_popular.json), used as a view-count proxy."""
    data = load_json_dict(GSC_POPULAR_JSON)
    counts = {}
    for entry in data.get("entries") or []:
        slug = str(entry.get("slug") or "").strip()
        if not slug:
            continue
        try:
            counts[slug] = int(entry.get("clicks") or 0)
        except (TypeError, ValueError):
            counts[slug] = 0
    return counts


_VIEW_COUNTS = _load_view_counts()


def _view_score(slug: str) -> int:
    """Small score bump for candidates with real traffic, capped so it only breaks ties."""
    return min(VIEW_SCORE_CAP, _VIEW_COUNTS.get(slug, 0) // VIEW_SCORE_DIVISOR)


def _score(post_category: str, post_tags: set, candidate: dict) -> int:
    score = CATEGORY_MATCH_WEIGHT if candidate["category"] == post_category else 0
    score += len(post_tags & _tags_for(candidate["title"]))
    score += _view_score(candidate["slug"])
    return score


def related_posts(post: dict, all_posts: list, limit: int = RELATED_POSTS_LIMIT) -> list:
    """Rank `all_posts` by category/tag similarity to `post`, excluding itself.

    Slugs curated in RELATED_POSTS_OVERRIDES are pinned first (in order), with the
    scored ranking filling any remaining slots.
    """
    by_slug = {p["slug"]: p for p in all_posts if p["slug"] != post["slug"]}

    pinned = [
        by_slug[slug]
        for slug in RELATED_POSTS_OVERRIDES.get(post["slug"], [])
        if slug in by_slug
    ]
    pinned_slugs = {p["slug"] for p in pinned}

    post_tags = _tags_for(post["title"])
    candidates = [p for p in by_slug.values() if p["slug"] not in pinned_slugs]
    ranked = sorted(
        candidates,
        key=lambda c: (_score(post["category"], post_tags, c), c["date"]),
        reverse=True,
    )
    return (pinned + ranked)[:limit]
