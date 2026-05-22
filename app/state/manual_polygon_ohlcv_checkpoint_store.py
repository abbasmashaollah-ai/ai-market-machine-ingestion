from __future__ import annotations

from datetime import date, datetime, timezone
import json
from typing import Callable, Protocol

from app.state.manual_polygon_ohlcv import (
    ManualPolygonOHLCVCheckpoint,
    ManualPolygonOHLCVCheckpointStatus,
    build_manual_polygon_ohlcv_checkpoint,
)


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


def _parse_date_value(value: object) -> date:
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value:
        return date.fromisoformat(value)
    return date.today()


def _parse_datetime_value(value: object) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str) and value:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return _utc_now()


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


def _adapt_json_metadata(metadata: dict[str, object]) -> object:
    try:
        from psycopg2.extras import Json as PsycopgJson  # type: ignore
    except ImportError:
        try:
            from psycopg.types.json import Jsonb as PsycopgJson  # type: ignore
        except ImportError:
            return metadata
    try:
        return PsycopgJson(metadata)
    except Exception:
        return json.dumps(metadata)


class ManualPolygonOHLCVCheckpointStore:
    def __init__(self, connection: _ConnectionLike | ConnectionFactory) -> None:
        self._connection_or_factory = connection

    def _connection(self) -> _ConnectionLike:
        connection = self._connection_or_factory
        return connection() if callable(connection) else connection

    def load(self, checkpoint_key: str) -> ManualPolygonOHLCVCheckpoint | None:
        connection = self._connection()
        try:
            rows = _fetch_all(
                connection,
                """
                SELECT checkpoint_id, vendor, dataset, symbol, timeframe, start_date, end_date, last_successful_date, status, metadata, created_at, updated_at
                FROM ingestion_checkpoints
                WHERE checkpoint_id = %s
                """.strip(),
                (checkpoint_key,),
            )
        except Exception as exc:
            raise RuntimeError("Failed to load manual Polygon OHLCV checkpoint state safely.") from exc
        if not rows:
            return None
        row = rows[0]
        metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
        return build_manual_polygon_ohlcv_checkpoint(
            checkpoint_key=str(row.get("checkpoint_id") or checkpoint_key),
            vendor=str(row.get("vendor") or metadata.get("vendor") or "polygon"),
            dataset=str(row.get("dataset") or metadata.get("dataset") or "ohlcv"),
            symbol=str(row.get("symbol") or metadata.get("symbol") or ""),
            timeframe=str(row.get("timeframe") or metadata.get("timeframe") or "1d"),
            planned_start_date=_parse_date_value(row.get("start_date") or metadata.get("planned_start_date")),
            planned_end_date=_parse_date_value(row.get("end_date") or metadata.get("planned_end_date")),
            status=ManualPolygonOHLCVCheckpointStatus(str(row.get("status") or "planned")),
            last_successful_observation_date=(
                _parse_date_value(row.get("last_successful_date")) if row.get("last_successful_date") else None
            ),
            created_at=_parse_datetime_value(row.get("created_at")),
            updated_at=_parse_datetime_value(row.get("updated_at")),
        )

    def save(self, checkpoint: ManualPolygonOHLCVCheckpoint) -> None:
        connection = self._connection()
        metadata = {
            "vendor": checkpoint.vendor,
            "dataset": checkpoint.dataset,
            "symbol": checkpoint.symbol,
            "timeframe": checkpoint.timeframe,
            "planned_start_date": checkpoint.planned_start_date.isoformat(),
            "planned_end_date": checkpoint.planned_end_date.isoformat(),
        }
        try:
            _execute(
                connection,
                """
                INSERT INTO ingestion_checkpoints (
                    checkpoint_id, vendor, dataset, symbol, timeframe, start_date, end_date, last_successful_date, status, attempt_count, created_at, updated_at, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (checkpoint_id) DO UPDATE SET
                    vendor = excluded.vendor,
                    dataset = excluded.dataset,
                    symbol = excluded.symbol,
                    timeframe = excluded.timeframe,
                    start_date = excluded.start_date,
                    end_date = excluded.end_date,
                    last_successful_date = excluded.last_successful_date,
                    status = excluded.status,
                    updated_at = excluded.updated_at,
                    metadata = excluded.metadata
                """.strip(),
                (
                    checkpoint.checkpoint_key,
                    checkpoint.vendor,
                    checkpoint.dataset,
                    checkpoint.symbol,
                    checkpoint.timeframe,
                    checkpoint.planned_start_date,
                    checkpoint.planned_end_date,
                    checkpoint.last_successful_observation_date,
                    checkpoint.status.value,
                    0,
                    checkpoint.created_at,
                    checkpoint.updated_at,
                    _adapt_json_metadata(metadata),
                ),
            )
            connection.commit()
        except Exception as exc:
            connection.rollback()
            raise RuntimeError("Failed to persist manual Polygon OHLCV checkpoint state safely.") from exc

    def update_successful_observation_date(self, checkpoint: ManualPolygonOHLCVCheckpoint, observation_date: date) -> ManualPolygonOHLCVCheckpoint:
        updated = build_manual_polygon_ohlcv_checkpoint(
            checkpoint_key=checkpoint.checkpoint_key,
            vendor=checkpoint.vendor,
            dataset=checkpoint.dataset,
            symbol=checkpoint.symbol,
            timeframe=checkpoint.timeframe,
            planned_start_date=checkpoint.planned_start_date,
            planned_end_date=checkpoint.planned_end_date,
            status=ManualPolygonOHLCVCheckpointStatus.COMPLETED,
            last_successful_observation_date=observation_date,
            created_at=checkpoint.created_at,
            updated_at=_utc_now(),
        )
        self.save(updated)
        return updated
