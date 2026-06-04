from __future__ import annotations

from app.features.market_features.market_feature_bundle import run_market_feature_bundle_dry_run
from app.features.market_features.market_feature_bundle_summary import build_market_feature_bundle_summary
from app.features.macro_liquidity.macro_liquidity_builder import build_macro_liquidity_observation


def test_summaries_produce_different_macro_labels() -> None:
    strong_bundle = run_market_feature_bundle_dry_run("2026-06-03")
    strong_summary = build_market_feature_bundle_summary(strong_bundle)
    strong_observation = build_macro_liquidity_observation(strong_summary, observation_date="2026-06-03")

    weak_summary = dict(strong_summary)
    weak_summary["liquidity_rates_state"] = "STRONG_LIQUIDITY_HEADWIND"
    weak_summary["cross_asset_state"] = "RISK_OFF_EVIDENCE"
    weak_summary["flows_positioning_state"] = "TIGHT_FLOW_CONDITIONS"
    weak_summary["volatility_state"] = "HIGH_VOLATILITY"
    weak_summary["breadth_participation_label"] = "NARROW_PARTICIPATION"
    weak_summary["sector_rotation_state"] = "RISK_OFF_EVIDENCE"
    weak_observation = build_macro_liquidity_observation(weak_summary, observation_date="2026-06-03")

    assert strong_observation["macro_liquidity_label"] in {"LIQUIDITY_TAILWIND", "STRONG_LIQUIDITY_TAILWIND", "MIXED_MACRO_LIQUIDITY"}
    assert weak_observation["macro_liquidity_label"] in {"LIQUIDITY_HEADWIND", "STRONG_LIQUIDITY_HEADWIND"}

