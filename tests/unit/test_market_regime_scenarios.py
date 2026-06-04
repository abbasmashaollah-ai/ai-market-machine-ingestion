from __future__ import annotations

from app.features.market_regime.market_regime_builder import build_market_regime_observation


def test_market_regime_scenarios_produce_different_labels() -> None:
    expansion = build_market_regime_observation(
        {
            "observation_date": "2026-06-03",
            "macro_liquidity_state": "STRONG_LIQUIDITY_TAILWIND",
            "market_risk_state": "LOW_MARKET_RISK",
            "breadth_participation_label": "BROAD_PARTICIPATION",
            "sector_rotation_state": "RISK_ON_LEADERSHIP",
            "cross_asset_state": "RISK_ON_CONFIRMATION",
            "volatility_state": "LOW_VOLATILITY",
            "price_states_by_symbol": {"AAPL": "STRONG_UPTREND"},
        },
        observation_date="2026-06-03",
    )
    stress = build_market_regime_observation(
        {
            "observation_date": "2026-06-03",
            "macro_liquidity_state": "STRONG_LIQUIDITY_HEADWIND",
            "market_risk_state": "EXTREME_MARKET_RISK",
            "breadth_participation_label": "DIVERGENT_PARTICIPATION",
            "sector_rotation_state": "DEFENSIVE_LEADERSHIP",
            "cross_asset_state": "RISK_OFF_PRESSURE",
            "volatility_state": "EXTREME_VOLATILITY",
            "price_states_by_symbol": {"AAPL": "STRONG_DOWNTREND"},
        },
        observation_date="2026-06-03",
    )
    assert expansion["market_regime_label"] != stress["market_regime_label"]

