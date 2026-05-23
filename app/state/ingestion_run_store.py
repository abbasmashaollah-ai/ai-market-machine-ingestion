from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Protocol

from app.state.errors import IngestionErrorRecord
from app.state.runs import IngestionRun, RunStatus


class _ExecuteResult(Protocol):
    rowcount: int


class _ConnectionLike(Protocol):
    def execute(self, sql: str, params: tuple[object, ...] = ()) -> _ExecuteResult: ...
    def cursor(self): ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...


ConnectionFactory = Callable[[], _ConnectionLike]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _use_cursor(connection: object) -> bool:
    return hasattr(connection, "cursor") and not hasattr(connection, "execute")


def _fetch_all(connection: object, sql: str, params: tuple[object, ...] = ()) -> list[dict[str, object]]:
    cursor = None
    try:
        if _use_cursor(connection):
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


def _execute(connection: object, sql: str, params: tuple[object, ...] = ()) -> _ExecuteResult | None:
    if _use_cursor(connection):
        cursor = connection.cursor()
        try:
            return cursor.execute(sql, params)
        finally:
            if hasattr(cursor, "close"):
                cursor.close()
    return connection.execute(sql, params)  # type: ignore[call-arg]


@dataclass(frozen=True)
class _TableContract:
    columns: set[str]


class IngestionRunStore:
    def __init__(self, connection: _ConnectionLike | ConnectionFactory) -> None:
        self._connection_or_factory = connection

    def _connection(self) -> _ConnectionLike:
        connection = self._connection_or_factory
        return connection() if callable(connection) else connection

    def _contract(self, connection: object, table_name: str) -> _TableContract:
        try:
            rows = _fetch_all(
                connection,
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = %s
                """.strip(),
                (table_name,),
            )
        except Exception as exc:
            raise RuntimeError(f"{table_name} table is not available for manual run history persistence.") from exc
        columns = {str(row.get("column_name")) for row in rows if row.get("column_name")}
        if not columns:
            raise RuntimeError(f"{table_name} table is not available for manual run history persistence.")
        return _TableContract(columns=columns)

    def _require_columns(self, table_name: str, contract: _TableContract, required: set[str]) -> None:
        if not required.issubset(contract.columns):
            missing = ", ".join(sorted(required - contract.columns))
            raise RuntimeError(
                f"{table_name} schema contract is not available for manual run history persistence. Missing columns: {missing}."
            )

    def save_run(self, run: IngestionRun) -> None:
        connection = self._connection()
        contract = self._contract(connection, "ingestion_runs")
        required = {"run_id", "vendor", "dataset", "status", "rows_fetched", "rows_written", "rows_rejected", "error_count", "created_at", "updated_at"}
        self._require_columns("ingestion_runs", contract, required)
        now = _utc_now()
        columns = ["run_id", "vendor", "dataset", "status", "rows_fetched", "rows_written", "rows_rejected", "error_count", "created_at", "updated_at"]
        values: list[object] = [
            run.run_id,
            str(run.metadata.get("vendor", "polygon")),
            str(run.metadata.get("dataset", "ohlcv")),
            run.status.value,
            run.rows_fetched,
            run.rows_written,
            run.rows_rejected,
            run.error_count,
            run.metadata.get("created_at") or now,
            run.metadata.get("updated_at") or now,
        ]
        if "job_id" in contract.columns:
            columns.append("job_id")
            job_id_value = run.metadata.get("job_id")
            values.append(job_id_value if isinstance(job_id_value, int) else None)
        if "started_at" in contract.columns:
            columns.append("started_at")
            values.append(run.metadata.get("started_at") or now)
        if "finished_at" in contract.columns:
            columns.append("finished_at")
            values.append(run.metadata.get("finished_at") or now)
        try:
            _execute(
                connection,
                f"INSERT INTO ingestion_runs ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})",
                tuple(values),
            )
            connection.commit()
        except Exception as exc:
            connection.rollback()
            raise RuntimeError("Failed to persist manual ingestion run history safely.") from exc

    def save_errors(self, run_id: str, errors: list[IngestionErrorRecord]) -> None:
        if not errors:
            return
        connection = self._connection()
        contract = self._contract(connection, "ingestion_errors")
        required = {"run_id", "vendor", "dataset", "symbol", "timeframe", "error_type", "error_message", "retryable", "created_at"}
        self._require_columns("ingestion_errors", contract, required)
        try:
            for error in errors:
                columns = ["run_id", "vendor", "dataset", "symbol", "timeframe", "error_type", "error_message", "retryable", "created_at"]
                values: list[object] = [
                    run_id,
                    str(error.metadata.get("vendor", "polygon")),
                    str(error.metadata.get("dataset", "ohlcv")),
                    error.metadata.get("symbol"),
                    error.metadata.get("timeframe"),
                    error.error_type,
                    error.message,
                    error.retryable,
                    error.occurred_at or _utc_now(),
                ]
                if "job_id" in contract.columns:
                    columns.append("job_id")
                    job_id_value = error.metadata.get("job_id")
                    values.append(job_id_value if isinstance(job_id_value, int) else None)
                _execute(
                    connection,
                    f"INSERT INTO ingestion_errors ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})",
                    tuple(values),
                )
            connection.commit()
        except Exception as exc:
            connection.rollback()
            raise RuntimeError("Failed to persist manual ingestion error history safely.") from exc
