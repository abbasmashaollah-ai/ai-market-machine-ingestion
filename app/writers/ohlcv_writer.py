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

    def _contract(self, connection: object) -> tuple[set[str], bool]:
        rows = self._fetch_all(
            connection,
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            """.strip(),
            ("public", "canonical_ohlcv"),
        )
        columns = {str(row.get("column_name")) for row in rows if row.get("column_name")}
        required = {
            "symbol",
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "source",
            "adjustment_status",
            "data_quality_status",
            "timeframe",
            "adjusted",
        }
        missing_columns = required - columns
        if missing_columns:
            raise RuntimeError(
                "canonical_ohlcv schema contract is not available for manual OHLCV persistence. "
                f"Missing columns: {', '.join(sorted(missing_columns))}."
            )
        index_rows = self._fetch_all(
            connection,
            """
            SELECT indexdef
            FROM pg_indexes
            WHERE schemaname = %s AND tablename = %s
            """.strip(),
            ("public", "canonical_ohlcv"),
        )
        index_defs = [str(row.get("indexdef") or "") for row in index_rows]
        conflict_target = any(
            "UNIQUE" in index_def.upper()
            and "symbol" in index_def
            and "timestamp" in index_def
            and "timeframe" in index_def
            and "adjusted" in index_def
            for index_def in index_defs
        )
        return columns, conflict_target

    def _dedupe(self, records: list[NormalizedOHLCVRecord]) -> tuple[list[NormalizedOHLCVRecord], int]:
        unique: "OrderedDict[tuple[object, ...], NormalizedOHLCVRecord]" = OrderedDict()
        skipped = 0
        for record in records:
            key = (record.symbol or record.symbol_id, record.timestamp, record.timeframe, record.adjusted)
            if key in unique:
                skipped += 1
                continue
            unique[key] = record
        return list(unique.values()), skipped

    def write(self, records: list[NormalizedOHLCVRecord]) -> WriterResult:
        if not records:
            return WriterResult(writer_name=self.writer_name, status=WriteStatus.SKIPPED, skipped_count=0)
        connection = None
        try:
            connection = self._connection()
            columns_present, conflict_target = self._contract(connection)
            if not conflict_target:
                raise RuntimeError(
                    "canonical_ohlcv uniqueness contract is not available for manual OHLCV persistence. "
                    "Expected a unique constraint or index on symbol + timestamp + timeframe + adjusted."
                )
            unique_records, skipped = self._dedupe(records)
            columns = ["symbol", "timestamp", "open", "high", "low", "close", "volume", "source", "adjustment_status", "data_quality_status", "timeframe", "adjusted"]
            if "created_at" in columns_present:
                columns.append("created_at")
            if "updated_at" in columns_present:
                columns.append("updated_at")
            update_clauses = [
                "open = excluded.open",
                "high = excluded.high",
                "low = excluded.low",
                "close = excluded.close",
                "volume = excluded.volume",
                "source = excluded.source",
                "adjustment_status = excluded.adjustment_status",
                "data_quality_status = excluded.data_quality_status",
                "timeframe = excluded.timeframe",
                "adjusted = excluded.adjusted",
            ]
            if "updated_at" in columns_present:
                update_clauses.append("updated_at = excluded.updated_at")

            for record in unique_records:
                row: list[object] = [
                    record.symbol or record.symbol_id,
                    record.timestamp,
                    record.open,
                    record.high,
                    record.low,
                    record.close,
                    record.volume,
                    record.source,
                    "adjusted" if record.adjusted else "unadjusted",
                    record.quality_status or "pending",
                    record.timeframe,
                    record.adjusted,
                ]
                if "created_at" in columns_present:
                    row.append(self._utc_now())
                if "updated_at" in columns_present:
                    row.append(self._utc_now())
                self._execute(
                    connection,
                    f"""
                    INSERT INTO canonical_ohlcv ({", ".join(columns)})
                    VALUES ({", ".join(["%s"] * len(columns))})
                    ON CONFLICT (symbol, timestamp, timeframe, adjusted) DO UPDATE SET
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
            if connection is not None and hasattr(connection, "rollback"):
                connection.rollback()
            message = f"{exc.__class__.__name__}: {exc}"
            return WriterResult(
                writer_name=self.writer_name,
                status=WriteStatus.FAILURE,
                failed_count=0,
                skipped_count=0,
                message=message,
                details={"error_type": exc.__class__.__name__, "error_message": message},
            )


def build_ohlcv_writer() -> CanonicalWriter:
    return OhlcvWriter()
