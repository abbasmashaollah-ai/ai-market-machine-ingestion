from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum


class ManualPolygonOHLCVCheckpointStatus(str, Enum):
    PLANNED = "planned"
    READY = "ready"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class ManualPolygonOHLCVCheckpoint:
    checkpoint_key: str
    vendor: str
    dataset: str
    symbol: str
    timeframe: str
    planned_start_date: date
    planned_end_date: date
    status: ManualPolygonOHLCVCheckpointStatus = ManualPolygonOHLCVCheckpointStatus.PLANNED
    last_successful_observation_date: date | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def build_manual_polygon_ohlcv_checkpoint(
    *,
    checkpoint_key: str,
    vendor: str,
    dataset: str,
    symbol: str,
    timeframe: str,
    planned_start_date: date,
    planned_end_date: date,
    status: ManualPolygonOHLCVCheckpointStatus = ManualPolygonOHLCVCheckpointStatus.PLANNED,
    last_successful_observation_date: date | None = None,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
) -> ManualPolygonOHLCVCheckpoint:
    return ManualPolygonOHLCVCheckpoint(
        checkpoint_key=checkpoint_key,
        vendor=vendor,
        dataset=dataset,
        symbol=symbol,
        timeframe=timeframe,
        planned_start_date=planned_start_date,
        planned_end_date=planned_end_date,
        status=status,
        last_successful_observation_date=last_successful_observation_date,
        created_at=created_at or datetime.now(timezone.utc),
        updated_at=updated_at or datetime.now(timezone.utc),
    )
