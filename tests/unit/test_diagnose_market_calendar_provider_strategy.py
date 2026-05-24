from __future__ import annotations

import unittest
from unittest.mock import patch


class DiagnoseMarketCalendarProviderStrategyTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_market_calendar_provider_strategy as mod

        return mod

    def _printed(self, mock_print) -> str:
        return "\n".join(" ".join(str(arg) for arg in call.args) for call in mock_print.mock_calls)

    def test_strategy_diagnostic_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_market_calendar_provider_strategy.py",
                "--exchange",
                "XNYS",
            ],
        ):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("exchange=XNYS", printed)
        self.assertIn("selected_strategy=hybrid", printed)
        self.assertIn("current_provider=minimal_static_helper", printed)
        self.assertIn("future_generation_source=trusted_exchange_calendar_source", printed)
        self.assertIn("future_storage_owner=ai-market-machine-data", printed)

    def test_ingestion_usage_and_fallback_present(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch("sys.argv", ["diagnose_market_calendar_provider_strategy.py"]):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("ingestion_usage=read_verified_calendar", printed)
        self.assertIn("fallback_mode=manual_only_minimal_helper", printed)
        self.assertIn("supports_holidays=planned", printed)
        self.assertIn("provider_strategy_status=planning_only_not_enabled", printed)

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_market_calendar_provider_strategy.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("requests", text)
        self.assertNotIn("POLYGON_API_KEY", text)
