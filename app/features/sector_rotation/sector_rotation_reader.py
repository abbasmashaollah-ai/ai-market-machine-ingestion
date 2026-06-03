"""Pure certified OHLCV row-to-history transformer for sector rotation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import date, datetime
from collections.abc import Mapping, Sequence

from app.features.sector_rotation.sector_universe import get_required_symbols


_ACCEPTABLE_QUALITY_STATUSES = {"VALID", "WARNING", "PENDING", None}
_ACCEPTABLE_CERTIFICATION_STATUSES = {"CERTIFIED", "PENDING", "UNCERTIFIED", None}
_ACCEPTABLE_FRESHNESS_STATUSES = {"FRESH", "DELAYED", "PENDING", "UNKNOWN", None, "STALE"}


@dataclass(frozen=True, slots=True)
class CertifiedOHLCVRow:
    symbol: str
    date: str | date | datetime
    close: float | int | None
    quality_status: str | None = None
    certification_status: str | None = None
    freshness_status: str | None = None
    source: str | None = None
    lineage: Mapping[str, object] | None = None


@dataclass(frozen=True, slots=True)
class SectorRotationReaderResult:
    price_history_by_symbol: dict[str, list[float | int]]
    warnings: tuple[str, ...] = field(default_factory=tuple)


def _normalize_symbol(symbol: object) -> str:
    if not isinstance(symbol, str):
        return ""
    normalized = symbol.strip().upper()
    if not normalized:
        return ""
    return normalized


def _normalize_timestamp(value: object) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _coerce_status(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        normalized = value.strip().upper()
        return normalized or None
    return str(value).strip().upper() or None


def coerce_certified_ohlcv_row(row: object) -> dict[str, object]:
    """Coerce mapping or dataclass input into a normalized OHLCV row dict."""

    if is_dataclass(row):
        raw = asdict(row)
    elif isinstance(row, Mapping):
        raw = dict(row)
    else:
        raise TypeError("certified OHLCV row must be a mapping or dataclass instance")

    normalized_symbol = _normalize_symbol(raw.get("symbol"))
    normalized_date = raw.get("date", raw.get("timestamp"))
    normalized_close = raw.get("close")
    quality_status = _coerce_status(raw.get("quality_status"))
    certification_status = _coerce_status(raw.get("certification_status"))
    freshness_status = _coerce_status(raw.get("freshness_status"))

    return {
        "symbol": normalized_symbol,
        "date": _normalize_timestamp(normalized_date) if normalized_date is not None else None,
        "close": normalized_close,
        "quality_status": quality_status,
        "certification_status": certification_status,
        "freshness_status": freshness_status,
        "source": raw.get("source"),
        "lineage": dict(raw.get("lineage") or {}),
    }


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _sorted_rows(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    indexed_rows: list[tuple[str, int, dict[str, object]]] = []
    for index, row in enumerate(rows):
        coerced = coerce_certified_ohlcv_row(row)
        indexed_rows.append((str(coerced.get("date") or ""), index, coerced))
    indexed_rows.sort(key=lambda item: (item[0], item[1]))
    return [row for _, _, row in indexed_rows]


def build_price_history_by_symbol(
    rows: Sequence[Mapping[str, object]] | Sequence[object],
    required_symbols: Sequence[str] | None = None,
    min_history_length: int | None = None,
    close_field: str = "close",
) -> SectorRotationReaderResult:
    """Build a price-history map from certified OHLCV rows."""

    required_symbols = tuple(_normalize_symbol(symbol) for symbol in (required_symbols or get_required_symbols()))
    required_symbol_set = {symbol for symbol in required_symbols if symbol}
    warnings: list[str] = []
    accepted_rows: list[dict[str, object]] = []

    for row in rows:
        coerced = coerce_certified_ohlcv_row(row)
        symbol = coerced["symbol"]
        if not symbol or symbol not in required_symbol_set:
            continue

        quality_status = coerced.get("quality_status")
        certification_status = coerced.get("certification_status")
        freshness_status = coerced.get("freshness_status")

        if quality_status not in _ACCEPTABLE_QUALITY_STATUSES:
            warnings.append(f"rejected_quality_status:{symbol}:{quality_status}")
            continue
        if certification_status not in _ACCEPTABLE_CERTIFICATION_STATUSES:
            warnings.append(f"rejected_certification_status:{symbol}:{certification_status}")
            continue
        if freshness_status not in _ACCEPTABLE_FRESHNESS_STATUSES:
            warnings.append(f"rejected_freshness_status:{symbol}:{freshness_status}")
            continue

        close_value = coerced.get(close_field)
        if close_value is None or not _is_number(close_value):
            warnings.append(f"missing_or_invalid_close:{symbol}")
            continue

        accepted_rows.append(coerced)

    accepted_rows = _sorted_rows(accepted_rows)
    price_history_by_symbol: dict[str, list[float | int]] = {symbol: [] for symbol in required_symbols if symbol}
    for row in accepted_rows:
        symbol = str(row["symbol"])
        price_history_by_symbol.setdefault(symbol, []).append(row[close_field])

    populated_symbols = tuple(symbol for symbol, history in price_history_by_symbol.items() if history)
    missing_symbols = get_missing_required_symbols(
        {symbol: price_history_by_symbol[symbol] for symbol in populated_symbols},
        required_symbols=required_symbols,
    )
    if missing_symbols:
        warnings.append(f"missing_required_symbols:{','.join(missing_symbols)}")

    if min_history_length is not None:
        for symbol, history in price_history_by_symbol.items():
            if len(history) < min_history_length:
                warnings.append(f"insufficient_history:{symbol}:{len(history)}<{min_history_length}")

    return SectorRotationReaderResult(price_history_by_symbol=price_history_by_symbol, warnings=tuple(warnings))


def get_missing_required_symbols(
    price_history_by_symbol: Mapping[str, Sequence[object]],
    required_symbols: Sequence[str] | None = None,
) -> tuple[str, ...]:
    required_symbols = tuple(_normalize_symbol(symbol) for symbol in (required_symbols or get_required_symbols()))
    existing_symbols = {_normalize_symbol(existing) for existing in price_history_by_symbol}
    missing = [symbol for symbol in required_symbols if symbol and symbol not in existing_symbols]
    return tuple(missing)


def validate_reader_history_coverage(
    price_history_by_symbol: Mapping[str, Sequence[object]],
    required_symbols: Sequence[str] | None = None,
    min_history_length: int = 61,
) -> tuple[bool, tuple[str, ...]]:
    """Validate symbol coverage and minimum history length for the reader output."""

    warnings: list[str] = []
    missing_symbols = get_missing_required_symbols(price_history_by_symbol, required_symbols=required_symbols)
    if missing_symbols:
        warnings.append(f"missing_required_symbols:{','.join(missing_symbols)}")
    for symbol, history in price_history_by_symbol.items():
        if len(history) < min_history_length:
            warnings.append(f"insufficient_history:{_normalize_symbol(symbol)}:{len(history)}<{min_history_length}")
    return (not warnings, tuple(warnings))
