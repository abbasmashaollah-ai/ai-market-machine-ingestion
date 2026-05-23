from __future__ import annotations

import unittest
from unittest.mock import patch


class DiagnosePolygonFlatfileE2EReadinessTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_polygon_flatfile_e2e_readiness as mod

        return mod

    def _printed(self, mock_print) -> str:
        return "\n".join(" ".join(str(arg) for arg in call.args) for call in mock_print.mock_calls)

    def test_e2e_diagnostic_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_polygon_flatfile_e2e_readiness.py",
                "--dataset",
                "ohlcv",
                "--asset-class",
                "stocks",
                "--timeframe",
                "1d",
            ],
        ):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("source_mode=flatfiles", printed)
        self.assertIn("flatfile_e2e_status=planning_only_not_enabled", printed)
        self.assertIn("live_flatfile_pipeline_enabled=false", printed)
        self.assertIn("api_path_current_live=true", printed)
        self.assertIn("flatfiles_future_historical_backfill=true", printed)
        self.assertIn("websocket_future_live_streaming=true", printed)

    def test_all_gates_included(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch("sys.argv", ["diagnose_polygon_flatfile_e2e_readiness.py"]):
            mod.main()
        printed = self._printed(print_mock)
        for field in (
            "official_layout_status=planning_only_not_enabled",
            "config_status=planning_only_not_enabled",
            "storage_policy_status=planning_only_not_enabled",
            "discovery_status=planning_only_not_enabled",
            "download_status=planning_only_not_enabled",
            "manifest_status=planning_only_not_enabled",
            "integrity_status=planning_only_not_enabled",
            "quarantine_status=planning_only_not_enabled",
            "parse_status=planning_only_not_enabled",
            "persistence_status=planning_only_not_enabled",
        ):
            self.assertIn(field, printed)

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_polygon_flatfile_e2e_readiness.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("POLYGON_API_KEY", text)
        self.assertNotIn("S3", text)
