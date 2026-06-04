import json

from app.features.options.options_job import run_options_dry_run
from tests.fixtures.options_data import build_options_metrics_scenario


def test_dry_run_produces_report_and_safety_flags() -> None:
    result = run_options_dry_run(build_options_metrics_scenario("high_volatility")["NVDA"], "2026-01-15")
    assert result.accepted_count == 1
    assert result.rejected_count == 0
    assert result.reports
    report = result.reports[0]
    assert report["options_regime_label"]
    assert report["safety_flags"]["no_db_writes"] is True
    assert report["safety_flags"]["no_vendor_calls"] is True
    assert report["safety_flags"]["no_scheduler_activation"] is True
    json.dumps(report)
