"""Deterministic series fixtures for market feature bundle liquidity/rates."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


LIQUIDITY_RATES_SERIES = ("FED_FUNDS", "US10Y", "US2Y", "REAL_YIELD_10Y", "DXY", "HYG", "SPY", "M2", "QT_QE_PROXY")


def _series_offset(series: str) -> int:
    return sum(ord(char) for char in series) % 17


def _slope_for_scenario(series: str, scenario: str) -> float:
    profiles = {
        "liquidity_tailwind": {
            "FED_FUNDS": -0.015,
            "US10Y": -0.02,
            "US2Y": -0.018,
            "REAL_YIELD_10Y": -0.012,
            "DXY": -0.025,
            "HYG": 0.03,
            "SPY": 0.04,
            "M2": 0.05,
            "QT_QE_PROXY": 0.03,
        },
        "liquidity_headwind": {
            "FED_FUNDS": 0.03,
            "US10Y": 0.04,
            "US2Y": 0.035,
            "REAL_YIELD_10Y": 0.025,
            "DXY": 0.03,
            "HYG": -0.04,
            "SPY": -0.03,
            "M2": -0.02,
            "QT_QE_PROXY": -0.03,
        },
        "mixed": {
            "FED_FUNDS": 0.005,
            "US10Y": -0.004,
            "US2Y": 0.003,
            "REAL_YIELD_10Y": -0.002,
            "DXY": 0.001,
            "HYG": 0.006,
            "SPY": -0.002,
            "M2": 0.004,
            "QT_QE_PROXY": 0.0,
        },
        "tight_conditions": {
            "FED_FUNDS": 0.05,
            "US10Y": 0.045,
            "US2Y": 0.05,
            "REAL_YIELD_10Y": 0.04,
            "DXY": 0.05,
            "HYG": -0.05,
            "SPY": -0.05,
            "M2": -0.04,
            "QT_QE_PROXY": -0.04,
        },
    }
    return profiles.get(scenario, {}).get(series, 0.0)


def _build_history_rows(series: str, scenario: str, rows: int = 65) -> list[dict[str, object]]:
    base = 100.0 + _series_offset(series) * 0.75
    slope = _slope_for_scenario(series, scenario)
    start = datetime(2024, 1, 2, tzinfo=timezone.utc)
    history: list[dict[str, object]] = []
    for index in range(rows):
        oscillation = ((index % 6) - 3) * 0.07
        value = round(base + (index * slope) + oscillation, 4)
        history.append({"timestamp": (start + timedelta(days=index)).isoformat(), "close": value})
    return history


def _build_scenario_histories(scenario: str) -> dict[str, list[dict[str, object]]]:
    return {series: _build_history_rows(series, scenario) for series in LIQUIDITY_RATES_SERIES}


def build_liquidity_rates_series_scenario(scenario: str) -> dict[str, list[dict[str, object]]]:
    normalized = str(scenario).strip().lower()
    if normalized not in {"liquidity_tailwind", "liquidity_headwind", "mixed", "tight_conditions"}:
        raise ValueError(f"unknown liquidity rates scenario: {scenario}")
    return _build_scenario_histories(normalized)


def build_liquidity_rates_series_fixtures() -> dict[str, list[dict[str, object]]]:
    return build_liquidity_rates_series_scenario("liquidity_tailwind")

