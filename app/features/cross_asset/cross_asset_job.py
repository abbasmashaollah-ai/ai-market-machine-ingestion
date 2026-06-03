"""Dry-run orchestration for cross-asset observations."""

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Mapping
from copy import deepcopy
from datetime import date, datetime, timezone

from app.features.cross_asset.cross_asset_builder import build_cross_asset_observation
from app.features.cross_asset.cross_asset_report import build_cross_asset_report
from app.features.cross_asset.cross_asset_writer import CrossAssetMockWriter, write_cross_asset_payloads


@dataclass(frozen=True, slots=True)
class CrossAssetDryRunResult:
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


def run_cross_asset_dry_run(
    close_history_by_symbol,
    observation_date,
    timestamp=None,
    writer: CrossAssetMockWriter | None = None,
):
    histories = deepcopy(dict(close_history_by_symbol))
    observation_row = build_cross_asset_observation(
        histories,
        observation_date,
        timestamp=_normalize_timestamp(timestamp),
    )
    observation_rows = [observation_row]
    writer = writer or CrossAssetMockWriter()
    writer_result = write_cross_asset_payloads(observation_rows, writer=writer)
    reports = [build_cross_asset_report(observation_row, writer_result=writer_result)]
    return CrossAssetDryRunResult(
        observation_rows=tuple(observation_rows),
        reports=tuple(reports),
        writer_result=writer_result,
        accepted_count=writer_result.accepted_count,
        rejected_count=writer_result.rejected_count,
        warnings=writer_result.warnings,
    )