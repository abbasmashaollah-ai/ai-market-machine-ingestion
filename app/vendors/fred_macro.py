from __future__ import annotations

from dataclasses import dataclass

from app.normalization.fred_macro import FredMacroSeriesDefinition, NormalizedFredMacroRecord, normalize_fred_macro_record
from app.vendors.fred.client import FredClient


@dataclass(frozen=True)
class FredMacroFetchResult:
    series_id: str
    requested_count: int
    normalized_count: int
    valid_count: int
    invalid_count: int
    latest_observation_date: str | None
    records: tuple[NormalizedFredMacroRecord, ...]
    invalid_rows: tuple[dict[str, object], ...]


def _extract_observations(payload: dict[str, object]) -> list[dict[str, object]]:
    observations = payload.get("observations")
    if isinstance(observations, list):
        return [row for row in observations if isinstance(row, dict)]
    return []


def _observation_date_text(observation: dict[str, object]) -> str:
    date_value = observation.get("date") or observation.get("observation_date")
    return str(date_value or "")


def _sort_observations_newest_first(observations: list[dict[str, object]]) -> list[dict[str, object]]:
    return sorted(observations, key=_observation_date_text, reverse=True)


def fetch_fred_macro_series(
    client: FredClient,
    series_definition: FredMacroSeriesDefinition,
    *,
    max_observations: int | None = None,
) -> FredMacroFetchResult:
    payload = client.fetch_series_observations_raw(series_definition.series_id)
    observations = _extract_observations(payload)
    observations = _sort_observations_newest_first(observations)
    if max_observations is not None:
        observations = observations[:max_observations]
    records: list[NormalizedFredMacroRecord] = []
    invalid_rows: list[dict[str, object]] = []
    for observation in observations:
        normalized = normalize_fred_macro_record(observation, series_definition)
        if normalized is None:
            invalid_rows.append(observation)
            continue
        records.append(normalized)
    records = sorted(records, key=lambda record: record.observation_date)
    latest_observation_date = records[-1].observation_date.isoformat() if records else None
    return FredMacroFetchResult(
        series_id=series_definition.series_id,
        requested_count=len(observations),
        normalized_count=len(records),
        valid_count=len(records),
        invalid_count=len(invalid_rows),
        latest_observation_date=latest_observation_date,
        records=tuple(records),
        invalid_rows=tuple(invalid_rows),
    )
