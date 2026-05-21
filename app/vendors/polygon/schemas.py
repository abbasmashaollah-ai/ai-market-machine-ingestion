from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PolygonAggregateBar:
    ticker: str
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    adjusted: bool = True


@dataclass(frozen=True)
class PolygonTickerReference:
    ticker: str
    name: str | None = None
    active: bool | None = None
    market: str | None = None
    locale: str | None = None
    primary_exchange: str | None = None
    type: str | None = None
