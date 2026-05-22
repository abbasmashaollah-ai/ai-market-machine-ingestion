from __future__ import annotations

from datetime import date, datetime, timezone
import json
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


def _is_text_column(data_type: object) -> bool:
    if not isinstance(data_type, str):
        return False
    normalized = data_type.lower()
    return normalized in {"text", "character varying", "character", "varchar", "json", "jsonb", "uuid"}


class _CheckpointContract:
    def __init__(
        self,
        *,
        key_column: str,
        vendor_column: str,
        dataset_column: str,
        symbol_column: str | None,
        timeframe_column: str | None,
        start_date_column: str | None,
        end_date_column: str | None,
        last_successful_column: str,
        status_column: str,
        attempt_count_column: str,
        created_at_column: str,
        updated_at_column: str,
        last_error_column: str | None,
        metadata_column: str | None,
    ) -> None:
        self.key_column = key_column
        self.vendor_column = vendor_column
        self.dataset_column = dataset_column
        self.symbol_column = symbol_column
        self.timeframe_column = timeframe_column
        self.start_date_column = start_date_column
        self.end_date_column = end_date_column
        self.last_successful_column = last_successful_column
        self.status_column = status_column
        self.attempt_count_column = attempt_count_column
        self.created_at_column = created_at_column
        self.updated_at_column = updated_at_column
        self.last_error_column = last_error_column
        self.metadata_column = metadata_column


