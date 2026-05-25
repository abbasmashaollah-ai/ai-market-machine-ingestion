from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Protocol

from app.models.normalized import NormalizedOHLCVRecord
from app.vendors.polygon.mapper import polygon_aggregate_to_normalized_ohlcv

POLYGON_VOLATILITY_SYMBOL_MAP: dict[str, str] = {
    "VIX": "I:VIX",
    "VVIX": "I:VVIX",
    "VXN": "I:VXN",
    "RVX": "I:RVX",
}


class PolygonVolatilityFetchAdapter(Protocol):
    def fetch_aggregates_raw(self, ticker: str, from_date: str, to_date: str) -> list[dict[str, object]]:
        ...


@dataclass(frozen=True)
class PolygonVolatilityRecordPlan:
    requested_symbol: str
    canonical_symbol: str
    vendor_symbol: str
    payload: dict[str, object]
    is_valid: bool
    errors: tuple[str, ...] = ()
    canonical_record: NormalizedOHLCVRecord | None = None


@dataclass(frozen=True)
class PolygonVolatilityPlan:
    requested_symbol: str
    canonical_symbol: str
    vendor_symbol: str
    requested_start_date: date
    requested_end_date: date
    timeframe: str
    fetch_enabled: bool
    payload_count: int
    valid_count: int
    invalid_count: int
    dry_run: bool = True
    errors: tuple[str, ...] = ()
    records: tuple[PolygonVolatilityRecordPlan, ...] = ()
    source: str = "polygon_aggregates"
    status: str = "planned"


@dataclass(frozen=True)
class PolygonVolatilityBatchPlan:
    requested_symbols: tuple[str, ...]
    requested_start_date: date
    requested_end_date: date
    timeframe: str
    fetch_enabled: bool
    total_payload_count: int
    total_valid_count: int
    total_invalid_count: int
    dry_run: bool = True
    symbol_plans: tuple[PolygonVolatilityPlan, ...] = ()
    batch_errors: tuple[dict[str, object], ...] = field(default_factory=tuple)
    status: str = "planned"


def canonical_volatility_symbol_to_polygon_symbol(symbol: str) -> str:
    normalized = symbol.strip().upper()
    if normalized not in POLYGON_VOLATILITY_SYMBOL_MAP:
        raise ValueError(f"unsupported volatility symbol: {symbol}")
    return POLYGON_VOLATILITY_SYMBOL_MAP[normalized]


def polygon_symbol_to_canonical_volatility_symbol(symbol: str) -> str:
    normalized = symbol.strip().upper()
    for canonical, polygon_symbol in POLYGON_VOLATILITY_SYMBOL_MAP.items():
        if polygon_symbol == normalized:
            return canonical
    raise ValueError(f"unsupported polygon volatility symbol: {symbol}")


def validate_polygon_volatility_payload(payload: dict[str, object]) -> tuple[bool, tuple[str, ...]]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return False, ("payload must be a dict",)
    if payload.get("ticker") is None and payload.get("symbol") is None:
        errors.append("ticker is required")
    for field_name in ("t", "date"):
        if payload.get(field_name) is not None:
            break
    else:
        errors.append("t or date is required")
    for field_name in ("o", "h", "l", "c", "v"):
        if payload.get(field_name) is None:
            errors.append(f"{field_name} is required")
    return not errors, tuple(errors)


def _normalize_payload_ticker(payload: dict[str, object]) -> str:
    raw = payload.get("ticker") or payload.get("symbol")
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("ticker is required")
    return raw.strip().upper()


def polygon_volatility_payload_to_canonical_record(
    payload: dict[str, object],
    *,
    symbol: str | None = None,
    vendor: str = "polygon",
    source: str = "polygon_aggregates",
    normalization_version: str = "polygon.volatility.v1",
) -> NormalizedOHLCVRecord:
    is_valid, errors = validate_polygon_volatility_payload(payload)
    if not is_valid:
        raise ValueError("; ".join(errors))
    vendor_symbol = _normalize_payload_ticker(payload)
    canonical_symbol = symbol or polygon_symbol_to_canonical_volatility_symbol(vendor_symbol)
    timestamp_value = payload.get("t")
    if timestamp_value is not None:
        timestamp = datetime.fromtimestamp(float(timestamp_value) / 1000.0, tz=timezone.utc)
    else:
        timestamp = datetime.fromisoformat(f"{payload['date']}T00:00:00").replace(tzinfo=timezone.utc)
    return polygon_aggregate_to_normalized_ohlcv(
        {
            "ticker": canonical_symbol,
            "t": int(timestamp.timestamp() * 1000),
            "o": payload["o"],
            "h": payload["h"],
            "l": payload["l"],
            "c": payload["c"],
            "v": payload["v"],
            "adjusted": payload.get("adjusted", True),
        },
        symbol_id=vendor_symbol,
        vendor=vendor,
        source=source,
        normalization_version=normalization_version,
    )


