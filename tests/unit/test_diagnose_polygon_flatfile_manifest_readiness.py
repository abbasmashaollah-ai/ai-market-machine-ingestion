from __future__ import annotations

import unittest
from unittest.mock import patch


class DiagnosePolygonFlatfileManifestReadinessTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_polygon_flatfile_manifest_readiness as mod

        return mod

    def _printed(self, mock_print) -> str:
        return "\n".join(" ".join(str(arg) for arg in call.args) for call in mock_print.mock_calls)

    def test_diagnostic_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_polygon_flatfile_manifest_readiness.py",
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
        self.assertIn("manifest_enabled=false", printed)
        self.assertIn("manifest_write_enabled=false", printed)
        self.assertIn("readiness_status=planning_only_not_enabled", printed)

    def test_required_fields_present(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch("sys.argv", ["diagnose_polygon_flatfile_manifest_readiness.py"]):
            mod.main()
        printed = self._printed(print_mock)
        for field in (
            "object_key=planned",
            "local_raw_path=planned",
            "local_staging_path=planned",
            "checksum=planned",
            "size_bytes=planned",
            "discovered_at=planned",
            "downloaded_at=planned",
            "parsed_at=planned",
            "validation_status=planned",
            "quarantine_status=planned",
            "lineage_status=planned",
        ):
            self.assertIn(field, printed)

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_polygon_flatfile_manifest_readiness.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("POLYGON_API_KEY", text)
        self.assertNotIn("S3", text)
