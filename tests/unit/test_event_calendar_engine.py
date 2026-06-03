from datetime import date

from app.features.event_calendar.event_calendar_engine import (
    calculate_days_to_event,
    calculate_event_risk_score,
    count_events_by_type,
    count_high_impact_events,
    determine_event_risk_label,
    find_next_high_impact_event,
    filter_events_by_lookahead,
    normalize_event_impact,
    normalize_event_type,
)
from tests.fixtures.event_calendar_events import build_event_calendar_events_scenario


def test_engine_helpers() -> None:
    events = build_event_calendar_events_scenario("fed_cpi_week")
    filtered = filter_events_by_lookahead(events, "2026-06-03", 10)
    assert len(filtered) == 4
    assert normalize_event_type("fomc") == "FED"
    assert normalize_event_type("nfp") == "JOBS"
    assert normalize_event_impact("critical") == "HIGH"
    assert count_events_by_type(filtered)["FED"] == 1
    assert count_high_impact_events(filtered) == 2
    next_event = find_next_high_impact_event(filtered, "2026-06-03")
    assert next_event["event_id"] == "F1"
    assert calculate_days_to_event(date(2026, 6, 3), "2026-06-04") == 1
    score = calculate_event_risk_score(filtered, "2026-06-03")
    assert score > 0
    assert determine_event_risk_label(event_risk_score=score, high_impact_event_count=2) in {
        "MODERATE_EVENT_RISK",
        "HIGH_EVENT_RISK",
        "EXTREME_EVENT_RISK",
    }
