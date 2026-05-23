from __future__ import annotations

import unittest
from unittest.mock import patch


class DiagnosePolygonQuotaReadinessTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_polygon_quota_readiness as mod

        return mod

    def test_within_budget(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_polygon_quota_readiness.py",
                "--estimated-requests",
                "4",
                "--max-requests",
                "6",
                "--sleep-seconds-between-requests",
                "3",
            ],
        ):
            mod.main()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("request_budget_status=within_budget", printed)
        self.assertIn("quota_readiness_status=ready", printed)

    def test_exceeds_budget(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_polygon_quota_readiness.py",
                "--estimated-requests",
                "8",
                "--max-requests",
                "6",
                "--sleep-seconds-between-requests",
                "3",
            ],
        ):
            mod.main()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("request_budget_status=exceeds_budget", printed)
        self.assertIn("quota_readiness_status=manual_review_needed", printed)

    def test_source_mode_api_recommendation(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_polygon_quota_readiness.py",
                "--estimated-requests",
                "8",
                "--max-requests",
                "6",
                "--sleep-seconds-between-requests",
                "3",
                "--source-mode",
                "api",
            ],
        ):
            mod.main()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("recommended_source_path=recent/daily/gap data and small controlled backfills", printed)

    def test_source_mode_flatfiles_recommendation(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_polygon_quota_readiness.py",
                "--estimated-requests",
                "8",
                "--max-requests",
                "6",
                "--sleep-seconds-between-requests",
                "3",
                "--source-mode",
                "flatfiles",
            ],
        ):
            mod.main()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("recommended_source_path=large historical downloads/backfills", printed)

    def test_source_mode_websocket_recommendation(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_polygon_quota_readiness.py",
                "--estimated-requests",
                "8",
                "--max-requests",
                "6",
                "--sleep-seconds-between-requests",
                "3",
                "--source-mode",
                "websocket",
            ],
        ):
            mod.main()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("recommended_source_path=future live streaming data", printed)

    def test_no_vendor_calls_and_no_db_writes(self) -> None:
        mod = self._module()
        with patch("builtins.print"), patch("sys.argv", ["diagnose_polygon_quota_readiness.py", "--estimated-requests", "4", "--max-requests", "6", "--sleep-seconds-between-requests", "3"]), patch.object(
            mod, "_recommended_source_path", wraps=mod._recommended_source_path
        ) as recommended_source_path:
            mod.main()
        recommended_source_path.assert_called()

    def test_source_has_no_schema_migration_scheduler_api_ai_behavior(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_polygon_quota_readiness.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("migration", text.lower())
        self.assertNotIn("strategy", text.lower())
        self.assertNotIn("prediction", text.lower())

