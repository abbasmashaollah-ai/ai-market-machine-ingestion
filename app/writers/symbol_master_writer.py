from __future__ import annotations

from collections import OrderedDict
from datetime import datetime, timezone
from typing import Callable, Protocol

from app.normalization.symbol_master import NormalizedSymbolMasterRecord, build_symbol_identity_idempotency_key
from app.writers.canonical_writer import CanonicalWriter, WriteStatus, WriterResult


class _ExecuteResult(Protocol):
    rowcount: int


class _ConnectionLike(Protocol):
    def execute(self, sql: str, params: tuple[object, ...] = ()) -> _ExecuteResult: ...
    def cursor(self): ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...


class SymbolMasterWriter:
    writer_name = "symbol_master_writer"

    def __init__(self, connection: _ConnectionLike | Callable[[], _ConnectionLike] | None = None) -> None:
        self._connection_or_factory = connection

    def _connection(self) -> _ConnectionLike:
        connection = self._connection_or_factory
        if connection is None:
            raise RuntimeError("symbol master writer requires a database connection.")
        if hasattr(connection, "execute") or hasattr(connection, "cursor"):
            return connection  # type: ignore[return-value]
        return connection()  # type: ignore[operator]

    def _use_cursor(self, connection: object) -> bool:
        return hasattr(connection, "cursor") and not hasattr(connection, "execute")

    def _fetch_all(self, connection: object, sql: str, params: tuple[object, ...] = ()) -> list[dict[str, object]]:
        cursor = None
        result = None
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
            description_source = cursor if cursor is not None else result
            columns = [desc[0] for desc in getattr(description_source, "description", [])]
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

    def _contract(self, connection: object) -> set[str]:
        rows = self._fetch_all(
            connection,
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            """.strip(),
            ("public", "symbol_master"),
        )
        columns = {str(row.get("column_name")) for row in rows if row.get("column_name")}
        required = {
            "symbol",
            "active",
            "vendor",
            "vendor_symbol",
            "exchange",
            "asset_type",
            "name",
            "currency",
            "first_seen_at",
            "last_seen_at",
        }
        missing_columns = required - columns
        if missing_columns:
            raise RuntimeError(
                "symbol_master schema contract is not available for manual symbol-master persistence. "
                f"Missing columns: {', '.join(sorted(missing_columns))}."
            )
        return columns

    def _dedupe(self, records: list[NormalizedSymbolMasterRecord]) -> tuple[list[NormalizedSymbolMasterRecord], int]:
        unique: "OrderedDict[str, NormalizedSymbolMasterRecord]" = OrderedDict()
        skipped = 0
        for record in records:
            key = record.symbol or ""
            if key in unique:
                skipped += 1
                continue
            unique[key] = record
        return list(unique.values()), skipped

    def _idempotency_key(self, record: NormalizedSymbolMasterRecord) -> str | None:
        return build_symbol_identity_idempotency_key(
            record.source_vendor or record.vendor,
            record.source_dataset,
            record.source_sha256,
            record.asset_type,
            record.symbol,
        )

    def write(self, records: list[NormalizedSymbolMasterRecord]) -> WriterResult:
        if not records:
            return WriterResult(writer_name=self.writer_name, status=WriteStatus.SKIPPED, skipped_count=0)
        connection = None
        try:
            connection = self._connection()
            columns_present = self._contract(connection)
            unique_records, skipped = self._dedupe(records)
            idempotency_keys = [key for key in (self._idempotency_key(record) for record in unique_records) if key]
            columns = [
                "symbol",
                "vendor",
                "vendor_symbol",
                "exchange",
                "asset_type",
                "name",
                "currency",
                "active",
                "first_seen_at",
                "last_seen_at",
            ]
            if "created_at" in columns_present:
                columns.append("created_at")
            if "updated_at" in columns_present:
                columns.append("updated_at")

            update_clauses = [
                "vendor = excluded.vendor",
                "vendor_symbol = excluded.vendor_symbol",
                "exchange = excluded.exchange",
                "asset_type = excluded.asset_type",
                "name = excluded.name",
                "currency = excluded.currency",
                "active = excluded.active",
                "first_seen_at = excluded.first_seen_at",
                "last_seen_at = excluded.last_seen_at",
            ]
            if "updated_at" in columns_present:
                update_clauses.append("updated_at = excluded.updated_at")

            for record in unique_records:
                row: list[object] = [
                    record.symbol,
                    record.vendor,
                    record.vendor_symbol,
                    record.exchange,
                    record.asset_type,
                    record.name,
                    record.currency,
                    record.active,
                    record.first_seen_at,
                    record.last_seen_at,
                ]
                if "created_at" in columns_present:
                    row.append(self._utc_now())
                if "updated_at" in columns_present:
                    row.append(self._utc_now())
                self._execute(
                    connection,
                    f"""
                    INSERT INTO symbol_master ({", ".join(columns)})
                    VALUES ({", ".join(["%s"] * len(columns))})
                    ON CONFLICT (symbol) DO UPDATE SET
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
                details={
                    "idempotency_keys": tuple(idempotency_keys),
                    "idempotency_key_formula": "sha256(source_vendor|source_dataset|source_sha256|asset_type|symbol)",
                    "idempotency_key_storage": "preserved_in_writer_result_only",
                },
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


def build_symbol_master_writer() -> CanonicalWriter:
    return SymbolMasterWriter()
