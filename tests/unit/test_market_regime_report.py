from __future__ import annotations

from app.features.market_regime.market_regime_report import build_market_regime_report


def test_market_regime_report_fields() -> None:
    observation = {
        "observation_date": "2026-06-03",
        "timestamp": "2026-06-03T00:00:00Z",
        "macro_liquidity_state": "MIXED_MACRO_LIQUIDITY",
        "market_risk_state": "MIXED_MARKET_RISK",
        "breadth_participation_label": "BROAD_PARTICIPATION",
        "sector_rotation_state": "BROAD_IMPROVEMENT",
        "cross_asset_state": "MIXED_INTERMARKET",
        "volatility_state": "MIXED_VOLATILITY",
        "price_states_by_symbol": {"AAPL": "UPTREND"},
        "liquidity_regime_score": 0.0,
        "risk_regime_score": 0.0,
        "participation_regime_score": 0.0,
        "rotation_regime_score": 0.5,
        "cross_asset_regime_score": 0.0,
        "trend_regime_score": 0.5,
        "volatility_regime_score": 0.0,
        "composite_market_regime_score": 0.14,
        "market_regime_label": "NEUTRAL_MIXED",
        "source": "market_feature_bundle_summary",
        "quality_status": "PENDING",
        "certification_status": "PENDING",
        "freshness_status": "PENDING",
        "lineage": {},
        "evidence": {},
    }
    report = build_market_regime_report(observation)
    assert report["market_regime_label"] == "NEUTRAL_MIXED"
    assert report["no_db_writes"] is True
    assert report["no_vendor_calls"] is True
    assert report["no_scheduler_activation"] is True

