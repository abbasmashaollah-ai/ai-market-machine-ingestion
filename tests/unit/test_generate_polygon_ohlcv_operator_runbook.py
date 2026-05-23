from __future__ import annotations

import os
import unittest
from unittest.mock import patch


class GeneratePolygonOhlcvOperatorRunbookTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.generate_polygon_ohlcv_operator_runbook as mod

        return mod

    def test_generated_runbook_includes_preflight(self) -> None:
        mod = self._module()
        with patch.object(mod, "build_preflight_report", return_value=([
            {"symbol": "SPY", "recommended_action": "run_daily_update", "recommended_command": "python -m scripts.run_polygon_ohlcv_daily_update --symbol SPY --as-of-date 2025-01-14 --timeframe 1d --source polygon_aggregates --max-requests 3"}
        ], {"symbols_total": 1, "request_budget_status": "within_budget", "preflight_status": "manual_review_needed", "symbols_ready": 0, "symbols_needing_update": 1, "symbols_with_complete_evidence": 0, "estimated_total_requests": 1})), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            ["generate_polygon_ohlcv_operator_runbook.py", "--symbol", "SPY", "--as-of-date", "2025-01-14"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("step=1 preflight_command=python -m scripts.preflight_polygon_ohlcv_operations", printed)
        self.assertIn("step=2 recommendation_verifier_command=python -m scripts.verify_polygon_preflight_recommendations", printed)

    def test_includes_recommendation_verifier(self) -> None:
        mod = self._module()
        with patch.object(mod, "build_preflight_report", return_value=([
            {"symbol": "SPY", "recommended_action": "run_daily_update", "recommended_command": "python -m scripts.run_polygon_ohlcv_daily_update --symbol SPY --as-of-date 2025-01-14 --timeframe 1d --source polygon_aggregates --max-requests 3"}
        ], {"symbols_total": 1, "request_budget_status": "within_budget", "preflight_status": "manual_review_needed", "symbols_ready": 0, "symbols_needing_update": 1, "symbols_with_complete_evidence": 0, "estimated_total_requests": 1})), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            ["generate_polygon_ohlcv_operator_runbook.py", "--symbol", "SPY", "--as-of-date", "2025-01-14"],
        ):
            mod.main()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("recommendation_verifier_command=", printed)

    def test_includes_per_symbol_evidence_verification(self) -> None:
        mod = self._module()
        with patch.object(mod, "build_preflight_report", return_value=([
            {"symbol": "SPY", "recommended_action": "run_daily_update", "recommended_command": "python -m scripts.run_polygon_ohlcv_daily_update --symbol SPY --as-of-date 2025-01-14 --timeframe 1d --source polygon_aggregates --max-requests 3"}
        ], {"symbols_total": 1, "request_budget_status": "within_budget", "preflight_status": "manual_review_needed", "symbols_ready": 0, "symbols_needing_update": 1, "symbols_with_complete_evidence": 0, "estimated_total_requests": 1})), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            ["generate_polygon_ohlcv_operator_runbook.py", "--symbol", "SPY", "--as-of-date", "2025-01-14", "--include-evidence-flags"],
        ):
            mod.main()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("step=4 evidence_command=python -m scripts.verify_polygon_ohlcv_evidence_chain", printed)

    def test_no_secrets_and_no_confirm_write(self) -> None:
        mod = self._module()
        with patch.object(mod, "build_preflight_report", return_value=([
            {"symbol": "SPY", "recommended_action": "run_daily_update", "recommended_command": "python -m scripts.run_polygon_ohlcv_daily_update --symbol SPY --as-of-date 2025-01-14 --timeframe 1d --source polygon_aggregates --max-requests 3"}
        ], {"symbols_total": 1, "request_budget_status": "within_budget", "preflight_status": "manual_review_needed", "symbols_ready": 0, "symbols_needing_update": 1, "symbols_with_complete_evidence": 0, "estimated_total_requests": 1})), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            ["generate_polygon_ohlcv_operator_runbook.py", "--symbol", "SPY", "--as-of-date", "2025-01-14"],
        ):
            mod.main()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertNotIn("DATABASE_URL", printed)
        self.assertNotIn("POLYGON_API_KEY", printed)
        self.assertNotIn("--confirm-write", printed)

    def test_blocked_state_if_recommendation_verifier_fails(self) -> None:
        mod = self._module()
        with patch.object(mod, "build_preflight_report", return_value=([
            {"symbol": "SPY", "recommended_action": "run_daily_update", "recommended_command": "python -m scripts.some_other_command --symbol SPY"}
        ], {"symbols_total": 1, "request_budget_status": "within_budget", "preflight_status": "manual_review_needed", "symbols_ready": 0, "symbols_needing_update": 1, "symbols_with_complete_evidence": 0, "estimated_total_requests": 1})), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            ["generate_polygon_ohlcv_operator_runbook.py", "--symbol", "SPY", "--as-of-date", "2025-01-14"],
        ):
            mod.main()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("runbook_status=blocked", printed)

    def test_no_vendor_calls_and_no_db_writes(self) -> None:
        mod = self._module()
        with patch.object(mod, "build_preflight_report", return_value=([], {"symbols_total": 0, "request_budget_status": "within_budget", "preflight_status": "ready", "symbols_ready": 0, "symbols_needing_update": 0, "symbols_with_complete_evidence": 0, "estimated_total_requests": 0})), patch(
            "builtins.print"
        ), patch("sys.argv", ["generate_polygon_ohlcv_operator_runbook.py", "--as-of-date", "2025-01-14"]):
            mod.main()

    def test_source_has_no_schema_migration_scheduler_api_ai_behavior(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "generate_polygon_ohlcv_operator_runbook.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("migration", text.lower())
        self.assertNotIn("strategy", text.lower())
        self.assertNotIn("prediction", text.lower())

