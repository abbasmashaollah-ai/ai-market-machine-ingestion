from app.features.flows_positioning.futures_positioning_engine import calculate_futures_positioning_score
from tests.fixtures.flows_positioning_data import build_flows_positioning_payload_scenario


def test_futures_positioning_score_is_deterministic() -> None:
    payload = build_flows_positioning_payload_scenario("risk_on_flows")
    assert calculate_futures_positioning_score(payload["futures_positioning"]) is not None
