from __future__ import annotations

from app.features.market_risk.market_risk_validator import validate_market_risk_observation, validate_market_risk_observations


def test_valid_observation_passes() -> None:
    row = {
        "observation_date": "2026-06-03",
        "source": "market_feature_bundle_summary",
        "market_risk_label": "MIXED_MARKET_RISK",
        "volatility_risk_score": 0.0,
        "options_risk_score": 0.0,
        "positioning_risk_score": 0.0,
        "event_risk_score": 0.0,
        "sentiment_risk_score": 0.0,
        "breadth_risk_score": 0.0,
        "macro_liquidity_risk_score": 0.0,
        "composite_market_risk_score": 0.0,
        "price_states_by_symbol": {},
    }
    result = validate_market_risk_observation(row)
    assert result.is_valid


def test_invalid_label_fails() -> None:
    result = validate_market_risk_observation({"observation_date": "2026-06-03", "source": "x", "market_risk_label": "BAD", "price_states_by_symbol": {}})
    assert not result.is_valid


def test_duplicate_batch_key_rejected() -> None:
    row = {
        "observation_date": "2026-06-03",
        "source": "market_feature_bundle_summary",
        "market_risk_label": "MIXED_MARKET_RISK",
        "price_states_by_symbol": {},
    }
    result = validate_market_risk_observations([row, row])
    assert not result.is_valid

