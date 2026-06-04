from __future__ import annotations

from app.features.macro_liquidity.macro_liquidity_engine import (
    calculate_composite_macro_liquidity_score,
    determine_macro_liquidity_label,
    map_breadth_participation_to_score,
    map_cross_asset_state_to_score,
    map_flows_positioning_state_to_score,
    map_liquidity_rates_state_to_score,
    map_sector_rotation_state_to_score,
    map_volatility_state_to_score,
)


def test_state_to_score_mappers() -> None:
    assert map_liquidity_rates_state_to_score("liquidity_tailwind") == 0.75
    assert map_liquidity_rates_state_to_score("strong_liquidity_headwind") == -1.0
    assert map_cross_asset_state_to_score("risk_on_evidence") == 0.75
    assert map_flows_positioning_state_to_score("mixed_positioning") == 0.0
    assert map_volatility_state_to_score("high_volatility") == -0.75
    assert map_breadth_participation_to_score("broad_participation") == 1.0
    assert map_sector_rotation_state_to_score("risk_off_evidence") == -0.75


def test_composite_score_and_labels() -> None:
    scores = {
        "rates_liquidity_pressure_score": 0.75,
        "cross_asset_confirmation_score": 0.75,
        "positioning_liquidity_score": 0.5,
        "volatility_liquidity_stress_score": -0.25,
        "participation_confirmation_score": 0.75,
        "sector_rotation_confirmation_score": 0.75,
    }
    composite = calculate_composite_macro_liquidity_score(scores)
    assert composite is not None
    assert determine_macro_liquidity_label(composite, scores) in {
        "STRONG_LIQUIDITY_TAILWIND",
        "LIQUIDITY_TAILWIND",
    }
    assert determine_macro_liquidity_label(-0.8, scores) == "STRONG_LIQUIDITY_HEADWIND"
    assert determine_macro_liquidity_label(0.0, {}) == "MIXED_MACRO_LIQUIDITY"

