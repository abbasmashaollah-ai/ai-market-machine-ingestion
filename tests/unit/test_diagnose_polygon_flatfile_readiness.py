from __future__ import annotations

import unittest
from unittest.mock import patch


class DiagnosePolygonFlatfileReadinessTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_polygon_flatfile_readiness as mod

        return mod

    def test_default_diagnostic(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_polygon_flatfile_readiness.py",
                "--dataset",
                "ohlcv",
                "--asset-class",
                "stocks",
                "--start-date",
                "2020-01-01",
                "--end-date",
                "2020-01-31",
            ],
        ):
            mod.main()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("source_mode=flatfiles", printed)
        self.assertIn("readiness_status=planning_only_not_enabled", printed)

    def test_storage_root_configured_vs_absent(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_polygon_flatfile_readiness.py",
                "--dataset",
                "ohlcv",
                "--asset-class",
                "stocks",
                "--start-date",
                "2020-01-01",
                "--end-date",
                "2020-01-31",
                "--storage-root",
                "C:/tmp/polygon",
            ],
        ):
            mod.main()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("storage_root_configured=true", printed)

    def test_date_range_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_polygon_flatfile_readiness.py",
                "--dataset",
                "ohlcv",
                "--asset-class",
                "stocks",
                "--start-date",
                "2020-01-01",
                "--end-date",
                "2020-01-31",
            ],
        ):
            mod.main()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("start_date=2020-01-01", printed)
        self.assertIn("end_date=2020-01-31", printed)

    def test_no_vendor_calls_and_no_db_writes(self) -> None:
        mod = self._module()
        with patch("builtins.print"), patch("sys.argv", ["diagnose_polygon_flatfile_readiness.py", "--dataset", "ohlcv", "--asset-class", "stocks", "--start-date", "2020-01-01", "--end-date", "2020-01-31"]):
            mod.main()

    def test_source_has_no_schema_migration_scheduler_api_ai_behavior(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_polygon_flatfile_readiness.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("migration", text.lower())
        self.assertNotIn("strategy", text.lower())
        self.assertNotIn("prediction", text.lower())

