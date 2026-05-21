from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol


class WriteStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class WriterResult:
    writer_name: str
    status: WriteStatus
    written_count: int = 0
    skipped_count: int = 0
    failed_count: int = 0
    message: str | None = None
    details: dict[str, object] = field(default_factory=dict)

    @property
    def succeeded(self) -> bool:
        return self.status == WriteStatus.SUCCESS


@dataclass(frozen=True)
class WriterBatchSummary:
    total_writers: int
    successful_writers: int
    failed_writers: int
    skipped_writers: int
    total_written: int
    total_skipped: int
    total_failed: int


def summarize_writer_results(results: list[WriterResult]) -> WriterBatchSummary:
    return WriterBatchSummary(
        total_writers=len(results),
        successful_writers=sum(1 for result in results if result.status == WriteStatus.SUCCESS),
        failed_writers=sum(1 for result in results if result.status == WriteStatus.FAILURE),
        skipped_writers=sum(1 for result in results if result.status == WriteStatus.SKIPPED),
        total_written=sum(result.written_count for result in results),
        total_skipped=sum(result.skipped_count for result in results),
        total_failed=sum(result.failed_count for result in results),
    )


class CanonicalWriter(Protocol):
    writer_name: str

    def write(self, records: list[object]) -> WriterResult:
        ...
