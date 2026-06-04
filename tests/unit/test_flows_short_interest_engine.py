from app.features.flows_positioning.short_interest_engine import calculate_short_interest_pressure_score
from tests.fixtures.flows_positioning_data import build_flows_positioning_payload_scenario


def test_short_interest_pressure_score_is_deterministic() -> None:
    payload = build_flows_positioning_payload_scenario("risk_off_flows")
    assert calculate_short_interest_pressure_score(payload["short_interest"]) is not None
