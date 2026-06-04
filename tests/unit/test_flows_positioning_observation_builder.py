import json
from datetime import datetime, timezone

from app.features.flows_positioning.flows_positioning_observation_builder import build_flows_positioning_observation
from tests.fixtures.flows_positioning_data import build_flows_positioning_payload_scenario


def test_observation_builder_is_json_friendly_and_preserves_fields() -> None:
    observation = build_flows_positioning_observation(
        build_flows_positioning_payload_scenario("mixed_positioning"),
        "2026-01-15",
        timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc),
    )
    assert observation["observation_date"] == "2026-01-15"
    assert observation["flow_regime_label"]
    assert observation["quality_status"] == "PENDING"
    assert observation["no_db_writes"] is True
    json.dumps(observation)
