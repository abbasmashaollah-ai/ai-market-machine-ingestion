"""Dry-run orchestration for volatility observations."""

from __future__ import annotations

from dataclasses import dataclass, field
from copy import deepcopy
from datetime import date, datetime, timezone

from app.features.volatility.volatility_builder import build_volatility_observation
from app.features.volatility.volatility_report import build_volatility_report
from app.features.volatility.volatility_writer import VolatilityMockWriter, write_volatility_payloads


@dataclass(frozen=True, slots=True)
class VolatilityDryRunResult:
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


def run_volatility_dry_run(series_history_by_name, observation_date, timestamp=None, writer: VolatilityMockWriter | None = None):
    histories = deepcopy(dict(series_history_by_name))
    observation_row = build_volatility_observation(
        histories,
        observation_date,
        timestamp=_normalize_timestamp(timestamp),
    )
    observation_rows = [observation_row]
    writer = writer or VolatilityMockWriter()
    writer_result = write_volatility_payloads(observation_rows, writer=writer)
    reports = [build_volatility_report(observation_row, writer_result=writer_result)]
    return VolatilityDryRunResult(
        observation_rows=tuple(observation_rows),
        reports=tuple(reports),
        writer_result=writer_result,
        accepted_count=writer_result.accepted_count,
        rejected_count=writer_result.rejected_count,
        warnings=writer_result.warnings,
    )
