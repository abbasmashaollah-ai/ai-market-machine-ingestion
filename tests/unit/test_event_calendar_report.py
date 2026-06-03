import json

from app.features.event_calendar.event_calendar_builder import build_event_calendar_observation
from app.features.event_calendar.event_calendar_report import build_event_calendar_report
from tests.fixtures.event_calendar_events import build_event_calendar_events_scenario


def test_report_is_json_friendly_and_contains_state() -> None:
    observation = build_event_calendar_observation(build_event_calendar_events_scenario("fed_cpi_week"), "2026-06-03")
    report = build_event_calendar_report(observation)
    assert report["event_risk_label"]
    assert report["no_db_writes"] is True
    json.dumps(report)
