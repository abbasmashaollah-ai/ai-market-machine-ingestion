from __future__ import annotations

from app.features.market_features.market_feature_bundle import run_market_feature_bundle_dry_run
from app.features.market_features.market_feature_bundle_summary import build_market_feature_bundle_summary
from app.features.market_regime.market_regime_builder import build_market_regime_observation


def test_build_market_regime_observation_fields() -> None:
    bundle = run_market_feature_bundle_dry_run("2026-06-03")
    summary = build_market_feature_bundle_summary(bundle)
    observation = build_market_regime_observation(summary, observation_date="2026-06-03")
    assert observation["observation_date"] == "2026-06-03"
    assert observation["source"] == "market_feature_bundle_summary"
    assert observation["market_regime_label"]
    assert observation["evidence"]["source_payload"]["macro_liquidity_state"]
    assert observation["quality_status"] == "PENDING"
    assert observation["certification_status"] == "PENDING"
    assert observation["freshness_status"] == "PENDING"

