from __future__ import annotations

import os
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch


class RunPolygonOhlcvTinyUniverseCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.run_polygon_ohlcv_tiny_universe_check as mod

        return mod

    def _summary(self):
        row = SimpleNamespace(
            symbol="SPY",
            requested_start_date=date(2025, 1, 2),
            effective_start_date=date(2025, 1, 2),
            rows_fetched=2,
            rows_valid=2,
            rows_invalid=0,
            rows_written=0,
            validation_failures=0,
            planned_start_date=date(2025, 1, 2),
            planned_end_date=date(2025, 1, 10),
            write_confirmed=False,
            checkpoint_loaded=False,
            status="completed",
            error_message=None,
        )
        return SimpleNamespace(
            symbol_summaries=(row,),
            series_total=1,
            series_completed=1,
            series_failed=0,
            series_skipped=0,
            total_rows_fetched=2,
            total_rows_written=0,
        )

    def test_defaults_to_tiny_universe(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "build_manual_polygon_ohlcv_incremental", return_value=self._summary()) as build_mock, patch(
            "builtins.print"
        ), patch(
            "sys.argv",
            [
                "run_polygon_ohlcv_tiny_universe_check.py",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
                "--timeframe",
                "1d",
            ],
        ):
            exit_code = mod.main()

        self.assertEqual(exit_code, 0)
        build_mock.assert_called_once()
        self.assertEqual(build_mock.call_args.kwargs["symbols"], ("SPY", "QQQ", "IWM"))

    def test_repeated_symbol_override(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "build_manual_polygon_ohlcv_incremental", return_value=self._summary()) as build_mock, patch(
            "sys.argv",
            [
                "run_polygon_ohlcv_tiny_universe_check.py",
                "--symbol",
                "SPY",
                "--symbol",
                "QQQ",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
            ],
        ):
            mod.main()

        self.assertEqual(build_mock.call_args.kwargs["symbols"], ("SPY", "QQQ"))

    def test_prints_safe_aggregate_summary(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "build_manual_polygon_ohlcv_incremental", return_value=self._summary()), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            [
                "run_polygon_ohlcv_tiny_universe_check.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("symbols_total=1", printed)
        self.assertIn("symbols_with_full_coverage=0", printed)
        self.assertIn("symbols_with_gaps=0", printed)
        self.assertNotIn("POLYGON_API_KEY", printed)
        self.assertNotIn("DATABASE_URL", printed)

    def test_confirmed_write_uses_existing_writer_and_checkpoint_paths(self) -> None:
        mod = self._module()
        summary = self._summary()
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
        ) as writer_cls, patch.object(mod, "build_manual_polygon_ohlcv_incremental", return_value=summary) as build_mock, patch(
            "builtins.print"
        ), patch(
            "sys.argv",
            [
                "run_polygon_ohlcv_tiny_universe_check.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
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

    def test_database_absence_skips_checkpoint_and_coverage_safely(self) -> None:
        mod = self._module()
        summary = self._summary()
        with patch.dict(os.environ, {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "build_manual_polygon_ohlcv_incremental", return_value=summary) as build_mock, patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            [
                "run_polygon_ohlcv_tiny_universe_check.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
            ],
        ):
            mod.main()

        build_kwargs = build_mock.call_args.kwargs
        self.assertIsNone(build_kwargs["writer"])
        self.assertIsNone(build_kwargs["checkpoint_store"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertNotIn("coverage_status=", printed)

    def test_source_has_no_schema_migration_scheduler_api_ai_logic(self) -> None:
        source = Path(__file__).resolve().parents[2] / "scripts" / "run_polygon_ohlcv_tiny_universe_check.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("scheduler", text.lower())
        self.assertNotIn("migration", text.lower())
        self.assertNotIn("strategy", text.lower())
        self.assertNotIn("prediction", text.lower())
