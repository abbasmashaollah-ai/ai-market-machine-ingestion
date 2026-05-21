from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SymbolSyncPlan:
    universe: str
    vendor: str | None = None
    expected_count: int = 0
    batch_size: int = 0
    symbols: tuple[str, ...] = field(default_factory=tuple)


def build_symbol_sync_plan(
    universe: str,
    *,
    vendor: str | None = None,
    expected_count: int = 0,
    batch_size: int = 0,
    symbols: tuple[str, ...] = (),
) -> SymbolSyncPlan:
    return SymbolSyncPlan(
        universe=universe,
        vendor=vendor,
        expected_count=expected_count,
        batch_size=batch_size,
        symbols=symbols,
    )
