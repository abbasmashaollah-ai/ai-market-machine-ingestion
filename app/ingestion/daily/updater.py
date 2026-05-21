from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Protocol


@dataclass(frozen=True)
class DailyUpdateRequest:
    vendor: str
    dataset: str
    trading_date: date
    symbol: str | None = None
    timeframe: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)


class DailyUpdater(Protocol):
    def run(self, request: DailyUpdateRequest) -> None:
        ...
