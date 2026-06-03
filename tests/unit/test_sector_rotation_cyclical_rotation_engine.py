from app.features.sector_rotation.cyclical_rotation_engine import (
    calculate_cyclical_leadership_score,
    calculate_growth_leadership_score,
    calculate_risk_on_leadership_score,
)


def test_cyclical_score_uses_cyclical_sectors_only() -> None:
    scores = {"XLY": 0.9, "XLE": 0.7, "XLF": 0.5, "XLI": 0.3, "XLB": 0.1, "XLK": 0.2, "XLP": 0.8}
    score = calculate_cyclical_leadership_score(scores)
    assert score == pytest.approx((0.9 + 0.7 + 0.5 + 0.3 + 0.1) / 5)


def test_growth_score_uses_growth_sectors_only() -> None:
    scores = {"XLK": 0.8, "XLC": 0.6, "XLY": 0.2, "XLP": 0.9}
    score = calculate_growth_leadership_score(scores)
    assert score == pytest.approx((0.8 + 0.6 + 0.2) / 3)


def test_risk_on_score_combines_cyclical_and_growth_groups() -> None:
    scores = {"XLK": 0.8, "XLC": 0.6, "XLY": 0.4, "XLE": 0.2, "XLP": 0.9}
    score = calculate_risk_on_leadership_score(scores)
    assert score == pytest.approx(((0.2 + 0.4) / 2 + (0.8 + 0.6 + 0.4) / 3) / 2)


def test_no_valid_group_returns_none() -> None:
    assert calculate_risk_on_leadership_score({"XLP": 0.9, "XLV": 0.8}) is None
import pytest

