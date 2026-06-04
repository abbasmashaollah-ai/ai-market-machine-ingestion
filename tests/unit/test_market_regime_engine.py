from __future__ import annotations

from app.features.market_regime.market_regime_engine import (
    calculate_composite_market_regime_score,
    determine_market_regime_label,
    map_breadth_participation_to_score,
    map_cross_asset_state_to_score,
    map_macro_liquidity_state_to_score,
    map_market_risk_state_to_score,
    map_price_states_to_trend_score,
    map_sector_rotation_state_to_score,
    map_volatility_state_to_score,
)


def test_market_regime_state_mappers_and_labels() -> None:
    assert map_macro_liquidity_state_to_score("LIQUIDITY_TAILWIND") > 0
    assert map_market_risk_state_to_score("LOW_MARKET_RISK") > 0
    assert map_breadth_participation_to_score("BROAD_PARTICIPATION") > 0
    assert map_sector_rotation_state_to_score("RISK_ON_LEADERSHIP") > 0
    assert map_cross_asset_state_to_score("RISK_ON_CONFIRMATION") > 0
    assert map_volatility_state_to_score("LOW_VOLATILITY") > 0
    assert map_price_states_to_trend_score({"AAPL": "UPTREND", "MSFT": "STRONG_UPTREND"}) > 0
    score = calculate_composite_market_regime_score(
        {
            "liquidity_regime_score": 0.5,
            "risk_regime_score": 0.5,
            "participation_regime_score": 0.5,
            "rotation_regime_score": 0.5,
            "cross_asset_regime_score": 0.5,
            "trend_regime_score": 0.5,
            "volatility_regime_score": 0.5,
        }
    )
    assert score == 0.5
    assert determine_market_regime_label(score, None) == "RISK_ON_FRAGILE"

