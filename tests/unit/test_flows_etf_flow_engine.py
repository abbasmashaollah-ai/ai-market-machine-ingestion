from app.features.flows_positioning.etf_flow_engine import (
    calculate_credit_flow_score,
    calculate_defensive_flow_score,
    calculate_equity_flow_score,
)
from tests.fixtures.flows_positioning_data import build_flows_positioning_payload_scenario


def test_etf_flow_scores_are_deterministic() -> None:
    payload = build_flows_positioning_payload_scenario("risk_on_flows")
    assert calculate_equity_flow_score(payload["etf_flows"]) is not None
    assert calculate_defensive_flow_score(payload["etf_flows"]) is not None
    assert calculate_credit_flow_score(payload["etf_flows"]) is not None
