from __future__ import annotations

from app.features.market_risk.market_risk_engine import (
    calculate_composite_market_risk_score,
    determine_market_risk_label,
    map_breadth_participation_to_score,
    map_event_calendar_state_to_score,
    map_flows_positioning_state_to_score,
    map_macro_liquidity_state_to_score,
    map_news_sentiment_state_to_score,
    map_options_state_to_score,
    map_volatility_state_to_score,
)


def test_state_to_score_mappers() -> None:
    assert map_volatility_state_to_score("high_volatility") == 0.8
    assert map_options_state_to_score("hedging_pressure") == 0.6
    assert map_flows_positioning_state_to_score("tight_flow_conditions") == 0.8
    assert map_event_calendar_state_to_score("high_event_risk") == 0.75
    assert map_news_sentiment_state_to_score("negative_sentiment") == 0.6
    assert map_breadth_participation_to_score("narrow_participation") == 0.5
    assert map_macro_liquidity_state_to_score("liquidity_headwind") == 0.6


def test_composite_score_and_labels() -> None:
    scores = {
        "volatility_risk_score": 0.8,
        "options_risk_score": 0.6,
        "positioning_risk_score": 0.8,
        "event_risk_score": 0.75,
        "sentiment_risk_score": 0.6,
        "breadth_risk_score": 0.5,
        "macro_liquidity_risk_score": 0.6,
    }
    composite = calculate_composite_market_risk_score(scores)
    assert composite is not None
    assert determine_market_risk_label(composite, scores) in {"HIGH_MARKET_RISK", "EXTREME_MARKET_RISK"}
    assert determine_market_risk_label(-0.7, scores) == "LOW_MARKET_RISK"
    assert determine_market_risk_label(0.0, {}) == "MIXED_MARKET_RISK"

