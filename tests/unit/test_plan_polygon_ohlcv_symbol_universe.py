from __future__ import annotations

import os
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch


class PlanPolygonOhlcvSymbolUniverseTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.plan_polygon_ohlcv_symbol_universe as mod

        return mod

    def test_default_universe(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            ["plan_polygon_ohlcv_symbol_universe.py"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("universe_name=manual_tiny_universe", printed)
        self.assertIn("symbols_requested=3", printed)

    def test_repeated_symbols(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            ["plan_polygon_ohlcv_symbol_universe.py", "--symbol", "SPY", "--symbol", "QQQ", "--symbol", "IWM"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("symbols_requested=3", printed)
        self.assertIn("symbol=SPY", printed)
        self.assertIn("symbol=QQQ", printed)
        self.assertIn("symbol=IWM", printed)

    def test_max_symbol_cap(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "builtins.print"
        ), patch(
            "sys.argv",
            [
                "plan_polygon_ohlcv_symbol_universe.py",
                "--symbol",
                "SPY",
                "--symbol",
                "QQQ",
                "--symbol",
                "IWM",
                "--max-symbols",
                "2",
            ],
        ):
            mod.main()

    def test_readiness_status(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            [
                "plan_polygon_ohlcv_symbol_universe.py",
                "--symbol",
                "SPY",
                "--symbol",
                "QQQ",
                "--symbol",
                "IWM",
                "--max-symbols",
                "2",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("universe_readiness_status=manual_review_needed", printed)

    def test_check_existing_with_mocked_rows(self) -> None:
        mod = self._module()
        fake_connection = Mock()
        fake_connection.execute.return_value.fetchall.return_value = [{"timestamp": date(2025, 1, 13), "source": "polygon_aggregates"}]
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=fake_connection), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            ["plan_polygon_ohlcv_symbol_universe.py", "--symbol", "SPY", "--check-existing"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("symbol_status=has_existing_data", printed)

    def test_database_required_only_with_check_existing(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "sys.argv",
            ["plan_polygon_ohlcv_symbol_universe.py", "--symbol", "SPY", "--check-existing"],
        ):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_no_vendor_calls_and_no_db_writes(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch.object(
            mod, "_open_connection"
        ) as open_connection_mock, patch(
            "builtins.print"
        ), patch(
            "sys.argv",
            ["plan_polygon_ohlcv_symbol_universe.py", "--symbol", "SPY"],
        ):
            mod.main()

        open_connection_mock.assert_not_called()

    def test_source_has_no_schema_migration_scheduler_api_ai_behavior(self) -> None:
        source = Path(__file__).resolve().parents[2] / "scripts" / "plan_polygon_ohlcv_symbol_universe.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("migration", text.lower())
        self.assertNotIn("strategy", text.lower())
        self.assertNotIn("prediction", text.lower())
