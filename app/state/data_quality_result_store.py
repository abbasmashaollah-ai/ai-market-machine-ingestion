from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Protocol

from app.quality.validators import ValidationResult


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


class DataQualityResultStore:
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
                ("data_quality_results",),
            )
        except Exception as exc:
            raise RuntimeError("data_quality_results table is not available for manual quality persistence.") from exc
        columns = {str(row.get("column_name")) for row in rows if row.get("column_name")}
        if not columns:
            raise RuntimeError("data_quality_results table is not available for manual quality persistence.")
        return _TableContract(columns=columns)

    def _require_columns(self, contract: _TableContract, required: set[str]) -> None:
        if not required.issubset(contract.columns):
            missing = ", ".join(sorted(required - contract.columns))
            raise RuntimeError(
                f"data_quality_results schema contract is not available for manual quality persistence. Missing columns: {missing}."
            )

    def save_results(
        self,
        *,
        vendor: str,
        dataset: str,
        symbol: str | None,
        timeframe: str | None,
        check_name: str,
        status: str,
        severity: str | None = None,
        message: str | None = None,
        observed_value: object | None = None,
        expected_value: object | None = None,
        run_id: str | None = None,
        job_id: int | None = None,
    ) -> None:
        connection = self._connection()
        contract = self._contract(connection)
        required = {"vendor", "dataset", "check_name", "status", "created_at"}
        self._require_columns(contract, required)
        columns = ["vendor", "dataset", "check_name", "status", "created_at"]
        values: list[object] = [vendor, dataset, check_name, status, _utc_now()]
        if "symbol" in contract.columns:
            columns.append("symbol")
            values.append(symbol)
        if "timeframe" in contract.columns:
            columns.append("timeframe")
            values.append(timeframe)
        if "severity" in contract.columns:
            columns.append("severity")
            values.append(severity)
        if "message" in contract.columns:
            columns.append("message")
            values.append(message)
        if "observed_value" in contract.columns:
            columns.append("observed_value")
            values.append(None if observed_value is None else str(observed_value))
        if "expected_value" in contract.columns:
            columns.append("expected_value")
            values.append(None if expected_value is None else str(expected_value))
        if "run_id" in contract.columns:
            columns.append("run_id")
            values.append(run_id)
        if "job_id" in contract.columns:
            columns.append("job_id")
            values.append(job_id)
        try:
            _execute(
                connection,
                f"INSERT INTO data_quality_results ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})",
                tuple(values),
            )
            connection.commit()
        except Exception as exc:
            connection.rollback()
            raise RuntimeError("Failed to persist manual data quality results safely.") from exc

    def save_validation_results(
        self,
        *,
        vendor: str,
        dataset: str,
        symbol: str | None,
        timeframe: str | None,
        results: list[ValidationResult],
        run_id: str | None = None,
        job_id: int | None = None,
    ) -> None:
        for result in results:
            observed_value = result.details.get("observed_value")
            expected_value = result.details.get("expected_value")
            self.save_results(
                vendor=vendor,
                dataset=dataset,
                symbol=symbol,
                timeframe=timeframe,
                check_name=result.check_name,
                status=result.status.value,
                severity=result.severity.value if hasattr(result.severity, "value") else str(result.severity),
                message=result.message,
                observed_value=observed_value,
                expected_value=expected_value,
                run_id=run_id,
                job_id=job_id,
            )
