from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.normalization.common import safe_text


@dataclass(frozen=True)
class NormalizedFredMacroRecord:
    series_id: str
    observation_date: date
    value: float | None
    source: str
    unit: str | None = None
    frequency: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class FredMacroSeriesDefinition:
    series_id: str
    unit: str
    frequency: str
    notes: str | None = None


STARTER_FRED_MACRO_SERIES: tuple[FredMacroSeriesDefinition, ...] = (
    FredMacroSeriesDefinition("DGS10", "percent", "daily", "10-year Treasury constant maturity rate"),
    FredMacroSeriesDefinition("DGS2", "percent", "daily", "2-year Treasury constant maturity rate"),
    FredMacroSeriesDefinition("FEDFUNDS", "percent", "monthly", "effective federal funds rate"),
    FredMacroSeriesDefinition("CPIAUCSL", "index", "monthly", "consumer price index for all urban consumers"),
    FredMacroSeriesDefinition("UNRATE", "percent", "monthly", "unemployment rate"),
)


def get_starter_fred_macro_series() -> tuple[FredMacroSeriesDefinition, ...]:
    return STARTER_FRED_MACRO_SERIES


def normalize_fred_macro_record(payload: dict[str, object], series_definition: FredMacroSeriesDefinition) -> NormalizedFredMacroRecord | None:
    series_id = safe_text(payload.get("series_id")) or series_definition.series_id
    observation_date_text = safe_text(payload.get("date") or payload.get("observation_date"))
    value = payload.get("value")
    if not observation_date_text:
        return None
    try:
        observation_date = date.fromisoformat(observation_date_text)
    except ValueError:
        return None
    normalized_value: float | None
    if value in (None, "."):
        normalized_value = None
    else:
        try:
            normalized_value = float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return None
    return NormalizedFredMacroRecord(
        series_id=series_id,
        observation_date=observation_date,
        value=normalized_value,
        source="fred",
        unit=series_definition.unit,
        frequency=series_definition.frequency,
        notes=series_definition.notes,
    )


def build_fred_macro_fixture_records() -> tuple[NormalizedFredMacroRecord, ...]:
    records: list[NormalizedFredMacroRecord] = []
    for series in STARTER_FRED_MACRO_SERIES:
        normalized = normalize_fred_macro_record(
            {"series_id": series.series_id, "date": "2026-01-01", "value": "1.0"},
            series,
        )
        if normalized is not None:
            records.append(normalized)
    return tuple(records)
