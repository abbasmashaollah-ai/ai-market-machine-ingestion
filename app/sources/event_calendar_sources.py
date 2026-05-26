from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EventCalendarSourceCandidate:
    source_name: str
    supported_event_types: tuple[str, ...] = field(default_factory=tuple)
    coverage_note: str = ""
    timezone_handling_note: str = ""
    rate_limit_cost_notes: str = ""
    status: str = "planned"
    priority: int = 0


def build_event_calendar_source_candidates() -> tuple[EventCalendarSourceCandidate, ...]:
    return (
        EventCalendarSourceCandidate(
            source_name="FRED/BLS/Fed official sources",
            supported_event_types=("CPI", "FOMC", "NFP"),
            coverage_note="Best fit for macro event release dates and official announcement schedules.",
            timezone_handling_note="Typically normalize to America/New_York for US macro release timestamps.",
            rate_limit_cost_notes="Low external cost if official feeds or public endpoints are approved.",
            status="planned",
            priority=1,
        ),
        EventCalendarSourceCandidate(
            source_name="exchange/calendar/manual rule source",
            supported_event_types=("OPEX",),
            coverage_note="Manual or exchange-calendar rules are the most reliable deterministic source for options expiration dates.",
            timezone_handling_note="Normalize to exchange-local close time, usually America/New_York for US listed options.",
            rate_limit_cost_notes="No live API required for deterministic rule-based computation; use external source only if approved later.",
            status="planned",
            priority=2,
        ),
        EventCalendarSourceCandidate(
            source_name="FMP/Finnhub/Nasdaq",
            supported_event_types=("earnings_date",),
            coverage_note="Useful for earnings calendar coverage when vendor entitlement is approved.",
            timezone_handling_note="Normalize to market-local or exchange-local timezone; preserve vendor-provided timezone where present.",
            rate_limit_cost_notes="Potential API cost and entitlement requirements depend on vendor plan.",
            status="planned",
            priority=3,
        ),
        EventCalendarSourceCandidate(
            source_name="manual fixture",
            supported_event_types=("CPI", "FOMC", "NFP", "OPEX", "earnings_date"),
            coverage_note="Test-only deterministic coverage for all supported event types.",
            timezone_handling_note="Uses fixed fixture timestamps and zones for repeatable tests.",
            rate_limit_cost_notes="No external requests; test/dry-run only.",
            status="test_only",
            priority=99,
        ),
    )
