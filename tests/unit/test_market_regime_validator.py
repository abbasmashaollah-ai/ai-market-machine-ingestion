from __future__ import annotations

from app.features.market_regime.market_regime_validator import validate_market_regime_observation, validate_market_regime_observations


def test_market_regime_validator_accepts_valid_row() -> None:
    row = {
        "observation_date": "2026-06-03",
        "source": "market_feature_bundle_summary",
        "market_regime_label": "NEUTRAL_MIXED",
        "price_states_by_symbol": {"AAPL": "UPTREND"},
    }
    result = validate_market_regime_observation(row)
    assert result.is_valid is True
    assert result.errors == ()


def test_market_regime_validator_rejects_invalid_and_duplicate_rows() -> None:
    invalid = {
        "observation_date": "2026-06-03",
        "source": "market_feature_bundle_summary",
        "market_regime_label": "NOT_ALLOWED",
        "price_states_by_symbol": "bad",
    }
    result = validate_market_regime_observation(invalid)
    assert result.is_valid is False
    batch = [dict(invalid), dict(invalid)]
    batch_result = validate_market_regime_observations(batch)
    assert batch_result.is_valid is False

