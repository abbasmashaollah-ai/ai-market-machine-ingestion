from __future__ import annotations

from dataclasses import dataclass

from app.normalization.common import safe_number, safe_text


@dataclass(frozen=True)
class NormalizedFlowsPositioningRecord:
    record_id: str | None
    record_type: str | None
    observation_date: str | None
    symbol: str | None
    asset_class: str | None
    value: float | None
    unit: str | None
    source: str | None
    raw_source_id: str | None
    notes: str | None


DEFAULT_FIXTURE_RECORDS: tuple[dict[str, object], ...] = (
    {
        "record_id": "flows-2026-05-29-etf",
        "record_type": "ETF flows",
        "observation_date": "2026-05-29",
        "symbol": "SPY",
        "asset_class": "equity",
        "value": 125000000.0,
        "unit": "usd",
        "source": "manual_fixture",
        "raw_source_id": "fixture-etf-flows-1",
        "notes": "deterministic fixture",
    },
    {
        "record_id": "flows-2026-05-29-fund",
        "record_type": "fund flows",
        "observation_date": "2026-05-29",
        "symbol": "VTI",
        "asset_class": "equity",
        "value": 83000000.0,
        "unit": "usd",
        "source": "manual_fixture",
        "raw_source_id": "fixture-fund-flows-1",
        "notes": "deterministic fixture",
    },
    {
        "record_id": "flows-2026-05-29-short-interest",
        "record_type": "short interest",
        "observation_date": "2026-05-29",
        "symbol": "AAPL",
        "asset_class": "equity",
        "value": 0.021,
        "unit": "ratio",
        "source": "manual_fixture",
        "raw_source_id": "fixture-short-interest-1",
        "notes": "deterministic fixture",
    },
    {
        "record_id": "flows-2026-05-29-institutional",
        "record_type": "institutional positioning",
        "observation_date": "2026-05-29",
        "symbol": "QQQ",
        "asset_class": "equity",
        "value": 0.64,
        "unit": "ratio",
        "source": "manual_fixture",
        "raw_source_id": "fixture-institutional-1",
        "notes": "deterministic fixture",
    },
    {
        "record_id": "flows-2026-05-29-cftc",
        "record_type": "CFTC/COT positioning",
        "observation_date": "2026-05-29",
        "symbol": None,
        "asset_class": "futures",
        "value": 15870.0,
        "unit": "contracts",
        "source": "manual_fixture",
        "raw_source_id": "fixture-cftc-1",
        "notes": "deterministic fixture",
    },
    {
        "record_id": "flows-2026-05-29-dark-pool",
        "record_type": "dark pool/off-exchange volume",
        "observation_date": "2026-05-29",
        "symbol": "MSFT",
        "asset_class": "equity",
        "value": 42000000.0,
        "unit": "shares",
        "source": "manual_fixture",
        "raw_source_id": "fixture-dark-pool-1",
        "notes": "deterministic fixture",
    },
)


def normalize_flows_positioning_record(payload: dict[str, object]) -> NormalizedFlowsPositioningRecord:
    return NormalizedFlowsPositioningRecord(
        record_id=safe_text(payload.get("record_id")),
        record_type=safe_text(payload.get("record_type")),
        observation_date=safe_text(payload.get("observation_date")),
        symbol=safe_text(payload.get("symbol")),
        asset_class=safe_text(payload.get("asset_class")),
        value=safe_number(payload.get("value")),
        unit=safe_text(payload.get("unit")),
        source=safe_text(payload.get("source")),
        raw_source_id=safe_text(payload.get("raw_source_id")),
        notes=safe_text(payload.get("notes")),
    )


def validate_flows_positioning_record(record: NormalizedFlowsPositioningRecord) -> tuple[str, ...]:
    errors: list[str] = []
    if not record.record_id:
        errors.append("record_id is required")
    if not record.record_type:
        errors.append("record_type is required")
    if not record.observation_date:
        errors.append("observation_date is required")
    if record.value is None:
        errors.append("value is required")
    if not record.unit:
        errors.append("unit is required")
    if not record.source:
        errors.append("source is required")
    if not record.raw_source_id:
        errors.append("raw_source_id is required")
    if not record.notes:
        errors.append("notes is required")
    return tuple(errors)
