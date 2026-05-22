from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timedelta
import re

from app.models.normalized import NormalizedOHLCVRecord
from app.normalization.common import safe_text
from app.normalization.ohlcv import normalize_ohlcv
from app.quality.ohlcv_checks import detect_duplicate_candles, validate_ohlcv_record
from app.state.manual_polygon_ohlcv import (
    ManualPolygonOHLCVCheckpoint,
    ManualPolygonOHLCVCheckpointStatus,
    build_manual_polygon_ohlcv_checkpoint,
)
from app.state.manual_polygon_ohlcv_checkpoint_store import ManualPolygonOHLCVCheckpointStore
from app.vendors.polygon.client import PolygonClientConfig, UnsupportedPolygonClient
from app.vendors.polygon.mapper import polygon_aggregate_to_normalized_ohlcv
from app.writers.canonical_writer import WriteStatus
from app.writers.ohlcv_writer import OhlcvWriter


@dataclass(frozen=True)
class ManualPolygonOHLCVIncrementalRow:
    symbol: str
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
class ManualPolygonOHLCVIncrementalSummary:
    symbol_summaries: tuple[ManualPolygonOHLCVIncrementalRow, ...]
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
    sanitized = re.sub(r"(?i)(postgres(?:ql)?://)([^\s:@/]+)(?::([^\s@/]+))?@", r"\1<redacted>@", sanitized)
    sanitized = re.sub(r"(?i)(password|passwd|pwd|token|secret|key)=([^\s&]+)", r"\1=<redacted>", sanitized)
    sanitized = re.sub(r"(?i)DATABASE_URL", "database connection", sanitized)
    sanitized = re.sub(r"(?i)POLYGON_API_KEY", "polygon api key", sanitized)
    return sanitized


def _build_polygon_client(api_key: str) -> UnsupportedPolygonClient:
    return UnsupportedPolygonClient(PolygonClientConfig(api_key=api_key))


def _build_checkpoint_key(*, symbol: str, timeframe: str, start_date: date, end_date: date) -> str:
    return f"polygon:ohlcv:{symbol}:{timeframe}:{start_date.isoformat()}:{end_date.isoformat()}"


def _build_checkpoint(*, symbol: str, timeframe: str, start_date: date, end_date: date, status: ManualPolygonOHLCVCheckpointStatus = ManualPolygonOHLCVCheckpointStatus.PLANNED, last_successful_observation_date: date | None = None) -> ManualPolygonOHLCVCheckpoint:
    return build_manual_polygon_ohlcv_checkpoint(
        checkpoint_key=_build_checkpoint_key(symbol=symbol, timeframe=timeframe, start_date=start_date, end_date=end_date),
        vendor="polygon",
        dataset="ohlcv",
        symbol=symbol,
        timeframe=timeframe,
        planned_start_date=start_date,
        planned_end_date=end_date,
        status=status,
        last_successful_observation_date=last_successful_observation_date,
    )


def _normalize_and_validate(symbol: str, raw_records: list[dict[str, object]], timeframe: str) -> tuple[list[NormalizedOHLCVRecord], int, int]:
    valid: list[NormalizedOHLCVRecord] = []
    invalid = 0
    validation_failures = 0
    for raw in raw_records:
        enriched = dict(raw)
        enriched["ticker"] = symbol
        enriched["timeframe"] = timeframe
        try:
            normalized = polygon_aggregate_to_normalized_ohlcv(enriched)
        except Exception:
            invalid += 1
            validation_failures += 1
            continue
        failures = [item for item in validate_ohlcv_record(normalized) if not item.passed]
        duplicate_failures = detect_duplicate_candles(valid + [normalized])
        if failures or duplicate_failures:
            invalid += 1
            validation_failures += len(failures) + len(duplicate_failures)
            continue
        valid.append(normalized)
    return valid, invalid, validation_failures


def _resolve_effective_start_date(*, requested_start_date: date, checkpoint: ManualPolygonOHLCVCheckpoint | None) -> date:
    if checkpoint and isinstance(checkpoint.last_successful_observation_date, date):
        return max(requested_start_date, checkpoint.last_successful_observation_date + timedelta(days=1))
    return requested_start_date


def _observation_date_from_row(row: dict[str, object]) -> date | None:
    raw = row.get("date") or row.get("observation_date")
    if isinstance(raw, date):
        return raw
    if isinstance(raw, str) and raw:
        try:
            return date.fromisoformat(raw)
        except ValueError:
            return None
    return None


def _filter_resumed(observations: list[dict[str, object]], checkpoint: ManualPolygonOHLCVCheckpoint | None) -> tuple[list[dict[str, object]], int]:
    if checkpoint is None or checkpoint.last_successful_observation_date is None:
        return observations, 0
    boundary = checkpoint.last_successful_observation_date
    filtered: list[dict[str, object]] = []
    skipped = 0
    for row in observations:
        observation_date = _observation_date_from_row(row)
        if observation_date is not None and observation_date <= boundary:
            skipped += 1
            continue
        filtered.append(row)
    return filtered, skipped


