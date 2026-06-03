"""Deterministic OHLCV fixtures for breadth feature tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


BREADTH_FIXTURE_SYMBOLS = (
    "SPY",
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "META",
    "GOOGL",
    "TSLA",
    "JPM",
    "XOM",
    "UNH",
    "LLY",
    "AVGO",
    "COST",
    "PG",
    "KO",
    "PEP",
    "HD",
    "MA",
    "DIS",
)


def _symbol_offset(symbol: str) -> int:
    return sum(ord(char) for char in symbol) % 19


def _trend_profile(symbol: str) -> float:
    if symbol in {"AAPL", "MSFT", "NVDA", "META", "AVGO", "MA"}:
        return 0.42
    if symbol in {"XOM", "JPM", "PG", "KO", "PEP", "HD"}:
        return -0.31
    if symbol in {"SPY", "AMZN", "GOOGL", "TSLA", "UNH", "LLY", "COST", "DIS"}:
        return 0.0
    return 0.12


def _build_history_rows(symbol: str, rows: int = 65) -> list[dict[str, object]]:
    base = 90.0 + (_symbol_offset(symbol) * 1.5)
    slope = _trend_profile(symbol)
    start = datetime(2024, 1, 2, tzinfo=timezone.utc)
    history: list[dict[str, object]] = []
    for index in range(rows):
        oscillation = ((index % 6) - 2.5) * 0.17
        close = round(base + (index * slope) + oscillation, 2)
        if symbol in {"SPY", "AMZN", "GOOGL", "TSLA", "UNH", "LLY", "COST", "DIS"} and index == rows - 1:
            close = round(base + ((rows - 2) * slope) + oscillation, 2)
        volume = float(1_000_000 + (_symbol_offset(symbol) * 25_000) + (index * 8_000))
        history.append(
            {
                "timestamp": (start + timedelta(days=index)).isoformat(),
                "close": close,
                "volume": volume,
            }
        )
    return history


def build_breadth_ohlcv_fixtures() -> dict[str, list[dict[str, object]]]:
    return {symbol: _build_history_rows(symbol) for symbol in BREADTH_FIXTURE_SYMBOLS}
