from app.features.prices.price_feature_engine import (
    calculate_drawdown_from_high,
    calculate_distance_from_moving_average,
    calculate_high_low_range,
    calculate_moving_average,
    calculate_price_return,
    calculate_price_trend_state,
    calculate_rolling_returns,
)


def test_return_math() -> None:
    assert calculate_price_return(100, 110) == 0.1


def test_insufficient_history_returns_none() -> None:
    assert calculate_rolling_returns([100], windows=(1, 5))[1] is None
    assert calculate_moving_average([100], 20) is None
    assert calculate_high_low_range([100], 20) is None
    assert calculate_drawdown_from_high([100], 20) is None


def test_moving_average_math() -> None:
    assert calculate_moving_average([1, 2, 3, 4, 5], 5) == 3.0


def test_distance_from_moving_average() -> None:
    assert calculate_distance_from_moving_average(110, 100) == 0.1


def test_high_low_range_and_drawdown() -> None:
    assert calculate_high_low_range([10, 12, 11, 15], 4) == 0.5
    assert calculate_drawdown_from_high([10, 12, 11, 15], 4) == (15 - 15) / 15


def test_trend_state_labels() -> None:
    assert calculate_price_trend_state({1: 0.02, 5: 0.03, 20: 0.04, 60: 0.05}, 0.02, 0.03) == "STRONG_UPTREND"
    assert calculate_price_trend_state({1: -0.02, 5: -0.03, 20: -0.04, 60: -0.05}, -0.02, -0.03) == "STRONG_DOWNTREND"
    assert calculate_price_trend_state({20: 0.01, 60: 0.02}, 0.01, 0.01) == "UPTREND"
    assert calculate_price_trend_state({20: -0.01, 60: -0.02}, -0.01, -0.01) == "DOWNTREND"
    assert calculate_price_trend_state({20: 0.01, 60: -0.02}, 0.01, -0.01) == "MIXED"
    assert calculate_price_trend_state({}, None, None) == "INSUFFICIENT_DATA"
