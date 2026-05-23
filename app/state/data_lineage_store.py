from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Protocol


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


class DataLineageStore:
    def __init__(self, connection: _ConnectionLike | ConnectionFactory) -> None:
        self._connection_or_factory = connection

    def _connection(self) -> _ConnectionLike:
        connection = self._connection_or_factory
        return connection() if callable(connection) else connection

    def _contract(self, connection: object) -> _TableContract:
        try:
            rows = _fetch_all(
                connection,
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = %s
                """.strip(),
                ("data_lineage",),
            )
        except Exception as exc:
            raise RuntimeError("data_lineage table is not available for manual lineage persistence.") from exc
        columns = {str(row.get("column_name")) for row in rows if row.get("column_name")}
        if not columns:
            raise RuntimeError("data_lineage table is not available for manual lineage persistence.")
        return _TableContract(columns=columns)

    def _require_columns(self, contract: _TableContract, required: set[str]) -> None:
        if not required.issubset(contract.columns):
            missing = ", ".join(sorted(required - contract.columns))
            raise RuntimeError(
                f"data_lineage schema contract is not available for manual lineage persistence. Missing columns: {missing}."
            )

    def save_chunk_lineage(
        self,
        *,
        vendor: str,
        dataset: str,
        symbol: str | None,
        timeframe: str | None,
        source_endpoint: str | None = None,
        request_params: str | None = None,
        response_status: int | None = None,
        row_count: int | None = None,
        normalization_version: str | None = None,
        quality_status: str | None = None,
        run_id: str | None = None,
        job_id: str | None = None,
    ) -> None:
        connection = self._connection()
        contract = self._contract(connection)
        required = {"vendor", "dataset", "created_at"}
        self._require_columns(contract, required)
        columns = ["vendor", "dataset", "created_at"]
        values: list[object] = [vendor, dataset, _utc_now()]
        optional_fields = (
            ("symbol", symbol),
            ("timeframe", timeframe),
            ("source_endpoint", source_endpoint),
            ("request_params", request_params),
            ("response_status", response_status),
            ("row_count", row_count),
            ("normalization_version", normalization_version),
            ("quality_status", quality_status),
            ("run_id", run_id),
            ("job_id", job_id),
        )
        for field_name, field_value in optional_fields:
            if field_name in contract.columns:
                columns.append(field_name)
                values.append(field_value)
        try:
            _execute(
                connection,
                f"INSERT INTO data_lineage ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})",
                tuple(values),
            )
            connection.commit()
        except Exception as exc:
            connection.rollback()
            raise RuntimeError("Failed to persist manual data lineage safely.") from exc
