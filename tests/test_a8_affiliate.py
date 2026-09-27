"""A8 category → career banners or お名前.com."""

from app.a8_affiliate import (
    A8_CATEGORIES,
    CATEGORY_A8_PROGRAM,
    NEURO_DIVE_A8,
    ONAMAE_A8,
    a8_banner_context,
)


def test_data_analysis_hidden():
    ctx = a8_banner_context("data-analysis")
    assert ctx["show_a8_banners"] is False
    assert ctx["show_a8_banner"] is False


def test_python_shows_onamae():
    ctx = a8_banner_context("python")
    assert ctx["show_a8_banners"] is True
    assert [b["id"] for b in ctx["a8_banners"]] == ["onamae"]
    assert ctx["a8_banners"][0]["click_url"] == ONAMAE_A8["click_url"]
    assert "2TT6RM" in ctx["a8_banners"][0]["click_url"]


def test_cloud_shows_onamae():
    ctx = a8_banner_context("cloud")
    assert ctx["show_a8_banners"] is True
    assert [b["id"] for b in ctx["a8_banners"]] == ["onamae"]


def test_terraform_shows_onamae():
    ctx = a8_banner_context("terraform")
    assert ctx["show_a8_banners"] is True
    assert [b["id"] for b in ctx["a8_banners"]] == ["onamae"]


def test_eng_comms_hidden():
    ctx = a8_banner_context("eng-comms")
    assert ctx["show_a8_banners"] is False


def test_pmbok_hidden():
    ctx = a8_banner_context("pmbok")
    assert ctx["show_a8_banners"] is False
    assert ctx["show_a8_banner"] is False


def test_disabled_via_env(monkeypatch):
    monkeypatch.setenv("A8_OKPY_ENABLED", "0")
    ctx = a8_banner_context("career")
    assert ctx["show_a8_banners"] is False


def test_category_map_keys():
    assert "python" in A8_CATEGORIES
    assert "cloud" in A8_CATEGORIES
    assert "career" in A8_CATEGORIES
    assert "data-analysis" not in A8_CATEGORIES
    assert CATEGORY_A8_PROGRAM["career"] == "neuro_dive"
    assert CATEGORY_A8_PROGRAM["python"] == "onamae"
    assert CATEGORY_A8_PROGRAM["cloud"] == "onamae"
    assert CATEGORY_A8_PROGRAM["terraform"] == "onamae"


def test_career_shows_neuro_dive_only():
    ctx = a8_banner_context("career")
    assert ctx["show_a8_banners"] is True
    assert [b["id"] for b in ctx["a8_banners"]] == ["neuro_dive"]
    assert ctx["a8_banners"][0]["click_url"] == NEURO_DIVE_A8["click_url"]
