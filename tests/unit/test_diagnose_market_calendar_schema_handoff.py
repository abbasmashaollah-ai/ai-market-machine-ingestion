from __future__ import annotations

import unittest
from unittest.mock import patch


class DiagnoseMarketCalendarSchemaHandoffTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_market_calendar_schema_handoff as mod

        return mod

    def _printed(self, mock_print) -> str:
        return "\n".join(" ".join(str(arg) for arg in call.args) for call in mock_print.mock_calls)

    def test_schema_handoff_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_market_calendar_schema_handoff.py",
                "--exchange",
                "XNYS",
            ],
        ):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("exchange=XNYS", printed)
        self.assertIn("schema_owner=ai-market-machine-data", printed)
        self.assertIn("ingestion_role=read_only_consumer", printed)
        self.assertIn("schema_handoff_status=planning_only_not_enabled", printed)

    def test_expected_fields_present(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch("sys.argv", ["diagnose_market_calendar_schema_handoff.py"]):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("planned_fields=exchange,calendar_date,is_trading_day,open_time,close_time,is_early_close,closure_reason,source,source_version,generated_at,verified_at", printed)
        self.assertIn("migration_required_in_ingestion=false", printed)
        self.assertIn("required_before_consumer_integration=data_schema_created,calendar_loaded,calendar_verified,read_contract_documented", printed)

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_market_calendar_schema_handoff.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("requests", text)
        self.assertNotIn("POLYGON_API_KEY", text)
