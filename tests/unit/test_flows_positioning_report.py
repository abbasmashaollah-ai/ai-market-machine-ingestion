import json

from app.features.flows_positioning.flows_positioning_builder import build_flows_positioning_observation
from app.features.flows_positioning.flows_positioning_report import build_flows_positioning_report
from tests.fixtures.flows_positioning_data import build_flows_positioning_payload_scenario


def test_report_contains_expected_fields() -> None:
    observation = build_flows_positioning_observation(build_flows_positioning_payload_scenario("crowded_long"), "2026-01-15")
    report = build_flows_positioning_report(observation, writer_result=type("R", (), {"accepted_count": 1, "rejected_count": 0})())
    assert report["flow_regime_label"]
    assert report["accepted_count"] == 1
    assert report["rejected_count"] == 0
    assert report["safety_flags"]["no_db_writes"] is True
    json.dumps(report)
