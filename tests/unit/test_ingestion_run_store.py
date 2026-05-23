from __future__ import annotations

import unittest
from datetime import datetime, timezone

from app.state.errors import IngestionErrorRecord
from app.state.ingestion_run_store import IngestionRunStore
from app.state.runs import IngestionRun, RunStatus


class _Result:
    def __init__(self, rows: list[dict[str, object]] | None = None, rowcount: int = 1) -> None:
        self._rows = rows or []
        self.rowcount = rowcount

    def fetchall(self) -> list[dict[str, object]]:
        return self._rows


class _Connection:
    def __init__(self, *, schema_rows: list[dict[str, object]]) -> None:
        self.schema_rows = schema_rows
        self.executed: list[tuple[str, tuple[object, ...]]] = []
        self.committed = False
        self.rolled_back = False

    def execute(self, sql: str, params: tuple[object, ...] = ()):
        self.executed.append((sql, params))
        if "information_schema.columns" in sql:
            table_name = params[0]
            rows = [row for row in self.schema_rows if row["table_name"] == table_name]
            return _Result(rows)
        return _Result([])

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


class IngestionRunStoreTests(unittest.TestCase):
    def _schema_rows(self) -> list[dict[str, object]]:
        return [
            {"table_name": "ingestion_runs", "column_name": "id"},
            {"table_name": "ingestion_runs", "column_name": "run_id"},
            {"table_name": "ingestion_runs", "column_name": "job_id"},
            {"table_name": "ingestion_runs", "column_name": "vendor"},
            {"table_name": "ingestion_runs", "column_name": "dataset"},
            {"table_name": "ingestion_runs", "column_name": "status"},
            {"table_name": "ingestion_runs", "column_name": "started_at"},
            {"table_name": "ingestion_runs", "column_name": "finished_at"},
            {"table_name": "ingestion_runs", "column_name": "rows_fetched"},
            {"table_name": "ingestion_runs", "column_name": "rows_written"},
            {"table_name": "ingestion_runs", "column_name": "rows_rejected"},
            {"table_name": "ingestion_runs", "column_name": "error_count"},
            {"table_name": "ingestion_runs", "column_name": "created_at"},
            {"table_name": "ingestion_runs", "column_name": "updated_at"},
            {"table_name": "ingestion_errors", "column_name": "id"},
            {"table_name": "ingestion_errors", "column_name": "run_id"},
            {"table_name": "ingestion_errors", "column_name": "job_id"},
            {"table_name": "ingestion_errors", "column_name": "vendor"},
            {"table_name": "ingestion_errors", "column_name": "dataset"},
            {"table_name": "ingestion_errors", "column_name": "symbol"},
            {"table_name": "ingestion_errors", "column_name": "timeframe"},
            {"table_name": "ingestion_errors", "column_name": "error_type"},
            {"table_name": "ingestion_errors", "column_name": "error_message"},
            {"table_name": "ingestion_errors", "column_name": "retryable"},
            {"table_name": "ingestion_errors", "column_name": "created_at"},
        ]

    def test_run_contract_writes_summary(self) -> None:
        connection = _Connection(schema_rows=self._schema_rows())
        store = IngestionRunStore(connection)
        run = IngestionRun(
            run_id="run-1",
            job_id="job-1",
            status=RunStatus.SUCCESS,
            rows_fetched=5,
            rows_written=4,
            rows_rejected=1,
            error_count=0,
            metadata={"vendor": "polygon", "dataset": "ohlcv", "started_at": datetime(2025, 1, 2, tzinfo=timezone.utc), "finished_at": datetime(2025, 1, 3, tzinfo=timezone.utc)},
        )

        store.save_run(run)

        self.assertTrue(connection.committed)
        self.assertFalse(connection.rolled_back)
        sql, params = connection.executed[-1]
        self.assertIn("INSERT INTO ingestion_runs", sql)
        self.assertEqual(params[0], "run-1")
        self.assertEqual(params[3], "success")

    def test_error_contract_writes_sanitized_errors(self) -> None:
        connection = _Connection(schema_rows=self._schema_rows())
        store = IngestionRunStore(connection)
        error = IngestionErrorRecord(
            error_id="err-1",
            run_id="run-1",
            error_type="rate_limit",
            message="VendorHttpStatusError: unexpected http status: 429",
            retryable=True,
            metadata={"symbol": "SPY"},
        )

        store.save_errors("run-1", [error])

        self.assertTrue(connection.committed)
        self.assertFalse(connection.rolled_back)
        sql, params = connection.executed[-1]
        self.assertIn("INSERT INTO ingestion_errors", sql)
        self.assertEqual(params[5], "rate_limit")
        self.assertNotIn("DATABASE_URL", str(params))

    def test_empty_error_list_is_noop(self) -> None:
        connection = _Connection(schema_rows=self._schema_rows())
        store = IngestionRunStore(connection)

        store.save_errors("run-1", [])

        self.assertFalse(connection.executed)
        self.assertFalse(connection.committed)

    def test_missing_contract_fails_safely(self) -> None:
        connection = _Connection(schema_rows=[])
        store = IngestionRunStore(connection)
        run = IngestionRun(run_id="run-1", job_id="job-1")

        with self.assertRaises(RuntimeError):
            store.save_run(run)

    def test_no_schema_creation_or_migration_sql(self) -> None:
        connection = _Connection(schema_rows=self._schema_rows())
        store = IngestionRunStore(connection)
        run = IngestionRun(run_id="run-1", job_id="job-1", metadata={"vendor": "polygon", "dataset": "ohlcv"})

        store.save_run(run)

        self.assertFalse(any("CREATE TABLE" in sql.upper() for sql, _ in connection.executed))
        self.assertFalse(any("ALTER TABLE" in sql.upper() for sql, _ in connection.executed))
