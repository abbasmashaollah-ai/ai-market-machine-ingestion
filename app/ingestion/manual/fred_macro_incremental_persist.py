from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
import re

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
    requested_start_date: date
    effective_start_date: date
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
    status: str = "completed"
    error_message: str | None = None


@dataclass(frozen=True)
class ManualFREDMacroIncrementalPersist:
    series_summaries: tuple[ManualFREDMacroIncrementalPersistRow, ...]
    series_total: int
    series_completed: int
    series_failed: int
    series_skipped: int
    total_rows_fetched: int
    total_rows_valid: int
    total_rows_invalid: int
    total_rows_written: int
    total_validation_failures: int


def _sanitize_error_message(message: str) -> str:
    sanitized = message
    sanitized = re.sub(r"(?i)sqlalchemy(?:\.engine)?(?:\.[A-Za-z_]+)*\.[A-Za-z_]+:.*", "sqlalchemy driver error: <redacted>", sanitized)
    sanitized = re.sub(r"(?i)(postgres(?:ql)?://)([^\s:@/]+)(?::([^\s@/]+))?@", r"\1<redacted>@", sanitized)
    sanitized = re.sub(r"(?i)(password|passwd|pwd|token|secret|key)=([^\s&]+)", r"\1=<redacted>", sanitized)
    sanitized = re.sub(r"(?i)DATABASE_URL", "database connection", sanitized)
    return sanitized


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


def _resolve_effective_start_date(
    *,
    requested_start_date: date,
    checkpoint: ManualFREDMacroCheckpoint | None,
) -> date:
    if checkpoint and isinstance(checkpoint.last_successful_observation_date, date):
        return max(requested_start_date, checkpoint.last_successful_observation_date + timedelta(days=1))
    return requested_start_date


def _observation_date_from_row(row: dict[str, object]) -> date | None:
    raw_date = row.get("date") or row.get("observation_date")
    if isinstance(raw_date, date):
        return raw_date
    if isinstance(raw_date, str) and raw_date:
        try:
            return date.fromisoformat(raw_date)
        except ValueError:
            return None
    return None


