from __future__ import annotations

from collections.abc import Callable
from contextlib import AbstractContextManager
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
import re
from typing import Protocol

from app.models.normalized import NormalizedMacroObservation
from app.writers.canonical_writer import CanonicalWriter, WriteStatus, WriterResult


class _ExecuteResult(Protocol):
    rowcount: int


class _ConnectionLike(Protocol):
    def execute(self, sql: str, params: tuple[object, ...]) -> _ExecuteResult: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
    def close(self) -> None: ...


ConnectionFactory = Callable[[], _ConnectionLike | AbstractContextManager[_ConnectionLike]]


@dataclass(frozen=True)
class MacroObservationRow:
    series_id: str
    observation_date: str
    value: float | None
    source: str
    release_timestamp: str | None
    revision_timestamp: str | None
    created_at: str


def _utc_iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()


def _observation_date(value: datetime | date) -> str:
    if isinstance(value, datetime):
        return value.date().isoformat()
    return value.isoformat()


def _normalize_source(record: NormalizedMacroObservation) -> str:
    if record.source and record.source.strip():
        return record.source
    if record.vendor and record.vendor.upper() == "FRED":
        return "FRED"
    return "FRED"


def _normalize_value(record: NormalizedMacroObservation) -> float | None:
    value = record.value
    if value is None:
        return None
    if isinstance(value, str):
        raw = value.strip()
        if not raw or raw == ".":
            return None
        try:
            return float(Decimal(raw))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(f"Invalid macro observation value: {value!r}") from exc
    return float(value)


def _row_from_record(record: NormalizedMacroObservation) -> MacroObservationRow:
    if not record.symbol_id:
        raise ValueError("symbol_id is required for macro_rate_observations writes")
    return MacroObservationRow(
        series_id=record.symbol_id,
        observation_date=_observation_date(record.timestamp),
        value=_normalize_value(record),
        source=_normalize_source(record),
        release_timestamp=None,
        revision_timestamp=None,
        created_at=_utc_iso(record.timestamp),
    )


def _sanitize_error_message(message: str) -> str:
    sanitized = message
    sanitized = re.sub(r"(?i)(postgres(?:ql)?://)([^\s:@/]+)(?::([^\s@/]+))?@", r"\1<redacted>@", sanitized)
    sanitized = re.sub(r"(?i)(password|passwd|pwd|token|secret|key)=([^\s&]+)", r"\1=<redacted>", sanitized)
    sanitized = re.sub(r"(?i)DATABASE_URL", "database connection", sanitized)
    return sanitized


class MacroWriter:
    writer_name = "macro_writer"

    def __init__(self, connection: _ConnectionLike | ConnectionFactory | None = None) -> None:
        self._connection = connection

    def write(self, records: list[NormalizedMacroObservation]) -> WriterResult:
        if self._connection is None:
            raise NotImplementedError("Macro writer requires an explicit database connection.")
        if not records:
            return WriterResult(
                writer_name=self.writer_name,
                status=WriteStatus.SKIPPED,
                written_count=0,
                skipped_count=0,
                failed_count=0,
                message="No macro records to write.",
                details={"written": 0, "updated": 0, "skipped": 0, "failed": 0},
            )

        rows: list[MacroObservationRow] = []
        skipped = 0
        seen: set[tuple[str, str, str]] = set()
        for record in records:
            row = _row_from_record(record)
            key = (row.series_id, row.observation_date, row.source)
            if key in seen:
                skipped += 1
                continue
            seen.add(key)
            rows.append(row)

        connection = self._resolve_connection()
        written = 0
        updated = 0
        try:
            for row in rows:
                result = connection.execute(
                    """
                    INSERT INTO macro_rate_observations (
                        series_id,
                        observation_date,
                        value,
                        source,
                        release_timestamp,
                        revision_timestamp,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(series_id, observation_date, source)
                    DO UPDATE SET
                        value = excluded.value,
                        release_timestamp = excluded.release_timestamp,
                        revision_timestamp = excluded.revision_timestamp
                    """.strip(),
                    (
                        row.series_id,
                        row.observation_date,
                        row.value,
                        row.source,
                        row.release_timestamp,
                        row.revision_timestamp,
                        row.created_at,
                    ),
                )
                rowcount = getattr(result, "rowcount", 0)
                if rowcount == 1:
                    written += 1
                else:
                    updated += 1
            connection.commit()
        except Exception as exc:
            connection.rollback()
            error_type = exc.__class__.__name__
            error_message = _sanitize_error_message(str(exc))
            return WriterResult(
                writer_name=self.writer_name,
                status=WriteStatus.FAILURE,
                written_count=written,
                skipped_count=skipped,
                failed_count=len(records) - written - skipped,
                message=f"{error_type}: {error_message}",
                details={
                    "written": written,
                    "updated": updated,
                    "skipped": skipped,
                    "failed": len(records) - written - skipped,
                    "error_type": error_type,
                    "error_message": error_message,
                },
            )

        return WriterResult(
            writer_name=self.writer_name,
            status=WriteStatus.SUCCESS,
            written_count=written + updated,
            skipped_count=skipped,
            failed_count=0,
            details={"written": written, "updated": updated, "skipped": skipped, "failed": 0},
        )

    def _resolve_connection(self) -> _ConnectionLike:
        connection = self._connection
        if not hasattr(connection, "execute") and callable(connection):
            connection = connection()
        if hasattr(connection, "__enter__") and hasattr(connection, "__exit__"):
            return connection.__enter__()
        return connection


def build_macro_writer(connection: _ConnectionLike | ConnectionFactory | None = None) -> CanonicalWriter:
    return MacroWriter(connection)
