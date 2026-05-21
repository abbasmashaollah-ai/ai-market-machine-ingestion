from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone


class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class AlertEvent:
    alert_type: str
    severity: AlertSeverity
    message: str
    run_id: str | None = None
    vendor: str | None = None
    dataset: str | None = None
    symbol: str | None = None
    timeframe: str | None = None
    job_id: str | None = None
    status: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def _build_alert(
    alert_type: str,
    severity: AlertSeverity,
    message: str,
    *,
    run_id: str | None = None,
    vendor: str | None = None,
    dataset: str | None = None,
    symbol: str | None = None,
    timeframe: str | None = None,
    job_id: str | None = None,
    status: str | None = None,
    **metadata: object,
) -> AlertEvent:
    return AlertEvent(
        alert_type=alert_type,
        severity=severity,
        message=message,
        run_id=run_id,
        vendor=vendor,
        dataset=dataset,
        symbol=symbol,
        timeframe=timeframe,
        job_id=job_id,
        status=status,
        metadata=metadata,
    )


def daily_ingestion_failure(**context: object) -> AlertEvent:
    return _build_alert("daily_ingestion_failure", AlertSeverity.HIGH, "daily ingestion failed", **context)


def stuck_checkpoint(**context: object) -> AlertEvent:
    return _build_alert("stuck_checkpoint", AlertSeverity.MEDIUM, "checkpoint is not advancing", **context)


def vendor_outage(**context: object) -> AlertEvent:
    return _build_alert("vendor_outage", AlertSeverity.HIGH, "vendor outage detected", **context)


def db_write_failure(**context: object) -> AlertEvent:
    return _build_alert("db_write_failure", AlertSeverity.CRITICAL, "database write failed", **context)


def excessive_quality_failures(**context: object) -> AlertEvent:
    return _build_alert("excessive_quality_failures", AlertSeverity.HIGH, "quality failures exceeded threshold", **context)

