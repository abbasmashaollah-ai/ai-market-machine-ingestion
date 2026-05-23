from __future__ import annotations

import unittest
from unittest.mock import patch


class DiagnosePolygonFlatfileParseReadinessTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_polygon_flatfile_parse_readiness as mod

        return mod

    def _printed(self, mock_print) -> str:
        return "\n".join(" ".join(str(arg) for arg in call.args) for call in mock_print.mock_calls)

    def test_diagnostic_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_polygon_flatfile_parse_readiness.py",
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
        self.assertIn("parse_enabled=false", printed)
        self.assertIn("parse_mode=dry_run_planning_only", printed)
        self.assertIn("parse_readiness_status=planning_only_not_enabled", printed)

    def test_required_columns_present(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch("sys.argv", ["diagnose_polygon_flatfile_parse_readiness.py"]):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("required_columns=symbol,timestamp,open,high,low,close,volume", printed)
        self.assertIn("normalization_target=shared_ohlcv_normalization", printed)
        self.assertIn("validation_target=shared_ohlcv_validation", printed)
        self.assertIn("writer_target=shared_ohlcv_writer", printed)
        self.assertIn("evidence_target=run_history,quality,lineage", printed)

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_polygon_flatfile_parse_readiness.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("POLYGON_API_KEY", text)
        self.assertNotIn("S3", text)
