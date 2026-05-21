from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta


@dataclass(frozen=True)
class BackfillRequest:
    vendor: str
    dataset: str
    start_date: date
    end_date: date
    symbol: str | None = None
    timeframe: str | None = None
    max_days_per_chunk: int = 30
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class DateChunk:
    start_date: date
    end_date: date


def split_date_range_into_chunks(
    start_date: date,
    end_date: date,
    *,
    max_days_per_chunk: int,
) -> list[DateChunk]:
    if start_date > end_date:
        raise ValueError("start_date must be less than or equal to end_date")
    if max_days_per_chunk <= 0:
        raise ValueError("max_days_per_chunk must be positive")

    chunks: list[DateChunk] = []
    current = start_date
    while current <= end_date:
        chunk_end = min(current + timedelta(days=max_days_per_chunk - 1), end_date)
        chunks.append(DateChunk(start_date=current, end_date=chunk_end))
        current = chunk_end + timedelta(days=1)
    return chunks
