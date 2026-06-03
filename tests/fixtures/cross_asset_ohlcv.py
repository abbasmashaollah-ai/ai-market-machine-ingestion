"""Deterministic OHLCV fixtures for cross-asset feature tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


CROSS_ASSET_SYMBOLS = ("SPY", "QQQ", "IWM", "TLT", "HYG", "GLD", "USO", "DXY", "VIX")


def _symbol_offset(symbol: str) -> int:
    return sum(ord(char) for char in symbol) % 23


def _trend_profile(symbol: str, scenario: str) -> float:
    if scenario == "risk_on":
        return {
            "SPY": 0.45,
            "QQQ": 0.5,
            "IWM": 0.4,
            "HYG": 0.22,
            "TLT": -0.18,
            "GLD": 0.03,
            "USO": 0.08,
            "DXY": -0.12,
            "VIX": -0.25,
        }.get(symbol, 0.0)
    if scenario == "risk_off":
        return {
            "SPY": -0.34,
            "QQQ": -0.31,
            "IWM": -0.38,
            "HYG": -0.28,
            "TLT": 0.35,
            "GLD": 0.18,
            "USO": -0.09,
            "DXY": 0.2,
            "VIX": 0.4,
        }.get(symbol, 0.0)
    if scenario == "mixed":
        return {
            "SPY": 0.12,
            "QQQ": 0.18,
            "IWM": -0.08,
            "HYG": 0.05,
            "TLT": -0.05,
            "GLD": 0.02,
            "USO": -0.04,
            "DXY": 0.03,
            "VIX": 0.06,
        }.get(symbol, 0.0)
    if scenario == "equity_credit_divergence":
        return {
            "SPY": 0.38,
            "QQQ": 0.42,
            "IWM": 0.31,
            "HYG": -0.26,
            "TLT": -0.12,
            "GLD": 0.04,
            "USO": 0.02,
            "DXY": -0.03,
            "VIX": -0.08,
        }.get(symbol, 0.0)
    return 0.0


def _build_history_rows(symbol: str, scenario: str, rows: int = 65) -> list[dict[str, object]]:
    base = 80.0 + (_symbol_offset(symbol) * 1.7)
    slope = _trend_profile(symbol, scenario)
    start = datetime(2024, 1, 2, tzinfo=timezone.utc)
    history: list[dict[str, object]] = []
    for index in range(rows):
        oscillation = ((index % 5) - 2) * 0.14
        close = round(base + (index * slope) + oscillation, 2)
        volume = float(900_000 + (_symbol_offset(symbol) * 17_000) + (index * 6_500))
        history.append({"timestamp": (start + timedelta(days=index)).isoformat(), "close": close, "volume": volume})
    return history


def _build_scenario_histories(scenario: str) -> tuple[dict[str, list[dict[str, object]]], dict[str, list[dict[str, object]]]]:
    close_history_by_symbol = {symbol: _build_history_rows(symbol, scenario) for symbol in CROSS_ASSET_SYMBOLS}
    target_signs = {
        "risk_on": {"SPY": 1, "QQQ": 1, "IWM": 1, "TLT": 1, "HYG": 1, "GLD": 1, "USO": 1, "DXY": 1, "VIX": 1},
        "risk_off": {"SPY": -1, "QQQ": -1, "IWM": -1, "TLT": -1, "HYG": -1, "GLD": -1, "USO": -1, "DXY": -1, "VIX": -1},
        "mixed": {"SPY": 1, "QQQ": 1, "IWM": -1, "TLT": -1, "HYG": 1, "GLD": -1, "USO": 1, "DXY": -1, "VIX": 1},
        "equity_credit_divergence": {"SPY": 1, "QQQ": 1, "IWM": 1, "TLT": -1, "HYG": -1, "GLD": 1, "USO": 1, "DXY": -1, "VIX": -1},
    }
    if scenario in target_signs:
        for symbol, history in close_history_by_symbol.items():
            prev_close = float(history[-2]["close"])
            last_close = float(history[-1]["close"])
            sign = target_signs[scenario][symbol]
            delta = max(abs(last_close - prev_close), 0.35)
            history[-1]["close"] = round(prev_close + delta + 0.2, 2) if sign > 0 else round(prev_close - delta - 0.2, 2)
    volume_history_by_symbol = {
        symbol: [{"timestamp": row["timestamp"], "volume": row["volume"]} for row in history]
        for symbol, history in close_history_by_symbol.items()
    }
    return close_history_by_symbol, volume_history_by_symbol


def build_cross_asset_fixture_histories_scenario(scenario: str) -> tuple[dict[str, list[dict[str, object]]], dict[str, list[dict[str, object]]]]:
    normalized = str(scenario).strip().lower()
    if normalized not in {"risk_on", "risk_off", "mixed", "equity_credit_divergence"}:
        raise ValueError(f"unknown cross asset scenario: {scenario}")
    return _build_scenario_histories(normalized)


def build_cross_asset_ohlcv_fixtures() -> dict[str, list[dict[str, object]]]:
    close_history_by_symbol, _ = build_cross_asset_fixture_histories_scenario("risk_on")
    return close_history_by_symbol