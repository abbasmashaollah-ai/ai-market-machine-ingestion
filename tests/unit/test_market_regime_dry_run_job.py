from __future__ import annotations

from app.features.market_features.market_feature_bundle import run_market_feature_bundle_dry_run
from app.features.market_features.market_feature_bundle_summary import build_market_feature_bundle_summary
from app.features.market_regime.market_regime_job import run_market_regime_dry_run


def test_dry_run_consumes_bundle_summary() -> None:
    bundle = run_market_feature_bundle_dry_run("2026-06-03")
    summary = build_market_feature_bundle_summary(bundle)
    result = run_market_regime_dry_run(summary, observation_date="2026-06-03")
    assert result.accepted_count == 1
    assert result.rejected_count == 0
    assert len(result.reports) == 1
    assert result.no_db_writes is True
    assert result.no_vendor_calls is True
    assert result.no_scheduler_activation is True

