from copy import deepcopy

from app.features.event_calendar.event_calendar_builder import build_event_calendar_observation
from app.features.event_calendar.event_calendar_writer import EventCalendarMockWriter, write_event_calendar_payloads
from tests.fixtures.event_calendar_events import build_event_calendar_events_scenario


def test_mock_writer_accepts_valid_rows_and_preserves_input() -> None:
    observation = build_event_calendar_observation(build_event_calendar_events_scenario("quiet_week"), "2026-06-03")
    rows = [observation]
    snapshot = deepcopy(rows)
    writer = EventCalendarMockWriter()
    result = write_event_calendar_payloads(rows, writer=writer)
    assert result.accepted_count == 1
    assert result.rejected_count == 0
    assert rows == snapshot
    assert writer.rows


def test_mock_writer_rejects_invalid_rows() -> None:
    observation = build_event_calendar_observation(build_event_calendar_events_scenario("quiet_week"), "2026-06-03")
    observation = dict(observation)
    observation["event_risk_label"] = None
    result = write_event_calendar_payloads([observation])
    assert result.accepted_count == 0
    assert result.rejected_count == 1
