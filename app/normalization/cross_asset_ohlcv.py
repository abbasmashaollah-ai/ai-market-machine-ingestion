from __future__ import annotations

from dataclasses import dataclass

from app.normalization.common import safe_date, safe_number, safe_text


@dataclass(frozen=True)
class NormalizedCrossAssetOhlcvRecord:
    symbol: str | None
    asset_group: str | None
    market_date: str | None
    open: float | None
    high: float | None
    low: float | None
    close: float | None
    volume: float | None
    source: str | None
    vendor_symbol: str | None
    notes: str | None


DEFAULT_FIXTURE_RECORDS: tuple[dict[str, object], ...] = (
    {
        "symbol": "TLT",
        "asset_group": "bonds/rates proxy",
        "market_date": "2026-05-29",
        "open": 92.1,
        "high": 92.8,
        "low": 91.9,
        "close": 92.4,
        "volume": 1234567,
        "source": "manual_fixture",
        "vendor_symbol": "TLT",
        "notes": "deterministic fixture",
    },
    {
        "symbol": "UUP",
        "asset_group": "DXY / dollar index proxy",
        "market_date": "2026-05-29",
        "open": 28.4,
        "high": 28.6,
        "low": 28.3,
        "close": 28.55,
        "volume": 456789,
        "source": "manual_fixture",
        "vendor_symbol": "UUP",
        "notes": "deterministic fixture",
    },
    {
        "symbol": "GLD",
        "asset_group": "commodity proxy",
        "market_date": "2026-05-29",
        "open": 212.0,
        "high": 213.1,
        "low": 211.4,
        "close": 212.7,
        "volume": 765432,
        "source": "manual_fixture",
        "vendor_symbol": "GLD",
        "notes": "deterministic fixture",
    },
    {
        "symbol": "BTC-USD",
        "asset_group": "crypto proxy",
        "market_date": "2026-05-29",
        "open": 68250.0,
        "high": 68980.0,
        "low": 67810.0,
        "close": 68720.0,
        "volume": 9876.0,
        "source": "manual_fixture",
        "vendor_symbol": "BTC-USD",
        "notes": "deterministic fixture",
    },
    {
        "symbol": "EURUSD",
        "asset_group": "FX proxy",
        "market_date": "2026-05-29",
        "open": 1.082,
        "high": 1.085,
        "low": 1.079,
        "close": 1.083,
        "volume": 0.0,
        "source": "manual_fixture",
        "vendor_symbol": "EURUSD",
        "notes": "deterministic fixture",
    },
)


def normalize_cross_asset_ohlcv_record(payload: dict[str, object]) -> NormalizedCrossAssetOhlcvRecord:
    return NormalizedCrossAssetOhlcvRecord(
        symbol=safe_text(payload.get("symbol")),
        asset_group=safe_text(payload.get("asset_group")),
        market_date=safe_text(safe_date(payload.get("market_date"))),
        open=safe_number(payload.get("open")),
        high=safe_number(payload.get("high")),
        low=safe_number(payload.get("low")),
        close=safe_number(payload.get("close")),
        volume=safe_number(payload.get("volume")),
        source=safe_text(payload.get("source")),
        vendor_symbol=safe_text(payload.get("vendor_symbol")),
        notes=safe_text(payload.get("notes")),
    )


def validate_cross_asset_ohlcv_record(record: NormalizedCrossAssetOhlcvRecord) -> tuple[str, ...]:
    errors: list[str] = []
    if not record.symbol:
        errors.append("symbol is required")
    if not record.asset_group:
        errors.append("asset_group is required")
    if not record.market_date:
        errors.append("market_date is required")
    if record.open is None:
        errors.append("open is required")
    if record.high is None:
        errors.append("high is required")
    if record.low is None:
        errors.append("low is required")
    if record.close is None:
        errors.append("close is required")
    if record.volume is None:
        errors.append("volume is required")
    if not record.source:
        errors.append("source is required")
    if not record.vendor_symbol:
        errors.append("vendor_symbol is required")
    if not record.notes:
        errors.append("notes is required")
    return tuple(errors)
