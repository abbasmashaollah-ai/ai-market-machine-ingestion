from __future__ import annotations

import os
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch


class PlanPolygonOhlcvSchedulerCycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.plan_polygon_ohlcv_scheduler_cycle as mod

        return mod

    def test_incremental_update_classification(self) -> None:
        mod = self._module()
        fake_connection = Mock()
        fake_connection.execute.return_value.fetchall.return_value = [{"timestamp": date(2025, 1, 10), "source": "polygon_aggregates", "adjusted": True}]
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=fake_connection), patch.object(
            mod, "_latest_expected_trading_day", return_value=date(2025, 1, 13)
        ), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            ["plan_polygon_ohlcv_scheduler_cycle.py", "--symbol", "SPY", "--as-of-date", "2025-01-14", "--check-existing"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("update_mode=incremental_update_needed", printed)
        self.assertIn("recommended_command=python -m scripts.run_polygon_ohlcv_daily_update", printed)

    def test_historical_gap_classification(self) -> None:
        mod = self._module()
        fake_connection = Mock()
        fake_connection.execute.return_value.fetchall.return_value = [{"timestamp": date(2025, 1, 1), "source": "polygon_aggregates", "adjusted": True}]
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=fake_connection), patch.object(
            mod, "_latest_expected_trading_day", return_value=date(2025, 1, 13)
        ), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            ["plan_polygon_ohlcv_scheduler_cycle.py", "--symbol", "SPY", "--as-of-date", "2025-01-14", "--check-existing"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("update_mode=historical_gap_detected", printed)
        self.assertIn("recommended_command=python -m scripts.run_polygon_ohlcv_chunked_backfill", printed)

    def test_no_existing_data_classification(self) -> None:
        mod = self._module()
        fake_connection = Mock()
        fake_connection.execute.return_value.fetchall.return_value = []
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=fake_connection), patch.object(
            mod, "_latest_expected_trading_day", return_value=date(2025, 1, 13)
        ), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            ["plan_polygon_ohlcv_scheduler_cycle.py", "--symbol", "SPY", "--as-of-date", "2025-01-14", "--check-existing"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("update_mode=no_existing_data", printed)

    def test_up_to_date_classification(self) -> None:
        mod = self._module()
        fake_connection = Mock()
        fake_connection.execute.return_value.fetchall.return_value = [{"timestamp": date(2025, 1, 13), "source": "polygon_aggregates", "adjusted": True}]
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=fake_connection), patch.object(
            mod, "_latest_expected_trading_day", return_value=date(2025, 1, 13)
        ), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            ["plan_polygon_ohlcv_scheduler_cycle.py", "--symbol", "SPY", "--as-of-date", "2025-01-14", "--check-existing"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("update_mode=up_to_date", printed)

    def test_request_budget_classification(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch.object(
            mod, "_latest_expected_trading_day", return_value=date(2025, 1, 13)
        ), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            [
                "plan_polygon_ohlcv_scheduler_cycle.py",
                "--symbol",
                "SPY",
                "--symbol",
                "QQQ",
                "--as-of-date",
                "2025-01-14",
                "--max-requests",
                "1",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("request_budget_status=exceeds_budget", printed)
        self.assertIn("scheduler_readiness_status=not_ready", printed)

    def test_database_required_only_with_check_existing(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "sys.argv",
            ["plan_polygon_ohlcv_scheduler_cycle.py", "--symbol", "SPY", "--as-of-date", "2025-01-14", "--check-existing"],
        ):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_no_vendor_calls_and_no_db_writes(self) -> None:
        mod = self._module()
        fake_connection = Mock()
        fake_connection.execute.return_value.fetchall.return_value = []
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=fake_connection), patch.object(
            mod, "_latest_expected_trading_day", return_value=date(2025, 1, 13)
        ), patch(
            "builtins.print"
        ), patch(
            "sys.argv",
            ["plan_polygon_ohlcv_scheduler_cycle.py", "--symbol", "SPY", "--as-of-date", "2025-01-14", "--check-existing"],
        ):
            mod.main()

        fake_connection.commit.assert_not_called()
        fake_connection.rollback.assert_not_called()
        self.assertFalse(any("INSERT" in str(call.args[0]).upper() for call in fake_connection.execute.mock_calls if call.args))

    def test_source_has_no_schema_migration_scheduler_api_ai_behavior(self) -> None:
        source = Path(__file__).resolve().parents[2] / "scripts" / "plan_polygon_ohlcv_scheduler_cycle.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("migration", text.lower())
        self.assertNotIn("strategy", text.lower())
        self.assertNotIn("prediction", text.lower())
