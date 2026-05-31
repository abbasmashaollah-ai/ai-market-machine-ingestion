from __future__ import annotations

from dataclasses import dataclass

from app.normalization.common import safe_number, safe_text


@dataclass(frozen=True)
class NormalizedBreadthParticipationRecord:
    metric_id: str | None
    metric_type: str | None
    observation_date: str | None
    universe: str | None
    symbol: str | None
    value: float | None
    numerator: float | None
    denominator: float | None
    source: str | None
    notes: str | None


DEFAULT_FIXTURE_RECORDS: tuple[dict[str, object], ...] = (
    {
        "metric_id": "breadth-2026-05-29-adv-dec",
        "metric_type": "advance_decline_count",
        "observation_date": "2026-05-29",
        "universe": "US equities",
        "symbol": None,
        "value": 1240,
        "numerator": 1240,
        "denominator": 980,
        "source": "manual_fixture",
        "notes": "deterministic fixture",
    },
    {
        "metric_id": "breadth-2026-05-29-new-highs-lows",
        "metric_type": "new_highs_new_lows",
        "observation_date": "2026-05-29",
        "universe": "US equities",
        "symbol": None,
        "value": -52,
        "numerator": 31,
        "denominator": 83,
        "source": "manual_fixture",
        "notes": "deterministic fixture",
    },
    {
        "metric_id": "breadth-2026-05-29-pct-above-ma",
        "metric_type": "percent_above_moving_average",
        "observation_date": "2026-05-29",
        "universe": "S&P 500",
        "symbol": None,
        "value": 0.61,
        "numerator": 305,
        "denominator": 500,
        "source": "manual_fixture",
        "notes": "deterministic fixture",
    },
    {
        "metric_id": "breadth-2026-05-29-up-down-volume",
        "metric_type": "up_down_volume",
        "observation_date": "2026-05-29",
        "universe": "US equities",
        "symbol": None,
        "value": 1.24,
        "numerator": 124,
        "denominator": 100,
        "source": "manual_fixture",
        "notes": "deterministic fixture",
    },
    {
        "metric_id": "breadth-2026-05-29-sector-participation",
        "metric_type": "sector_participation",
        "observation_date": "2026-05-29",
        "universe": "S&P 500 sectors",
        "symbol": "XLK",
        "value": 0.83,
        "numerator": 10,
        "denominator": 12,
        "source": "manual_fixture",
        "notes": "deterministic fixture",
    },
    {
        "metric_id": "breadth-2026-05-29-index-breadth",
        "metric_type": "index_universe_breadth",
        "observation_date": "2026-05-29",
        "universe": "Russell 3000",
        "symbol": None,
        "value": 0.74,
        "numerator": 2220,
        "denominator": 3000,
        "source": "manual_fixture",
        "notes": "deterministic fixture",
    },
)


def normalize_breadth_participation_record(payload: dict[str, object]) -> NormalizedBreadthParticipationRecord:
    return NormalizedBreadthParticipationRecord(
        metric_id=safe_text(payload.get("metric_id")),
        metric_type=safe_text(payload.get("metric_type")),
        observation_date=safe_text(payload.get("observation_date")),
        universe=safe_text(payload.get("universe")),
        symbol=safe_text(payload.get("symbol")),
        value=safe_number(payload.get("value")),
        numerator=safe_number(payload.get("numerator")),
        denominator=safe_number(payload.get("denominator")),
        source=safe_text(payload.get("source")),
        notes=safe_text(payload.get("notes")),
    )


def validate_breadth_participation_record(record: NormalizedBreadthParticipationRecord) -> tuple[str, ...]:
    errors: list[str] = []
    if not record.metric_id:
        errors.append("metric_id is required")
    if not record.metric_type:
        errors.append("metric_type is required")
    if not record.observation_date:
        errors.append("observation_date is required")
    if not record.universe:
        errors.append("universe is required")
    if record.value is None:
        errors.append("value is required")
    if record.numerator is None:
        errors.append("numerator is required")
    if record.denominator is None:
        errors.append("denominator is required")
    if not record.source:
        errors.append("source is required")
    if not record.notes:
        errors.append("notes is required")
    return tuple(errors)
