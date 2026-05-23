from __future__ import annotations

import unittest
from unittest.mock import patch


class DiagnoseIngestionFailureRecoveryRunbookTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_ingestion_failure_recovery_runbook as mod

        return mod

    def _printed(self, mock_print) -> str:
        return "\n".join(" ".join(str(arg) for arg in call.args) for call in mock_print.mock_calls)

    def test_all_failure_classes_included(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_ingestion_failure_recovery_runbook.py",
                "--vendor",
                "polygon",
                "--dataset",
                "ohlcv",
            ],
        ):
            mod.main()
        printed = self._printed(print_mock)
        for failure_class in (
            "rate_limit",
            "vendor_http_error",
            "validation_failed",
            "coverage_missing",
            "checkpoint_missing",
            "lineage_missing",
            "quality_failed",
            "storage_integrity_failed",
            "parse_failed",
        ):
            self.assertIn(f"failure_class={failure_class}", printed)

    def test_safe_command_generation(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch("sys.argv", ["diagnose_ingestion_failure_recovery_runbook.py"]):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("recommended_command=scripts.diagnose_ohlcv_coverage", printed)
        self.assertIn("recommended_command=scripts.inspect_polygon_ohlcv_checkpoint", printed)
        self.assertIn("recommended_command=manual_review_only", printed)

    def test_no_confirm_write_and_no_secrets(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch("sys.argv", ["diagnose_ingestion_failure_recovery_runbook.py"]):
            mod.main()
        printed = self._printed(print_mock)
        self.assertNotIn("--confirm-write", printed)
        self.assertNotIn("POLYGON_API_KEY", printed)
        self.assertNotIn("DATABASE_URL", printed)
        self.assertIn("automatic_recovery_enabled=false", printed)

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_ingestion_failure_recovery_runbook.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("POLYGON_API_KEY", text)
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("subprocess", text)