def build_manual_polygon_ohlcv_incremental(
    *,
    symbols: tuple[str, ...],
    start_date: date,
    end_date: date,
    timeframe: str,
    api_key: str,
    writer: OhlcvWriter | None = None,
    confirmed_write: bool = False,
    checkpoint_store: ManualPolygonOHLCVCheckpointStore | None = None,
    use_checkpoint: bool = False,
    update_checkpoint: bool = False,
) -> ManualPolygonOHLCVIncrementalSummary:
    client = _build_polygon_client(api_key)
    rows: list[ManualPolygonOHLCVIncrementalRow] = []
    for symbol in symbols:
        checkpoint_key = _build_checkpoint_key(symbol=symbol, timeframe=timeframe, start_date=start_date, end_date=end_date)
        checkpoint_loaded = False
        checkpoint = None
        try:
            if use_checkpoint and checkpoint_store is not None:
                checkpoint = checkpoint_store.load(checkpoint_key)
                checkpoint_loaded = checkpoint is not None
            resume_checkpoint = checkpoint if (
                checkpoint_loaded and isinstance(getattr(checkpoint, "last_successful_observation_date", None), date)
            ) else None
            effective_start = _resolve_effective_start_date(requested_start_date=start_date, checkpoint=resume_checkpoint)
            if effective_start > end_date:
                rows.append(
                    ManualPolygonOHLCVIncrementalRow(
                        symbol=symbol,
                        requested_start_date=start_date,
                        effective_start_date=effective_start,
                        rows_fetched=0,
                        rows_valid=0,
                        rows_invalid=0,
                        rows_written=0,
                        validation_failures=0,
                        planned_start_date=start_date,
                        planned_end_date=end_date,
                        write_confirmed=confirmed_write,
                        checkpoint_key=checkpoint_key,
                        checkpoint_loaded=checkpoint_loaded,
                        status="skipped_already_current",
                    )
                )
                continue
            raw_records = client.fetch_aggregates_raw(symbol, effective_start.isoformat(), end_date.isoformat())
            raw_records, resumed_skipped = _filter_resumed(raw_records, resume_checkpoint)
            if resumed_skipped and not raw_records:
                rows.append(
                    ManualPolygonOHLCVIncrementalRow(
                        symbol=symbol,
                        requested_start_date=start_date,
                        effective_start_date=effective_start,
                        rows_fetched=0,
                        rows_valid=0,
                        rows_invalid=0,
                        rows_written=0,
                        validation_failures=0,
                        planned_start_date=start_date,
                        planned_end_date=end_date,
                        write_confirmed=confirmed_write,
                        checkpoint_key=checkpoint_key,
                        checkpoint_loaded=checkpoint_loaded,
                        status="skipped_already_current",
                    )
                )
                continue
            valid_rows, rows_invalid, validation_failures = _normalize_and_validate(symbol, raw_records, timeframe)
            rows_written = 0
            status = "completed"
            error_message = None
            if confirmed_write and writer is not None and valid_rows:
                write_result = writer.write(valid_rows)
                rows_written = write_result.written_count
                if write_result.status == WriteStatus.SUCCESS:
                    if update_checkpoint and checkpoint_store is not None and rows_written > 0:
                        latest = max(record.timestamp.date() for record in valid_rows)
                        checkpoint_to_save = checkpoint or _build_checkpoint(
                            symbol=symbol,
                            timeframe=timeframe,
                            start_date=start_date,
                            end_date=end_date,
                        )
                        checkpoint_store.update_successful_observation_date(checkpoint_to_save, latest)
                else:
                    status = "failed"
                    error_message = _sanitize_error_message(str(write_result.message or "write failed"))
            rows.append(
                ManualPolygonOHLCVIncrementalRow(
                    symbol=symbol,
                    requested_start_date=start_date,
                    effective_start_date=effective_start,
                    rows_fetched=len(raw_records),
                    rows_valid=len(valid_rows),
                    rows_invalid=rows_invalid,
                    rows_written=rows_written,
                    validation_failures=validation_failures,
                    planned_start_date=start_date,
                    planned_end_date=end_date,
                    write_confirmed=confirmed_write,
                    checkpoint_key=checkpoint_key,
                    checkpoint_loaded=checkpoint_loaded,
                    status=status,
                    error_message=error_message,
                )
            )
        except Exception as exc:
            rows.append(
                ManualPolygonOHLCVIncrementalRow(
                    symbol=symbol,
                    requested_start_date=start_date,
                    effective_start_date=start_date,
                    rows_fetched=0,
                    rows_valid=0,
                    rows_invalid=0,
                    rows_written=0,
                    validation_failures=0,
                    planned_start_date=start_date,
                    planned_end_date=end_date,
                    write_confirmed=confirmed_write,
                    checkpoint_key=checkpoint_key,
                    checkpoint_loaded=checkpoint_loaded,
                    status="failed",
                    error_message=_sanitize_error_message(f"{exc.__class__.__name__}: {exc}"),
                )
            )
    return ManualPolygonOHLCVIncrementalSummary(
        symbol_summaries=tuple(rows),
        series_total=len(rows),
        series_completed=sum(1 for row in rows if row.status == "completed"),
        series_failed=sum(1 for row in rows if row.status == "failed"),
        series_skipped=sum(1 for row in rows if row.status.startswith("skipped")),
        total_rows_fetched=sum(row.rows_fetched for row in rows),
        total_rows_valid=sum(row.rows_valid for row in rows),
        total_rows_invalid=sum(row.rows_invalid for row in rows),
        total_rows_written=sum(row.rows_written for row in rows),
        total_validation_failures=sum(row.validation_failures for row in rows),
    )
