from __future__ import annotations

from dataclasses import dataclass, field

from app.normalization.volatility_index import STARTER_VOLATILITY_INDEX_SYMBOLS


@dataclass(frozen=True)
class VolatilityIndexSourceCandidate:
    source_name: str
    supported_symbols: tuple[str, ...] = field(default_factory=tuple)
    historical_coverage_note: str = ""
    vendor_symbol_mapping_note: str = ""
    rate_limit_cost_notes: str = ""
    status: str = "planned"
    priority: int = 0


def build_volatility_index_source_candidates() -> tuple[VolatilityIndexSourceCandidate, ...]:
    return (
        VolatilityIndexSourceCandidate(
            source_name="Polygon",
            supported_symbols=STARTER_VOLATILITY_INDEX_SYMBOLS,
            historical_coverage_note="Best fit for broad historical reference coverage if approved later.",
            vendor_symbol_mapping_note="Likely maps canonical symbols to Polygon vendor tickers such as I:VIX variants where applicable.",
            rate_limit_cost_notes="Likely higher-cost reference access; use sparingly and cache outputs.",
            status="planned",
            priority=1,
        ),
        VolatilityIndexSourceCandidate(
            source_name="Cboe",
            supported_symbols=STARTER_VOLATILITY_INDEX_SYMBOLS,
            historical_coverage_note="Likely strongest native source for Cboe-family volatility indexes if approved later.",
            vendor_symbol_mapping_note="Expected to preserve canonical symbols while mapping to vendor-native identifiers where needed.",
            rate_limit_cost_notes="Potentially lower mapping overhead but vendor terms still need explicit approval.",
            status="planned",
            priority=2,
        ),
        VolatilityIndexSourceCandidate(
            source_name="manual fixture",
            supported_symbols=STARTER_VOLATILITY_INDEX_SYMBOLS,
            historical_coverage_note="Test-only baseline fixture with deterministic sample coverage only.",
            vendor_symbol_mapping_note="Uses canonical symbols directly and does not require external vendor mapping.",
            rate_limit_cost_notes="No external requests; test/dry-run only.",
            status="test_only",
            priority=99,
        ),
    )
