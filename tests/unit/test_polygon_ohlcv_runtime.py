from __future__ import annotations

import os
import unittest
from datetime import date, datetime, timezone
from unittest.mock import Mock, patch

from app.models.normalized import NormalizedOHLCVRecord
from app.writers.canonical_writer import WriteStatus
from app.writers.ohlcv_writer import OhlcvWriter


class PolygonOhlcvRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def test_dry_run_success_with_mocked_payload(self) -> None:
        from app.ingestion.manual.polygon_ohlcv_incremental import build_manual_polygon_ohlcv_incremental

        fake_client = Mock()
        fake_client.fetch_aggregates_raw.return_value = [
            {"ticker": "SPY", "t": 1735776000000, "o": 100, "h": 101, "l": 99, "c": 100.5, "v": 1234, "adjusted": True}
        ]
        with patch("app.ingestion.manual.polygon_ohlcv_incremental._build_polygon_client", return_value=fake_client):
            summary = build_manual_polygon_ohlcv_incremental(
                symbols=("SPY",),
                start_date=date(2025, 1, 2),
                end_date=date(2025, 1, 10),
                timeframe="1d",
                api_key="polygon-secret",
            )

        self.assertEqual(summary.series_total, 1)
        self.assertEqual(summary.total_rows_fetched, 1)
        self.assertEqual(summary.total_rows_valid, 1)

    def test_dry_run_uses_live_transport_factory_when_key_present(self) -> None:
        from app.ingestion.manual.polygon_ohlcv_incremental import build_manual_polygon_ohlcv_incremental

        fake_client = Mock()
        fake_client.fetch_aggregates_raw.return_value = []
        with patch("app.ingestion.manual.polygon_ohlcv_incremental._build_polygon_client", return_value=fake_client) as client_mock:
            summary = build_manual_polygon_ohlcv_incremental(
                symbols=("SPY",),
                start_date=date(2025, 1, 2),
                end_date=date(2025, 1, 10),
                timeframe="1d",
                api_key="polygon-secret",
            )

        client_mock.assert_called_once()
        self.assertEqual(summary.total_rows_fetched, 0)

    def test_validation_failure_reporting(self) -> None:
        from app.ingestion.manual.polygon_ohlcv_incremental import build_manual_polygon_ohlcv_incremental

        fake_client = Mock()
        fake_client.fetch_aggregates_raw.return_value = [
            {"ticker": "SPY", "t": 1735776000000, "o": 100, "h": 99, "l": 101, "c": 100.5, "v": -1, "adjusted": True}
        ]
        with patch("app.ingestion.manual.polygon_ohlcv_incremental._build_polygon_client", return_value=fake_client):
            summary = build_manual_polygon_ohlcv_incremental(
                symbols=("SPY",),
                start_date=date(2025, 1, 2),
                end_date=date(2025, 1, 10),
                timeframe="1d",
                api_key="polygon-secret",
            )

        self.assertEqual(summary.total_rows_invalid, 1)
        self.assertGreaterEqual(summary.total_validation_failures, 1)

    def test_missing_polygon_key_fails_for_dry_run_cli(self) -> None:
        import scripts.dry_run_polygon_ohlcv_incremental as mod

        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "sys.argv",
            [
                "dry_run_polygon_ohlcv_incremental.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
            ],
            ):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_persist_requires_database_only_when_confirmed(self) -> None:
        import scripts.persist_polygon_ohlcv_incremental as mod

        with patch.dict(os.environ, {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch(
            "sys.argv",
            [
                "persist_polygon_ohlcv_incremental.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
            ],
        ), patch.object(mod, "build_manual_polygon_ohlcv_incremental") as build_mock:
            build_mock.return_value.symbol_summaries = ()
            build_mock.return_value.series_total = 0
            build_mock.return_value.series_completed = 0
            build_mock.return_value.series_failed = 0
            build_mock.return_value.series_skipped = 0
            build_mock.return_value.total_rows_fetched = 0
            build_mock.return_value.total_rows_valid = 0
            build_mock.return_value.total_rows_invalid = 0
            build_mock.return_value.total_rows_written = 0
            build_mock.return_value.total_validation_failures = 0
            exit_code = mod.main()

        self.assertEqual(exit_code, 0)
        build_mock.assert_called_once()

    def test_inspect_cli_prints_safe_output(self) -> None:
        import scripts.inspect_polygon_ohlcv_checkpoint as mod

        checkpoint = type(
            "Checkpoint",
            (),
            {
                "checkpoint_key": "polygon:ohlcv:SPY:1d:2025-01-02:2025-01-10",
                "symbol": "SPY",
                "status": type("Status", (), {"value": "completed"})(),
                "planned_start_date": date(2025, 1, 2),
                "planned_end_date": date(2025, 1, 10),
                "last_successful_observation_date": date(2025, 1, 9),
                "updated_at": datetime(2025, 1, 10, 12, 0, tzinfo=timezone.utc),
            },
        )()
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection") as open_connection, patch.object(mod, "ManualPolygonOHLCVCheckpointStore") as store_cls, patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            [
                "inspect_polygon_ohlcv_checkpoint.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
            ],
        ):
            store = Mock()
            store.load.return_value = checkpoint
            store_cls.return_value = store
            open_connection.return_value = Mock()
            exit_code = mod.main()

        self.assertEqual(exit_code, 0)
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("checkpoint_found=true", printed)
        self.assertNotIn("DATABASE_URL", printed)

    def test_persist_routes_through_writer_and_checkpoint(self) -> None:
        from app.ingestion.manual.polygon_ohlcv_incremental import build_manual_polygon_ohlcv_incremental

        fake_client = Mock()
        fake_client.fetch_aggregates_raw.return_value = [
            {"ticker": "SPY", "t": 1735776000000, "o": 100, "h": 101, "l": 99, "c": 100.5, "v": 1234, "adjusted": True}
        ]
        writer = Mock()
        writer.write.return_value = type("Result", (), {"written_count": 1, "status": WriteStatus.SUCCESS})()
        checkpoint_store = Mock()
        with patch("app.ingestion.manual.polygon_ohlcv_incremental._build_polygon_client", return_value=fake_client):
            summary = build_manual_polygon_ohlcv_incremental(
                symbols=("SPY",),
                start_date=date(2025, 1, 2),
                end_date=date(2025, 1, 10),
                timeframe="1d",
                api_key="polygon-secret",
                writer=writer,
                confirmed_write=True,
                checkpoint_store=checkpoint_store,
                use_checkpoint=True,
                update_checkpoint=True,
            )

        writer.write.assert_called_once()
        checkpoint_store.update_successful_observation_date.assert_called_once()
        self.assertEqual(summary.total_rows_written, 1)

    def test_already_current_skip_behavior(self) -> None:
        from app.ingestion.manual.polygon_ohlcv_incremental import build_manual_polygon_ohlcv_incremental

        fake_client = Mock()
        fake_client.fetch_aggregates_raw.return_value = [
            {"ticker": "SPY", "t": 1735776000000, "o": 100, "h": 101, "l": 99, "c": 100.5, "v": 1234, "adjusted": True}
        ]
        checkpoint_store = Mock()
        checkpoint_store.load.return_value = type(
            "Checkpoint",
            (),
            {"last_successful_observation_date": date(2025, 1, 10), "checkpoint_key": "polygon:ohlcv:SPY:1d:2025-01-02:2025-01-10"},
        )()
        with patch("app.ingestion.manual.polygon_ohlcv_incremental._build_polygon_client", return_value=fake_client):
            summary = build_manual_polygon_ohlcv_incremental(
                symbols=("SPY",),
                start_date=date(2025, 1, 2),
                end_date=date(2025, 1, 10),
                timeframe="1d",
                api_key="polygon-secret",
                writer=None,
                confirmed_write=False,
                checkpoint_store=checkpoint_store,
                use_checkpoint=True,
                update_checkpoint=True,
            )

        self.assertEqual(summary.series_skipped, 1)
        self.assertEqual(summary.total_rows_written, 0)
        checkpoint_store.update_successful_observation_date.assert_not_called()

    def test_ohlcv_writer_writes_and_upserts(self) -> None:
        class Result:
            rowcount = 1

            def fetchall(self):
                return []

        class Connection:
            def __init__(self) -> None:
                self.executed = []
                self.committed = False
                self.rolled_back = False

            def execute(self, sql: str, params: tuple[object, ...] = ()):
                self.executed.append((sql, params))
                if "information_schema.columns" in sql:
                    return type("Rows", (), {"fetchall": lambda self: [
                        {"column_name": "id"},
                        {"column_name": "symbol"},
                        {"column_name": "timestamp"},
                        {"column_name": "open"},
                        {"column_name": "high"},
                        {"column_name": "low"},
                        {"column_name": "close"},
                        {"column_name": "volume"},
                        {"column_name": "source"},
                        {"column_name": "timeframe"},
                        {"column_name": "adjusted"},
                        {"column_name": "adjustment_status"},
                        {"column_name": "data_quality_status"},
                        {"column_name": "created_at"},
                        {"column_name": "updated_at"},
                    ]})()
                if "FROM pg_indexes" in sql:
                    return type("Rows", (), {"fetchall": lambda self: [
                        {"indexdef": "CREATE UNIQUE INDEX canonical_ohlcv_symbol_timestamp_timeframe_adjusted_idx ON public.canonical_ohlcv USING btree (symbol, timestamp, timeframe, adjusted)"},
                    ]})()
                return Result()

            def commit(self):
                self.committed = True

            def rollback(self):
                self.rolled_back = True

        writer = OhlcvWriter(Connection())
        record = NormalizedOHLCVRecord(
            symbol="SPY",
            symbol_id=None,
            timestamp=datetime(2025, 1, 2, tzinfo=timezone.utc),
            open=100,
            high=101,
            low=99,
            close=100.5,
            volume=1234,
            vendor="polygon",
            source="polygon_aggregates",
        )
        result = writer.write([record])
        self.assertEqual(result.status, WriteStatus.SUCCESS)
        sql, params = writer._connection_or_factory.executed[-1]
        self.assertIn(
            "INSERT INTO canonical_ohlcv (symbol, timestamp, open, high, low, close, volume, source, adjustment_status, data_quality_status, timeframe, adjusted",
            sql,
        )
        self.assertIn("ON CONFLICT (symbol, timestamp, timeframe, adjusted)", sql)
        self.assertEqual(params[0], "SPY")
        self.assertNotIn("symbol_id", sql)

    def test_writer_rejects_missing_approved_columns_safely(self) -> None:
        class Connection:
            def execute(self, sql: str, params: tuple[object, ...] = ()):
                if "information_schema.columns" in sql:
                    return type("Rows", (), {"fetchall": lambda self: [
                        {"column_name": "symbol"},
                        {"column_name": "timestamp"},
                    ]})()
                if "FROM pg_indexes" in sql:
                    return type("Rows", (), {"fetchall": lambda self: []})()
                return type("Result", (), {"fetchall": lambda self: []})()

            def commit(self):
                return None

            def rollback(self):
                return None

        writer = OhlcvWriter(Connection())
        record = NormalizedOHLCVRecord(
            symbol="SPY",
            symbol_id=None,
            timestamp=datetime(2025, 1, 2, tzinfo=timezone.utc),
            open=100,
            high=101,
            low=99,
            close=100.5,
            volume=1234,
            source="polygon_aggregates",
        )
        result = writer.write([record])
        self.assertEqual(result.status, WriteStatus.FAILURE)
        self.assertIn("Missing columns", result.message or "")
        self.assertNotIn("DATABASE_URL", result.message or "")

    def test_no_symbol_id_required(self) -> None:
        class Connection:
            def __init__(self) -> None:
                self.executed = []

            def execute(self, sql: str, params: tuple[object, ...] = ()):
                self.executed.append((sql, params))
                if "information_schema.columns" in sql:
                    return type("Rows", (), {"fetchall": lambda self: [
                        {"column_name": "id"},
                        {"column_name": "symbol"},
                        {"column_name": "timestamp"},
                        {"column_name": "open"},
                        {"column_name": "high"},
                        {"column_name": "low"},
                        {"column_name": "close"},
                        {"column_name": "volume"},
                        {"column_name": "source"},
                        {"column_name": "adjustment_status"},
                        {"column_name": "data_quality_status"},
                        {"column_name": "timeframe"},
                        {"column_name": "adjusted"},
                    ]})()
                if "FROM pg_indexes" in sql:
                    return type("Rows", (), {"fetchall": lambda self: [
                        {"indexdef": "CREATE UNIQUE INDEX canonical_ohlcv_symbol_timestamp_timeframe_adjusted_idx ON public.canonical_ohlcv USING btree (symbol, timestamp, timeframe, adjusted)"},
                    ]})()
                return type("Result", (), {"fetchall": lambda self: []})()

            def commit(self):
                return None

            def rollback(self):
                return None

        connection = Connection()
        writer = OhlcvWriter(connection)
        record = NormalizedOHLCVRecord(
            symbol="SPY",
            symbol_id=None,
            timestamp=datetime(2025, 1, 2, tzinfo=timezone.utc),
            open=100,
            high=101,
            low=99,
            close=100.5,
            volume=1234,
            source="polygon_aggregates",
        )
        result = writer.write([record])
        self.assertEqual(result.status, WriteStatus.SUCCESS)
        self.assertEqual(connection.executed[-1][1][0], "SPY")

    def test_conflict_constraint_absent_is_sanitized(self) -> None:
        class Connection:
            def execute(self, sql: str, params: tuple[object, ...] = ()):
                if "information_schema.columns" in sql:
                    return type("Rows", (), {"fetchall": lambda self: [
                        {"column_name": "id"},
                        {"column_name": "symbol"},
                        {"column_name": "timestamp"},
                        {"column_name": "open"},
                        {"column_name": "high"},
                        {"column_name": "low"},
                        {"column_name": "close"},
                        {"column_name": "volume"},
                        {"column_name": "source"},
                        {"column_name": "adjustment_status"},
                        {"column_name": "data_quality_status"},
                        {"column_name": "timeframe"},
                        {"column_name": "adjusted"},
                    ]})()
                if "FROM pg_indexes" in sql:
                    return type("Rows", (), {"fetchall": lambda self: []})()
                return type("Result", (), {"fetchall": lambda self: []})()

            def commit(self):
                return None

            def rollback(self):
                return None

        writer = OhlcvWriter(Connection())
        record = NormalizedOHLCVRecord(
            symbol="SPY",
            symbol_id=None,
            timestamp=datetime(2025, 1, 2, tzinfo=timezone.utc),
            open=100,
            high=101,
            low=99,
            close=100.5,
            volume=1234,
            source="polygon_aggregates",
        )
        result = writer.write([record])
        self.assertEqual(result.status, WriteStatus.FAILURE)
        self.assertIn("uniqueness contract", result.message or "")
        self.assertNotIn("DATABASE_URL", result.message or "")
