"""Deterministic volatility index fixtures for feature tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


VOLATILITY_SERIES = ("VIX", "VVIX", "VXN", "RVX")


def _series_offset(series: str) -> int:
    return sum(ord(char) for char in series) % 11


def _trend_for_scenario(series: str, scenario: str) -> float:
    profiles = {
        "low_volatility": {"VIX": -0.08, "VVIX": -0.05, "VXN": -0.03, "RVX": -0.04},
        "elevated_volatility": {"VIX": 0.18, "VVIX": 0.12, "VXN": 0.1, "RVX": 0.11},
        "high_volatility": {"VIX": 0.38, "VVIX": 0.28, "VXN": 0.24, "RVX": 0.22},
        "extreme_volatility": {"VIX": 0.62, "VVIX": 0.5, "VXN": 0.46, "RVX": 0.44},
        "mixed_volatility": {"VIX": 0.16, "VVIX": -0.08, "VXN": 0.11, "RVX": -0.05},
    }
    return profiles.get(scenario, {}).get(series, 0.0)


def _build_history_rows(series: str, scenario: str, rows: int = 65) -> list[dict[str, object]]:
    base = {"VIX": 12.0, "VVIX": 82.0, "VXN": 18.0, "RVX": 21.0}[series]
    slope = _trend_for_scenario(series, scenario)
    start = datetime(2024, 1, 2, tzinfo=timezone.utc)
    history: list[dict[str, object]] = []
    for index in range(rows):
        oscillation = ((index % 6) - 2.5) * 0.08
        value = round(base + (index * slope) + oscillation + (_series_offset(series) * 0.04), 4)
        history.append({"timestamp": (start + timedelta(days=index)).isoformat(), "close": value})
    return history


def _build_scenario_histories(scenario: str) -> dict[str, list[dict[str, object]]]:
    return {series: _build_history_rows(series, scenario) for series in VOLATILITY_SERIES}


def build_volatility_series_scenario(scenario: str) -> dict[str, list[dict[str, object]]]:
    normalized = str(scenario).strip().lower()
    if normalized not in {"low_volatility", "elevated_volatility", "high_volatility", "extreme_volatility", "mixed_volatility"}:
        raise ValueError(f"unknown volatility scenario: {scenario}")
    return _build_scenario_histories(normalized)


def build_volatility_series_fixtures() -> dict[str, list[dict[str, object]]]:
    return build_volatility_series_scenario("low_volatility")
