from __future__ import annotations

import unittest

from app.quality.validators import fail_result, pass_result
from app.state.data_quality_result_store import DataQualityResultStore


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
            return _Result(self.schema_rows)
        return _Result([])

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


class DataQualityResultStoreTests(unittest.TestCase):
    def _schema_rows(self) -> list[dict[str, object]]:
        return [
            {"column_name": "id"},
            {"column_name": "run_id"},
            {"column_name": "job_id"},
            {"column_name": "vendor"},
            {"column_name": "dataset"},
            {"column_name": "symbol"},
            {"column_name": "timeframe"},
            {"column_name": "check_name"},
            {"column_name": "status"},
            {"column_name": "severity"},
            {"column_name": "message"},
            {"column_name": "observed_value"},
            {"column_name": "expected_value"},
            {"column_name": "created_at"},
        ]

    def test_contract_writes_compact_result(self) -> None:
        connection = _Connection(schema_rows=self._schema_rows())
        store = DataQualityResultStore(connection)

        store.save_results(
            vendor="polygon",
            dataset="ohlcv",
            symbol="SPY",
            timeframe="1d",
            check_name="chunk_validation_summary",
            status="pass",
            severity="info",
            message="chunk completed",
            observed_value=6,
            expected_value=6,
            run_id="run-1",
            job_id=1,
        )

        self.assertTrue(connection.committed)
        sql, params = connection.executed[-1]
        self.assertIn("INSERT INTO data_quality_results", sql)
        self.assertEqual(params[0], "polygon")
        self.assertEqual(params[2], "chunk_validation_summary")

    def test_missing_contract_fails_safely(self) -> None:
        store = DataQualityResultStore(_Connection(schema_rows=[]))

        with self.assertRaises(RuntimeError):
            store.save_results(
                vendor="polygon",
                dataset="ohlcv",
                symbol="SPY",
                timeframe="1d",
                check_name="chunk_validation_summary",
                status="pass",
            )

    def test_validation_results_use_details(self) -> None:
        connection = _Connection(schema_rows=self._schema_rows())
        store = DataQualityResultStore(connection)

        store.save_validation_results(
            vendor="polygon",
            dataset="ohlcv",
            symbol="SPY",
            timeframe="1d",
            results=[pass_result("chunk_validation_summary", observed_value=6, expected_value=6), fail_result("chunk_invalid_rows", "invalid rows", observed_value=1, expected_value=0)],
        )

        self.assertTrue(connection.committed)
        self.assertEqual(len([sql for sql, _ in connection.executed if "INSERT INTO data_quality_results" in sql]), 2)
