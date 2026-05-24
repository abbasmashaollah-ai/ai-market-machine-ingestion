from __future__ import annotations

import unittest
from unittest.mock import patch


class DiagnoseMarketCalendarProviderInterfaceTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_market_calendar_provider_interface as mod

        return mod

    def _printed(self, mock_print) -> str:
        return "\n".join(" ".join(str(arg) for arg in call.args) for call in mock_print.mock_calls)

    def test_interface_diagnostic_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_market_calendar_provider_interface.py",
                "--exchange",
                "XNYS",
            ],
        ):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("exchange=XNYS", printed)
        self.assertIn("provider_interface_status=planning_only_not_enabled", printed)
        self.assertIn("current_provider=minimal_static_helper", printed)
        self.assertIn("future_provider=verified_calendar_consumer", printed)
        self.assertIn("ingestion_role=read_only_calendar_consumer", printed)

    def test_planned_methods_and_ownership_present(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch("sys.argv", ["diagnose_market_calendar_provider_interface.py"]):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("is_trading_day(date)", printed)
        self.assertIn("previous_trading_day(date)", printed)
        self.assertIn("next_trading_day(date)", printed)
        self.assertIn("trading_days(start_date,end_date)", printed)
        self.assertIn("market_open_close(date)", printed)
        self.assertIn("is_early_close(date)", printed)
        self.assertIn("closure_reason(date)", printed)
        self.assertIn("data_owner=ai-market-machine-data", printed)

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_market_calendar_provider_interface.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("requests", text)
        self.assertNotIn("POLYGON_API_KEY", text)
