"""A8 category → banner mapping for OKPy."""

from app.a8_affiliate import (
    CATEGORY_A8_PROGRAM,
    NEURO_DIVE_A8,
    PRO_JIN_A8,
    a8_banner_context,
)


def test_data_analysis_shows_neuro_dive():
    ctx = a8_banner_context("data-analysis")
    assert ctx["show_a8_banner"] is True
    assert ctx["a8_banner"]["id"] == "neuro_dive"
    assert ctx["a8_banner"]["click_url"] == NEURO_DIVE_A8["click_url"]


def test_ai_models_shows_neuro_dive():
    ctx = a8_banner_context("ai-models")
    assert ctx["a8_banner"]["id"] == "neuro_dive"


def test_eng_comms_shows_pro_jin():
    ctx = a8_banner_context("eng-comms")
    assert ctx["show_a8_banner"] is True
    assert ctx["a8_banner"]["id"] == "pro_jin"
    assert ctx["a8_banner"]["click_url"] == PRO_JIN_A8["click_url"]


def test_fit_journey_shows_pro_jin():
    ctx = a8_banner_context("fit-journey")
    assert ctx["a8_banner"]["id"] == "pro_jin"


def test_python_hidden():
    ctx = a8_banner_context("python")
    assert ctx["show_a8_banner"] is False


def test_disabled_via_env(monkeypatch):
    monkeypatch.setenv("A8_OKPY_ENABLED", "0")
    ctx = a8_banner_context("data-analysis")
    assert ctx["show_a8_banner"] is False


def test_category_map_keys():
    assert CATEGORY_A8_PROGRAM["data-model"] == "neuro_dive"
    assert CATEGORY_A8_PROGRAM["eng-comms"] == "pro_jin"
