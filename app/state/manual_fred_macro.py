from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum


class ManualFREDMacroCheckpointStatus(str, Enum):
    PLANNED = "planned"
    READY = "ready"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class ManualFREDMacroCheckpoint:
    checkpoint_key: str
    vendor: str
    dataset: str
    series_id: str
    timeframe: str
    planned_start_date: date
    planned_end_date: date
    status: ManualFREDMacroCheckpointStatus = ManualFREDMacroCheckpointStatus.PLANNED
    last_successful_observation_date: date | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def build_manual_fred_macro_checkpoint(
    *,
    checkpoint_key: str,
    vendor: str,
    dataset: str,
    series_id: str,
    timeframe: str,
    planned_start_date: date,
    planned_end_date: date,
    status: ManualFREDMacroCheckpointStatus = ManualFREDMacroCheckpointStatus.PLANNED,
    last_successful_observation_date: date | None = None,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
) -> ManualFREDMacroCheckpoint:
    return ManualFREDMacroCheckpoint(
        checkpoint_key=checkpoint_key,
        vendor=vendor,
        dataset=dataset,
        series_id=series_id,
        timeframe=timeframe,
        planned_start_date=planned_start_date,
        planned_end_date=planned_end_date,
        status=status,
        last_successful_observation_date=last_successful_observation_date,
        created_at=created_at or datetime.now(timezone.utc),
        updated_at=updated_at or datetime.now(timezone.utc),
    )
