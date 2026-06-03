"""Deterministic production-shaped OHLCV fixtures for sector rotation tests."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable

from app.features.sector_rotation.sector_universe import get_required_symbols


SECTOR_ROTATION_FIXTURE_SYMBOLS = tuple(get_required_symbols(include_benchmark=True))


@dataclass(frozen=True, slots=True)
class FakeSectorRotationDataReadClient:
    payload_by_symbol: dict[str, dict[str, object]]
    calls: tuple[tuple[str, dict[str, object]], ...] = ()

    def get_symbol_ohlcv_history(self, symbol, start_date=None, end_date=None, limit=None, order="asc"):
        symbol_key = str(symbol).upper()
        call = (
            symbol_key,
            {
                "start_date": start_date,
                "end_date": end_date,
                "limit": limit,
                "order": order,
            },
        )
        object.__setattr__(self, "calls", self.calls + (call,))
        return self.payload_by_symbol[symbol_key]


def _symbol_offset(symbol: str) -> int:
    return sum(ord(char) for char in symbol) % 17


def _build_history_rows(symbol: str, rows: int = 65) -> list[dict[str, object]]:
    base = 100.0 + _symbol_offset(symbol)
    slope = 0.12 + (_symbol_offset(symbol) % 5) * 0.03
    start = datetime(2024, 1, 2, tzinfo=timezone.utc)
    history: list[dict[str, object]] = []
    for index in range(rows):
        close = round(base + (index * slope), 2)
        open_value = round(close - 0.18, 2)
        high = round(close + 0.21, 2)
        low = round(close - 0.29, 2)
        volume = float(1_000_000 + (_symbol_offset(symbol) * 10_000) + index * 5_000)
        history.append(
            {
                "id": index + 1,
                "symbol": symbol,
                "timestamp": (start + timedelta(days=index)).isoformat(),
                "open": open_value,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
                "source": "FIXTURE",
                "adjustment_status": "UNADJUSTED",
                "data_quality_status": "VALIDATED",
                "timeframe": "1d",
                "adjusted": False,
            }
        )
    return history


def build_sector_rotation_ohlcv_payload(symbol: str) -> dict[str, object]:
    normalized = str(symbol).upper()
    if normalized not in SECTOR_ROTATION_FIXTURE_SYMBOLS:
        raise KeyError(f"unknown sector rotation fixture symbol: {symbol}")

    historical_ohlcv = _build_history_rows(normalized)
    return {
        "symbol": normalized,
        "symbol_metadata": {
            "symbol": normalized,
            "universe": "SPDR_SECTORS",
        },
        "historical_ohlcv": historical_ohlcv,
        "ohlcv_coverage": {
            "symbol": normalized,
            "rows": len(historical_ohlcv),
            "coverage_status": "COMPLETE",
            "quality_status": "PASS",
            "certification_status": "CERTIFIED",
            "warnings": [],
        },
        "freshness_status": "UNKNOWN",
        "coverage_status": "COMPLETE",
        "quality_status": "PASS",
        "certification_status": "CERTIFIED",
        "warnings": [],
    }


def build_all_sector_rotation_ohlcv_payloads() -> dict[str, dict[str, object]]:
    return {symbol: build_sector_rotation_ohlcv_payload(symbol) for symbol in SECTOR_ROTATION_FIXTURE_SYMBOLS}


def build_fake_data_read_client_for_sector_rotation() -> FakeSectorRotationDataReadClient:
    return FakeSectorRotationDataReadClient(payload_by_symbol=build_all_sector_rotation_ohlcv_payloads())
