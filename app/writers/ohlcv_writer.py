from __future__ import annotations

from collections import OrderedDict
from datetime import datetime, timezone
from typing import Callable, Protocol

from app.models.normalized import NormalizedOHLCVRecord
from app.writers.canonical_writer import CanonicalWriter, WriteStatus, WriterResult


class _ExecuteResult(Protocol):
    rowcount: int


class _ConnectionLike(Protocol):
    def execute(self, sql: str, params: tuple[object, ...] = ()) -> _ExecuteResult: ...
    def cursor(self): ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...


class OhlcvWriter:
    writer_name = "ohlcv_writer"

    def __init__(self, connection: _ConnectionLike | Callable[[], _ConnectionLike] | None = None) -> None:
        self._connection_or_factory = connection

    def _connection(self) -> _ConnectionLike:
        connection = self._connection_or_factory
        if connection is None:
            raise RuntimeError("OHLCV writer requires a database connection.")
        return connection() if callable(connection) else connection

    def _use_cursor(self, connection: object) -> bool:
        return hasattr(connection, "cursor") and not hasattr(connection, "execute")

    def _fetch_all(self, connection: object, sql: str, params: tuple[object, ...] = ()) -> list[dict[str, object]]:
        cursor = None
        try:
            if self._use_cursor(connection):
                cursor = connection.cursor()
                cursor.execute(sql, params)
                rows = cursor.fetchall()
            else:
                result = connection.execute(sql, params)  # type: ignore[call-arg]
                rows = result.fetchall() if hasattr(result, "fetchall") else []
            if not rows:
                return []
            first = rows[0]
            if isinstance(first, dict):
                return [row for row in rows if isinstance(row, dict)]
            columns = [desc[0] for desc in getattr(cursor, "description", [])] if cursor is not None else []
            return [dict(zip(columns, row)) for row in rows]
        finally:
            if cursor is not None and hasattr(cursor, "close"):
                cursor.close()

    def _execute(self, connection: object, sql: str, params: tuple[object, ...] = ()) -> _ExecuteResult | None:
        if self._use_cursor(connection):
            cursor = connection.cursor()
            try:
                return cursor.execute(sql, params)
            finally:
                if hasattr(cursor, "close"):
                    cursor.close()
        return connection.execute(sql, params)  # type: ignore[call-arg]

    def _utc_now(self) -> datetime:
        return datetime.now(timezone.utc)

    def _contract(self, connection: object) -> dict[str, bool]:
        rows = self._fetch_all(
            connection,
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %s
            """.strip(),
            ("canonical_ohlcv",),
        )
        columns = {str(row.get("column_name")) for row in rows if row.get("column_name")}
        required = {"symbol_id", "timestamp", "timeframe", "adjusted", "open", "high", "low", "close", "volume", "vendor", "source"}
        if not required.issubset(columns):
            raise RuntimeError("canonical_ohlcv schema contract is not available for manual OHLCV persistence.")
        return {
            "ingestion_run_id": "ingestion_run_id" in columns,
            "normalization_version": "normalization_version" in columns,
            "quality_status": "quality_status" in columns,
            "created_at": "created_at" in columns,
            "updated_at": "updated_at" in columns,
        }

    def _dedupe(self, records: list[NormalizedOHLCVRecord]) -> tuple[list[NormalizedOHLCVRecord], int]:
        unique: "OrderedDict[tuple[object, ...], NormalizedOHLCVRecord]" = OrderedDict()
        skipped = 0
        for record in records:
            key = (record.symbol_id or record.symbol, record.timestamp, record.timeframe, record.adjusted)
            if key in unique:
                skipped += 1
                continue
            unique[key] = record
        return list(unique.values()), skipped

    def write(self, records: list[NormalizedOHLCVRecord]) -> WriterResult:
        if not records:
            return WriterResult(writer_name=self.writer_name, status=WriteStatus.SKIPPED, skipped_count=0)
        connection = self._connection()
        contract = self._contract(connection)
        unique_records, skipped = self._dedupe(records)
        columns = ["symbol_id", "timestamp", "timeframe", "adjusted", "open", "high", "low", "close", "volume", "vendor", "source"]
        if contract["ingestion_run_id"]:
            columns.append("ingestion_run_id")
        if contract["normalization_version"]:
            columns.append("normalization_version")
        if contract["quality_status"]:
            columns.append("quality_status")
        if contract["created_at"]:
            columns.append("created_at")
        if contract["updated_at"]:
            columns.append("updated_at")
        update_clauses = [
            "open = excluded.open",
            "high = excluded.high",
            "low = excluded.low",
            "close = excluded.close",
            "volume = excluded.volume",
            "vendor = excluded.vendor",
            "source = excluded.source",
        ]
        if contract["ingestion_run_id"]:
            update_clauses.append("ingestion_run_id = excluded.ingestion_run_id")
        if contract["normalization_version"]:
            update_clauses.append("normalization_version = excluded.normalization_version")
        if contract["quality_status"]:
            update_clauses.append("quality_status = excluded.quality_status")
        if contract["updated_at"]:
            update_clauses.append("updated_at = excluded.updated_at")

        try:
            for record in unique_records:
                row: list[object] = [
                    record.symbol_id or record.symbol,
                    record.timestamp,
                    record.timeframe,
                    record.adjusted,
                    record.open,
                    record.high,
                    record.low,
                    record.close,
                    record.volume,
                    record.vendor,
                    record.source,
                ]
                if contract["ingestion_run_id"]:
                    row.append(record.ingestion_run_id)
                if contract["normalization_version"]:
                    row.append(record.normalization_version)
                if contract["quality_status"]:
                    row.append(record.quality_status)
                if contract["created_at"]:
                    row.append(self._utc_now())
                if contract["updated_at"]:
                    row.append(self._utc_now())
                self._execute(
                    connection,
                    f"""
                    INSERT INTO canonical_ohlcv ({", ".join(columns)})
                    VALUES ({", ".join(["%s"] * len(columns))})
                    ON CONFLICT (symbol_id, timestamp, timeframe, adjusted) DO UPDATE SET
                        {", ".join(update_clauses)}
                    """.strip(),
                    tuple(row),
                )
            connection.commit()
            return WriterResult(
                writer_name=self.writer_name,
                status=WriteStatus.SUCCESS,
                written_count=len(unique_records),
                skipped_count=skipped,
            )
        except Exception as exc:
            connection.rollback()
            message = f"{exc.__class__.__name__}: {exc}"
            return WriterResult(
                writer_name=self.writer_name,
                status=WriteStatus.FAILURE,
                failed_count=len(unique_records),
                skipped_count=skipped,
                message=message,
                details={"error_type": exc.__class__.__name__, "error_message": message},
            )


def build_ohlcv_writer() -> CanonicalWriter:
    return OhlcvWriter()
