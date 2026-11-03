"""A8 retired on OKPy; Amazon JP CTA by category."""

import re

import pytest

from app import app
from app.a8_affiliate import A8_CATEGORIES, a8_banner_context
from app.amazon_affiliate import DEFAULT_AMAZON_KEYWORD, amazon_banner_context, amazon_keyword


@pytest.mark.parametrize(
    "category,keyword",
    [
        ("python", "Python 本"),
        ("cloud", "AWS 本"),
        ("terraform", "Terraform 本"),
        ("career", "IT 転職 本"),
        ("data-analysis", DEFAULT_AMAZON_KEYWORD),
        ("", DEFAULT_AMAZON_KEYWORD),
    ],
)
def test_amazon_keyword_by_category(category, keyword):
    assert amazon_keyword(category) == keyword
    ctx = amazon_banner_context(category)
    assert ctx["show_amazon_cta"] is True
    assert "amazon.co.jp/s?k=" in ctx["amazon_cta"]["click_url"]
    assert "tag=starful06-22" in ctx["amazon_cta"]["click_url"]


def test_default_keyword_is_programming_book():
    assert DEFAULT_AMAZON_KEYWORD == "プログラミング 本"


@pytest.mark.parametrize("category", ["python", "cloud", "terraform", "career", "pmbok"])
def test_a8_banner_never_shown(category):
    ctx = a8_banner_context(category)
    assert ctx["show_a8_banners"] is False
    assert ctx["show_a8_banner"] is False
    assert ctx["a8_banners"] == []
    assert not A8_CATEGORIES


def test_disabled_via_env(monkeypatch):
    monkeypatch.setenv("AFFILIATE_OKPY_ENABLED", "0")
    assert amazon_banner_context("python")["show_amazon_cta"] is False


def test_pages_show_amazon_not_a8():
    client = app.test_client()
    for path in ("/category/python", "/category/career", "/category/career/mbti/INTJ"):
        r = client.get(path)
        if r.status_code != 200:
            continue
        html = r.get_data(as_text=True)
        assert "px.a8.net" not in html
        assert "neuro" not in html.lower()
        assert "お名前.com" not in html
        assert "amazon.co.jp/s?k=" in html
    from app import CACHED_POSTS

    py = next(p for p in CACHED_POSTS if p["category"] == "python")
    html = client.get(f"/blog/{py['slug']}").get_data(as_text=True)
    assert "px.a8.net" not in html
    assert re.search(r"amazon\.co\.jp/s\?k=Python%20%E6%9C%AC", html)
