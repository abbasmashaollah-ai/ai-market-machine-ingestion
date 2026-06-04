from app.features.prices.price_feature_engine import (
    above_moving_average,
    calculate_atr_14d,
    calculate_drawdown_from_high,
    calculate_distance_from_moving_average,
    calculate_high_low_range,
    calculate_liquidity_score,
    calculate_moving_average,
    calculate_moving_average_100d,
    calculate_moving_average_200d,
    calculate_dollar_volume,
    calculate_relative_volume_20d,
    calculate_price_return,
    calculate_price_trend_state,
    calculate_rolling_returns,
    calculate_realized_volatility,
    calculate_return_252d,
    calculate_true_range,
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
    assert calculate_moving_average_100d(list(range(1, 101))) == 50.5
    assert calculate_moving_average_200d(list(range(1, 201))) == 100.5


def test_distance_from_moving_average() -> None:
    assert calculate_distance_from_moving_average(110, 100) == 0.1
    assert above_moving_average(110, 100) is True
    assert above_moving_average(90, 100) is False


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


def test_long_window_return_and_realized_volatility() -> None:
    closes = [float(value) for value in range(100, 353)]
    assert calculate_return_252d(closes) is not None
    assert calculate_realized_volatility(closes, 20) is not None
    assert calculate_realized_volatility(closes, 60) is not None


def test_ohlcv_liquidity_helpers() -> None:
    history = [
        {"high": 11, "low": 9, "close": 10, "volume": 100},
        {"high": 12, "low": 10, "close": 11, "volume": 110},
        {"high": 13, "low": 11, "close": 12, "volume": 120},
        {"high": 14, "low": 12, "close": 13, "volume": 130},
        {"high": 15, "low": 13, "close": 14, "volume": 140},
        {"high": 16, "low": 14, "close": 15, "volume": 150},
        {"high": 17, "low": 15, "close": 16, "volume": 160},
        {"high": 18, "low": 16, "close": 17, "volume": 170},
        {"high": 19, "low": 17, "close": 18, "volume": 180},
        {"high": 20, "low": 18, "close": 19, "volume": 190},
        {"high": 21, "low": 19, "close": 20, "volume": 200},
        {"high": 22, "low": 20, "close": 21, "volume": 210},
        {"high": 23, "low": 21, "close": 22, "volume": 220},
        {"high": 24, "low": 22, "close": 23, "volume": 230},
    ]
    assert calculate_true_range(None, 11, 9, 10) == 2.0
    assert calculate_atr_14d(history) is not None
    assert calculate_dollar_volume(history[-1]) == 23 * 230

    expanded_history = history + [
        {"high": 25, "low": 23, "close": 24, "volume": 240},
        {"high": 26, "low": 24, "close": 25, "volume": 250},
        {"high": 27, "low": 25, "close": 26, "volume": 260},
        {"high": 28, "low": 26, "close": 27, "volume": 270},
        {"high": 29, "low": 27, "close": 28, "volume": 280},
        {"high": 30, "low": 28, "close": 29, "volume": 290},
    ]
    assert calculate_relative_volume_20d(expanded_history) is not None
    assert calculate_liquidity_score(expanded_history) is not None
