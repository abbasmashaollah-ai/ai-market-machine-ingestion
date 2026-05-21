from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Protocol


class CheckpointStatus(str):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETE = "complete"
    FAILED = "failed"
    STALE = "stale"


@dataclass(frozen=True)
class IngestionCheckpoint:
    checkpoint_id: str
    job_id: str
    last_successful_date: date | None = None
    attempt_count: int = 0
    status: str = CheckpointStatus.PENDING
    metadata: dict[str, object] = field(default_factory=dict)


class CheckpointStore(Protocol):
    def load(self, checkpoint_id: str) -> IngestionCheckpoint | None:
        ...

    def save(self, checkpoint: IngestionCheckpoint) -> None:
        ...
