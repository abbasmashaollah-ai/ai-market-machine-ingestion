"""Deterministic OHLCV fixtures for market feature bundle breadth."""

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

_BROAD_STRENGTH = {"AAPL", "MSFT", "NVDA", "META", "AVGO", "MA", "SPY", "AMZN", "GOOGL", "TSLA", "LLY", "COST"}
_BROAD_WEAKNESS = {"XOM", "JPM", "PG", "KO", "PEP", "HD", "UNH", "DIS"}
_MIXED = {"AAPL", "MSFT", "NVDA", "XOM", "JPM", "PG", "SPY", "AMZN"}
_NARROW_STRENGTH = {"AAPL", "MSFT", "NVDA"}


def _symbol_offset(symbol: str) -> int:
    return sum(ord(char) for char in symbol) % 19


def _trend_profile(symbol: str, scenario: str) -> float:
    if scenario == "broad_strength":
        if symbol in _BROAD_STRENGTH:
            return 0.42
        if symbol in _BROAD_WEAKNESS:
            return -0.31
        return 0.0
    if scenario == "broad_weakness":
        if symbol in _BROAD_WEAKNESS:
            return -0.42
        if symbol in _BROAD_STRENGTH:
            return 0.12
        return -0.06
    if scenario == "mixed":
        if symbol in _MIXED:
            return 0.18 if symbol in {"AAPL", "MSFT", "NVDA", "SPY"} else -0.17
        return 0.0
    if scenario == "narrow_strength":
        if symbol in _NARROW_STRENGTH:
            return 0.55
        return 0.0
    if symbol in {"AAPL", "MSFT", "NVDA", "META", "AVGO", "MA"}:
        return 0.42
    if symbol in {"XOM", "JPM", "PG", "KO", "PEP", "HD"}:
        return -0.31
    if symbol in {"SPY", "AMZN", "GOOGL", "TSLA", "UNH", "LLY", "COST", "DIS"}:
        return 0.0
    return 0.12


def _build_history_rows(symbol: str, scenario: str, rows: int = 65) -> list[dict[str, object]]:
    base = 90.0 + (_symbol_offset(symbol) * 1.5)
    slope = _trend_profile(symbol, scenario)
    start = datetime(2024, 1, 2, tzinfo=timezone.utc)
    history: list[dict[str, object]] = []
    for index in range(rows):
        oscillation = ((index % 6) - 2.5) * 0.17
        close = round(base + (index * slope) + oscillation, 2)
        if scenario == "broad_strength" and symbol in {"SPY", "AMZN", "GOOGL", "TSLA", "UNH", "LLY", "COST", "DIS"} and index == rows - 1:
            close = round(base + ((rows - 2) * slope) + oscillation, 2)
        if scenario == "narrow_strength" and symbol not in _NARROW_STRENGTH and index == rows - 1:
            close = round(base + oscillation, 2)
        volume = float(1_000_000 + (_symbol_offset(symbol) * 25_000) + (index * 8_000))
        history.append({"timestamp": (start + timedelta(days=index)).isoformat(), "close": close, "volume": volume})
    return history


def _build_scenario_histories(scenario: str) -> tuple[dict[str, list[dict[str, object]]], dict[str, list[dict[str, object]]]]:
    close_history_by_symbol = {symbol: _build_history_rows(symbol, scenario) for symbol in BREADTH_FIXTURE_SYMBOLS}
    for symbol, history in close_history_by_symbol.items():
        if len(history) < 2:
            continue
        prev_close = float(history[-2]["close"])
        last_close = float(history[-1]["close"])
        if scenario == "broad_weakness":
            if symbol in _BROAD_WEAKNESS:
                history[-1]["close"] = round(prev_close - abs(last_close - prev_close) - 0.35, 2)
            else:
                history[-1]["close"] = round(prev_close - 0.12, 2)
        elif scenario == "mixed":
            if symbol in {"AAPL", "MSFT", "NVDA", "SPY"}:
                history[-1]["close"] = round(prev_close + abs(last_close - prev_close) + 0.15, 2)
            elif symbol in {"XOM", "JPM", "PG"}:
                history[-1]["close"] = round(prev_close - abs(last_close - prev_close) - 0.2, 2)
            else:
                history[-1]["close"] = prev_close
        elif scenario == "narrow_strength":
            if symbol in _NARROW_STRENGTH:
                history[-1]["close"] = round(prev_close + abs(last_close - prev_close) + 0.5, 2)
            else:
                history[-1]["close"] = prev_close
    volume_history_by_symbol = {
        symbol: [{"timestamp": row["timestamp"], "volume": row["volume"]} for row in history]
        for symbol, history in close_history_by_symbol.items()
    }
    return close_history_by_symbol, volume_history_by_symbol


def build_breadth_fixture_histories_scenario(scenario: str) -> tuple[dict[str, list[dict[str, object]]], dict[str, list[dict[str, object]]]]:
    normalized = str(scenario).strip().lower()
    if normalized not in {"broad_strength", "broad_weakness", "mixed", "narrow_strength"}:
        raise ValueError(f"unknown breadth scenario: {scenario}")
    return _build_scenario_histories(normalized)

