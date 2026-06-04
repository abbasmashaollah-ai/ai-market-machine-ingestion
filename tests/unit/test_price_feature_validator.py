from copy import deepcopy

from app.features.prices.price_feature_builder import build_price_feature_observation
from app.features.prices.price_feature_validator import validate_price_feature_observation, validate_price_feature_observations
from tests.fixtures.price_ohlcv import build_price_ohlcv_fixtures


def test_valid_observation_passes_validation() -> None:
    fixtures = build_price_ohlcv_fixtures()
    observation = build_price_feature_observation("SPY", [row["close"] for row in fixtures["SPY"]], "2026-01-15")

    result = validate_price_feature_observation(observation)

    assert result.is_valid is True
    assert result.errors == ()


def test_missing_required_field_fails_validation() -> None:
    observation = build_price_feature_observation("AAPL", [100, 101, 102, 103, 104, 105], "2026-01-15")
    observation = dict(observation)
    observation.pop("source")

    result = validate_price_feature_observation(observation)

    assert result.is_valid is False
    assert any(error.field_name == "source" for error in result.errors)


def test_invalid_latest_close_fails_validation() -> None:
    observation = build_price_feature_observation("MSFT", [100, 101, 102, 103, 104, 105], "2026-01-15")
    observation = dict(observation)
    observation["latest_close"] = -1

    result = validate_price_feature_observation(observation)

    assert result.is_valid is False
    assert any(error.field_name == "latest_close" for error in result.errors)


def test_invalid_trend_state_fails_validation() -> None:
    observation = build_price_feature_observation("MSFT", [100, 101, 102, 103, 104, 105], "2026-01-15")
    observation = dict(observation)
    observation["price_trend_state"] = "BUY_NOW"

    result = validate_price_feature_observation(observation)

    assert result.is_valid is False
    assert any(error.field_name == "price_trend_state" for error in result.errors)


def test_missing_metadata_fields_fail_validation() -> None:
    observation = build_price_feature_observation("MSFT", [100, 101, 102, 103, 104, 105], "2026-01-15")
    observation = dict(observation)
    observation.pop("dataset_version")
    observation.pop("source_attribution")

    result = validate_price_feature_observation(observation)

    assert result.is_valid is False
    assert any(error.field_name == "dataset_version" for error in result.errors)
    assert any(error.field_name == "source_attribution" for error in result.errors)


def test_duplicate_batch_key_fails_validation() -> None:
    fixtures = build_price_ohlcv_fixtures()
    rows = [
        build_price_feature_observation("SPY", [row["close"] for row in fixtures["SPY"]], "2026-01-15"),
        build_price_feature_observation("SPY", [row["close"] for row in fixtures["SPY"]], "2026-01-15"),
    ]

    results = validate_price_feature_observations(rows)

    assert results[0].is_valid is True
    assert results[1].is_valid is False
    assert any(error.field_name == "batch_key" for error in results[1].errors)
