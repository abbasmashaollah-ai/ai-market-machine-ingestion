from __future__ import annotations

import unittest
from unittest.mock import patch


class DiagnoseMarketCalendarConsumerReadinessTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_market_calendar_consumer_readiness as mod

        return mod

    def _printed(self, mock_print) -> str:
        return "\n".join(" ".join(str(arg) for arg in call.args) for call in mock_print.mock_calls)

    def test_consumer_diagnostic_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_market_calendar_consumer_readiness.py",
                "--exchange",
                "XNYS",
            ],
        ):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("exchange=XNYS", printed)
        self.assertIn("consumer_enabled=false", printed)
        self.assertIn("consumer_mode=planning_only_not_enabled", printed)
        self.assertIn("ingestion_role=read_only_consumer", printed)

    def test_required_fields_and_owner_present(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch("sys.argv", ["diagnose_market_calendar_consumer_readiness.py"]):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("schema_owner=ai-market-machine-data", printed)
        self.assertIn("read_source=planned_table_or_view_or_api", printed)
        self.assertIn("required_contract_fields=exchange,calendar_date,is_trading_day,open_time,close_time,is_early_close,closure_reason,source,source_version,generated_at,verified_at", printed)
        self.assertIn("fallback_mode=manual_only_minimal_helper", printed)
        self.assertIn("consumer_readiness_status=planning_only_not_enabled", printed)

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_market_calendar_consumer_readiness.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("requests", text)
        self.assertNotIn("POLYGON_API_KEY", text)
