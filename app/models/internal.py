from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RuntimeIdentity:
    run_id: str
    environment: str


@dataclass(frozen=True)
class RuntimeScope:
    vendor: str | None = None
    dataset: str | None = None
    symbol: str | None = None
    timeframe: str | None = None


@dataclass(frozen=True)
class RuntimeEnvelope:
    identity: RuntimeIdentity
    scope: RuntimeScope
    created_at: datetime
