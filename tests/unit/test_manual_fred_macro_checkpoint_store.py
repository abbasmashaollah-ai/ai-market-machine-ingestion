from __future__ import annotations

import unittest
from datetime import date

from app.state.manual_fred_macro import ManualFREDMacroCheckpointStatus, build_manual_fred_macro_checkpoint
from app.state.manual_fred_macro_checkpoint_store import ManualFREDMacroCheckpointStore


class _Result:
    def __init__(self, rows: list[dict[str, object]] | None = None, rowcount: int = 1) -> None:
        self._rows = rows or []
        self.rowcount = rowcount

    def fetchall(self) -> list[dict[str, object]]:
        return self._rows


class _Connection:
    def __init__(self, *, schema_rows: list[dict[str, object]], checkpoint_rows: list[dict[str, object]] | None = None) -> None:
        self.schema_rows = schema_rows
        self.checkpoint_rows = checkpoint_rows or []
        self.executed: list[tuple[str, tuple[object, ...]]] = []
        self.committed = False
        self.rolled_back = False

    def execute(self, sql: str, params: tuple[object, ...] = ()):
        self.executed.append((sql, params))
        if "information_schema.columns" in sql:
            return _Result(self.schema_rows)
        if "FROM ingestion_checkpoints" in sql:
            return _Result(self.checkpoint_rows)
        return _Result([])

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


class ManualFredMacroCheckpointStoreTests(unittest.TestCase):
    def _schema_rows(self) -> list[dict[str, object]]:
        return [
            {"column_name": "checkpoint_id"},
            {"column_name": "job_id"},
            {"column_name": "last_successful_date"},
            {"column_name": "attempt_count"},
            {"column_name": "status"},
            {"column_name": "metadata"},
        ]

    def test_checkpoint_read_by_key(self) -> None:
        connection = _Connection(
            schema_rows=self._schema_rows(),
            checkpoint_rows=[
                {
                    "checkpoint_id": "fred:macro_observations:GDP:1d:2025-01-01:2025-12-31",
                    "job_id": "fred:macro_observations:GDP:1d:2025-01-01:2025-12-31",
                    "last_successful_date": "2025-01-10",
                    "attempt_count": 1,
                    "status": "completed",
                    "metadata": {
                        "vendor": "fred",
                        "dataset": "macro_observations",
                        "series_id": "GDP",
                        "timeframe": "1d",
                        "planned_start_date": "2025-01-01",
                        "planned_end_date": "2025-12-31",
                    },
                }
            ],
        )
        store = ManualFREDMacroCheckpointStore(connection)

        checkpoint = store.load("fred:macro_observations:GDP:1d:2025-01-01:2025-12-31")

        self.assertIsNotNone(checkpoint)
        self.assertEqual(checkpoint.status, ManualFREDMacroCheckpointStatus.COMPLETED)
        self.assertEqual(checkpoint.last_successful_observation_date, date(2025, 1, 10))

    def test_checkpoint_update_after_successful_confirmed_write(self) -> None:
        connection = _Connection(schema_rows=self._schema_rows())
        store = ManualFREDMacroCheckpointStore(connection)
        checkpoint = build_manual_fred_macro_checkpoint(
            checkpoint_key="fred:macro_observations:GDP:1d:2025-01-01:2025-12-31",
            vendor="fred",
            dataset="macro_observations",
            series_id="GDP",
            timeframe="1d",
            planned_start_date=date(2025, 1, 1),
            planned_end_date=date(2025, 12, 31),
        )

        store.update_successful_observation_date(checkpoint, date(2025, 1, 10))

        self.assertTrue(connection.committed)
        self.assertFalse(connection.rolled_back)
        self.assertTrue(any("INSERT INTO ingestion_checkpoints" in sql for sql, _ in connection.executed))

    def test_missing_checkpoint_table_fails_safely(self) -> None:
        connection = _Connection(schema_rows=[])
        store = ManualFREDMacroCheckpointStore(connection)

        with self.assertRaises(RuntimeError):
            store.load("fred:macro_observations:GDP:1d:2025-01-01:2025-12-31")

    def test_no_schema_creation(self) -> None:
        connection = _Connection(schema_rows=self._schema_rows())
        store = ManualFREDMacroCheckpointStore(connection)
        checkpoint = build_manual_fred_macro_checkpoint(
            checkpoint_key="fred:macro_observations:GDP:1d:2025-01-01:2025-12-31",
            vendor="fred",
            dataset="macro_observations",
            series_id="GDP",
            timeframe="1d",
            planned_start_date=date(2025, 1, 1),
            planned_end_date=date(2025, 12, 31),
        )

        store.save(checkpoint)

        self.assertFalse(any("CREATE TABLE" in sql.upper() for sql, _ in connection.executed))

    def test_no_migrations(self) -> None:
        connection = _Connection(schema_rows=self._schema_rows())
        store = ManualFREDMacroCheckpointStore(connection)
        checkpoint = build_manual_fred_macro_checkpoint(
            checkpoint_key="fred:macro_observations:GDP:1d:2025-01-01:2025-12-31",
            vendor="fred",
            dataset="macro_observations",
            series_id="GDP",
            timeframe="1d",
            planned_start_date=date(2025, 1, 1),
            planned_end_date=date(2025, 12, 31),
        )

        store.save(checkpoint)

        self.assertFalse(connection.rolled_back)

