"""Dry-run orchestration for event calendar observations."""

from __future__ import annotations

from dataclasses import dataclass, field
from copy import deepcopy
from datetime import date, datetime, timezone

from app.features.event_calendar.event_calendar_builder import build_event_calendar_observation
from app.features.event_calendar.event_calendar_report import build_event_calendar_report
from app.features.event_calendar.event_calendar_writer import EventCalendarMockWriter, write_event_calendar_payloads


@dataclass(frozen=True, slots=True)
class EventCalendarDryRunResult:
    observation_rows: tuple[dict[str, object], ...]
    reports: tuple[dict[str, object], ...]
    writer_result: object
    accepted_count: int
    rejected_count: int
    warnings: tuple[str, ...] = field(default_factory=tuple)
    no_db_writes: bool = True
    no_vendor_calls: bool = True
    no_scheduler_activation: bool = True


def _normalize_timestamp(value: date | datetime | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def run_event_calendar_dry_run(events, observation_date, timestamp=None, lookahead_days=10, writer: EventCalendarMockWriter | None = None):
    event_rows = deepcopy(list(events or []))
    observation_row = build_event_calendar_observation(
        event_rows,
        observation_date,
        timestamp=_normalize_timestamp(timestamp),
        lookahead_days=lookahead_days,
    )
    observation_rows = [observation_row]
    writer = writer or EventCalendarMockWriter()
    writer_result = write_event_calendar_payloads(observation_rows, writer=writer)
    reports = [build_event_calendar_report(observation_row, writer_result=writer_result)]
    return EventCalendarDryRunResult(
        observation_rows=tuple(observation_rows),
        reports=tuple(reports),
        writer_result=writer_result,
        accepted_count=writer_result.accepted_count,
        rejected_count=writer_result.rejected_count,
        warnings=writer_result.warnings,
    )
