from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.ingestion.manual.fred_macro_dry_run import _build_fred_client, _extract_observations
from app.ingestion.manual.fred_macro_incremental import select_incremental_series_ids
from app.models.normalized import NormalizedMacroObservation
from app.normalization.common import safe_text
from app.quality.macro_checks import validate_macro_observation
from app.vendors.fred.mapper import fred_observation_to_normalized_macro
from app.writers.macro_writer import MacroWriter


@dataclass(frozen=True)
class ManualFREDMacroIncrementalPersistRow:
    series_id: str
    rows_fetched: int
    rows_valid: int
    rows_invalid: int
    rows_written: int
    validation_failures: int
    planned_start_date: date
    planned_end_date: date
    write_confirmed: bool


@dataclass(frozen=True)
class ManualFREDMacroIncrementalPersist:
    series_summaries: tuple[ManualFREDMacroIncrementalPersistRow, ...]


def _build_valid_records(
    *,
    series_id: str,
    observations: list[dict[str, object]],
) -> tuple[list[NormalizedMacroObservation], int, int]:
    valid_rows: list[NormalizedMacroObservation] = []
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
            continue
        valid_rows.append(normalized)
    return valid_rows, rows_invalid, validation_failures


def build_manual_fred_macro_incremental_persist(
    *,
    series_ids: tuple[str, ...],
    start_date: date,
    end_date: date,
    api_key: str,
    writer: MacroWriter | None = None,
    confirmed_write: bool = False,
) -> ManualFREDMacroIncrementalPersist:
    client = _build_fred_client(api_key)
    summaries: list[ManualFREDMacroIncrementalPersistRow] = []
    for series_id in series_ids:
        payload = client.fetch_series_observations_raw(
            series_id,
            observation_start=start_date.isoformat(),
            observation_end=end_date.isoformat(),
        )
        observations = _extract_observations(payload)
        valid_rows, rows_invalid, validation_failures = _build_valid_records(
            series_id=series_id,
            observations=observations,
        )
        rows_written = 0
        if confirmed_write and writer is not None and valid_rows:
            write_result = writer.write(valid_rows)
            rows_written = write_result.written_count
        summaries.append(
            ManualFREDMacroIncrementalPersistRow(
                series_id=series_id,
                rows_fetched=len(observations),
                rows_valid=len(valid_rows),
                rows_invalid=rows_invalid,
                rows_written=rows_written,
                validation_failures=validation_failures,
                planned_start_date=start_date,
                planned_end_date=end_date,
                write_confirmed=confirmed_write,
            )
        )
    return ManualFREDMacroIncrementalPersist(series_summaries=tuple(summaries))

