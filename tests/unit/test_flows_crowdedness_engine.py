from app.features.flows_positioning.crowdedness_engine import calculate_crowdedness_score
from app.features.flows_positioning.etf_flow_engine import (
    calculate_credit_flow_score,
    calculate_defensive_flow_score,
    calculate_equity_flow_score,
)
from app.features.flows_positioning.fund_exposure_engine import calculate_fund_exposure_score
from app.features.flows_positioning.futures_positioning_engine import calculate_futures_positioning_score
from app.features.flows_positioning.options_positioning_engine import calculate_options_positioning_score
from app.features.flows_positioning.short_interest_engine import calculate_short_interest_pressure_score
from tests.fixtures.flows_positioning_data import build_flows_positioning_payload_scenario


def test_crowdedness_score_is_deterministic() -> None:
    payload = build_flows_positioning_payload_scenario("crowded_long")
    component_scores = {
        "equity_flow_score": calculate_equity_flow_score(payload["etf_flows"]),
        "defensive_flow_score": calculate_defensive_flow_score(payload["etf_flows"]),
        "credit_flow_score": calculate_credit_flow_score(payload["etf_flows"]),
        "options_positioning_score": calculate_options_positioning_score(payload["options_positioning"]),
        "futures_positioning_score": calculate_futures_positioning_score(payload["futures_positioning"]),
        "short_interest_pressure_score": calculate_short_interest_pressure_score(payload["short_interest"]),
        "fund_exposure_score": calculate_fund_exposure_score(payload["fund_exposure"]),
    }
    assert calculate_crowdedness_score(component_scores) is not None
