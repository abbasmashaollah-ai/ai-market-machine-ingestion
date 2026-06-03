"""Dry-run orchestration for price feature observations."""

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Mapping
from copy import deepcopy
from datetime import date, datetime, timezone

from app.features.prices.price_feature_builder import build_price_feature_observation
from app.features.prices.price_feature_report import build_price_feature_report
from app.features.prices.price_feature_writer import PriceFeatureMockWriter, write_price_feature_payloads


@dataclass(frozen=True, slots=True)
class PriceFeatureDryRunResult:
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


def run_price_feature_dry_run(
    close_history_by_symbol: Mapping[str, list[dict[str, object]] | list[object]],
    observation_date,
    timestamp=None,
    writer: PriceFeatureMockWriter | None = None,
    source: str = "fixture_ohlcv",
):
    histories = deepcopy(dict(close_history_by_symbol))
    observation_rows: list[dict[str, object]] = []
    for symbol, history in histories.items():
        closes = [row["close"] if isinstance(row, Mapping) else row for row in history]
        observation_rows.append(
            build_price_feature_observation(
                symbol,
                closes,
                observation_date,
                timestamp=_normalize_timestamp(timestamp),
                source=source,
            )
        )

    writer = writer or PriceFeatureMockWriter()
    writer_result = write_price_feature_payloads(observation_rows, writer=writer)
    reports = [build_price_feature_report(row) for row in observation_rows]

    return PriceFeatureDryRunResult(
        observation_rows=tuple(observation_rows),
        reports=tuple(reports),
        writer_result=writer_result,
        accepted_count=writer_result.accepted_count,
        rejected_count=writer_result.rejected_count,
        warnings=writer_result.warnings,
    )