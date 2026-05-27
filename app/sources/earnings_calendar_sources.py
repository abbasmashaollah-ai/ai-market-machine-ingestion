from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EarningsCalendarSourceCandidate:
    source_name: str
    supported_event_types: tuple[str, ...] = field(default_factory=tuple)
    coverage_note: str = ""
    timezone_handling_note: str = ""
    event_time_handling_note: str = ""
    rate_limit_cost_notes: str = ""
    status: str = "planned"
    priority: int = 0


def build_earnings_calendar_source_candidates() -> tuple[EarningsCalendarSourceCandidate, ...]:
    return (
        EarningsCalendarSourceCandidate(
            source_name="FMP",
            supported_event_types=("earnings_date",),
            coverage_note="Useful for earnings-date coverage when vendor access is approved.",
            timezone_handling_note="Normalize to market-local or exchange-local timezone; preserve vendor-provided timezone where present.",
            event_time_handling_note="Preserve a precise release time when available; otherwise keep the release window explicit.",
            rate_limit_cost_notes="Potential API cost and entitlement requirements depend on vendor plan.",
            status="planned",
            priority=1,
        ),
        EarningsCalendarSourceCandidate(
            source_name="Finnhub",
            supported_event_types=("earnings_date",),
            coverage_note="Useful for supplementary earnings-date coverage when vendor access is approved.",
            timezone_handling_note="Normalize to market-local or exchange-local timezone; preserve vendor-provided timezone where present.",
            event_time_handling_note="Preserve a precise release time when available; otherwise keep the release window explicit.",
            rate_limit_cost_notes="Potential API cost and entitlement requirements depend on vendor plan.",
            status="planned",
            priority=2,
        ),
        EarningsCalendarSourceCandidate(
            source_name="Nasdaq",
            supported_event_types=("earnings_date",),
            coverage_note="Useful for earnings calendar coverage when vendor access is approved.",
            timezone_handling_note="Normalize to market-local or exchange-local timezone; preserve vendor-provided timezone where present.",
            event_time_handling_note="Preserve a precise release time when available; otherwise keep the release window explicit.",
            rate_limit_cost_notes="Potential API cost and entitlement requirements depend on vendor plan.",
            status="planned",
            priority=3,
        ),
        EarningsCalendarSourceCandidate(
            source_name="manual_fixture",
            supported_event_types=("earnings_date",),
            coverage_note="Test-only deterministic coverage for earnings-date planning.",
            timezone_handling_note="Uses fixed fixture timestamps and zones for repeatable tests.",
            event_time_handling_note="Uses fixed fixture times or nulls for deterministic dry-run behavior.",
            rate_limit_cost_notes="No external requests; test/dry-run only.",
            status="test_only",
            priority=99,
        ),
    )

