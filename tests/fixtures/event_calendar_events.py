"""Deterministic event calendar fixtures for feature tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


def _event_date(offset_days: int) -> str:
    return (datetime(2026, 6, 3, tzinfo=timezone.utc) + timedelta(days=offset_days)).date().isoformat()


def _build_event(event_id: str, offset_days: int, event_type: str, title: str, impact: str, symbol: str | None = None) -> dict[str, object]:
    payload = {
        "event_id": event_id,
        "event_date": _event_date(offset_days),
        "event_type": event_type,
        "title": title,
        "impact": impact,
        "source": "fixture_event_calendar",
    }
    if symbol is not None:
        payload["symbol"] = symbol
    return payload


def build_event_calendar_events_scenario(scenario: str) -> list[dict[str, object]]:
    normalized = str(scenario).strip().lower()
    if normalized == "quiet_week":
        return [
            _build_event("Q1", 4, "HOLIDAY", "Market Holiday", "LOW"),
            _build_event("Q2", 6, "OTHER", "Low Impact Advisory", "LOW"),
        ]
    if normalized == "fed_cpi_week":
        return [
            _build_event("F1", 1, "FED", "FOMC Decision", "HIGH"),
            _build_event("C1", 3, "CPI", "CPI Release", "HIGH"),
            _build_event("J1", 5, "JOBS", "Jobs Report", "MEDIUM"),
            _build_event("E1", 7, "EARNINGS", "Mega-cap Earnings", "MEDIUM", symbol="AAPL"),
        ]
    if normalized == "earnings_heavy_week":
        return [
            _build_event("E1", 1, "EARNINGS", "AAPL Earnings", "HIGH", symbol="AAPL"),
            _build_event("E2", 1, "EARNINGS", "MSFT Earnings", "HIGH", symbol="MSFT"),
            _build_event("E3", 2, "EARNINGS", "AMZN Earnings", "MEDIUM", symbol="AMZN"),
            _build_event("E4", 3, "EARNINGS", "GOOGL Earnings", "MEDIUM", symbol="GOOGL"),
        ]
    if normalized == "opex_week":
        return [
            _build_event("O1", 2, "OPEX", "Monthly OPEX", "HIGH"),
            _build_event("O2", 4, "TREASURY_AUCTION", "10Y Auction", "MEDIUM"),
            _build_event("O3", 5, "HOLIDAY", "Observed Holiday", "LOW"),
        ]
    if normalized == "extreme_macro_week":
        return [
            _build_event("M1", 0, "FED", "FOMC Decision", "HIGH"),
            _build_event("M2", 1, "CPI", "CPI Release", "HIGH"),
            _build_event("M3", 2, "PPI", "PPI Release", "HIGH"),
            _build_event("M4", 3, "JOBS", "Jobs Report", "HIGH"),
            _build_event("M5", 4, "GDP", "GDP Release", "HIGH"),
            _build_event("M6", 5, "TREASURY_AUCTION", "20Y Auction", "HIGH"),
            _build_event("M7", 6, "OPEX", "OPEX", "HIGH"),
        ]
    raise ValueError(f"unknown event calendar scenario: {scenario}")

