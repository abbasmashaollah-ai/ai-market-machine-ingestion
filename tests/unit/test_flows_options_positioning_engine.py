from app.features.flows_positioning.options_positioning_engine import calculate_options_positioning_score
from tests.fixtures.flows_positioning_data import build_flows_positioning_payload_scenario


def test_options_positioning_score_is_deterministic() -> None:
    payload = build_flows_positioning_payload_scenario("mixed_positioning")
    assert calculate_options_positioning_score(payload["options_positioning"]) is not None
