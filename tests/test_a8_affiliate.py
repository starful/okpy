"""A8 category → Neuro Dive + @PRO人 (one row)."""

from app.a8_affiliate import (
    A8_CATEGORIES,
    CATEGORY_A8_PROGRAM,
    NEURO_DIVE_A8,
    PRO_JIN_A8,
    a8_banner_context,
)


def test_data_analysis_shows_both():
    ctx = a8_banner_context("data-analysis")
    assert ctx["show_a8_banners"] is True
    assert len(ctx["a8_banners"]) == 2
    assert ctx["a8_banners"][0]["id"] == "neuro_dive"
    assert ctx["a8_banners"][0]["click_url"] == NEURO_DIVE_A8["click_url"]
    assert ctx["a8_banners"][1]["id"] == "pro_jin"
    assert ctx["a8_banners"][1]["click_url"] == PRO_JIN_A8["click_url"]


def test_python_shows_both():
    ctx = a8_banner_context("python")
    assert ctx["show_a8_banners"] is True
    assert [b["id"] for b in ctx["a8_banners"]] == ["neuro_dive", "pro_jin"]


def test_cloud_shows_both():
    ctx = a8_banner_context("cloud")
    assert ctx["show_a8_banners"] is True


def test_eng_comms_shows_both():
    ctx = a8_banner_context("eng-comms")
    assert ctx["show_a8_banners"] is True
    assert ctx["a8_banners"][1]["id"] == "pro_jin"


def test_pmbok_hidden():
    ctx = a8_banner_context("pmbok")
    assert ctx["show_a8_banners"] is False
    assert ctx["show_a8_banner"] is False


def test_disabled_via_env(monkeypatch):
    monkeypatch.setenv("A8_OKPY_ENABLED", "0")
    ctx = a8_banner_context("data-analysis")
    assert ctx["show_a8_banners"] is False


def test_category_map_keys():
    assert "python" in A8_CATEGORIES
    assert "cloud" in A8_CATEGORIES
    assert CATEGORY_A8_PROGRAM["data-model"] == "neuro_dive"
    assert CATEGORY_A8_PROGRAM["eng-comms"] == "pro_jin"
