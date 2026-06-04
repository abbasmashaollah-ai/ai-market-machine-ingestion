from __future__ import annotations

from app.features.market_features.market_feature_bundle import run_market_feature_bundle_dry_run
from app.features.market_features.market_feature_bundle_summary import build_market_feature_bundle_summary
from app.features.market_risk.market_risk_builder import build_market_risk_observation


def test_summaries_produce_different_market_risk_labels() -> None:
    bundle = run_market_feature_bundle_dry_run("2026-06-03")
    summary = build_market_feature_bundle_summary(bundle)
    strong_observation = build_market_risk_observation(summary, observation_date="2026-06-03")

    weak_summary = dict(summary)
    weak_summary["volatility_state"] = "EXTREME_VOLATILITY"
    weak_summary["options_state"] = "HEDGING_PRESSURE"
    weak_summary["flows_positioning_state"] = "TIGHT_FLOW_CONDITIONS"
    weak_summary["event_calendar_state"] = "HIGH_EVENT_RISK"
    weak_summary["news_sentiment_state"] = "NEGATIVE_SENTIMENT"
    weak_summary["breadth_participation_label"] = "NARROW_PARTICIPATION"
    weak_summary["macro_liquidity_state"] = "STRONG_LIQUIDITY_HEADWIND"
    weak_observation = build_market_risk_observation(weak_summary, observation_date="2026-06-03")

    assert strong_observation["market_risk_label"] in {"MIXED_MARKET_RISK", "LOW_MARKET_RISK", "NORMAL_MARKET_RISK", "ELEVATED_MARKET_RISK", "HIGH_MARKET_RISK", "EXTREME_MARKET_RISK"}
    assert weak_observation["market_risk_label"] in {"HIGH_MARKET_RISK", "EXTREME_MARKET_RISK"}

