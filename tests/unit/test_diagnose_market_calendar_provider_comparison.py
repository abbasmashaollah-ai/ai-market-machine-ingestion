from __future__ import annotations

import unittest
from unittest.mock import patch


class DiagnoseMarketCalendarProviderComparisonTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_market_calendar_provider_comparison as mod

        return mod

    def _printed(self, mock_print) -> str:
        return "\n".join(" ".join(str(arg) for arg in call.args) for call in mock_print.mock_calls)

    def test_comparison_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_market_calendar_provider_comparison.py",
                "--exchange",
                "XNYS",
                "--start-date",
                "2025-01-01",
                "--end-date",
                "2025-01-15",
            ],
        ):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("exchange=XNYS", printed)
        self.assertIn("start_date=2025-01-01", printed)
        self.assertIn("end_date=2025-01-15", printed)
        self.assertIn("comparison_status=diagnostic_only", printed)
        self.assertIn("production_switch_enabled=false", printed)

    def test_differing_dates_present_when_applicable(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_market_calendar_provider_comparison.py",
                "--exchange",
                "XNYS",
                "--start-date",
                "2025-01-01",
                "--end-date",
                "2025-01-15",
            ],
        ):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("differing_dates=", printed)
        self.assertIn("differing_dates_count=", printed)
        self.assertIn("differing_dates_count=1", printed)
        self.assertIn("differing_dates=2025-01-01", printed)

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_market_calendar_provider_comparison.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("requests", text)
        self.assertNotIn("POLYGON_API_KEY", text)