class ManualFREDMacroCheckpointStore:
    def __init__(self, connection: _ConnectionLike | ConnectionFactory) -> None:
        self._connection_or_factory = connection

    def _connection(self) -> _ConnectionLike:
        connection = self._connection_or_factory
        return connection() if callable(connection) else connection

    def _contract(self, connection: object) -> _CheckpointContract:
        try:
            rows = _fetch_all(
                connection,
                """
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
                """.strip(),
                ("ingestion_checkpoints",),
            )
        except Exception as exc:
            raise RuntimeError("ingestion_checkpoints table is not available for manual checkpoint persistence.") from exc

        columns = {str(row.get("column_name")): row.get("data_type") for row in rows if row.get("column_name")}
        if "checkpoint_id" not in columns or not _is_text_column(columns["checkpoint_id"]):
            raise RuntimeError(
                "ingestion_checkpoints schema contract is not available for manual checkpoint persistence. "
                "Expected text-compatible checkpoint_id column."
            )
        if "vendor" not in columns or "dataset" not in columns or "status" not in columns:
            raise RuntimeError(
                "ingestion_checkpoints schema contract is not available for manual checkpoint persistence. "
                "Missing required vendor/dataset/status columns."
            )
        return _CheckpointContract(
            key_column="checkpoint_id",
            vendor_column="vendor",
            dataset_column="dataset",
            symbol_column="symbol" if "symbol" in columns else None,
            timeframe_column="timeframe" if "timeframe" in columns else None,
            start_date_column="start_date" if "start_date" in columns else None,
            end_date_column="end_date" if "end_date" in columns else None,
            last_successful_column="last_successful_date",
            status_column="status",
            attempt_count_column="attempt_count",
            created_at_column="created_at",
            updated_at_column="updated_at",
            last_error_column="last_error" if "last_error" in columns else None,
            metadata_column="metadata" if "metadata" in columns else None,
        )

    def _serialize_metadata(self, metadata: dict[str, object]) -> object:
        return _adapt_json_metadata(metadata)

    def load(self, checkpoint_key: str) -> ManualFREDMacroCheckpoint | None:
        connection = self._connection()
        contract = self._contract(connection)
        try:
            rows = _fetch_all(
                connection,
                f"""
                SELECT checkpoint_id, vendor, dataset, symbol, timeframe, start_date, end_date, last_successful_date, status, metadata, created_at, updated_at
                FROM ingestion_checkpoints
                WHERE {contract.key_column} = %s
                """.strip(),
                (checkpoint_key,),
            )
        except Exception as exc:
            raise RuntimeError("Failed to load manual FRED macro checkpoint state safely.") from exc
        if not rows:
            return None
        row = rows[0]
        metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
        return build_manual_fred_macro_checkpoint(
            checkpoint_key=str(row.get("checkpoint_id") or checkpoint_key),
            vendor=str(row.get("vendor") or metadata.get("vendor") or "fred"),
            dataset=str(row.get("dataset") or metadata.get("dataset") or "macro_observations"),
            series_id=str(row.get("symbol") or metadata.get("series_id") or ""),
            timeframe=str(row.get("timeframe") or metadata.get("timeframe") or "1d"),
            planned_start_date=date.fromisoformat(
                str(row.get("start_date") or metadata.get("planned_start_date") or date.today().isoformat())
            ),
            planned_end_date=date.fromisoformat(
                str(row.get("end_date") or metadata.get("planned_end_date") or date.today().isoformat())
            ),
            status=ManualFREDMacroCheckpointStatus(str(row.get("status") or "planned")),
            last_successful_observation_date=(
                date.fromisoformat(str(row.get("last_successful_date"))) if row.get("last_successful_date") else None
            ),
            created_at=_utc_now(),
            updated_at=_utc_now(),
        )

    def save(self, checkpoint: ManualFREDMacroCheckpoint) -> None:
        connection = self._connection()
        contract = self._contract(connection)
        metadata = {
            "vendor": checkpoint.vendor,
            "dataset": checkpoint.dataset,
            "series_id": checkpoint.series_id,
            "timeframe": checkpoint.timeframe,
            "planned_start_date": checkpoint.planned_start_date.isoformat(),
            "planned_end_date": checkpoint.planned_end_date.isoformat(),
        }
        columns = [
            contract.key_column,
            contract.vendor_column,
            contract.dataset_column,
        ]
        values: list[object] = [
            checkpoint.checkpoint_key,
            checkpoint.vendor,
            checkpoint.dataset,
        ]
        if contract.symbol_column:
            columns.append(contract.symbol_column)
            values.append(checkpoint.series_id)
        if contract.timeframe_column:
            columns.append(contract.timeframe_column)
            values.append(checkpoint.timeframe)
        if contract.start_date_column:
            columns.append(contract.start_date_column)
            values.append(checkpoint.planned_start_date)
        if contract.end_date_column:
            columns.append(contract.end_date_column)
            values.append(checkpoint.planned_end_date)
        columns.extend([contract.last_successful_column, contract.status_column, contract.attempt_count_column, contract.created_at_column, contract.updated_at_column])
        values.extend(
            [
                checkpoint.last_successful_observation_date,
                checkpoint.status.value,
                0,
                checkpoint.created_at,
                checkpoint.updated_at,
            ]
        )
        if contract.last_error_column:
            columns.append(contract.last_error_column)
            values.append(None)
        if contract.metadata_column:
            columns.append(contract.metadata_column)
            values.append(self._serialize_metadata(metadata))
        update_clauses = [
            "vendor = excluded.vendor",
            "dataset = excluded.dataset",
        ]
        if contract.symbol_column:
            update_clauses.append(f"{contract.symbol_column} = excluded.{contract.symbol_column}")
        if contract.timeframe_column:
            update_clauses.append(f"{contract.timeframe_column} = excluded.{contract.timeframe_column}")
        if contract.start_date_column:
            update_clauses.append(f"{contract.start_date_column} = excluded.{contract.start_date_column}")
        if contract.end_date_column:
            update_clauses.append(f"{contract.end_date_column} = excluded.{contract.end_date_column}")
        update_clauses.extend(
            [
                "last_successful_date = excluded.last_successful_date",
                "status = excluded.status",
                "attempt_count = excluded.attempt_count",
                "updated_at = excluded.updated_at",
            ]
        )
        if contract.metadata_column:
            update_clauses.append("metadata = excluded.metadata")
        try:
            _execute(
                connection,
                f"""
                INSERT INTO ingestion_checkpoints ({", ".join(columns)})
                VALUES ({", ".join(["%s"] * len(columns))})
                ON CONFLICT ({contract.key_column}) DO UPDATE SET
                    {", ".join(update_clauses)}
                """.strip(),
                tuple(values),
            )
            connection.commit()
        except Exception as exc:
            connection.rollback()
            raise RuntimeError("Failed to persist manual FRED macro checkpoint state safely.") from exc

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
