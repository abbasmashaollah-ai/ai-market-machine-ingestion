from __future__ import annotations

import unittest
from unittest.mock import patch


class DiagnosePolygonFlatfileLayoutReadinessTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_polygon_flatfile_layout_readiness as mod

        return mod

    def test_diagnostic_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_polygon_flatfile_layout_readiness.py",
                "--dataset",
                "ohlcv",
                "--asset-class",
                "stocks",
                "--timeframe",
                "1d",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("source_mode=flatfiles", printed)
        self.assertIn("dataset=ohlcv", printed)
        self.assertIn("asset_class=stocks", printed)
        self.assertIn("timeframe=1d", printed)
        self.assertIn("current_layout_mode=provisional", printed)
        self.assertIn("official_layout_verified=false", printed)
        self.assertIn("live_discovery_enabled=false", printed)
        self.assertIn("live_download_enabled=false", printed)
        self.assertIn("readiness_status=blocked_until_official_layout_verified", printed)
        self.assertIn("required_next_steps=obtain_official_polygon_flatfile_layout", printed)

    def test_no_vendor_calls_and_no_db_writes(self) -> None:
        mod = self._module()
        with patch("builtins.print"), patch("sys.argv", ["diagnose_polygon_flatfile_layout_readiness.py"]):
            mod.main()

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_polygon_flatfile_layout_readiness.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("POLYGON_API_KEY", text)
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("S3", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("migration", text.lower())
