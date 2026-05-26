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
    notes: str | None = None


def build_etf_index_universe_candidates() -> tuple[NormalizedEtfIndexUniverseCandidate, ...]:
    candidates = [
        ("SPY", "core_etf", "core ETF", "etf", "symbol_master", True, "S&P 500 proxy"),
        ("QQQ", "core_etf", "core ETF", "etf", "symbol_master", True, "Nasdaq-100 proxy"),
        ("IWM", "core_etf", "core ETF", "etf", "symbol_master", True, "Russell 2000 proxy"),
        ("DIA", "core_etf", "core ETF", "etf", "symbol_master", True, "Dow Jones proxy"),
        ("XLK", "sector_etf", "sector ETF", "etf", "symbol_master", True, "Technology"),
        ("XLF", "sector_etf", "sector ETF", "etf", "symbol_master", True, "Financials"),
        ("XLE", "sector_etf", "sector ETF", "etf", "symbol_master", True, "Energy"),
        ("XLV", "sector_etf", "sector ETF", "etf", "symbol_master", True, "Health Care"),
        ("XLY", "sector_etf", "sector ETF", "etf", "symbol_master", True, "Consumer Discretionary"),
        ("XLP", "sector_etf", "sector ETF", "etf", "symbol_master", True, "Consumer Staples"),
        ("XLI", "sector_etf", "sector ETF", "etf", "symbol_master", True, "Industrials"),
        ("XLU", "sector_etf", "sector ETF", "etf", "symbol_master", True, "Utilities"),
        ("XLB", "sector_etf", "sector ETF", "etf", "symbol_master", True, "Materials"),
        ("XLRE", "sector_etf", "sector ETF", "etf", "symbol_master", True, "Real Estate"),
        ("XLC", "sector_etf", "sector ETF", "etf", "symbol_master", True, "Communication Services"),
        ("SPX", "major_index", "major index proxy", "index", "symbol_master", True, "SPY proxy for S&P 500"),
        ("NDX", "major_index", "major index proxy", "index", "symbol_master", True, "QQQ proxy for Nasdaq-100"),
        ("RUT", "major_index", "major index proxy", "index", "symbol_master", True, "IWM proxy for Russell 2000"),
        ("DJI", "major_index", "major index proxy", "index", "symbol_master", True, "DIA proxy for Dow Jones"),
        ("XBI", "industry_etf_placeholder", "industry ETF placeholder", "etf", "symbol_master", False, "planned, not active"),
        ("IBB", "industry_etf_placeholder", "industry ETF placeholder", "etf", "symbol_master", False, "planned, not active"),
        ("SMH", "industry_etf_placeholder", "industry ETF placeholder", "etf", "symbol_master", False, "planned, not active"),
    ]
    return tuple(
        NormalizedEtfIndexUniverseCandidate(
            symbol=symbol,
            universe_group=group,
            universe_label=label,
            asset_type=asset_type,
            source=source,
            active_required=active_required,
            notes=notes,
        )
        for symbol, group, label, asset_type, source, active_required, notes in candidates
    )


def summarize_candidate_groups(candidates: tuple[NormalizedEtfIndexUniverseCandidate, ...]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for candidate in candidates:
        counts[candidate.universe_group] = counts.get(candidate.universe_group, 0) + 1
    return counts
