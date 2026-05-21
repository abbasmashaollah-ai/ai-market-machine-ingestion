from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FredObservation:
    series_id: str
    date: str
    value: str | None = None
    realtime_start: str | None = None
    realtime_end: str | None = None


@dataclass(frozen=True)
class FredSeriesMetadata:
    series_id: str
    title: str | None = None
    frequency: str | None = None
    units: str | None = None
    seasonal_adjustment: str | None = None
    observation_start: str | None = None
    observation_end: str | None = None
