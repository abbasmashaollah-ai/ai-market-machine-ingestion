from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum


class ManualFREDMacroRunStatus(str, Enum):
    PLANNED = "planned"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class ManualFREDMacroRunResult:
    checkpoint_key: str
    series_id: str
    status: ManualFREDMacroRunStatus
    planned_start_date: date
    planned_end_date: date
    rows_planned: int
    rows_fetched: int
    rows_valid: int
    rows_invalid: int
    rows_written: int
    validation_failures: int
    error_message: str | None = None
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None


def build_manual_fred_macro_run_result(
    *,
    checkpoint_key: str,
    series_id: str,
    status: ManualFREDMacroRunStatus,
    planned_start_date: date,
    planned_end_date: date,
    rows_planned: int,
    rows_fetched: int,
    rows_valid: int,
    rows_invalid: int,
    rows_written: int,
    validation_failures: int,
    error_message: str | None = None,
    started_at: datetime | None = None,
    finished_at: datetime | None = None,
) -> ManualFREDMacroRunResult:
    return ManualFREDMacroRunResult(
        checkpoint_key=checkpoint_key,
        series_id=series_id,
        status=status,
        planned_start_date=planned_start_date,
        planned_end_date=planned_end_date,
        rows_planned=rows_planned,
        rows_fetched=rows_fetched,
        rows_valid=rows_valid,
        rows_invalid=rows_invalid,
        rows_written=rows_written,
        validation_failures=validation_failures,
        error_message=error_message,
        started_at=started_at or datetime.now(timezone.utc),
        finished_at=finished_at,
    )
