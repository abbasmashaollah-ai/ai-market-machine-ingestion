from app.features.flows_positioning.flows_positioning_engine import (
    calculate_crowdedness_score,
    calculate_credit_flow_score,
    calculate_defensive_flow_score,
    calculate_equity_flow_score,
    calculate_fund_exposure_score,
    calculate_futures_positioning_score,
    calculate_options_positioning_score,
    calculate_positioning_risk_score,
    calculate_short_interest_pressure_score,
    determine_flow_regime_label,
)
from tests.fixtures.flows_positioning_data import build_flows_positioning_payload_scenario


def test_component_scores() -> None:
    payload = build_flows_positioning_payload_scenario("risk_on_flows")
    assert calculate_equity_flow_score(payload["etf_flows"]) is not None
    assert calculate_defensive_flow_score(payload["etf_flows"]) is not None
    assert calculate_credit_flow_score(payload["etf_flows"]) is not None
    assert calculate_options_positioning_score(payload["options_positioning"]) is not None
    assert calculate_futures_positioning_score(payload["futures_positioning"]) is not None
    assert calculate_short_interest_pressure_score(payload["short_interest"]) is not None
    assert calculate_fund_exposure_score(payload["fund_exposure"]) is not None


def test_crowdedness_and_risk_scores() -> None:
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
    component_scores["crowdedness_score"] = calculate_crowdedness_score(component_scores)
    component_scores["positioning_risk_score"] = calculate_positioning_risk_score(component_scores)
    assert component_scores["crowdedness_score"] is not None
    assert component_scores["positioning_risk_score"] is not None
    assert determine_flow_regime_label(component_scores) in {"CROWDED_LONG", "RISK_ON_FLOWS"}
