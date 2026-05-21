from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    RETRYING = "retrying"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class IngestionRun:
    run_id: str
    job_id: str
    status: RunStatus = RunStatus.PENDING
    rows_fetched: int = 0
    rows_written: int = 0
    rows_rejected: int = 0
    error_count: int = 0
    metadata: dict[str, object] = field(default_factory=dict)

    @property
    def rows_total(self) -> int:
        return self.rows_fetched

    @property
    def rows_processed(self) -> int:
        return self.rows_written + self.rows_rejected

    @property
    def has_errors(self) -> bool:
        return self.error_count > 0

