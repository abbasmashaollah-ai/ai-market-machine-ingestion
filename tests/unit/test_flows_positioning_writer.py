from copy import deepcopy

from app.features.flows_positioning.flows_positioning_builder import build_flows_positioning_observation
from app.features.flows_positioning.flows_positioning_writer import FlowsPositioningMockWriter, write_flows_positioning_payloads
from tests.fixtures.flows_positioning_data import build_flows_positioning_payload_scenario


def test_mock_writer_accepts_valid_rows() -> None:
    observation = build_flows_positioning_observation(build_flows_positioning_payload_scenario("risk_on_flows"), "2026-01-15")
    writer = FlowsPositioningMockWriter()
    result = write_flows_positioning_payloads([observation], writer=writer)
    assert result.accepted_count == 1
    assert result.rejected_count == 0
    assert result.no_db_writes is True


def test_mock_writer_preserves_input() -> None:
    observation = build_flows_positioning_observation(build_flows_positioning_payload_scenario("risk_on_flows"), "2026-01-15")
    snapshot = deepcopy(observation)
    write_flows_positioning_payloads([observation], writer=FlowsPositioningMockWriter())
    assert observation == snapshot
