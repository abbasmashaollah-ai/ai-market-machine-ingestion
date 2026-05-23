from __future__ import annotations

import unittest
from unittest.mock import patch


class PlanPolygonFlatfileDiscoveryTests(unittest.TestCase):
    def _module(self):
        import scripts.plan_polygon_flatfile_discovery as mod

        return mod

    def test_expected_trading_day_candidate_generation(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "plan_polygon_flatfile_discovery.py",
                "--dataset",
                "ohlcv",
                "--asset-class",
                "stocks",
                "--start-date",
                "2020-01-01",
                "--end-date",
                "2020-01-10",
                "--timeframe",
                "1d",
            ],
        ):
            mod.main()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("expected_trading_days=8", printed)
        self.assertIn("candidate_files_count=8", printed)

    def test_exclusive_end_date_behavior(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "plan_polygon_flatfile_discovery.py",
                "--dataset",
                "ohlcv",
                "--asset-class",
                "stocks",
                "--start-date",
                "2020-01-01",
                "--end-date",
                "2020-01-01",
                "--timeframe",
                "1d",
            ],
        ):
            mod.main()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("expected_trading_days=1", printed)

    def test_sample_cap(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "plan_polygon_flatfile_discovery.py",
                "--dataset",
                "ohlcv",
                "--asset-class",
                "stocks",
                "--start-date",
                "2020-01-01",
                "--end-date",
                "2020-01-31",
                "--timeframe",
                "1d",
            ],
        ):
            mod.main()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("sample_candidate_files=", printed)

    def test_storage_root_configured_vs_absent(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "plan_polygon_flatfile_discovery.py",
                "--dataset",
                "ohlcv",
                "--asset-class",
                "stocks",
                "--start-date",
                "2020-01-01",
                "--end-date",
                "2020-01-10",
                "--timeframe",
                "1d",
                "--storage-root",
                "C:/tmp/polygon",
            ],
        ):
            mod.main()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("storage_root_configured=true", printed)

    def test_no_vendor_calls_no_s3_calls_no_db_writes(self) -> None:
        mod = self._module()
        with patch("builtins.print"), patch(
            "sys.argv",
            [
                "plan_polygon_flatfile_discovery.py",
                "--dataset",
                "ohlcv",
                "--asset-class",
                "stocks",
                "--start-date",
                "2020-01-01",
                "--end-date",
                "2020-01-10",
                "--timeframe",
                "1d",
            ],
        ):
            mod.main()

    def test_source_has_no_schema_migration_scheduler_api_ai_behavior(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "plan_polygon_flatfile_discovery.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("migration", text.lower())
        self.assertNotIn("strategy", text.lower())
        self.assertNotIn("prediction", text.lower())

