from __future__ import annotations

import unittest
from unittest.mock import patch


class DiagnosePolygonFlatfileIntegrityReadinessTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_polygon_flatfile_integrity_readiness as mod

        return mod

    def _printed(self, mock_print) -> str:
        return "\n".join(" ".join(str(arg) for arg in call.args) for call in mock_print.mock_calls)

    def test_diagnostic_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_polygon_flatfile_integrity_readiness.py",
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
        self.assertIn("checksum_policy_defined=false", printed)
        self.assertIn("checksum_algorithm=planned", printed)
        self.assertIn("integrity_readiness_status=planning_only_not_enabled", printed)

    def test_required_policy_flags_present(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch("sys.argv", ["diagnose_polygon_flatfile_integrity_readiness.py"]):
            mod.main()
        printed = self._printed(print_mock)
        for field in (
            "size_check_required=true",
            "empty_file_check_required=true",
            "schema_probe_required=true",
            "quarantine_policy_required=true",
            "manifest_integration_required=true",
            "required_before_download_enablement=checksum_policy_defined, quarantine_policy_defined, manifest_write_enabled",
        ):
            self.assertIn(field, printed)

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_polygon_flatfile_integrity_readiness.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("POLYGON_API_KEY", text)
        self.assertNotIn("S3", text)
