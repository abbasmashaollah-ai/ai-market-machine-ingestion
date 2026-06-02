from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from app.normalization.volatility_index import NormalizedVolatilityIndexRecord, normalize_volatility_index_record
from app.vendors.polygon_volatility_index import polygon_canonical_symbol, polygon_vendor_symbol

VOLATILITY_OBSERVATION_INDEX_FAMILY = "volatility_index"
VOLATILITY_OBSERVATION_SOURCE = "polygon"
VOLATILITY_OBSERVATION_NORMALIZATION_VERSION = "volatility.observations.v1"


@dataclass(frozen=True)
class VolatilityObservationProducerResult:
    records: tuple[dict[str, object], ...]
    accepted_count: int
    rejected_count: int
    rejected_records: tuple[dict[str, object], ...] = ()
    warnings: tuple[str, ...] = ()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_source_record(
    record: object,
) -> tuple[NormalizedVolatilityIndexRecord | None, dict[str, object], tuple[str, ...], bool, bool]:
    warnings: list[str] = []
    if isinstance(record, NormalizedVolatilityIndexRecord):
        return record, dict(record.__dict__), (), True, True
    if not isinstance(record, dict):
        return None, {}, ("record is not a dict or normalized volatility record",), False, False

    source_symbol = record.get("source_symbol") or record.get("vendor_symbol") or record.get("symbol")
    canonical_symbol = record.get("symbol")
    if isinstance(source_symbol, str) and source_symbol:
        try:
            canonical_symbol = polygon_canonical_symbol(source_symbol)
        except ValueError:
            warnings.append(f"unsupported source_symbol: {source_symbol}")
    normalized = normalize_volatility_index_record(
        {
            "symbol": canonical_symbol,
            "observation_date": record.get("observation_date"),
            "value": record.get("value"),
            "source": record.get("source") or VOLATILITY_OBSERVATION_SOURCE,
            "vendor_symbol": source_symbol if isinstance(source_symbol, str) else None,
            "unit": record.get("unit") or "index",
            "notes": record.get("notes"),
        }
    )
    entitlement_error = record.get("entitlement_error") or record.get("source_error") or record.get("error")
    if isinstance(entitlement_error, str) and entitlement_error.strip():
        warnings.append(entitlement_error.strip())
    has_timestamp = record.get("timestamp") is not None or record.get("t") is not None
    has_source = isinstance(record.get("source"), str) and bool(str(record.get("source")).strip())
    return normalized, dict(record), tuple(warnings), has_timestamp, has_source


def _observation_timestamp(source_record: dict[str, object], observation_date: date | None) -> datetime | None:
    raw = source_record.get("timestamp") or source_record.get("t")
    if isinstance(raw, datetime):
        return raw.astimezone(timezone.utc) if raw.tzinfo else raw.replace(tzinfo=timezone.utc)
    if isinstance(raw, (int, float)):
        return datetime.fromtimestamp(float(raw) / 1000.0, tz=timezone.utc)
    if isinstance(raw, str) and raw.strip():
        try:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            parsed = None
        if parsed is not None:
            return parsed.astimezone(timezone.utc) if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    if observation_date is not None:
        return datetime(observation_date.year, observation_date.month, observation_date.day, tzinfo=timezone.utc)
    return None


def _lineage(record: NormalizedVolatilityIndexRecord, source_record: dict[str, object]) -> dict[str, object]:
    source_symbol = record.vendor_symbol or polygon_vendor_symbol(record.symbol or "")
    ts = _observation_timestamp(source_record, record.observation_date)
    return {
        "producer": "ai-market-machine-ingestion",
        "target_table": "volatility_index_observations",
        "normalization_version": VOLATILITY_OBSERVATION_NORMALIZATION_VERSION,
        "source": record.source or VOLATILITY_OBSERVATION_SOURCE,
        "source_symbol": source_symbol,
        "symbol": record.symbol,
        "observation_timestamp": ts.isoformat() if ts else None,
        "upstream_fields": tuple(sorted(source_record.keys())),
    }


def _evidence(record: NormalizedVolatilityIndexRecord, source_record: dict[str, object]) -> dict[str, object]:
    return {
        "source": record.source or VOLATILITY_OBSERVATION_SOURCE,
        "source_symbol": record.vendor_symbol,
        "symbol": record.symbol,
        "observation_date": record.observation_date.isoformat() if record.observation_date else None,
        "source_payload": dict(source_record),
    }


def _build_payload(record: NormalizedVolatilityIndexRecord, source_record: dict[str, object]) -> dict[str, object]:
    timestamp = _observation_timestamp(source_record, record.observation_date)
    source_symbol = record.vendor_symbol or polygon_vendor_symbol(record.symbol or "")
    return {
        "symbol": record.symbol,
        "index_family": VOLATILITY_OBSERVATION_INDEX_FAMILY,
        "observation_date": record.observation_date.isoformat() if record.observation_date else None,
        "timestamp": timestamp.isoformat() if timestamp else None,
        "value": record.value,
        "close": record.value,
        "source": record.source or VOLATILITY_OBSERVATION_SOURCE,
        "source_symbol": source_symbol,
        "source_attribution": f"{record.source or VOLATILITY_OBSERVATION_SOURCE}:{source_symbol}",
        "daily_or_intraday": "daily",
        "lineage": _lineage(record, source_record),
        "quality_status": "pass",
        "certification_status": "pending",
        "freshness_status": "unknown",
        "freshness_checked_at": _utc_now().isoformat(),
        "evidence": _evidence(record, source_record),
    }


def _validate_payload(payload: dict[str, object]) -> list[str]:
    required = (
        "symbol",
        "index_family",
        "observation_date",
        "timestamp",
        "value",
        "close",
        "source",
        "source_symbol",
        "source_attribution",
        "daily_or_intraday",
        "lineage",
        "quality_status",
        "certification_status",
        "freshness_status",
        "freshness_checked_at",
        "evidence",
    )
    errors: list[str] = []
    for field_name in required:
        if payload.get(field_name) in (None, ""):
            errors.append(f"{field_name} is required")
    return errors


def build_volatility_observations_dry_run(
    records: list[object],
    *,
    source_name: str = VOLATILITY_OBSERVATION_SOURCE,
) -> VolatilityObservationProducerResult:
    accepted: list[dict[str, object]] = []
    rejected: list[dict[str, object]] = []
    warnings: list[str] = []

    for index, item in enumerate(records):
        normalized, source_record, item_warnings, has_timestamp, has_source = _normalize_source_record(item)
        warnings.extend(item_warnings)
        if normalized is None:
            rejected.append({"index": index, "record": item, "errors": item_warnings})
            continue
        if source_name and normalized.source and normalized.source != source_name:
            warnings.append(f"record {index} source mismatch: expected {source_name}, got {normalized.source}")
        if not has_timestamp and not isinstance(item, NormalizedVolatilityIndexRecord):
            rejected.append({"index": index, "record": source_record, "errors": ("timestamp is required",)})
            continue
        if not has_source and not isinstance(item, NormalizedVolatilityIndexRecord):
            rejected.append({"index": index, "record": source_record, "errors": ("source is required",)})
            continue
        payload = _build_payload(normalized, source_record)
        errors = _validate_payload(payload)
        if errors:
            rejected.append({"index": index, "record": payload, "errors": tuple(errors)})
            continue
        accepted.append(payload)

    return VolatilityObservationProducerResult(
        records=tuple(accepted),
        accepted_count=len(accepted),
        rejected_count=len(rejected),
        rejected_records=tuple(rejected),
        warnings=tuple(warnings),
    )
