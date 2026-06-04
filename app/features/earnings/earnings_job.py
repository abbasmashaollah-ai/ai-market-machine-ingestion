"""Dry-run orchestration for earnings observations."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from app.features.earnings.earnings_builder import build_earnings_observation
from app.features.earnings.earnings_report import build_earnings_report
from app.features.earnings.earnings_writer import EarningsMockWriter, write_earnings_payloads


@dataclass(frozen=True, slots=True)
class EarningsDryRunResult:
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


def run_earnings_dry_run(earnings_by_symbol, observation_date, timestamp=None, writer: EarningsMockWriter | None = None):
    earnings_payloads = deepcopy(dict(earnings_by_symbol or {}))
    observation_rows: list[dict[str, object]] = []
    for symbol in sorted(earnings_payloads):
        observation_rows.append(
            build_earnings_observation(
                symbol,
                earnings_payloads[symbol],
                observation_date,
                timestamp=_normalize_timestamp(timestamp),
            )
        )
    writer = writer or EarningsMockWriter()
    writer_result = write_earnings_payloads(observation_rows, writer=writer)
    reports = [build_earnings_report(observation_row, writer_result=writer_result) for observation_row in observation_rows]
    return EarningsDryRunResult(
        observation_rows=tuple(observation_rows),
        reports=tuple(reports),
        writer_result=writer_result,
        accepted_count=writer_result.accepted_count,
        rejected_count=writer_result.rejected_count,
        warnings=writer_result.warnings,
    )

