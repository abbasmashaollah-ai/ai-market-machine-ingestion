from __future__ import annotations

import os
import unittest
from unittest.mock import patch


class DiagnosePolygonFlatfileDownloadReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.diagnose_polygon_flatfile_download_readiness as mod

        return mod

    def _printed(self, mock_print) -> str:
        return "\n".join(" ".join(str(arg) for arg in call.args) for call in mock_print.mock_calls)

    def test_diagnostic_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_polygon_flatfile_download_readiness.py",
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
        self.assertIn("download_enabled=false", printed)
        self.assertIn("download_mode=dry_run_planning_only", printed)
        self.assertIn("download_readiness_status=planning_only_not_enabled", printed)

    def test_storage_root_configured_vs_absent(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["diagnose_polygon_flatfile_download_readiness.py"],
        ):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("storage_root_configured=false", printed)

        with patch.dict(os.environ, {"POLYGON_FLATFILE_STORAGE_ROOT": "C:/tmp/flatfiles"}, clear=True), patch(
            "builtins.print"
        ) as print_mock, patch("sys.argv", ["diagnose_polygon_flatfile_download_readiness.py"]):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("storage_root_configured=true", printed)

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_polygon_flatfile_download_readiness.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("POLYGON_API_KEY", text)
        self.assertNotIn("S3", text)
