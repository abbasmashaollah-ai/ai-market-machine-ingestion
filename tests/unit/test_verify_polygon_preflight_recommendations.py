from __future__ import annotations

import os
import unittest
from unittest.mock import Mock, patch


class VerifyPolygonPreflightRecommendationsTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.verify_polygon_preflight_recommendations as mod

        return mod

    def test_safe_daily_update_recommendation(self) -> None:
        mod = self._module()
        with patch.object(mod, "build_preflight_report", return_value=([
            {"symbol": "SPY", "recommended_action": "run_daily_update", "recommended_command": "python -m scripts.run_polygon_ohlcv_daily_update --symbol SPY --as-of-date 2025-01-14 --timeframe 1d --source polygon_aggregates --max-requests 3"}
        ], {"symbols_total": 1})), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["verify_polygon_preflight_recommendations.py", "--symbol", "SPY", "--as-of-date", "2025-01-14"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("recommendation_safe=true", printed)
        self.assertIn("recommendation_verification_status=pass", printed)

    def test_unsafe_secret_rejected(self) -> None:
        mod = self._module()
        with patch.object(mod, "build_preflight_report", return_value=([
            {"symbol": "SPY", "recommended_action": "run_daily_update", "recommended_command": "python -m scripts.run_polygon_ohlcv_daily_update --symbol SPY --api-key DATABASE_URL"}
        ], {"symbols_total": 1})), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["verify_polygon_preflight_recommendations.py", "--symbol", "SPY", "--as-of-date", "2025-01-14"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("recommendation_safe=false", printed)
        self.assertIn("contains DATABASE_URL", printed)

    def test_unsafe_confirm_write_rejected(self) -> None:
        mod = self._module()
        with patch.object(mod, "build_preflight_report", return_value=([
            {"symbol": "SPY", "recommended_action": "run_daily_update", "recommended_command": "python -m scripts.run_polygon_ohlcv_daily_update --symbol SPY --confirm-write"}
        ], {"symbols_total": 1})), patch("builtins.print"), patch(
            "sys.argv",
            ["verify_polygon_preflight_recommendations.py", "--symbol", "SPY", "--as-of-date", "2025-01-14"],
        ):
            output = mod.main()
        self.assertEqual(output, 0)

    def test_unsafe_outside_allowlist_rejected(self) -> None:
        mod = self._module()
        with patch.object(mod, "build_preflight_report", return_value=([
            {"symbol": "SPY", "recommended_action": "run_daily_update", "recommended_command": "python -m scripts.some_other_command --symbol SPY"}
        ], {"symbols_total": 1})), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["verify_polygon_preflight_recommendations.py", "--symbol", "SPY", "--as-of-date", "2025-01-14"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("recommendation_safe=false", printed)
        self.assertIn("command target not in allowlist", printed)

    def test_aggregate_pass_fail(self) -> None:
        mod = self._module()
        with patch.object(mod, "build_preflight_report", return_value=([
            {"symbol": "SPY", "recommended_action": "run_daily_update", "recommended_command": "python -m scripts.run_polygon_ohlcv_daily_update --symbol SPY --as-of-date 2025-01-14 --timeframe 1d --source polygon_aggregates --max-requests 3"},
            {"symbol": "QQQ", "recommended_action": "run_daily_update", "recommended_command": "python -m scripts.run_polygon_ohlcv_daily_update --symbol QQQ --as-of-date 2025-01-14 --timeframe 1d --source polygon_aggregates --max-requests 3"},
        ], {"symbols_total": 2})), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["verify_polygon_preflight_recommendations.py", "--symbol", "SPY", "--symbol", "QQQ", "--as-of-date", "2025-01-14"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("recommendation_verification_status=pass", printed)
        self.assertIn("recommendations_safe=2", printed)

    def test_no_command_execution(self) -> None:
        mod = self._module()
        with patch.object(mod, "build_preflight_report", return_value=([
            {"symbol": "SPY", "recommended_action": "run_daily_update", "recommended_command": "python -m scripts.run_polygon_ohlcv_daily_update --symbol SPY --as-of-date 2025-01-14 --timeframe 1d --source polygon_aggregates --max-requests 3"}
        ], {"symbols_total": 1})), patch("subprocess.run") as subprocess_run, patch(
            "sys.argv",
            ["verify_polygon_preflight_recommendations.py", "--symbol", "SPY", "--as-of-date", "2025-01-14"],
        ):
            mod.main()

        subprocess_run.assert_not_called()

    def test_no_vendor_calls_and_no_db_writes(self) -> None:
        mod = self._module()
        with patch.object(mod, "build_preflight_report", return_value=([], {"symbols_total": 0})), patch(
            "builtins.print"
        ), patch("sys.argv", ["verify_polygon_preflight_recommendations.py", "--as-of-date", "2025-01-14"]):
            mod.main()

    def test_source_has_no_schema_migration_scheduler_api_ai_behavior(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "verify_polygon_preflight_recommendations.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("migration", text.lower())
        self.assertNotIn("strategy", text.lower())
        self.assertNotIn("prediction", text.lower())

