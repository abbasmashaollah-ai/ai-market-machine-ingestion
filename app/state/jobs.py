from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    RETRYING = "retrying"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class IngestionJob:
    job_id: str
    vendor: str
    dataset: str
    status: JobStatus = JobStatus.PENDING
    created_at: datetime | None = None
    updated_at: datetime | None = None
    metadata: dict[str, object] = field(default_factory=dict)


def transition_job_status(current: JobStatus, next_status: JobStatus) -> JobStatus:
    allowed = {
        JobStatus.PENDING: {JobStatus.RUNNING, JobStatus.SKIPPED, JobStatus.CANCELLED},
        JobStatus.RUNNING: {
            JobStatus.SUCCESS,
            JobStatus.FAILED,
            JobStatus.PARTIAL,
            JobStatus.RETRYING,
            JobStatus.SKIPPED,
            JobStatus.CANCELLED,
        },
        JobStatus.RETRYING: {JobStatus.RUNNING, JobStatus.FAILED, JobStatus.CANCELLED},
        JobStatus.PARTIAL: {JobStatus.RETRYING, JobStatus.SUCCESS, JobStatus.FAILED, JobStatus.CANCELLED},
        JobStatus.FAILED: {JobStatus.RETRYING, JobStatus.CANCELLED},
        JobStatus.SUCCESS: set(),
        JobStatus.SKIPPED: set(),
        JobStatus.CANCELLED: set(),
    }
    if next_status not in allowed[current]:
        raise ValueError(f"Invalid transition from {current.value} to {next_status.value}")
    return next_status
