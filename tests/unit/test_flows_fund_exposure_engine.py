from app.features.flows_positioning.fund_exposure_engine import calculate_fund_exposure_score
from tests.fixtures.flows_positioning_data import build_flows_positioning_payload_scenario


def test_fund_exposure_score_is_deterministic() -> None:
    payload = build_flows_positioning_payload_scenario("mixed_positioning")
    assert calculate_fund_exposure_score(payload["fund_exposure"]) is not None
