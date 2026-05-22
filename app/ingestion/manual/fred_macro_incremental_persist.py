from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from app.ingestion.manual.fred_macro_dry_run import _build_fred_client, _extract_observations
from app.ingestion.manual.fred_macro_incremental import select_incremental_series_ids
from app.state.manual_fred_macro import ManualFREDMacroCheckpoint, ManualFREDMacroCheckpointStatus, build_manual_fred_macro_checkpoint
from app.state.manual_fred_macro_checkpoint_store import ManualFREDMacroCheckpointStore
from app.models.normalized import NormalizedMacroObservation
from app.normalization.common import safe_text
from app.quality.macro_checks import validate_macro_observation
from app.vendors.fred.mapper import fred_observation_to_normalized_macro
from app.writers.macro_writer import MacroWriter
from app.writers.canonical_writer import WriteStatus


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
    checkpoint_key: str
    checkpoint_loaded: bool = False


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


def _build_checkpoint_key(*, series_id: str, start_date: date, end_date: date) -> str:
    return f"fred:macro_observations:{series_id}:1d:{start_date.isoformat()}:{end_date.isoformat()}"


def _build_checkpoint(
    *,
    series_id: str,
    start_date: date,
    end_date: date,
    status: ManualFREDMacroCheckpointStatus = ManualFREDMacroCheckpointStatus.PLANNED,
    last_successful_observation_date: date | None = None,
) -> ManualFREDMacroCheckpoint:
    return build_manual_fred_macro_checkpoint(
        checkpoint_key=_build_checkpoint_key(series_id=series_id, start_date=start_date, end_date=end_date),
        vendor="fred",
        dataset="macro_observations",
        series_id=series_id,
        timeframe="1d",
        planned_start_date=start_date,
        planned_end_date=end_date,
        status=status,
        last_successful_observation_date=last_successful_observation_date,
    )


def build_manual_fred_macro_incremental_persist(
    *,
    series_ids: tuple[str, ...],
    start_date: date,
    end_date: date,
    api_key: str,
    writer: MacroWriter | None = None,
    confirmed_write: bool = False,
    checkpoint_store: ManualFREDMacroCheckpointStore | None = None,
    use_checkpoint: bool = False,
    update_checkpoint: bool = False,
) -> ManualFREDMacroIncrementalPersist:
    client = _build_fred_client(api_key)
    summaries: list[ManualFREDMacroIncrementalPersistRow] = []
    for series_id in series_ids:
        planned_start = start_date
        checkpoint_key = _build_checkpoint_key(series_id=series_id, start_date=start_date, end_date=end_date)
        checkpoint_loaded = False
        checkpoint = None
        if use_checkpoint and checkpoint_store is not None:
            checkpoint = checkpoint_store.load(checkpoint_key)
            checkpoint_loaded = checkpoint is not None
            if checkpoint and isinstance(checkpoint.last_successful_observation_date, date):
                planned_start = max(start_date, checkpoint.last_successful_observation_date + timedelta(days=1))
        payload = client.fetch_series_observations_raw(
            series_id,
            observation_start=planned_start.isoformat(),
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
            if (
                update_checkpoint
                and checkpoint_store is not None
                and rows_written > 0
                and write_result.status == WriteStatus.SUCCESS
            ):
                latest_observation_date = max(record.timestamp.date() for record in valid_rows)
                checkpoint_to_save = checkpoint or _build_checkpoint(
                    series_id=series_id,
                    start_date=start_date,
                    end_date=end_date,
                )
                checkpoint_store.update_successful_observation_date(checkpoint_to_save, latest_observation_date)
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
                checkpoint_key=checkpoint_key,
                checkpoint_loaded=checkpoint_loaded,
            )
        )
    return ManualFREDMacroIncrementalPersist(series_summaries=tuple(summaries))
