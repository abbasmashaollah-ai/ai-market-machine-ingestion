from __future__ import annotations

import unittest

from app.state.data_lineage_store import DataLineageStore


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


class DataLineageStoreTests(unittest.TestCase):
    def _schema_rows(self) -> list[dict[str, object]]:
        return [
            {"column_name": "id"},
            {"column_name": "vendor"},
            {"column_name": "dataset"},
            {"column_name": "symbol"},
            {"column_name": "timeframe"},
            {"column_name": "source_endpoint"},
            {"column_name": "request_params"},
            {"column_name": "response_status"},
            {"column_name": "row_count"},
            {"column_name": "normalization_version"},
            {"column_name": "quality_status"},
            {"column_name": "run_id"},
            {"column_name": "job_id"},
            {"column_name": "created_at"},
        ]

    def test_contract_writes_compact_row(self) -> None:
        connection = _Connection(schema_rows=self._schema_rows())
        store = DataLineageStore(connection)

        store.save_chunk_lineage(
            vendor="polygon",
            dataset="ohlcv",
            symbol="SPY",
            timeframe="1d",
            source_endpoint="v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}",
            request_params='{"symbol":"SPY"}',
            response_status=200,
            row_count=5,
            normalization_version="polygon_ohlcv_normalization_v1",
            quality_status="pass",
            run_id="run-1",
            job_id="polygon_ohlcv_chunked_backfill",
        )

        self.assertTrue(connection.committed)
        self.assertFalse(connection.rolled_back)
        sql, params = connection.executed[-1]
        self.assertIn("INSERT INTO data_lineage", sql)
        self.assertEqual(params[0], "polygon")
        self.assertEqual(params[3], "SPY")
        self.assertEqual(params[9], "polygon_ohlcv_normalization_v1")

    def test_missing_contract_fails_safely(self) -> None:
        store = DataLineageStore(_Connection(schema_rows=[]))

        with self.assertRaises(RuntimeError):
            store.save_chunk_lineage(vendor="polygon", dataset="ohlcv", symbol="SPY", timeframe="1d")

    def test_no_schema_creation_or_migration_sql(self) -> None:
        connection = _Connection(schema_rows=self._schema_rows())
        store = DataLineageStore(connection)

        store.save_chunk_lineage(vendor="polygon", dataset="ohlcv", symbol="SPY", timeframe="1d")

        self.assertFalse(any("CREATE TABLE" in sql.upper() for sql, _ in connection.executed))
        self.assertFalse(any("ALTER TABLE" in sql.upper() for sql, _ in connection.executed))
