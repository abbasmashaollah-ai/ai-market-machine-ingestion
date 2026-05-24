from __future__ import annotations

import unittest
from unittest.mock import patch


class DiagnoseMarketCalendarMockConsumerContractTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_market_calendar_mock_consumer_contract as mod

        return mod

    def _printed(self, mock_print) -> str:
        return "\n".join(" ".join(str(arg) for arg in call.args) for call in mock_print.mock_calls)

    def test_mock_contract_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_market_calendar_mock_consumer_contract.py",
                "--exchange",
                "XNYS",
            ],
        ):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("exchange=XNYS", printed)
        self.assertIn("consumer_contract_status=mock_contract_planned", printed)
        self.assertIn("db_integration_enabled=false", printed)
        self.assertIn("production_calendar_enabled=false", printed)

    def test_return_expectations_present(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch("sys.argv", ["diagnose_market_calendar_mock_consumer_contract.py"]):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("is_trading_day_returns_bool=true", printed)
        self.assertIn("previous_trading_day_returns_date=true", printed)
        self.assertIn("next_trading_day_returns_date=true", printed)
        self.assertIn("trading_days_returns_ordered_dates=true", printed)
        self.assertIn("market_open_close_returns_times=true", printed)
        self.assertIn("early_close_returns_bool=true", printed)
        self.assertIn("closure_reason_returns_nullable_string=true", printed)

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_market_calendar_mock_consumer_contract.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("requests", text)
        self.assertNotIn("POLYGON_API_KEY", text)
