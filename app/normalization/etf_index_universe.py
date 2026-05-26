from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NormalizedEtfIndexUniverseCandidate:
    symbol: str
    universe_group: str
    universe_label: str
    asset_type: str
    source: str
    active_required: bool
    index_symbol: str | None = None
    proxy_symbol: str | None = None
    proxy_required: bool = False
    notes: str | None = None


def build_etf_index_universe_candidates() -> tuple[NormalizedEtfIndexUniverseCandidate, ...]:
    return (
        NormalizedEtfIndexUniverseCandidate("SPY", "core_etf", "core ETF", "etf", "symbol_master", True, notes="S&P 500 proxy"),
        NormalizedEtfIndexUniverseCandidate("QQQ", "core_etf", "core ETF", "etf", "symbol_master", True, notes="Nasdaq-100 proxy"),
        NormalizedEtfIndexUniverseCandidate("IWM", "core_etf", "core ETF", "etf", "symbol_master", True, notes="Russell 2000 proxy"),
        NormalizedEtfIndexUniverseCandidate("DIA", "core_etf", "core ETF", "etf", "symbol_master", True, notes="Dow Jones proxy"),
        NormalizedEtfIndexUniverseCandidate("XLK", "sector_etf", "sector ETF", "etf", "symbol_master", True, notes="Technology"),
        NormalizedEtfIndexUniverseCandidate("XLF", "sector_etf", "sector ETF", "etf", "symbol_master", True, notes="Financials"),
        NormalizedEtfIndexUniverseCandidate("XLE", "sector_etf", "sector ETF", "etf", "symbol_master", True, notes="Energy"),
        NormalizedEtfIndexUniverseCandidate("XLV", "sector_etf", "sector ETF", "etf", "symbol_master", True, notes="Health Care"),
        NormalizedEtfIndexUniverseCandidate("XLY", "sector_etf", "sector ETF", "etf", "symbol_master", True, notes="Consumer Discretionary"),
        NormalizedEtfIndexUniverseCandidate("XLP", "sector_etf", "sector ETF", "etf", "symbol_master", True, notes="Consumer Staples"),
        NormalizedEtfIndexUniverseCandidate("XLI", "sector_etf", "sector ETF", "etf", "symbol_master", True, notes="Industrials"),
        NormalizedEtfIndexUniverseCandidate("XLU", "sector_etf", "sector ETF", "etf", "symbol_master", True, notes="Utilities"),
        NormalizedEtfIndexUniverseCandidate("XLB", "sector_etf", "sector ETF", "etf", "symbol_master", True, notes="Materials"),
        NormalizedEtfIndexUniverseCandidate("XLRE", "sector_etf", "sector ETF", "etf", "symbol_master", True, notes="Real Estate"),
        NormalizedEtfIndexUniverseCandidate("XLC", "sector_etf", "sector ETF", "etf", "symbol_master", True, notes="Communication Services"),
        NormalizedEtfIndexUniverseCandidate(
            symbol="SPX",
            universe_group="major_index",
            universe_label="major index label",
            asset_type="index",
            source="symbol_master",
            active_required=False,
            index_symbol="SPX",
            proxy_symbol="SPY",
            proxy_required=True,
            notes="S&P 500 label mapped to SPY",
        ),
        NormalizedEtfIndexUniverseCandidate(
            symbol="NDX",
            universe_group="major_index",
            universe_label="major index label",
            asset_type="index",
            source="symbol_master",
            active_required=False,
            index_symbol="NDX",
            proxy_symbol="QQQ",
            proxy_required=True,
            notes="Nasdaq-100 label mapped to QQQ",
        ),
        NormalizedEtfIndexUniverseCandidate(
            symbol="RUT",
            universe_group="major_index",
            universe_label="major index label",
            asset_type="index",
            source="symbol_master",
            active_required=False,
            index_symbol="RUT",
            proxy_symbol="IWM",
            proxy_required=True,
            notes="Russell 2000 label mapped to IWM",
        ),
        NormalizedEtfIndexUniverseCandidate(
            symbol="DJI",
            universe_group="major_index",
            universe_label="major index label",
            asset_type="index",
            source="symbol_master",
            active_required=False,
            index_symbol="DJI",
            proxy_symbol="DIA",
            proxy_required=True,
            notes="Dow Jones label mapped to DIA",
        ),
        NormalizedEtfIndexUniverseCandidate("XBI", "industry_etf_placeholder", "industry ETF placeholder", "etf", "symbol_master", False, notes="planned, not active"),
        NormalizedEtfIndexUniverseCandidate("IBB", "industry_etf_placeholder", "industry ETF placeholder", "etf", "symbol_master", False, notes="planned, not active"),
        NormalizedEtfIndexUniverseCandidate("SMH", "industry_etf_placeholder", "industry ETF placeholder", "etf", "symbol_master", False, notes="planned, not active"),
    )


def summarize_candidate_groups(candidates: tuple[NormalizedEtfIndexUniverseCandidate, ...]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for candidate in candidates:
        counts[candidate.universe_group] = counts.get(candidate.universe_group, 0) + 1
    return counts
