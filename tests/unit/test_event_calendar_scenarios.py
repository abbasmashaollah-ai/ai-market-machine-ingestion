from app.features.event_calendar.event_calendar_job import run_event_calendar_dry_run
from tests.fixtures.event_calendar_events import build_event_calendar_events_scenario


def test_scenario_labels_differ() -> None:
    labels = {}
    for scenario in ("quiet_week", "fed_cpi_week", "earnings_heavy_week", "opex_week", "extreme_macro_week"):
        events = build_event_calendar_events_scenario(scenario)
        result = run_event_calendar_dry_run(events, "2026-06-03")
        labels[scenario] = result.reports[0]["event_risk_label"]
    assert len(set(labels.values())) >= 3
