from __future__ import annotations

from app.features.macro_liquidity.macro_liquidity_validator import validate_macro_liquidity_observation, validate_macro_liquidity_observations


def test_valid_observation_passes() -> None:
    row = {
        "observation_date": "2026-06-03",
        "source": "market_feature_bundle_summary",
        "macro_liquidity_label": "MIXED_MACRO_LIQUIDITY",
        "rates_liquidity_pressure_score": 0.0,
        "cross_asset_confirmation_score": 0.0,
        "positioning_liquidity_score": 0.0,
        "volatility_liquidity_stress_score": 0.0,
        "participation_confirmation_score": 0.0,
        "composite_macro_liquidity_score": 0.0,
    }
    result = validate_macro_liquidity_observation(row)
    assert result.is_valid


def test_invalid_label_fails() -> None:
    result = validate_macro_liquidity_observation({"observation_date": "2026-06-03", "source": "x", "macro_liquidity_label": "BAD"})
    assert not result.is_valid


def test_duplicate_batch_key_rejected() -> None:
    row = {
        "observation_date": "2026-06-03",
        "source": "market_feature_bundle_summary",
        "macro_liquidity_label": "MIXED_MACRO_LIQUIDITY",
    }
    result = validate_macro_liquidity_observations([row, row])
    assert not result.is_valid

