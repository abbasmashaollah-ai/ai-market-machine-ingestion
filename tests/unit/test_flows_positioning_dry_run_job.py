import json

from app.features.flows_positioning.flows_positioning_job import run_flows_positioning_dry_run
from tests.fixtures.flows_positioning_data import build_flows_positioning_payload_scenario


def test_dry_run_produces_report_and_safety_flags() -> None:
    result = run_flows_positioning_dry_run(build_flows_positioning_payload_scenario("risk_off_flows"), "2026-01-15")
    assert result.accepted_count == 1
    assert result.rejected_count == 0
    assert result.reports
    report = result.reports[0]
    assert report["flow_regime_label"]
    assert report["safety_flags"]["no_db_writes"] is True
    assert report["safety_flags"]["no_vendor_calls"] is True
    assert report["safety_flags"]["no_scheduler_activation"] is True
    json.dumps(report)
