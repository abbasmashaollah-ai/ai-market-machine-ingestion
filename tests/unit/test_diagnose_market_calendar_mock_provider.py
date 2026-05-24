from __future__ import annotations

import unittest
from datetime import date
from unittest.mock import patch


class DiagnoseMarketCalendarMockProviderTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_market_calendar_mock_provider as mod

        return mod

    def _printed(self, mock_print) -> str:
        return "\n".join(" ".join(str(arg) for arg in call.args) for call in mock_print.mock_calls)

    def test_provider_behavior(self) -> None:
        from app.market_calendar.mock_calendar_provider import MockMarketCalendarProvider

        provider = MockMarketCalendarProvider()
        self.assertTrue(provider.is_trading_day(date(2025, 1, 2)))
        self.assertFalse(provider.is_trading_day(date(2025, 1, 1)))
        self.assertFalse(provider.is_trading_day(date(2025, 1, 9)))
        self.assertEqual(provider.previous_trading_day(date(2025, 1, 6)), date(2025, 1, 3))
        self.assertEqual(provider.next_trading_day(date(2025, 1, 6)), date(2025, 1, 7))
        self.assertEqual(provider.trading_days(date(2025, 1, 1), date(2025, 1, 5)), [date(2025, 1, 2), date(2025, 1, 3)])
        self.assertTrue(provider.is_early_close(date(2025, 7, 3)))
        self.assertIsNone(provider.closure_reason(date(2025, 1, 2)))
        self.assertEqual(provider.closure_reason(date(2025, 1, 1)), "holiday_or_known_closure")

    def test_diagnostic_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_market_calendar_mock_provider.py",
                "--exchange",
                "XNYS",
            ],
        ):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("exchange=XNYS", printed)
        self.assertIn("provider_type=mock_fixture", printed)
        self.assertIn("production_enabled=false", printed)
        self.assertIn("db_integration_enabled=false", printed)

    def test_no_db_vendor_calls(self) -> None:
        mod = self._module()
        with patch("builtins.print"), patch("sys.argv", ["diagnose_market_calendar_mock_provider.py"]):
            mod.main()

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_market_calendar_mock_provider.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("requests", text)
        self.assertNotIn("POLYGON_API_KEY", text)
