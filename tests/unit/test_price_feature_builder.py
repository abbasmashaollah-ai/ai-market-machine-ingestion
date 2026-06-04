import json

from app.features.prices.price_feature_builder import build_price_feature_observation
from tests.fixtures.price_ohlcv import build_price_ohlcv_fixtures


def test_observation_includes_expected_fields() -> None:
    fixtures = build_price_ohlcv_fixtures()
    close_history = [row["close"] for row in fixtures["SPY"]]
    observation = build_price_feature_observation("spy", close_history, "2026-01-15")

    expected_fields = {
        "symbol",
        "observation_date",
        "timestamp",
        "latest_close",
        "return_1d",
        "return_5d",
        "return_20d",
        "return_60d",
        "return_252d",
        "moving_average_20d",
        "moving_average_50d",
        "moving_average_100d",
        "moving_average_200d",
        "distance_from_ma_20d",
        "distance_from_ma_50d",
        "above_ma_20d",
        "above_ma_50d",
        "above_ma_100d",
        "above_ma_200d",
        "realized_vol_20d",
        "realized_vol_60d",
        "atr_14d",
        "dollar_volume",
        "average_dollar_volume_20d",
        "relative_volume_20d",
        "liquidity_score",
        "drawdown_from_20d_high",
        "drawdown_from_60d_high",
        "high_low_range_20d",
        "high_low_range_60d",
        "price_trend_state",
        "source",
        "dataset_version",
        "source_attribution",
        "quality_status",
        "certification_status",
        "freshness_status",
        "lineage",
        "evidence",
    }
    assert set(observation) == expected_fields
    assert observation["symbol"] == "SPY"
    assert observation["quality_status"] == "PENDING"
    assert observation["certification_status"] == "PENDING"
    assert observation["freshness_status"] == "PENDING"
    assert observation["dataset_version"] == "price_feature_v2"
    assert observation["source_attribution"] == "fixture_ohlcv"


def test_observation_is_json_friendly_and_uses_metadata_defaults() -> None:
    observation = build_price_feature_observation("AAPL", [100, 101, 102, 103, 104, 105], "2026-01-15")
    json.dumps(observation)
    assert observation["lineage"] == {}
    assert observation["evidence"] == {}
    assert observation["atr_14d"] is None
    assert observation["dollar_volume"] is None
    assert observation["average_dollar_volume_20d"] is None
    assert observation["relative_volume_20d"] is None
    assert observation["liquidity_score"] is None


def test_no_db_vendor_or_live_api_behavior() -> None:
    observation = build_price_feature_observation("MSFT", [100, 101, 102, 103, 104, 105], "2026-01-15")
    assert observation["source"] == "fixture_ohlcv"
    assert "writer" not in observation
    assert "vendor" not in observation


def test_compatibility_wrapper_imports_builder() -> None:
    from app.features.prices.price_feature_builder import build_price_feature_observation as wrapper

    observation = wrapper("MSFT", [100, 101, 102, 103, 104, 105], "2026-01-15")
    assert observation["symbol"] == "MSFT"


def test_ohlcv_observation_includes_liquidity_fields() -> None:
    history = [
        {"date": "2026-01-01", "open": 100, "high": 101, "low": 99, "close": 100, "volume": 1000},
        {"date": "2026-01-02", "open": 100, "high": 102, "low": 99, "close": 101, "volume": 1100},
        {"date": "2026-01-03", "open": 101, "high": 103, "low": 100, "close": 102, "volume": 1200},
        {"date": "2026-01-04", "open": 102, "high": 104, "low": 101, "close": 103, "volume": 1300},
        {"date": "2026-01-05", "open": 103, "high": 105, "low": 102, "close": 104, "volume": 1400},
        {"date": "2026-01-06", "open": 104, "high": 106, "low": 103, "close": 105, "volume": 1500},
        {"date": "2026-01-07", "open": 105, "high": 107, "low": 104, "close": 106, "volume": 1600},
        {"date": "2026-01-08", "open": 106, "high": 108, "low": 105, "close": 107, "volume": 1700},
        {"date": "2026-01-09", "open": 107, "high": 109, "low": 106, "close": 108, "volume": 1800},
        {"date": "2026-01-10", "open": 108, "high": 110, "low": 107, "close": 109, "volume": 1900},
        {"date": "2026-01-11", "open": 109, "high": 111, "low": 108, "close": 110, "volume": 2000},
        {"date": "2026-01-12", "open": 110, "high": 112, "low": 109, "close": 111, "volume": 2100},
        {"date": "2026-01-13", "open": 111, "high": 113, "low": 110, "close": 112, "volume": 2200},
        {"date": "2026-01-14", "open": 112, "high": 114, "low": 111, "close": 113, "volume": 2300},
        {"date": "2026-01-15", "open": 113, "high": 115, "low": 112, "close": 114, "volume": 2400},
        {"date": "2026-01-16", "open": 114, "high": 116, "low": 113, "close": 115, "volume": 2500},
        {"date": "2026-01-17", "open": 115, "high": 117, "low": 114, "close": 116, "volume": 2600},
        {"date": "2026-01-18", "open": 116, "high": 118, "low": 115, "close": 117, "volume": 2700},
        {"date": "2026-01-19", "open": 117, "high": 119, "low": 116, "close": 118, "volume": 2800},
        {"date": "2026-01-20", "open": 118, "high": 120, "low": 117, "close": 119, "volume": 2900},
        {"date": "2026-01-21", "open": 119, "high": 121, "low": 118, "close": 120, "volume": 3000},
        {"date": "2026-01-22", "open": 120, "high": 122, "low": 119, "close": 121, "volume": 3100},
        {"date": "2026-01-23", "open": 121, "high": 123, "low": 120, "close": 122, "volume": 3200},
        {"date": "2026-01-24", "open": 122, "high": 124, "low": 121, "close": 123, "volume": 3300},
        {"date": "2026-01-25", "open": 123, "high": 125, "low": 122, "close": 124, "volume": 3400},
    ]
    observation = build_price_feature_observation("NVDA", history, "2026-01-25")
    assert observation["atr_14d"] is not None
    assert observation["dollar_volume"] == 124 * 3400
    assert observation["average_dollar_volume_20d"] is not None
    assert observation["relative_volume_20d"] is not None
    assert observation["liquidity_score"] is not None
    assert observation["source_attribution"] == "fixture_ohlcv"
