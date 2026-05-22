from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.normalization.common import safe_text
from app.quality.macro_checks import validate_macro_observation
from app.vendors.common.http import UrlLibHttpClient
from app.vendors.fred.client import FredClientConfig, UnsupportedFredClient
from app.vendors.fred.mapper import fred_observation_to_normalized_macro


@dataclass(frozen=True)
class ManualFREDMacroIncrementalDryRunRow:
    series_id: str
    rows_fetched: int
    rows_valid: int
    rows_invalid: int
    validation_failures: int
    planned_start_date: date
    planned_end_date: date


@dataclass(frozen=True)
class ManualFREDMacroIncrementalDryRun:
    series_summaries: tuple[ManualFREDMacroIncrementalDryRunRow, ...]


def _extract_observations(payload: dict[str, object]) -> list[dict[str, object]]:
    observations = payload.get("observations")
    if isinstance(observations, list):
        return [row for row in observations if isinstance(row, dict)]
    return []


def _build_fred_client(api_key: str) -> UnsupportedFredClient:
    return UnsupportedFredClient(FredClientConfig(api_key=api_key), http_client=UrlLibHttpClient())


def build_manual_fred_macro_incremental_dry_run(
    *,
    series_ids: tuple[str, ...],
    start_date: date,
    end_date: date,
    api_key: str,
) -> ManualFREDMacroIncrementalDryRun:
    client = _build_fred_client(api_key)
    summaries: list[ManualFREDMacroIncrementalDryRunRow] = []
    for series_id in series_ids:
        payload = client.fetch_series_observations_raw(
            series_id,
            observation_start=start_date.isoformat(),
            observation_end=end_date.isoformat(),
        )
        observations = _extract_observations(payload)
        rows_valid = 0
        rows_invalid = 0
        validation_failures = 0
        for observation in observations:
            enriched = dict(observation)
            enriched["series_id"] = series_id
            if safe_text(enriched.get("value")) == ".":
                enriched["value"] = None
            try:
                normalized = fred_observation_to_normalized_macro(enriched)
            except Exception:
                rows_invalid += 1
                validation_failures += 1
                continue
            failures = [result for result in validate_macro_observation(normalized) if not result.passed]
            if failures:
                rows_invalid += 1
                validation_failures += len(failures)
            else:
                rows_valid += 1
        summaries.append(
            ManualFREDMacroIncrementalDryRunRow(
                series_id=series_id,
                rows_fetched=len(observations),
                rows_valid=rows_valid,
                rows_invalid=rows_invalid,
                validation_failures=validation_failures,
                planned_start_date=start_date,
                planned_end_date=end_date,
            )
        )
    return ManualFREDMacroIncrementalDryRun(series_summaries=tuple(summaries))
