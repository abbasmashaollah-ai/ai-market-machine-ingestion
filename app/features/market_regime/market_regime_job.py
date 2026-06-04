"""Dry-run orchestration for market regime observations."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from app.features.market_regime.market_regime_builder import build_market_regime_observation
from app.features.market_regime.market_regime_report import build_market_regime_report
from app.features.market_regime.market_regime_writer import MarketRegimeMockWriter, write_market_regime_payloads


@dataclass(frozen=True, slots=True)
class MarketRegimeDryRunResult:
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


def run_market_regime_dry_run(feature_summary, observation_date=None, timestamp=None, writer: MarketRegimeMockWriter | None = None):
    payload = deepcopy(dict(feature_summary or {}))
    observation_row = build_market_regime_observation(
        payload,
        observation_date=observation_date,
        timestamp=_normalize_timestamp(timestamp),
    )
    observation_rows = [observation_row]
    writer = writer or MarketRegimeMockWriter()
    writer_result = write_market_regime_payloads(observation_rows, writer=writer)
    reports = [build_market_regime_report(observation_row, writer_result=writer_result)]
    return MarketRegimeDryRunResult(
        observation_rows=tuple(observation_rows),
        reports=tuple(reports),
        writer_result=writer_result,
        accepted_count=writer_result.accepted_count,
        rejected_count=writer_result.rejected_count,
        warnings=writer_result.warnings,
    )

