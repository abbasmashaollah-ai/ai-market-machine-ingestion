from __future__ import annotations

from dataclasses import asdict
from datetime import date, datetime, timezone
from typing import Callable, Protocol

from app.state.manual_fred_macro import ManualFREDMacroCheckpoint, ManualFREDMacroCheckpointStatus, build_manual_fred_macro_checkpoint


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


class ManualFREDMacroCheckpointStore:
    def __init__(self, connection: _ConnectionLike | ConnectionFactory) -> None:
        self._connection_or_factory = connection

    def _connection(self) -> _ConnectionLike:
        connection = self._connection_or_factory
        return connection() if callable(connection) else connection

    def _validate_contract(self, connection: object) -> None:
        try:
            rows = _fetch_all(
                connection,
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = %s
                """.strip(),
                ("ingestion_checkpoints",),
            )
        except Exception as exc:
            raise RuntimeError("ingestion_checkpoints table is not available for manual checkpoint persistence.") from exc
        available = {str(row.get("column_name")) for row in rows if row.get("column_name")}
        required = {
            "checkpoint_id",
            "job_id",
            "last_successful_date",
            "attempt_count",
            "status",
            "metadata",
        }
        if not required.issubset(available):
            missing = sorted(required - available)
            raise RuntimeError(
                "ingestion_checkpoints schema contract is not available for manual checkpoint persistence. "
                f"Missing columns: {missing}"
            )

    def load(self, checkpoint_id: str) -> ManualFREDMacroCheckpoint | None:
        connection = self._connection()
        self._validate_contract(connection)
        try:
            rows = _fetch_all(
                connection,
                """
                SELECT checkpoint_id, job_id, last_successful_date, attempt_count, status, metadata
                FROM ingestion_checkpoints
                WHERE checkpoint_id = %s
                """.strip(),
                (checkpoint_id,),
            )
        except Exception as exc:
            raise RuntimeError("Failed to load manual FRED macro checkpoint state.") from exc
        if not rows:
            return None
        row = rows[0]
        metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
        return build_manual_fred_macro_checkpoint(
            checkpoint_key=str(row.get("checkpoint_id") or checkpoint_id),
            vendor=str(metadata.get("vendor") or "fred"),
            dataset=str(metadata.get("dataset") or "macro_observations"),
            series_id=str(metadata.get("series_id") or ""),
            timeframe=str(metadata.get("timeframe") or "1d"),
            planned_start_date=date.fromisoformat(str(metadata.get("planned_start_date") or date.today().isoformat())),
            planned_end_date=date.fromisoformat(str(metadata.get("planned_end_date") or date.today().isoformat())),
            status=ManualFREDMacroCheckpointStatus(str(row.get("status") or "planned")),
            last_successful_observation_date=(
                date.fromisoformat(str(row.get("last_successful_date"))) if row.get("last_successful_date") else None
            ),
            created_at=_utc_now(),
            updated_at=_utc_now(),
        )

    def save(self, checkpoint: ManualFREDMacroCheckpoint) -> None:
        connection = self._connection()
        self._validate_contract(connection)
        payload = asdict(checkpoint)
        metadata = {
            "vendor": checkpoint.vendor,
            "dataset": checkpoint.dataset,
            "series_id": checkpoint.series_id,
            "timeframe": checkpoint.timeframe,
            "planned_start_date": checkpoint.planned_start_date.isoformat(),
            "planned_end_date": checkpoint.planned_end_date.isoformat(),
        }
        try:
            _execute(
                connection,
                """
                INSERT INTO ingestion_checkpoints (
                    checkpoint_id,
                    job_id,
                    last_successful_date,
                    attempt_count,
                    status,
                    metadata
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (checkpoint_id) DO UPDATE SET
                    last_successful_date = excluded.last_successful_date,
                    attempt_count = excluded.attempt_count,
                    status = excluded.status,
                    metadata = excluded.metadata
                """.strip(),
                (
                    checkpoint.checkpoint_key,
                    checkpoint.checkpoint_key,
                    checkpoint.last_successful_observation_date,
                    0,
                    checkpoint.status.value,
                    metadata,
                ),
            )
            connection.commit()
        except Exception as exc:
            connection.rollback()
            raise RuntimeError("Failed to persist manual FRED macro checkpoint state.") from exc

    def update_successful_observation_date(self, checkpoint: ManualFREDMacroCheckpoint, observation_date: date) -> ManualFREDMacroCheckpoint:
        updated = build_manual_fred_macro_checkpoint(
            checkpoint_key=checkpoint.checkpoint_key,
            vendor=checkpoint.vendor,
            dataset=checkpoint.dataset,
            series_id=checkpoint.series_id,
            timeframe=checkpoint.timeframe,
            planned_start_date=checkpoint.planned_start_date,
            planned_end_date=checkpoint.planned_end_date,
            status=ManualFREDMacroCheckpointStatus.COMPLETED,
            last_successful_observation_date=observation_date,
            created_at=checkpoint.created_at,
            updated_at=_utc_now(),
        )
        self.save(updated)
        return updated

