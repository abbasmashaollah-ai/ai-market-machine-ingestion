from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MacroEventCalendarSourceCandidate:
    source_name: str
    supported_event_types: tuple[str, ...] = field(default_factory=tuple)
    coverage_note: str = ""
    timezone_handling_note: str = ""
    event_time_handling_note: str = ""
    rate_limit_cost_notes: str = ""
    status: str = "planned"
    priority: int = 0


def build_macro_event_calendar_source_candidates() -> tuple[MacroEventCalendarSourceCandidate, ...]:
    return (
        MacroEventCalendarSourceCandidate(
            source_name="BLS CPI",
            supported_event_types=("CPI",),
            coverage_note="Official CPI release dates and timestamps are best sourced from BLS release calendars.",
            timezone_handling_note="Normalize to America/New_York for US macro release times.",
            event_time_handling_note="Preserve the official release time when published; otherwise keep the release window explicit.",
            rate_limit_cost_notes="Public-source access is low cost; avoid unnecessary polling.",
            status="planned",
            priority=1,
        ),
        MacroEventCalendarSourceCandidate(
            source_name="Federal Reserve FOMC",
            supported_event_types=("FOMC",),
            coverage_note="Federal Reserve calendars and statements are the authoritative source for FOMC event timing.",
            timezone_handling_note="Normalize to America/New_York for US central bank announcements.",
            event_time_handling_note="Preserve statement time or scheduled release time when provided by the Fed.",
            rate_limit_cost_notes="Public-source access is low cost; avoid unnecessary polling.",
            status="planned",
            priority=2,
        ),
        MacroEventCalendarSourceCandidate(
            source_name="BLS NFP",
            supported_event_types=("NFP",),
            coverage_note="Official labor release calendars are the authoritative source for NFP release dates.",
            timezone_handling_note="Normalize to America/New_York for US labor release times.",
            event_time_handling_note="Preserve the official release time when published; otherwise keep the release window explicit.",
            rate_limit_cost_notes="Public-source access is low cost; avoid unnecessary polling.",
            status="planned",
            priority=3,
        ),
        MacroEventCalendarSourceCandidate(
            source_name="manual_fixture",
            supported_event_types=("CPI", "FOMC", "NFP"),
            coverage_note="Test-only deterministic coverage for CPI, FOMC, and NFP planning.",
            timezone_handling_note="Uses fixed fixture timestamps and zones for repeatable tests.",
            event_time_handling_note="Uses fixed fixture times for deterministic dry-run behavior.",
            rate_limit_cost_notes="No external requests; test/dry-run only.",
            status="test_only",
            priority=99,
        ),
    )

