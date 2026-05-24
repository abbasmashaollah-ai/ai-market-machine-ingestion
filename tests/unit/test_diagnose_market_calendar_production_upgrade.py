from __future__ import annotations

import unittest
from unittest.mock import patch


class DiagnoseMarketCalendarProductionUpgradeTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_market_calendar_production_upgrade as mod

        return mod

    def _printed(self, mock_print) -> str:
        return "\n".join(" ".join(str(arg) for arg in call.args) for call in mock_print.mock_calls)

    def test_diagnostic_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_market_calendar_production_upgrade.py",
                "--exchange",
                "XNYS",
                "--start-date",
                "2025-01-01",
                "--end-date",
                "2025-01-31",
            ],
        ):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("exchange=XNYS", printed)
        self.assertIn("start_date=2025-01-01", printed)
        self.assertIn("end_date=2025-01-31", printed)
        self.assertIn("current_calendar_mode=minimal_explicit_closures", printed)
        self.assertIn("calendar_upgrade_status=planning_only_not_enabled", printed)

    def test_required_fields_and_blocker(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_market_calendar_production_upgrade.py",
                "--exchange",
                "XNYS",
                "--start-date",
                "2025-01-01",
                "--end-date",
                "2025-01-31",
            ],
        ):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("production_calendar_required=true", printed)
        self.assertIn("holiday_calendar_required=true", printed)
        self.assertIn("special_closures_required=true", printed)
        self.assertIn("early_closes_required=true", printed)
        self.assertIn("required_before_production_scheduler=true", printed)

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_market_calendar_production_upgrade.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("requests", text)
        self.assertNotIn("POLYGON_API_KEY", text)