def _plan_for_payload(
    *,
    requested_symbol: str,
    vendor_symbol: str,
    payload: dict[str, object],
) -> PolygonVolatilityRecordPlan:
    is_valid, errors = validate_polygon_volatility_payload(payload)
    if not is_valid:
        return PolygonVolatilityRecordPlan(
            requested_symbol=requested_symbol,
            canonical_symbol=requested_symbol,
            vendor_symbol=vendor_symbol,
            payload=dict(payload),
            is_valid=False,
            errors=errors,
        )
    canonical_record = polygon_volatility_payload_to_canonical_record(payload, symbol=requested_symbol)
    return PolygonVolatilityRecordPlan(
        requested_symbol=requested_symbol,
        canonical_symbol=canonical_record.symbol or requested_symbol,
        vendor_symbol=vendor_symbol,
        payload=dict(payload),
        is_valid=True,
        canonical_record=canonical_record,
    )


def build_polygon_volatility_dry_run_plan(
    *,
    symbols: tuple[str, ...],
    start_date: date,
    end_date: date,
    timeframe: str = "1d",
    fetch_adapter: PolygonVolatilityFetchAdapter | None = None,
    fetch_enabled: bool = False,
) -> PolygonVolatilityBatchPlan:
    symbol_plans: list[PolygonVolatilityPlan] = []
    batch_errors: list[dict[str, object]] = []
    total_payload_count = 0
    total_valid_count = 0
    total_invalid_count = 0

    for requested_symbol in symbols:
        try:
            vendor_symbol = canonical_volatility_symbol_to_polygon_symbol(requested_symbol)
        except ValueError as exc:
            batch_errors.append({"symbol": requested_symbol, "kind": "unsupported_symbol", "message": str(exc)})
            symbol_plans.append(
                PolygonVolatilityPlan(
                    requested_symbol=requested_symbol,
                    canonical_symbol=requested_symbol,
                    vendor_symbol=requested_symbol,
                    requested_start_date=start_date,
                    requested_end_date=end_date,
                    timeframe=timeframe,
                    fetch_enabled=fetch_enabled,
                    payload_count=0,
                    valid_count=0,
                    invalid_count=0,
                    errors=(str(exc),),
                    status="failed",
                )
            )
            continue

        payloads: list[dict[str, object]] = []
        errors: list[str] = []
        if fetch_enabled and fetch_adapter is not None:
            try:
                payloads = fetch_adapter.fetch_aggregates_raw(
                    vendor_symbol,
                    from_date=start_date.isoformat(),
                    to_date=end_date.isoformat(),
                )
            except Exception as exc:
                errors.append(str(exc))
        plans = tuple(_plan_for_payload(requested_symbol=requested_symbol, vendor_symbol=vendor_symbol, payload=payload) for payload in payloads)
        valid_count = sum(1 for plan in plans if plan.is_valid)
        invalid_count = len(plans) - valid_count
        total_payload_count += len(plans)
        total_valid_count += valid_count
        total_invalid_count += invalid_count
        status = "completed" if not errors else "failed"
        if errors:
            batch_errors.append({"symbol": requested_symbol, "kind": "fetch_error", "message": "; ".join(errors)})
        symbol_plans.append(
            PolygonVolatilityPlan(
                requested_symbol=requested_symbol,
                canonical_symbol=requested_symbol,
                vendor_symbol=vendor_symbol,
                requested_start_date=start_date,
                requested_end_date=end_date,
                timeframe=timeframe,
                fetch_enabled=fetch_enabled,
                payload_count=len(plans),
                valid_count=valid_count,
                invalid_count=invalid_count,
                dry_run=True,
                errors=tuple(errors),
                records=plans,
                status=status,
            )
        )

    batch_status = "failed" if batch_errors else "planned"
    return PolygonVolatilityBatchPlan(
        requested_symbols=symbols,
        requested_start_date=start_date,
        requested_end_date=end_date,
        timeframe=timeframe,
        fetch_enabled=fetch_enabled,
        total_payload_count=total_payload_count,
        total_valid_count=total_valid_count,
        total_invalid_count=total_invalid_count,
        dry_run=True,
        symbol_plans=tuple(symbol_plans),
        batch_errors=tuple(batch_errors),
        status=batch_status,
    )
