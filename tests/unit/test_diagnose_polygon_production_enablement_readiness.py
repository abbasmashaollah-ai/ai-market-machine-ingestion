from __future__ import annotations

import unittest
from unittest.mock import patch


class DiagnosePolygonProductionEnablementReadinessTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_polygon_production_enablement_readiness as mod

        return mod

    def _printed(self, mock_print) -> str:
        return "\n".join(" ".join(str(arg) for arg in call.args) for call in mock_print.mock_calls)

    def test_all_checklist_fields_present(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_polygon_production_enablement_readiness.py",
                "--vendor",
                "polygon",
                "--dataset",
                "ohlcv",
            ],
        ):
            mod.main()
        printed = self._printed(print_mock)
        for field in (
            "api_ingestion_path=available",
            "daily_runner=available",
            "chunked_backfill_runner=available",
            "checkpointing=available",
            "run_history=available",
            "quality_results=available",
            "lineage=available",
            "evidence_chain=available",
            "scheduler_stub=disabled_by_default",
            "scheduler_disabled_verification=available",
            "quota_policy=available",
            "retry_recovery_policy=planning_only_not_enabled",
            "monitoring_alerting=planning_only_not_enabled",
            "market_calendar=manual_only_not_production_complete",
            "symbol_universe=manual_ready",
            "flatfile_pipeline=planning_only_not_enabled",
            "websocket_pipeline=not_started",
        ):
            self.assertIn(field, printed)

    def test_blockers_and_status(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch("sys.argv", ["diagnose_polygon_production_enablement_readiness.py"]):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("blockers=complete_market_calendar,monitoring_alerting_implementation,retry_recovery_implementation,production_scheduler_enablement_review,flatfile_live_discovery_download_parse,larger_universe_scale_test,vendor_tier_review", printed)
        self.assertIn("production_enablement_status=not_ready", printed)
        self.assertIn("core_foundation_status=strong_manual_foundation", printed)

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_polygon_production_enablement_readiness.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("POLYGON_API_KEY", text)
        self.assertNotIn("requests", text)
