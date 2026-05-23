from __future__ import annotations

import os
import unittest
from unittest.mock import patch


class RunPolygonOhlcvSchedulerCycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.run_polygon_ohlcv_scheduler_cycle as mod

        return mod

    def test_default_no_op(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            ["run_polygon_ohlcv_scheduler_cycle.py", "--symbol", "SPY", "--as-of-date", "2025-01-14"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("status=scheduler_disabled", printed)

    def test_missing_env_var_blocks(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            [
                "run_polygon_ohlcv_scheduler_cycle.py",
                "--symbol",
                "SPY",
                "--as-of-date",
                "2025-01-14",
                "--enable-scheduler-cycle",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("status=scheduler_disabled", printed)
        self.assertIn("ENABLE_POLYGON_OHLCV_SCHEDULER=true", printed)

    def test_missing_flag_blocks(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"ENABLE_POLYGON_OHLCV_SCHEDULER": "true"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["run_polygon_ohlcv_scheduler_cycle.py", "--symbol", "SPY", "--as-of-date", "2025-01-14"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("status=scheduler_disabled", printed)

    def test_both_flag_and_env_required(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"ENABLE_POLYGON_OHLCV_SCHEDULER": "true"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "run_polygon_ohlcv_scheduler_cycle.py",
                "--symbol",
                "SPY",
                "--as-of-date",
                "2025-01-14",
                "--enable-scheduler-cycle",
            ],
        ):
            with patch.object(mod, "build_preflight_report", return_value=([], {"preflight_status": "ready", "request_budget_status": "within_budget", "symbols_total": 0, "symbols_ready": 0, "symbols_needing_update": 0, "symbols_with_complete_evidence": 0, "symbols_requiring_manual_review": 0, "estimated_total_requests": 0})), patch.object(
                mod, "run_daily_update_main", return_value=0
            ) as runner:
                mod.main()
        runner.assert_not_called()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("status=completed", printed)

    def test_no_vendor_call_when_disabled(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch.object(
            mod, "run_daily_update_main"
        ) as runner, patch("builtins.print"), patch(
            "sys.argv",
            ["run_polygon_ohlcv_scheduler_cycle.py", "--symbol", "SPY", "--as-of-date", "2025-01-14"],
        ):
            mod.main()

        runner.assert_not_called()

    def test_no_db_write_when_disabled(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch.object(
            mod, "run_daily_update_main"
        ) as runner, patch("builtins.print"), patch(
            "sys.argv",
            ["run_polygon_ohlcv_scheduler_cycle.py", "--symbol", "SPY", "--as-of-date", "2025-01-14"],
        ):
            mod.main()

        runner.assert_not_called()

    def test_enabled_path_calls_safe_runner_mock(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"ENABLE_POLYGON_OHLCV_SCHEDULER": "true"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "build_preflight_report", return_value=([
            {"symbol": "SPY", "recommended_action": "run_daily_update"}
        ], {"preflight_status": "ready", "request_budget_status": "within_budget", "symbols_total": 1, "symbols_ready": 1, "symbols_needing_update": 0, "symbols_with_complete_evidence": 1, "symbols_requiring_manual_review": 0, "estimated_total_requests": 1})), patch.object(
            mod, "run_daily_update_main", return_value=0
        ) as runner, patch("builtins.print"), patch(
            "sys.argv",
            ["run_polygon_ohlcv_scheduler_cycle.py", "--symbol", "SPY", "--as-of-date", "2025-01-14", "--enable-scheduler-cycle"],
        ):
            mod.main()

        runner.assert_called()

    def test_preflight_blocked_prevents_execution(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"ENABLE_POLYGON_OHLCV_SCHEDULER": "true"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "build_preflight_report", return_value=([], {"preflight_status": "blocked", "request_budget_status": "exceeds_budget", "symbols_total": 1, "symbols_ready": 0, "symbols_needing_update": 1, "symbols_with_complete_evidence": 0, "symbols_requiring_manual_review": 1, "estimated_total_requests": 99})), patch.object(
            mod, "run_daily_update_main"
        ) as runner, patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["run_polygon_ohlcv_scheduler_cycle.py", "--symbol", "SPY", "--as-of-date", "2025-01-14", "--enable-scheduler-cycle"],
        ):
            mod.main()

        runner.assert_not_called()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("status=blocked_preflight", printed)

    def test_source_has_no_schema_migration_scheduler_api_ai_behavior(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "run_polygon_ohlcv_scheduler_cycle.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("migration", text.lower())
        self.assertNotIn("strategy", text.lower())
        self.assertNotIn("prediction", text.lower())

