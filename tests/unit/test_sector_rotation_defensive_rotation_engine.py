from app.features.sector_rotation.defensive_rotation_engine import (
    calculate_defensive_leadership_score,
    calculate_group_leadership_score,
    calculate_rate_sensitive_leadership_score,
)
from app.features.sector_rotation.sector_universe import get_spdr_sector_definitions


def _definitions_by_symbol() -> dict[str, object]:
    return {definition.symbol: definition for definition in get_spdr_sector_definitions()}


def test_defensive_score_uses_defensive_sectors_only() -> None:
    scores = {"XLP": 0.8, "XLV": 0.6, "XLU": 0.4, "XLK": 0.1, "XLF": 0.9}
    score = calculate_defensive_leadership_score(scores)
    assert score == pytest.approx((0.8 + 0.6 + 0.4) / 3)


def test_rate_sensitive_score_uses_rate_sensitive_sectors_only() -> None:
    scores = {"XLE": 0.5, "XLF": 0.7, "XLRE": 0.3, "XLU": 0.1, "XLP": 0.9}
    score = calculate_rate_sensitive_leadership_score(scores)
    assert score == pytest.approx((0.5 + 0.7 + 0.3 + 0.1) / 4)


def test_missing_symbols_are_ignored_and_lowercase_works() -> None:
    definitions = _definitions_by_symbol()
    score = calculate_group_leadership_score({"xlp": 1.0, "missing": 0.5, "XLV": None}, definitions, "is_defensive_sector")
    assert score == pytest.approx(1.0)


def test_no_valid_group_returns_none() -> None:
    assert calculate_defensive_leadership_score({"XLK": 0.9, "XLF": 0.8}) is None
import pytest

