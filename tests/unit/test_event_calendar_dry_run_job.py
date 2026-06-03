import json
from datetime import datetime, timezone

from app.features.event_calendar.event_calendar_job import run_event_calendar_dry_run
from tests.fixtures.event_calendar_events import build_event_calendar_events_scenario


def test_dry_run_produces_report_and_safety_flags() -> None:
    events = build_event_calendar_events_scenario("extreme_macro_week")
    result = run_event_calendar_dry_run(events, "2026-06-03", timestamp=datetime(2026, 6, 3, 16, 0, tzinfo=timezone.utc))
    assert result.accepted_count == 1
    assert result.no_db_writes is True
    assert result.no_vendor_calls is True
    assert result.no_scheduler_activation is True
    json.dumps([dict(report) for report in result.reports])
