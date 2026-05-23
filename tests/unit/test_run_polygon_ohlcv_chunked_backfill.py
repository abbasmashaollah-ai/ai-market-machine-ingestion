from __future__ import annotations

import os
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch


class RunPolygonOhlcvChunkedBackfillTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.run_polygon_ohlcv_chunked_backfill as mod

        return mod

    def _summary(self, *, rows_fetched: int = 2, rows_written: int = 0, status: str = "completed"):
        row = SimpleNamespace(
            symbol="SPY",
            requested_start_date=date(2025, 1, 2),
            effective_start_date=date(2025, 1, 2),
            rows_fetched=rows_fetched,
            rows_valid=rows_fetched,
            rows_invalid=0,
            rows_written=rows_written,
            validation_failures=0,
            planned_start_date=date(2025, 1, 2),
            planned_end_date=date(2025, 1, 10),
            write_confirmed=False,
            checkpoint_loaded=False,
            status=status,
            error_message=None,
        )
        return SimpleNamespace(
            symbol_summaries=(row,),
            series_total=1,
            series_completed=1,
            series_failed=0,
            series_skipped=0,
            total_rows_fetched=rows_fetched,
            total_rows_written=rows_written,
        )

    def test_chunk_planning_exclusive_end_date_behavior(self) -> None:
        mod = self._module()
        chunks = mod.split_date_range_into_chunks(date(2025, 1, 2), date(2025, 1, 10), max_days_per_chunk=3)
        self.assertEqual([(chunk.start_date.isoformat(), chunk.end_date.isoformat()) for chunk in chunks], [
            ("2025-01-02", "2025-01-04"),
            ("2025-01-05", "2025-01-07"),
            ("2025-01-08", "2025-01-10"),
        ])

    def test_defaults_to_tiny_universe(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "build_manual_polygon_ohlcv_incremental", return_value=self._summary()) as build_mock, patch(
            "builtins.print"
        ), patch(
            "sys.argv",
            [
                "run_polygon_ohlcv_chunked_backfill.py",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
                "--chunk-days",
                "3",
            ],
        ):
            mod.main()

        self.assertEqual(build_mock.call_count, 9)
        self.assertEqual([call.kwargs["symbols"] for call in build_mock.mock_calls[:3]], [("SPY",), ("SPY",), ("SPY",)])

    def test_repeated_symbol_override(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "build_manual_polygon_ohlcv_incremental", return_value=self._summary()) as build_mock, patch(
            "sys.argv",
            [
                "run_polygon_ohlcv_chunked_backfill.py",
                "--symbol",
                "SPY",
                "--symbol",
                "QQQ",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
                "--chunk-days",
                "3",
            ],
        ):
            mod.main()

        self.assertEqual(build_mock.call_args.kwargs["symbols"], ("QQQ",))

    def test_chunk_days_splitting(self) -> None:
        mod = self._module()
        chunks = mod.split_date_range_into_chunks(date(2025, 1, 2), date(2025, 1, 10), max_days_per_chunk=4)
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0].start_date, date(2025, 1, 2))
        self.assertEqual(chunks[0].end_date, date(2025, 1, 5))

    def test_max_symbols_cap(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch(
            "sys.argv",
            [
                "run_polygon_ohlcv_chunked_backfill.py",
                "--symbol",
                "SPY",
                "--symbol",
                "QQQ",
                "--symbol",
                "IWM",
                "--symbol",
                "DIA",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
                "--chunk-days",
                "3",
            ],
        ):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_max_chunks_cap(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch(
            "sys.argv",
            [
                "run_polygon_ohlcv_chunked_backfill.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-02-01",
                "--chunk-days",
                "5",
                "--max-chunks",
                "2",
            ],
        ):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_dry_run_execution_summary(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "build_manual_polygon_ohlcv_incremental", return_value=self._summary()) as build_mock, patch(
            "scripts.run_polygon_ohlcv_chunked_backfill.time.sleep"
        ) as sleep_mock, patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            [
                "run_polygon_ohlcv_chunked_backfill.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
                "--chunk-days",
                "3",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("chunks_total=3", printed)
        self.assertIn("total_rows_written=0", printed)
        self.assertIn("rate_limit_failures=0", printed)
        self.assertIn("stopped_due_to_rate_limit=false", printed)
        self.assertNotIn("POLYGON_API_KEY", printed)
        self.assertNotIn("DATABASE_URL", printed)
        self.assertEqual(build_mock.call_count, 3)
        self.assertEqual(sleep_mock.call_count, 3)

    def test_sleep_option_used_without_slowing_tests(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "build_manual_polygon_ohlcv_incremental", return_value=self._summary()) as build_mock, patch(
            "scripts.run_polygon_ohlcv_chunked_backfill.time.sleep"
        ) as sleep_mock, patch(
            "sys.argv",
            [
                "run_polygon_ohlcv_chunked_backfill.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
                "--chunk-days",
                "3",
                "--sleep-seconds-between-chunks",
                "5",
                "--dry-run-no-sleep",
            ],
        ):
            mod.main()

        sleep_mock.assert_not_called()
        self.assertEqual(build_mock.call_count, 3)

    def test_detects_sanitized_rate_limit_failure_and_stops(self) -> None:
        mod = self._module()
        failure = self._summary(status="failed")
        failure.symbol_summaries = (
            SimpleNamespace(
                symbol="SPY",
                requested_start_date=date(2025, 1, 2),
                effective_start_date=date(2025, 1, 2),
                rows_fetched=0,
                rows_valid=0,
                rows_invalid=0,
                rows_written=0,
                validation_failures=0,
                planned_start_date=date(2025, 1, 2),
                planned_end_date=date(2025, 1, 10),
                write_confirmed=False,
                checkpoint_loaded=False,
                status="failed",
                error_message="VendorHttpStatusError: unexpected http status: 429",
            ),
        )
        with patch.dict(os.environ, {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "build_manual_polygon_ohlcv_incremental", side_effect=[failure, self._summary(), self._summary()]) as build_mock, patch(
            "scripts.run_polygon_ohlcv_chunked_backfill.time.sleep"
        ), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            [
                "run_polygon_ohlcv_chunked_backfill.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
                "--chunk-days",
                "3",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("rate_limit_failures=1", printed)
        self.assertIn("stopped_due_to_rate_limit=true", printed)
        self.assertIn("chunks_not_run=2", printed)
        self.assertEqual(build_mock.call_count, 1)

    def test_continue_until_max_rate_limit_failures_exceeded(self) -> None:
        mod = self._module()
        failure = self._summary(status="failed")
        failure.symbol_summaries = (
            SimpleNamespace(
                symbol="SPY",
                requested_start_date=date(2025, 1, 2),
                effective_start_date=date(2025, 1, 2),
                rows_fetched=0,
                rows_valid=0,
                rows_invalid=0,
                rows_written=0,
                validation_failures=0,
                planned_start_date=date(2025, 1, 2),
                planned_end_date=date(2025, 1, 10),
                write_confirmed=False,
                checkpoint_loaded=False,
                status="failed",
                error_message="VendorHttpStatusError: unexpected http status: 429",
            ),
        )
        with patch.dict(os.environ, {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "build_manual_polygon_ohlcv_incremental", side_effect=[failure, failure, self._summary()]) as build_mock, patch(
            "scripts.run_polygon_ohlcv_chunked_backfill.time.sleep"
        ), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            [
                "run_polygon_ohlcv_chunked_backfill.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
                "--chunk-days",
                "3",
                "--no-stop-on-rate-limit",
                "--max-rate-limit-failures",
                "2",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("rate_limit_failures=2", printed)
        self.assertIn("stopped_due_to_rate_limit=true", printed)
        self.assertIn("chunks_not_run=1", printed)
        self.assertEqual(build_mock.call_count, 2)

    def test_confirmed_write_routes_through_existing_persistence_logic(self) -> None:
        mod = self._module()
        fake_connection = Mock()
        fake_connection.execute.return_value.fetchall.return_value = []
        with patch.dict(
            os.environ,
            {"POLYGON_API_KEY": "polygon-secret", "DATABASE_URL": "postgresql://user:pass@host/db"},
            clear=True,
        ), patch.object(mod, "load_local_env_if_available", return_value=False), patch.object(
            mod, "_open_connection", return_value=fake_connection
        ) as open_connection_mock, patch.object(mod, "ManualPolygonOHLCVCheckpointStore") as checkpoint_store_cls, patch.object(
            mod, "OhlcvWriter"
        ) as writer_cls, patch.object(mod, "build_manual_polygon_ohlcv_incremental", return_value=self._summary(rows_written=2)) as build_mock, patch(
            "builtins.print"
        ), patch(
            "sys.argv",
            [
                "run_polygon_ohlcv_chunked_backfill.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
                "--chunk-days",
                "3",
                "--confirm-write",
            ],
        ):
            mod.main()

        open_connection_mock.assert_called_once()
        checkpoint_store_cls.assert_called_once_with(fake_connection)
        writer_cls.assert_called_once_with(fake_connection)
        self.assertTrue(build_mock.call_args.kwargs["confirmed_write"])
        self.assertIs(build_mock.call_args.kwargs["writer"], writer_cls.return_value)
        self.assertIs(build_mock.call_args.kwargs["checkpoint_store"], checkpoint_store_cls.return_value)
        self.assertTrue(build_mock.call_args.kwargs["confirmed_write"])

    def test_missing_polygon_key_fails_safely(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "sys.argv",
            [
                "run_polygon_ohlcv_chunked_backfill.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
                "--chunk-days",
                "3",
            ],
        ):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_missing_database_url_with_confirm_write_fails_safely(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch(
            "sys.argv",
            [
                "run_polygon_ohlcv_chunked_backfill.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
                "--chunk-days",
                "3",
                "--confirm-write",
            ],
        ):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_source_has_no_schema_migration_scheduler_api_ai_behavior(self) -> None:
        source = Path(__file__).resolve().parents[2] / "scripts" / "run_polygon_ohlcv_chunked_backfill.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("scheduler", text.lower())
        self.assertNotIn("migration", text.lower())
        self.assertNotIn("strategy", text.lower())
        self.assertNotIn("prediction", text.lower())
