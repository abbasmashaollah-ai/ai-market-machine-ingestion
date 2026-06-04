import json

from app.features.prices.price_feature_builder import build_price_feature_observation
from app.features.prices.price_feature_report import build_price_feature_report
from tests.fixtures.price_ohlcv import build_price_ohlcv_fixtures


def test_report_is_json_friendly_and_has_safety_flags() -> None:
    fixtures = build_price_ohlcv_fixtures()
    close_history = [row["close"] for row in fixtures["MSFT"]]
    observation = build_price_feature_observation("MSFT", close_history, "2026-01-15")
    report = build_price_feature_report(observation)

    json.dumps(report)
    assert report["no_db_writes"] is True
    assert report["no_vendor_calls"] is True
    assert report["no_scheduler_activation"] is True
    assert report["symbol"] == "MSFT"
    assert report["returns"]["return_20d"] is not None
    assert report["dataset_version"] == "price_feature_v2"
    assert report["source_attribution"] == "fixture_ohlcv"
    assert "moving_average_100d" in report["moving_average_context"]
    assert "moving_average_200d" in report["moving_average_context"]
    assert "above_ma_20d" in report["moving_average_context"]
    assert "realized_vol_20d" in report["volatility_context"]
