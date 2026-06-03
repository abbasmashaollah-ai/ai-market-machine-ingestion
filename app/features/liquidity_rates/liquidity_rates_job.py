"""Dry-run orchestration for liquidity/rates observations."""

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Mapping
from copy import deepcopy
from datetime import date, datetime, timezone

from app.features.liquidity_rates.liquidity_rates_builder import build_liquidity_rates_observation
from app.features.liquidity_rates.liquidity_rates_report import build_liquidity_rates_report
from app.features.liquidity_rates.liquidity_rates_writer import LiquidityRatesMockWriter, write_liquidity_rates_payloads


@dataclass(frozen=True, slots=True)
class LiquidityRatesDryRunResult:
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


def run_liquidity_rates_dry_run(series_history_by_name, observation_date, timestamp=None, writer: LiquidityRatesMockWriter | None = None):
    histories = deepcopy(dict(series_history_by_name))
    observation_row = build_liquidity_rates_observation(
        histories,
        observation_date,
        timestamp=_normalize_timestamp(timestamp),
    )
    observation_rows = [observation_row]
    writer = writer or LiquidityRatesMockWriter()
    writer_result = write_liquidity_rates_payloads(observation_rows, writer=writer)
    reports = [build_liquidity_rates_report(observation_row, writer_result=writer_result)]
    return LiquidityRatesDryRunResult(
        observation_rows=tuple(observation_rows),
        reports=tuple(reports),
        writer_result=writer_result,
        accepted_count=writer_result.accepted_count,
        rejected_count=writer_result.rejected_count,
        warnings=writer_result.warnings,
    )