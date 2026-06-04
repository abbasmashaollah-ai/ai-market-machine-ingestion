from __future__ import annotations

from app.features.macro_liquidity.macro_liquidity_builder import build_macro_liquidity_observation
from app.features.market_features.market_feature_bundle import run_market_feature_bundle_dry_run
from app.features.market_features.market_feature_bundle_summary import build_market_feature_bundle_summary
from app.features.market_risk.market_risk_report import build_market_risk_report


def test_report_includes_safety_flags_and_scores() -> None:
    summary = build_market_feature_bundle_summary(run_market_feature_bundle_dry_run("2026-06-03"))
    summary["macro_liquidity_state"] = "LIQUIDITY_TAILWIND"
    observation = build_macro_liquidity_observation(summary, observation_date="2026-06-03")
    # reuse macro_liquidity observation to seed a stable summary-like structure
    market_risk_observation = {
        "observation_date": observation["observation_date"],
        "timestamp": observation["timestamp"],
        "volatility_state": summary["volatility_state"],
        "options_state": "MIXED_OPTIONS",
        "flows_positioning_state": summary["flows_positioning_state"],
        "event_calendar_state": summary["event_calendar_state"],
        "news_sentiment_state": summary["news_sentiment_state"],
        "breadth_participation_label": summary["breadth_participation_label"],
        "macro_liquidity_state": summary["macro_liquidity_state"],
        "price_states_by_symbol": summary["price_states_by_symbol"],
        "volatility_risk_score": 0.0,
        "options_risk_score": 0.0,
        "positioning_risk_score": 0.0,
        "event_risk_score": 0.0,
        "sentiment_risk_score": 0.0,
        "breadth_risk_score": 0.0,
        "macro_liquidity_risk_score": 0.0,
        "composite_market_risk_score": 0.0,
        "market_risk_label": "MIXED_MARKET_RISK",
        "source": "market_feature_bundle_summary",
        "quality_status": "PENDING",
        "certification_status": "PENDING",
        "freshness_status": "PENDING",
        "lineage": {},
        "evidence": {},
    }
    report = build_market_risk_report(market_risk_observation)
    assert report["market_risk_label"] == "MIXED_MARKET_RISK"
    assert report["no_db_writes"] is True
    assert report["no_vendor_calls"] is True
    assert report["no_scheduler_activation"] is True