def _filter_resumed_observations(
    *,
    observations: list[dict[str, object]],
    checkpoint: ManualFREDMacroCheckpoint | None,
) -> tuple[list[dict[str, object]], int]:
    if checkpoint is None or checkpoint.last_successful_observation_date is None:
        return observations, 0
    filtered: list[dict[str, object]] = []
    skipped = 0
    boundary = checkpoint.last_successful_observation_date
    for observation in observations:
        observation_date = _observation_date_from_row(observation)
        if observation_date is not None and observation_date <= boundary:
            skipped += 1
            continue
        filtered.append(observation)
    return filtered, skipped


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
        requested_start = start_date
        checkpoint_key = _build_checkpoint_key(series_id=series_id, start_date=start_date, end_date=end_date)
        checkpoint_loaded = False
        checkpoint = None
        try:
            if use_checkpoint and checkpoint_store is not None:
                checkpoint = checkpoint_store.load(checkpoint_key)
                checkpoint_loaded = checkpoint is not None
            resume_checkpoint = checkpoint if (
                checkpoint_loaded and isinstance(getattr(checkpoint, "last_successful_observation_date", None), date)
            ) else None
            effective_start = _resolve_effective_start_date(
                requested_start_date=requested_start,
                checkpoint=resume_checkpoint,
            )
            if effective_start > end_date:
                summaries.append(
                    ManualFREDMacroIncrementalPersistRow(
                        series_id=series_id,
                        requested_start_date=requested_start,
                        effective_start_date=effective_start,
                        rows_fetched=0,
                        rows_valid=0,
                        rows_invalid=0,
                        rows_written=0,
                        validation_failures=0,
                        planned_start_date=requested_start,
                        planned_end_date=end_date,
                        write_confirmed=confirmed_write,
                        checkpoint_key=checkpoint_key,
                        checkpoint_loaded=checkpoint_loaded,
                        status="skipped_already_current",
                    )
                )
                continue
            payload = client.fetch_series_observations_raw(
                series_id,
                observation_start=effective_start.isoformat(),
                observation_end=end_date.isoformat(),
            )
            observations = _extract_observations(payload)
            observations, resumed_skipped = _filter_resumed_observations(
                observations=observations,
                checkpoint=resume_checkpoint,
            )
            if resumed_skipped and not observations:
                summaries.append(
                    ManualFREDMacroIncrementalPersistRow(
                        series_id=series_id,
                        requested_start_date=requested_start,
                        effective_start_date=effective_start,
                        rows_fetched=0,
                        rows_valid=0,
                        rows_invalid=0,
                        rows_written=0,
                        validation_failures=0,
                        planned_start_date=requested_start,
                        planned_end_date=end_date,
                        write_confirmed=confirmed_write,
                        checkpoint_key=checkpoint_key,
                        checkpoint_loaded=checkpoint_loaded,
                        status="skipped_already_current",
                    )
                )
                continue
            valid_rows, rows_invalid, validation_failures = _build_valid_records(
                series_id=series_id,
                observations=observations,
            )
            rows_written = 0
            status = "completed"
            error_message = None
            if confirmed_write and writer is not None and valid_rows:
                write_result = writer.write(valid_rows)
                rows_written = write_result.written_count
                if write_result.status == WriteStatus.SUCCESS:
                    if (
                        update_checkpoint
                        and checkpoint_store is not None
                        and rows_written > 0
                    ):
                        latest_observation_date = max(record.timestamp.date() for record in valid_rows)
                        checkpoint_to_save = checkpoint or _build_checkpoint(
                            series_id=series_id,
                            start_date=requested_start,
                            end_date=end_date,
                        )
                        checkpoint_store.update_successful_observation_date(checkpoint_to_save, latest_observation_date)
                else:
                    status = "failed"
                    error_message = _sanitize_error_message(
                        str(getattr(write_result, "message", None) or getattr(write_result, "details", {}).get("error_message", "") or "write failed")
                    )
            summaries.append(
                ManualFREDMacroIncrementalPersistRow(
                    series_id=series_id,
                    requested_start_date=requested_start,
                    effective_start_date=effective_start,
                    rows_fetched=len(observations),
                    rows_valid=len(valid_rows),
                    rows_invalid=rows_invalid,
                    rows_written=rows_written,
                    validation_failures=validation_failures,
                    planned_start_date=requested_start,
                    planned_end_date=end_date,
                    write_confirmed=confirmed_write,
                    checkpoint_key=checkpoint_key,
                    checkpoint_loaded=checkpoint_loaded,
                    status=status,
                    error_message=error_message,
                )
            )
        except Exception as exc:
            summaries.append(
                ManualFREDMacroIncrementalPersistRow(
                    series_id=series_id,
                    requested_start_date=requested_start,
                    effective_start_date=requested_start,
                    rows_fetched=0,
                    rows_valid=0,
                    rows_invalid=0,
                    rows_written=0,
                    validation_failures=0,
                    planned_start_date=requested_start,
                    planned_end_date=end_date,
                    write_confirmed=confirmed_write,
                    checkpoint_key=checkpoint_key,
                    checkpoint_loaded=checkpoint_loaded,
                    status="failed",
                    error_message=_sanitize_error_message(f"{exc.__class__.__name__}: {exc}"),
                )
            )

    series_total = len(summaries)
    series_completed = sum(1 for row in summaries if row.status == "completed")
    series_failed = sum(1 for row in summaries if row.status == "failed")
    series_skipped = sum(1 for row in summaries if row.status.startswith("skipped"))
    total_rows_fetched = sum(row.rows_fetched for row in summaries)
    total_rows_valid = sum(row.rows_valid for row in summaries)
    total_rows_invalid = sum(row.rows_invalid for row in summaries)
    total_rows_written = sum(row.rows_written for row in summaries)
    total_validation_failures = sum(row.validation_failures for row in summaries)
    return ManualFREDMacroIncrementalPersist(
        series_summaries=tuple(summaries),
        series_total=series_total,
        series_completed=series_completed,
        series_failed=series_failed,
        series_skipped=series_skipped,
        total_rows_fetched=total_rows_fetched,
        total_rows_valid=total_rows_valid,
        total_rows_invalid=total_rows_invalid,
        total_rows_written=total_rows_written,
        total_validation_failures=total_validation_failures,
    )
