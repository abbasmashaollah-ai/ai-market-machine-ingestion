import json

from app.features.event_calendar.event_calendar_builder import build_event_calendar_observation
from tests.fixtures.event_calendar_events import build_event_calendar_events_scenario


def test_builder_fields() -> None:
    observation = build_event_calendar_observation(build_event_calendar_events_scenario("fed_cpi_week"), "2026-06-03")
    assert observation["event_count"] == 4
    assert observation["fed_event_count"] == 1
    assert observation["event_risk_label"]
    assert observation["quality_status"] == "PENDING"
    json.dumps(observation)
