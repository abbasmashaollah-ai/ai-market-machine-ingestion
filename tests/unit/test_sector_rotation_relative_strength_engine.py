import pytest

from app.features.sector_rotation.relative_strength_engine import (
    calculate_period_return,
    calculate_relative_strength,
    calculate_relative_strength_map,
    calculate_symbol_returns,
    rank_symbols_by_metric,
)


def test_calculate_period_return_math() -> None:
    assert calculate_period_return(100, 110) == pytest.approx(0.10)
    assert calculate_period_return(50, 25) == pytest.approx(-0.5)


def test_calculate_period_return_invalid_inputs_return_none() -> None:
    assert calculate_period_return(None, 110) is None
    assert calculate_period_return(0, 110) is None
    assert calculate_period_return(100, None) is None


def test_calculate_symbol_returns_with_insufficient_history_returns_none() -> None:
    returns = calculate_symbol_returns([100], windows=(1, 5))
    assert returns == {1: None, 5: None}


def test_calculate_symbol_returns_by_window() -> None:
    returns = calculate_symbol_returns([100, 105, 110, 121], windows=(1, 3))
    assert returns[1] == pytest.approx((121 / 110) - 1)
    assert returns[3] == pytest.approx((121 / 100) - 1)


def test_relative_strength_subtraction_and_map() -> None:
    assert calculate_relative_strength(0.08, 0.05) == pytest.approx(0.03)
    assert calculate_relative_strength(None, 0.05) is None

    rel_map = calculate_relative_strength_map(
        {
            "XLK": {5: 0.08, 20: 0.12},
            "XLP": {5: 0.03, 20: 0.04},
        },
        {5: 0.05, 20: 0.10},
    )
    assert rel_map == {
        "XLK": {5: pytest.approx(0.03), 20: pytest.approx(0.02)},
        "XLP": {5: pytest.approx(-0.02), 20: pytest.approx(-0.06)},
    }


def test_rank_symbols_by_metric_is_deterministic_with_alphabetical_tie_break() -> None:
    ranked = rank_symbols_by_metric({"XLF": 0.2, "XLK": 0.2, "XLP": 0.1, "XLE": None})
    assert ranked == ["XLF", "XLK", "XLP"]

    ranked_ascending = rank_symbols_by_metric({"B": 2.0, "A": 2.0, "C": 1.0}, descending=False)
    assert ranked_ascending == ["C", "A", "B"]

