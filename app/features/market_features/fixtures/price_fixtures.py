"""Deterministic close-history fixtures for market feature bundle prices."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


def _symbol_offset(symbol: str) -> int:
    return sum(ord(char) for char in symbol) % 13


def _build_close_history(symbol: str, rows: int = 65) -> list[dict[str, object]]:
    base = {"SPY": 100.0, "AAPL": 150.0, "MSFT": 200.0}[symbol]
    offset = _symbol_offset(symbol)
    start = datetime(2024, 1, 2, tzinfo=timezone.utc)
    history: list[dict[str, object]] = []
    for index in range(rows):
        drift = (index * 0.35) if symbol != "MSFT" else (index * 0.22)
        seasonal = ((index % 7) - 3) * 0.11
        close = round(base + drift + seasonal + (offset * 0.05), 2)
        history.append({"timestamp": (start + timedelta(days=index)).isoformat(), "close": close})
    return history


def build_price_ohlcv_fixtures() -> dict[str, list[dict[str, object]]]:
    return {symbol: _build_close_history(symbol) for symbol in ("SPY", "AAPL", "MSFT")}
