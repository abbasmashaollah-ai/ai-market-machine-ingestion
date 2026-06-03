"""Sector rotation universe contract and helpers."""

from __future__ import annotations

from dataclasses import dataclass

SPY_BENCHMARK = "SPY"
SECTOR_ROTATION_UNIVERSE = "SPDR_SECTORS"


@dataclass(frozen=True, slots=True)
class SectorDefinition:
    symbol: str
    name: str
    is_defensive_sector: bool = False
    is_cyclical_sector: bool = False
    is_growth_sector: bool = False
    is_rate_sensitive_sector: bool = False


_SECTOR_DEFINITIONS: tuple[SectorDefinition, ...] = (
    SectorDefinition("XLC", "Communication Services", is_growth_sector=True),
    SectorDefinition("XLY", "Consumer Discretionary", is_cyclical_sector=True, is_growth_sector=True),
    SectorDefinition("XLP", "Consumer Staples", is_defensive_sector=True),
    SectorDefinition("XLE", "Energy", is_cyclical_sector=True, is_rate_sensitive_sector=True),
    SectorDefinition("XLF", "Financials", is_cyclical_sector=True, is_rate_sensitive_sector=True),
    SectorDefinition("XLV", "Health Care", is_defensive_sector=True),
    SectorDefinition("XLI", "Industrials", is_cyclical_sector=True),
    SectorDefinition("XLB", "Materials", is_cyclical_sector=True),
    SectorDefinition("XLRE", "Real Estate", is_defensive_sector=True, is_rate_sensitive_sector=True),
    SectorDefinition("XLK", "Technology", is_growth_sector=True),
    SectorDefinition("XLU", "Utilities", is_defensive_sector=True, is_rate_sensitive_sector=True),
)

_SECTOR_BY_SYMBOL = {definition.symbol: definition for definition in _SECTOR_DEFINITIONS}


def get_spdr_sector_definitions() -> tuple[SectorDefinition, ...]:
    """Return the fixed SPDR sector definitions in deterministic order."""

    return _SECTOR_DEFINITIONS


def get_sector_symbols() -> tuple[str, ...]:
    """Return the fixed sector symbols in deterministic order."""

    return tuple(definition.symbol for definition in _SECTOR_DEFINITIONS)


def get_required_symbols(include_benchmark: bool = True) -> tuple[str, ...]:
    """Return the required symbols for sector rotation work."""

    sector_symbols = get_sector_symbols()
    if include_benchmark:
        return (SPY_BENCHMARK, *sector_symbols)
    return sector_symbols


def is_sector_symbol(symbol: str) -> bool:
    """Return True when symbol belongs to the SPDR sector universe."""

    return symbol.strip().upper() in _SECTOR_BY_SYMBOL


def get_sector_definition(symbol: str) -> SectorDefinition:
    """Return the sector definition for symbol.

    Raises:
        ValueError: If symbol is empty or missing.
        KeyError: If symbol is not part of the sector universe.
    """

    normalized = symbol.strip().upper()
    if not normalized:
        raise ValueError("sector symbol is required")
    try:
        return _SECTOR_BY_SYMBOL[normalized]
    except KeyError as exc:
        raise KeyError(f"unknown SPDR sector symbol: {symbol!r}") from exc

