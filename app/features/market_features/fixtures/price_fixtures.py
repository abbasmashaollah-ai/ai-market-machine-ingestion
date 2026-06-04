"""Deterministic OHLCV fixtures for market feature bundle prices."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


def _symbol_offset(symbol: str) -> int:
    return sum(ord(char) for char in symbol) % 13


def _build_ohlcv_history(symbol: str, rows: int = 65) -> list[dict[str, object]]:
    base = {"SPY": 100.0, "AAPL": 150.0, "MSFT": 200.0}[symbol]
    offset = _symbol_offset(symbol)
    start = datetime(2024, 1, 2, tzinfo=timezone.utc)
    history: list[dict[str, object]] = []
    previous_close: float | None = None
    for index in range(rows):
        drift = (index * 0.35) if symbol != "MSFT" else (index * 0.22)
        seasonal = ((index % 7) - 3) * 0.11
        close = round(base + drift + seasonal + (offset * 0.05), 2)
        open_price = round(previous_close if previous_close is not None else close - 0.18, 2)
        high = round(max(open_price, close) + 0.42 + (index % 4) * 0.03, 2)
        low = round(min(open_price, close) - 0.55 - (index % 3) * 0.02, 2)
        volume = int(1_000_000 + index * 17_500 + offset * 1_000)
        history.append(
            {
                "timestamp": (start + timedelta(days=index)).isoformat(),
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
            }
        )
        previous_close = close
    return history


def build_price_ohlcv_fixtures() -> dict[str, list[dict[str, object]]]:
    return {symbol: _build_ohlcv_history(symbol) for symbol in ("SPY", "AAPL", "MSFT")}
