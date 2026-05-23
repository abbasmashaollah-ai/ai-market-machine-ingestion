from __future__ import annotations

import unittest
from unittest.mock import patch


class DiagnoseIngestionMonitoringReadinessTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_ingestion_monitoring_readiness as mod

        return mod

    def _printed(self, mock_print) -> str:
        return "\n".join(" ".join(str(arg) for arg in call.args) for call in mock_print.mock_calls)

    def test_diagnostic_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_ingestion_monitoring_readiness.py",
                "--vendor",
                "polygon",
                "--dataset",
                "ohlcv",
            ],
        ):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("vendor=polygon", printed)
        self.assertIn("dataset=ohlcv", printed)
        self.assertIn("monitoring_enabled=false", printed)
        self.assertIn("alerting_enabled=false", printed)
        self.assertIn("monitoring_readiness_status=planning_only_not_enabled", printed)

    def test_required_alerts_and_metrics_present(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch("sys.argv", ["diagnose_ingestion_monitoring_readiness.py"]):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("required_alerts=failed_run,rate_limit,missing_coverage,quality_failed,lineage_missing,scheduler_disabled,scheduler_blocked", printed)
        self.assertIn("required_metrics=rows_fetched,rows_written,rows_rejected,error_count,coverage_ratio,latency_seconds,request_count", printed)

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_ingestion_monitoring_readiness.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("POLYGON_API_KEY", text)
        self.assertNotIn("requests", text)
