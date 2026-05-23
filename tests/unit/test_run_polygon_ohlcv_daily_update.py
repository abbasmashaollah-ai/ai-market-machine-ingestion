from __future__ import annotations

import os
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch


class RunPolygonOhlcvDailyUpdateTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.run_polygon_ohlcv_daily_update as mod

        return mod

    def _summary(self, *, rows_fetched: int = 2, rows_written: int = 0, status: str = "completed"):
        row = SimpleNamespace(
            symbol="SPY",
            requested_start_date=date(2025, 1, 11),
            effective_start_date=date(2025, 1, 11),
            rows_fetched=rows_fetched,
            rows_valid=rows_fetched,
            rows_invalid=0,
            rows_written=rows_written,
            validation_failures=0,
            planned_start_date=date(2025, 1, 11),
            planned_end_date=date(2025, 1, 13),
            write_confirmed=False,
            checkpoint_loaded=False,
            status=status,
            error_message=None,
        )
        return SimpleNamespace(symbol_summaries=(row,), total_rows_fetched=rows_fetched, total_rows_written=rows_written)

    def test_up_to_date_symbols_are_skipped(self) -> None:
        mod = self._module()
        fake_connection = Mock()
        fake_connection.execute.return_value.fetchall.return_value = [{"timestamp": date(2025, 1, 13), "source": "polygon_aggregates", "adjusted": True}]
        with patch.dict(os.environ, {"POLYGON_API_KEY": "polygon-secret", "DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=fake_connection), patch.object(mod, "_latest_expected_trading_day", return_value=date(2025, 1, 13)), patch.object(
            mod, "build_manual_polygon_ohlcv_incremental"
        ) as build_mock, patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            ["run_polygon_ohlcv_daily_update.py", "--symbol", "SPY", "--as-of-date", "2025-01-13", "--check-existing"],
        ):
            mod.main()

        build_mock.assert_not_called()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("status=up_to_date", printed)

    def test_update_needed_symbols_call_runtime(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_latest_expected_trading_day", return_value=date(2025, 1, 13)), patch.object(
            mod, "build_manual_polygon_ohlcv_incremental", return_value=self._summary()
        ) as build_mock, patch(
            "builtins.print"
        ), patch(
            "sys.argv",
            ["run_polygon_ohlcv_daily_update.py", "--symbol", "SPY", "--as-of-date", "2025-01-13"],
        ):
            mod.main()

        self.assertEqual(build_mock.call_count, 1)
        self.assertEqual(build_mock.call_args.kwargs["symbols"], ("SPY",))
        self.assertEqual(build_mock.call_args.kwargs["start_date"], date(2025, 1, 13))
        self.assertEqual(build_mock.call_args.kwargs["end_date"], date(2025, 1, 13))

    def test_no_expected_trading_day_is_skipped(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_latest_expected_trading_day", return_value=None), patch.object(
            mod, "build_manual_polygon_ohlcv_incremental"
        ) as build_mock, patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            ["run_polygon_ohlcv_daily_update.py", "--symbol", "SPY", "--as-of-date", "2025-01-13"],
        ):
            mod.main()

        build_mock.assert_not_called()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("status=no_expected_trading_day", printed)

    def test_no_existing_data_uses_planned_window(self) -> None:
        mod = self._module()
        fake_connection = Mock()
        fake_connection.execute.return_value.fetchall.return_value = []
        with patch.dict(
            os.environ,
            {"POLYGON_API_KEY": "polygon-secret", "DATABASE_URL": "postgresql://user:pass@host/db"},
            clear=True,
        ), patch.object(mod, "load_local_env_if_available", return_value=False), patch.object(
            mod, "_open_connection", return_value=fake_connection
        ), patch.object(mod, "_latest_expected_trading_day", return_value=date(2025, 1, 13)), patch.object(
            mod, "build_manual_polygon_ohlcv_incremental", return_value=self._summary()
        ) as build_mock, patch(
            "builtins.print"
        ), patch(
            "sys.argv",
            [
                "run_polygon_ohlcv_daily_update.py",
                "--symbol",
                "SPY",
                "--as-of-date",
                "2025-01-13",
                "--check-existing",
            ],
        ):
            mod.main()

        self.assertEqual(build_mock.call_args.kwargs["start_date"], date(2025, 1, 13))
        self.assertEqual(build_mock.call_args.kwargs["end_date"], date(2025, 1, 13))

    def test_confirm_write_passed_through(self) -> None:
        mod = self._module()
        fake_connection = Mock()
        fake_connection.execute.return_value.fetchall.return_value = [{"timestamp": date(2025, 1, 10), "source": "polygon_aggregates", "adjusted": True}]
        with patch.dict(
            os.environ,
            {"POLYGON_API_KEY": "polygon-secret", "DATABASE_URL": "postgresql://user:pass@host/db"},
            clear=True,
        ), patch.object(mod, "load_local_env_if_available", return_value=False), patch.object(
            mod, "_open_connection", return_value=fake_connection
        ), patch.object(mod, "_latest_expected_trading_day", return_value=date(2025, 1, 13)), patch.object(
            mod, "ManualPolygonOHLCVCheckpointStore"
        ) as checkpoint_store_cls, patch.object(mod, "OhlcvWriter") as writer_cls, patch.object(
            mod, "build_manual_polygon_ohlcv_incremental", return_value=self._summary(rows_written=2)
        ) as build_mock, patch(
            "builtins.print"
        ), patch(
            "sys.argv",
            [
                "run_polygon_ohlcv_daily_update.py",
                "--symbol",
                "SPY",
                "--as-of-date",
                "2025-01-13",
                "--confirm-write",
            ],
        ):
            mod.main()

        self.assertTrue(build_mock.call_args.kwargs["confirmed_write"])
        self.assertIs(build_mock.call_args.kwargs["writer"], writer_cls.return_value)
        self.assertIs(build_mock.call_args.kwargs["checkpoint_store"], checkpoint_store_cls.return_value)

    def test_record_flags_route_through_existing_stores(self) -> None:
        mod = self._module()
        fake_connection = Mock()
        fake_connection.execute.return_value.fetchall.return_value = [{"timestamp": date(2025, 1, 10), "source": "polygon_aggregates", "adjusted": True}]
        with patch.dict(
            os.environ,
            {"POLYGON_API_KEY": "polygon-secret", "DATABASE_URL": "postgresql://user:pass@host/db"},
            clear=True,
        ), patch.object(mod, "load_local_env_if_available", return_value=False), patch.object(
            mod, "_open_connection", return_value=fake_connection
        ), patch.object(mod, "_latest_expected_trading_day", return_value=date(2025, 1, 13)), patch.object(
            mod, "build_manual_polygon_ohlcv_incremental", return_value=self._summary()
        ), patch.object(mod, "IngestionRunStore") as run_store_cls, patch.object(
            mod, "DataQualityResultStore"
        ) as quality_store_cls, patch.object(
            mod, "DataLineageStore"
        ) as lineage_store_cls, patch(
            "builtins.print"
        ), patch(
            "sys.argv",
            [
                "run_polygon_ohlcv_daily_update.py",
                "--symbol",
                "SPY",
                "--as-of-date",
                "2025-01-13",
                "--check-existing",
                "--record-run",
                "--record-quality",
                "--record-lineage",
            ],
        ):
            mod.main()

        run_store_cls.assert_called_once_with(fake_connection)
        quality_store_cls.assert_called_once_with(fake_connection)
        lineage_store_cls.assert_called_once_with(fake_connection)

    def test_request_budget_blocks_before_vendor_call(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_latest_expected_trading_day", return_value=date(2025, 1, 13)), patch.object(
            mod, "build_manual_polygon_ohlcv_incremental"
        ) as build_mock, patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            [
                "run_polygon_ohlcv_daily_update.py",
                "--symbol",
                "SPY",
                "--symbol",
                "QQQ",
                "--as-of-date",
                "2025-01-13",
                "--max-requests",
                "1",
            ],
        ):
            mod.main()

        build_mock.assert_not_called()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("status=blocked_over_budget", printed)

    def test_no_secrets_printed(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_latest_expected_trading_day", return_value=date(2025, 1, 13)), patch.object(
            mod, "build_manual_polygon_ohlcv_incremental", return_value=self._summary()
        ), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            ["run_polygon_ohlcv_daily_update.py", "--symbol", "SPY", "--as-of-date", "2025-01-13"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertNotIn("POLYGON_API_KEY", printed)
        self.assertNotIn("DATABASE_URL", printed)

    def test_source_has_no_schema_migration_scheduler_api_ai_behavior(self) -> None:
        source = Path(__file__).resolve().parents[2] / "scripts" / "run_polygon_ohlcv_daily_update.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("scheduler", text.lower())
        self.assertNotIn("migration", text.lower())
        self.assertNotIn("strategy", text.lower())
        self.assertNotIn("prediction", text.lower())
