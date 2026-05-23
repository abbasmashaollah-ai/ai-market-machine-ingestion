from __future__ import annotations

import os
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch


class PlanPolygonOhlcvDailyUpdateTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.plan_polygon_ohlcv_daily_update as mod

        return mod

    def test_defaults_to_tiny_universe(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch.object(
            mod, "_latest_expected_trading_day", return_value=date(2025, 1, 13)
        ), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            [
                "plan_polygon_ohlcv_daily_update.py",
                "--as-of-date",
                "2025-01-13",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("symbols_total=3", printed)
        self.assertIn("symbol=SPY", printed)
        self.assertIn("symbol=QQQ", printed)
        self.assertIn("symbol=IWM", printed)

    def test_repeated_symbol_override(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch.object(
            mod, "_latest_expected_trading_day", return_value=date(2025, 1, 13)
        ), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            [
                "plan_polygon_ohlcv_daily_update.py",
                "--symbol",
                "SPY",
                "--symbol",
                "QQQ",
                "--as-of-date",
                "2025-01-13",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("symbols_total=2", printed)
        self.assertIn("symbol=SPY", printed)
        self.assertIn("symbol=QQQ", printed)

    def test_market_calendar_latest_trading_day(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch.object(
            mod, "expected_trading_days", side_effect=lambda start, end: [date(2025, 1, 10)] if start == end == date(2025, 1, 10) else []
        ) as calendar_mock, patch(
            "builtins.print"
        ), patch(
            "sys.argv",
            ["plan_polygon_ohlcv_daily_update.py", "--as-of-date", "2025-01-10"],
        ):
            mod.main()

        self.assertTrue(calendar_mock.called)

    def test_source_filtered_latest_existing_date(self) -> None:
        mod = self._module()
        fake_connection = Mock()
        fake_connection.execute.return_value.fetchall.return_value = [{"timestamp": date(2025, 1, 10), "source": "polygon_aggregates", "adjusted": True}]
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=fake_connection), patch.object(
            mod, "_latest_expected_trading_day", return_value=date(2025, 1, 10)
        ), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            [
                "plan_polygon_ohlcv_daily_update.py",
                "--symbol",
                "SPY",
                "--as-of-date",
                "2025-01-13",
                "--check-existing",
                "--source",
                "polygon_aggregates",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("latest_existing_date=2025-01-10", printed)
        self.assertIn("status=up_to_date", printed)
        self.assertIn("source=polygon_aggregates", printed)

    def test_update_needed(self) -> None:
        mod = self._module()
        fake_connection = Mock()
        fake_connection.execute.return_value.fetchall.return_value = [{"timestamp": date(2025, 1, 9), "source": "polygon_aggregates", "adjusted": True}]
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=fake_connection), patch.object(
            mod, "_latest_expected_trading_day", return_value=date(2025, 1, 10)
        ), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            [
                "plan_polygon_ohlcv_daily_update.py",
                "--symbol",
                "SPY",
                "--as-of-date",
                "2025-01-13",
                "--check-existing",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("status=update_needed", printed)
        self.assertIn("needed_start_date=2025-01-10", printed)
        self.assertIn("needed_end_date=2025-01-14", printed)

    def test_no_existing_data(self) -> None:
        mod = self._module()
        fake_connection = Mock()
        fake_connection.execute.return_value.fetchall.return_value = []
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=fake_connection), patch.object(
            mod, "_latest_expected_trading_day", return_value=date(2025, 1, 10)
        ), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            [
                "plan_polygon_ohlcv_daily_update.py",
                "--symbol",
                "SPY",
                "--as-of-date",
                "2025-01-13",
                "--check-existing",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("status=no_existing_data", printed)

    def test_no_expected_trading_day(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch.object(
            mod, "_latest_expected_trading_day", return_value=None
        ), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            [
                "plan_polygon_ohlcv_daily_update.py",
                "--symbol",
                "SPY",
                "--as-of-date",
                "2025-01-13",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("status=no_expected_trading_day", printed)

    def test_database_required_only_with_check_existing(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "builtins.print"
        ), patch(
            "sys.argv",
            [
                "plan_polygon_ohlcv_daily_update.py",
                "--symbol",
                "SPY",
                "--as-of-date",
                "2025-01-13",
                "--check-existing",
            ],
        ):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_no_vendor_calls_and_no_db_writes(self) -> None:
        mod = self._module()
        fake_connection = Mock()
        fake_connection.execute.return_value.fetchall.return_value = []
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=fake_connection), patch.object(
            mod, "_latest_expected_trading_day", return_value=date(2025, 1, 10)
        ), patch(
            "builtins.print"
        ), patch(
            "sys.argv",
            [
                "plan_polygon_ohlcv_daily_update.py",
                "--symbol",
                "SPY",
                "--as-of-date",
                "2025-01-13",
                "--check-existing",
            ],
        ):
            mod.main()

        fake_connection.commit.assert_not_called()
        fake_connection.rollback.assert_not_called()
        self.assertFalse(any("INSERT" in str(call.args[0]).upper() for call in fake_connection.execute.mock_calls if call.args))

    def test_source_has_no_vendor_or_write_behavior(self) -> None:
        source = Path(__file__).resolve().parents[2] / "scripts" / "plan_polygon_ohlcv_daily_update.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("POLYGON_API_KEY", text)
        self.assertNotIn("insert into", text.lower())
        self.assertNotIn("writer", text.lower())
        self.assertNotIn("api_key", text.lower())

