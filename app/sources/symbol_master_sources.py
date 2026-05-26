from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SymbolMasterSourcePlan:
    source_name: str
    supported_asset_types: tuple[str, ...] = field(default_factory=tuple)
    active_delisted_support: str = "unknown"
    vendor_symbol_support: bool = False
    exchange_support: bool = False
    rate_limit_cost_notes: str = ""
    status: str = "planned"
    priority: int = 0


def build_symbol_master_source_plan() -> tuple[SymbolMasterSourcePlan, ...]:
    return (
        SymbolMasterSourcePlan(
            source_name="FMP",
            supported_asset_types=("equity", "etf"),
            active_delisted_support=True,
            vendor_symbol_support=True,
            exchange_support=True,
            rate_limit_cost_notes="Expected low-cost public/paid API usage; exact quota depends on plan.",
            status="planned",
            priority=1,
        ),
        SymbolMasterSourcePlan(
            source_name="Polygon",
            supported_asset_types=("equity", "etf", "index"),
            active_delisted_support=True,
            vendor_symbol_support=True,
            exchange_support=True,
            rate_limit_cost_notes="Expected higher-cost reference access; use sparingly and cache results.",
            status="planned",
            priority=2,
        ),
        SymbolMasterSourcePlan(
            source_name="SEC",
            supported_asset_types=("equity",),
            active_delisted_support=False,
            vendor_symbol_support=False,
            exchange_support=False,
            rate_limit_cost_notes="Later enrichment only; no live symbol-master resolution path yet.",
            status="planned",
            priority=3,
        ),
        SymbolMasterSourcePlan(
            source_name="Nasdaq/official listings",
            supported_asset_types=("equity", "etf"),
            active_delisted_support=True,
            vendor_symbol_support=True,
            exchange_support=True,
            rate_limit_cost_notes="Use only if a stable official listing contract is approved.",
            status="planned",
            priority=4,
        ),
        SymbolMasterSourcePlan(
            source_name="manual fixture",
            supported_asset_types=("equity", "etf", "index"),
            active_delisted_support=True,
            vendor_symbol_support=True,
            exchange_support=True,
            rate_limit_cost_notes="Test/dry-run only; no external requests.",
            status="test_only",
            priority=99,
        ),
    )
