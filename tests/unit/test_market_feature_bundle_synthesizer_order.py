from __future__ import annotations

from app.features.market_features.market_feature_bundle import run_market_feature_bundle_dry_run
from app.features.market_features.market_feature_bundle_summary import build_market_feature_bundle_summary


def test_market_feature_bundle_synthesizer_order_and_no_circular_dependency() -> None:
    bundle = run_market_feature_bundle_dry_run("2026-06-03")

    assert bundle["macro_liquidity"]["report"]["macro_liquidity_label"]
    assert bundle["market_risk"]["report"]["market_risk_label"]
    assert bundle["market_regime"]["report"]["market_regime_label"]

    macro_payload = bundle["macro_liquidity"]["report"]["evidence"]["source_payload"]
    assert not macro_payload.get("market_risk_state")
    assert not macro_payload.get("market_regime_state")

    market_risk_payload = bundle["market_risk"]["report"]["evidence"]["source_payload"]
    assert market_risk_payload["macro_liquidity_state"]
    assert not market_risk_payload.get("market_regime_state")

    market_regime_payload = bundle["market_regime"]["report"]["evidence"]["source_payload"]
    assert market_regime_payload["macro_liquidity_state"]
    assert market_regime_payload["market_risk_state"]

    summary = build_market_feature_bundle_summary(bundle)
    assert summary["macro_liquidity_state"]
    assert summary["market_risk_state"]
    assert summary["market_regime_state"]
    assert summary["total_warnings"] == 0
    for flag_value in summary["safety_flags"].values():
        assert flag_value is True
