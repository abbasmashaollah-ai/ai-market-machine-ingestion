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
        "moving_average_20d",
        "moving_average_50d",
        "distance_from_ma_20d",
        "distance_from_ma_50d",
        "drawdown_from_20d_high",
        "drawdown_from_60d_high",
        "high_low_range_20d",
        "high_low_range_60d",
        "price_trend_state",
        "source",
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


def test_observation_is_json_friendly_and_uses_metadata_defaults() -> None:
    observation = build_price_feature_observation("AAPL", [100, 101, 102, 103, 104, 105], "2026-01-15")
    json.dumps(observation)
    assert observation["lineage"] == {}
    assert observation["evidence"] == {}


def test_no_db_vendor_or_live_api_behavior() -> None:
    observation = build_price_feature_observation("MSFT", [100, 101, 102, 103, 104, 105], "2026-01-15")
    assert observation["source"] == "fixture_ohlcv"
    assert "writer" not in observation
    assert "vendor" not in observation
