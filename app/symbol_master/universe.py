from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class UniverseName(str, Enum):
    US_EQUITIES = "us_equities"
    ETFS = "etfs"
    INDEXES = "indexes"


@dataclass(frozen=True)
class UniverseRequest:
    universe: UniverseName
    vendor: str | None = None
    as_of: str | None = None
    symbols: tuple[str, ...] = field(default_factory=tuple)


def build_universe_request(
    universe: str,
    *,
    vendor: str | None = None,
    as_of: str | None = None,
    symbols: tuple[str, ...] = (),
) -> UniverseRequest:
    return UniverseRequest(universe=UniverseName(universe), vendor=vendor, as_of=as_of, symbols=symbols)
