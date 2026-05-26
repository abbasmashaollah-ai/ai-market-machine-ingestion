from __future__ import annotations

from collections import OrderedDict
from datetime import datetime, timezone
import re
from typing import Callable, Protocol

from app.normalization.fred_macro import NormalizedFredMacroRecord
from app.writers.canonical_writer import CanonicalWriter, WriteStatus, WriterResult


class _ExecuteResult(Protocol):
    rowcount: int


class _ConnectionLike(Protocol):
    def execute(self, sql: str, params: tuple[object, ...] = ()) -> _ExecuteResult: ...
    def cursor(self): ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _dedupe(records: list[NormalizedFredMacroRecord]) -> tuple[list[NormalizedFredMacroRecord], int]:
    unique: "OrderedDict[tuple[str, str, str], NormalizedFredMacroRecord]" = OrderedDict()
    skipped = 0
    for record in records:
        key = (record.series_id, record.observation_date.isoformat(), record.source)
        if key in unique:
            skipped += 1
            continue
        unique[key] = record
    return list(unique.values()), skipped


def _insert_sql() -> str:
    return """
    INSERT INTO macro_rate_observations (
        series_id,
        observation_date,
        value,
        source,
        release_timestamp,
        revision_timestamp,
        created_at
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (series_id, observation_date, source)
    DO UPDATE SET
        value = excluded.value
    """.strip()


def _sanitize_error_message(message: str) -> str:
    sanitized = message
    sanitized = re.sub(r"(?i)postgres(?:ql)?://[^\s@]+@", "database connection://<redacted>@", sanitized)
    sanitized = re.sub(r"(?i)postgres(?:ql)?://[^\s]+", "database connection", sanitized)
    sanitized = re.sub(r"(?i)(password|passwd|pwd|token|secret|key)=([^\s&]+)", r"\1=<redacted>", sanitized)
    sanitized = re.sub(r"(?i)DATABASE_URL", "database connection", sanitized)
    sanitized = re.sub(r"(?i)permission denied", "database permission denied", sanitized)
    sanitized = re.sub(r"(?i)relation \"[^\"]+\" does not exist", "missing table or view", sanitized)
    sanitized = re.sub(r"(?i)column \"[^\"]+\" does not exist", "missing column", sanitized)
    sanitized = re.sub(r"(?i)duplicate key value violates unique constraint", "unique constraint violation", sanitized)
    sanitized = re.sub(r"(?i)could not connect to server", "connection failure", sanitized)
    sanitized = re.sub(r"(?i)connection refused", "connection failure", sanitized)
    sanitized = re.sub(r"(?i)syntax error at or near", "sql failure", sanitized)
    return sanitized.strip()


class FredMacroWriter:
    writer_name = "fred_macro_writer"

    def __init__(self, connection: _ConnectionLike | Callable[[], _ConnectionLike] | None = None) -> None:
        self._connection_or_factory = connection

    def _connection(self) -> _ConnectionLike:
        connection = self._connection_or_factory
        if connection is None:
            raise RuntimeError("fred macro writer requires a database connection.")
        if hasattr(connection, "execute") or hasattr(connection, "cursor"):
            return connection  # type: ignore[return-value]
        return connection()  # type: ignore[operator]

    def _execute(self, connection: object, sql: str, params: tuple[object, ...]) -> _ExecuteResult | None:
        if hasattr(connection, "cursor") and not hasattr(connection, "execute"):
            cursor = connection.cursor()
            try:
                return cursor.execute(sql, params)
            finally:
                if hasattr(cursor, "close"):
                    cursor.close()
        return connection.execute(sql, params)  # type: ignore[call-arg]

    def write(self, records: list[NormalizedFredMacroRecord]) -> WriterResult:
        if not records:
            return WriterResult(writer_name=self.writer_name, status=WriteStatus.SKIPPED, skipped_count=0)
        connection = None
        try:
            connection = self._connection()
            unique_records, skipped = _dedupe(records)
            for record in unique_records:
                self._execute(
                    connection,
                    _insert_sql(),
                    (
                        record.series_id,
                        record.observation_date,
                        record.value,
                        record.source,
                        None,
                        None,
                        _utc_now(),
                    ),
                )
            connection.commit()
            return WriterResult(
                writer_name=self.writer_name,
                status=WriteStatus.SUCCESS,
                written_count=len(unique_records),
                skipped_count=skipped,
            )
        except Exception as exc:
            if connection is not None and hasattr(connection, "rollback"):
                connection.rollback()
            sanitized_message = _sanitize_error_message(str(exc))
            message = f"{exc.__class__.__name__}: {sanitized_message}"
            return WriterResult(
                writer_name=self.writer_name,
                status=WriteStatus.FAILURE,
                failed_count=0,
                skipped_count=0,
                message=message,
                details={"error_type": exc.__class__.__name__, "error_message": sanitized_message},
            )
        finally:
            if connection is not None and hasattr(connection, "close"):
                try:
                    connection.close()
                except Exception:
                    pass


def build_fred_macro_writer(connection: _ConnectionLike | Callable[[], _ConnectionLike] | None = None) -> CanonicalWriter:
    return FredMacroWriter(connection)
