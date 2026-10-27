"""Related-post recommendations by category/tag similarity.

Posts carry no explicit tags field, so the Hatena tag/keyword hints in
blog_categories.py double as a lightweight tag vocabulary, combined with
title keyword overlap to tell apart posts within the same category.
"""

import re

try:
    from .blog_categories import (
        CLOUD_TAGS,
        CLOUD_TITLE_KEYWORDS,
        HATENA_TAG_PRIORITY,
        TERRAFORM_TAGS,
        TERRAFORM_TITLE_KEYWORDS,
    )
except ImportError:
    from blog_categories import (
        CLOUD_TAGS,
        CLOUD_TITLE_KEYWORDS,
        HATENA_TAG_PRIORITY,
        TERRAFORM_TAGS,
        TERRAFORM_TITLE_KEYWORDS,
    )

RELATED_POSTS_LIMIT = 3

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


def _score(post_category: str, post_tags: set, candidate: dict) -> int:
    score = 10 if candidate["category"] == post_category else 0
    score += len(post_tags & _tags_for(candidate["title"]))
    return score


def related_posts(post: dict, all_posts: list, limit: int = RELATED_POSTS_LIMIT) -> list:
    """Rank `all_posts` by category/tag similarity to `post`, excluding itself."""
    post_tags = _tags_for(post["title"])
    candidates = [p for p in all_posts if p["slug"] != post["slug"]]
    ranked = sorted(
        candidates,
        key=lambda c: (_score(post["category"], post_tags, c), c["date"]),
        reverse=True,
    )
    return ranked[:limit]
