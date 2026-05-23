from __future__ import annotations

import os
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch


class PlanPolygonOhlcvBackfillTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.plan_polygon_ohlcv_backfill as mod

        return mod

    def test_defaults_to_tiny_universe_planning(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            [
                "plan_polygon_ohlcv_backfill.py",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
            ],
        ):
            exit_code = mod.main()

        self.assertEqual(exit_code, 0)
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("symbols_total=3", printed)
        self.assertIn("per_symbol_expected_rows=6", printed)
        self.assertIn("total_expected_rows=18", printed)

    def test_repeated_symbol_planning(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            [
                "plan_polygon_ohlcv_backfill.py",
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

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("symbols_total=2", printed)
        self.assertIn("symbol=SPY", printed)
        self.assertIn("symbol=QQQ", printed)

    def test_market_calendar_integration(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "builtins.print"
        ), patch(
            "sys.argv",
            [
                "plan_polygon_ohlcv_backfill.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
            ],
        ), patch.object(mod, "expected_trading_days", return_value=[date(2025, 1, 2), date(2025, 1, 5)]) as calendar_mock:
            mod.main()

        calendar_mock.assert_called_once_with(date(2025, 1, 2), date(2025, 1, 10))

    def test_exclusive_end_date_behavior(self) -> None:
        mod = self._module()
        fake_connection = Mock()
        fake_connection.execute.return_value.fetchall.return_value = [{"timestamp": date(2025, 1, 2)}]
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=fake_connection), patch.object(mod, "expected_trading_days", return_value=[date(2025, 1, 2)]) as calendar_mock, patch(
            "builtins.print"
        ), patch(
            "sys.argv",
            [
                "plan_polygon_ohlcv_backfill.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
                "--check-existing",
            ],
        ):
            mod.main()

        self.assertEqual(fake_connection.execute.call_args.args[1][2], date(2025, 1, 11))
        calendar_mock.assert_called_once()

    def test_no_polygon_api_key_required(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "builtins.print"
        ), patch(
            "sys.argv",
            [
                "plan_polygon_ohlcv_backfill.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
            ],
        ):
            exit_code = mod.main()

        self.assertEqual(exit_code, 0)

    def test_check_existing_reads_db_coverage_when_database_present(self) -> None:
        mod = self._module()
        fake_connection = Mock()
        fake_connection.execute.return_value.fetchall.return_value = [{"timestamp": date(2025, 1, 2)}]
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=fake_connection) as open_connection_mock, patch.object(
            mod, "expected_trading_days", return_value=[date(2025, 1, 2), date(2025, 1, 5)]
        ), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            [
                "plan_polygon_ohlcv_backfill.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
                "--check-existing",
            ],
        ):
            mod.main()

        open_connection_mock.assert_called_once()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("per_symbol_missing_rows=1", printed)
        self.assertIn("total_missing_rows=1", printed)

    def test_no_db_writes(self) -> None:
        mod = self._module()
        fake_connection = Mock()
        fake_connection.execute.return_value.fetchall.return_value = []
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=fake_connection), patch(
            "builtins.print"
        ), patch(
            "sys.argv",
            [
                "plan_polygon_ohlcv_backfill.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
                "--check-existing",
            ],
        ):
            mod.main()

        fake_connection.commit.assert_not_called()
        fake_connection.rollback.assert_not_called()
        self.assertFalse(any("INSERT" in str(call.args[0]) for call in fake_connection.execute.mock_calls if call.args))

    def test_safe_output(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            [
                "plan_polygon_ohlcv_backfill.py",
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
        self.assertNotIn("DATABASE_URL", printed)
        self.assertNotIn("POLYGON_API_KEY", printed)

    def test_source_has_no_vendor_or_write_behavior(self) -> None:
        source = Path(__file__).resolve().parents[2] / "scripts" / "plan_polygon_ohlcv_backfill.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("POLYGON_API_KEY", text)
        self.assertNotIn("insert into", text.lower())
        self.assertNotIn("writer", text.lower())
        self.assertNotIn("api_key", text.lower())
