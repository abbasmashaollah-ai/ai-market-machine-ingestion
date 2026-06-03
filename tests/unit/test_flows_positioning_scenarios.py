from app.features.flows_positioning.flows_positioning_builder import build_flows_positioning_observation
from tests.fixtures.flows_positioning_data import build_flows_positioning_payload_scenario


def test_scenarios_produce_different_labels() -> None:
    labels = {
        scenario: build_flows_positioning_observation(build_flows_positioning_payload_scenario(scenario), "2026-01-15")["flow_regime_label"]
        for scenario in ("risk_on_flows", "risk_off_flows", "crowded_long", "crowded_short", "mixed_positioning", "low_signal")
    }
    assert labels["risk_on_flows"] in {"RISK_ON_FLOWS", "MIXED_POSITIONING"}
    assert labels["risk_off_flows"] in {"RISK_OFF_FLOWS", "DEFENSIVE_ROTATION"}
    assert labels["crowded_long"] in {"CROWDED_LONG", "RISK_ON_FLOWS"}
    assert labels["crowded_short"] in {"CROWDED_SHORT", "RISK_OFF_FLOWS"}
    assert labels["mixed_positioning"] in {"MIXED_POSITIONING", "LOW_SIGNAL_POSITIONING", "RISK_ON_FLOWS", "RISK_OFF_FLOWS"}
    assert labels["low_signal"] in {"LOW_SIGNAL_POSITIONING", "INSUFFICIENT_DATA"}
