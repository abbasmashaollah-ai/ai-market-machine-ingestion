from __future__ import annotations

import unittest
from unittest.mock import patch


class DiagnoseIngestionRetryRecoveryReadinessTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_ingestion_retry_recovery_readiness as mod

        return mod

    def _printed(self, mock_print) -> str:
        return "\n".join(" ".join(str(arg) for arg in call.args) for call in mock_print.mock_calls)

    def test_diagnostic_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_ingestion_retry_recovery_readiness.py",
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
        self.assertIn("retry_enabled=false", printed)
        self.assertIn("automatic_recovery_enabled=false", printed)
        self.assertIn("retry_policy_status=planning_only_not_enabled", printed)

    def test_required_failure_classes_and_actions_present(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch("sys.argv", ["diagnose_ingestion_retry_recovery_readiness.py"]):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("required_failure_classes=rate_limit,vendor_http_error,validation_failed,coverage_missing,checkpoint_missing,lineage_missing,quality_failed,storage_integrity_failed,parse_failed", printed)
        self.assertIn("required_recovery_actions=retry_later,resume_from_checkpoint,reduce_scope,quarantine,manual_review,skip_non_trading_day,rebuild_evidence", printed)

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_ingestion_retry_recovery_readiness.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("POLYGON_API_KEY", text)
        self.assertNotIn("requests", text)
