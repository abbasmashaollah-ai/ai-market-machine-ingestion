from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class MetricEvent:
    name: str
    value: int | float
    unit: str
    run_id: str | None = None
    vendor: str | None = None
    dataset: str | None = None
    symbol: str | None = None
    timeframe: str | None = None
    job_id: str | None = None
    status: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def build_metric_event(
    name: str,
    value: int | float,
    unit: str,
    *,
    run_id: str | None = None,
    vendor: str | None = None,
    dataset: str | None = None,
    symbol: str | None = None,
    timeframe: str | None = None,
    job_id: str | None = None,
    status: str | None = None,
) -> MetricEvent:
    return MetricEvent(
        name=name,
        value=value,
        unit=unit,
        run_id=run_id,
        vendor=vendor,
        dataset=dataset,
        symbol=symbol,
        timeframe=timeframe,
        job_id=job_id,
        status=status,
    )

