from __future__ import annotations

from app.features.macro_liquidity.macro_liquidity_report import build_macro_liquidity_report


def test_report_includes_safety_flags_and_scores() -> None:
    observation = {
        "observation_date": "2026-06-03",
        "timestamp": "2026-06-03T00:00:00Z",
        "liquidity_rates_state": "LIQUIDITY_TAILWIND",
        "cross_asset_state": "RISK_ON_EVIDENCE",
        "flows_positioning_state": "MIXED_POSITIONING",
        "volatility_state": "MIXED_VOLATILITY",
        "breadth_participation_label": "BROAD_PARTICIPATION",
        "sector_rotation_state": "RISK_ON_EVIDENCE",
        "rates_liquidity_pressure_score": 0.75,
        "cross_asset_confirmation_score": 0.75,
        "positioning_liquidity_score": 0.0,
        "volatility_liquidity_stress_score": 0.0,
        "participation_confirmation_score": 1.0,
        "composite_macro_liquidity_score": 0.5,
        "macro_liquidity_label": "LIQUIDITY_TAILWIND",
        "source": "market_feature_bundle_summary",
        "quality_status": "PENDING",
        "certification_status": "PENDING",
        "freshness_status": "PENDING",
        "lineage": {},
        "evidence": {},
    }
    report = build_macro_liquidity_report(observation)
    assert report["macro_liquidity_label"] == "LIQUIDITY_TAILWIND"
    assert report["no_db_writes"] is True
    assert report["no_vendor_calls"] is True
    assert report["no_scheduler_activation"] is True

