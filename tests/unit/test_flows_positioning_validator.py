from copy import deepcopy

from app.features.flows_positioning.flows_positioning_builder import build_flows_positioning_observation
from app.features.flows_positioning.flows_positioning_validator import validate_flows_positioning_observation
from tests.fixtures.flows_positioning_data import build_flows_positioning_payload_scenario


def test_valid_observation_passes() -> None:
    observation = build_flows_positioning_observation(build_flows_positioning_payload_scenario("risk_on_flows"), "2026-01-15")
    result = validate_flows_positioning_observation(observation)
    assert result.is_valid is True


def test_invalid_observation_fails() -> None:
    observation = build_flows_positioning_observation(build_flows_positioning_payload_scenario("risk_on_flows"), "2026-01-15")
    invalid = dict(observation)
    invalid["flow_regime_label"] = None
    result = validate_flows_positioning_observation(invalid)
    assert result.is_valid is False
    assert any(error.field_name == "flow_regime_label" for error in result.errors)


def test_validator_does_not_mutate_input() -> None:
    observation = build_flows_positioning_observation(build_flows_positioning_payload_scenario("risk_on_flows"), "2026-01-15")
    snapshot = deepcopy(observation)
    validate_flows_positioning_observation(observation)
    assert observation == snapshot
