from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone


def _utc_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _require_timeframe(timeframe: str) -> str:
    if not timeframe:
        raise ValueError("timeframe is required")
    return timeframe


@dataclass(frozen=True)
class NormalizedOHLCVRecord:
    symbol: str | None
    symbol_id: str | None
    timestamp: datetime
    market_date: date | None = None
    timeframe: str = field(default="1d")
    adjusted: bool = field(default=False)
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: float | None = None
    vendor: str | None = None
    source: str | None = None
    ingestion_run_id: str | None = None
    normalization_version: str | None = None
    quality_status: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "timestamp", _utc_datetime(self.timestamp))
        object.__setattr__(self, "timeframe", _require_timeframe(self.timeframe))


@dataclass(frozen=True)
class NormalizedMacroObservation:
    symbol: str | None
    symbol_id: str | None
    timestamp: datetime
    market_date: date | None = None
    timeframe: str = field(default="1d")
    adjusted: bool = field(default=False)
    value: float | None = None
    vendor: str | None = None
    source: str | None = None
    ingestion_run_id: str | None = None
    normalization_version: str | None = None
    quality_status: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "timestamp", _utc_datetime(self.timestamp))
        object.__setattr__(self, "timeframe", _require_timeframe(self.timeframe))


@dataclass(frozen=True)
class NormalizedSymbolRecord:
    symbol: str | None
    symbol_id: str | None
    vendor: str | None = None
    source: str | None = None
    ingestion_run_id: str | None = None
    normalization_version: str | None = None
    quality_status: str | None = None
    asset_class: str | None = None
    exchange: str | None = None
    active: bool | None = None

