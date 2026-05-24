from __future__ import annotations

import unittest
from unittest.mock import patch


class DiagnoseVerifiedCalendarConsumerImplementationPlanTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_verified_calendar_consumer_implementation_plan as mod

        return mod

    def _printed(self, mock_print) -> str:
        return "\n".join(" ".join(str(arg) for arg in call.args) for call in mock_print.mock_calls)

    def test_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch("sys.argv", ["diagnose_verified_calendar_consumer_implementation_plan.py", "--exchange", "XNYS"]):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("exchange=XNYS", printed)
        self.assertIn("implementation_status=planning_only_not_enabled", printed)
        self.assertIn("current_minimal_helper_status=manual_only_fallback", printed)
        self.assertIn("mock_provider_status=test_support_only", printed)
        self.assertIn("verified_consumer_status=not_implemented", printed)
        self.assertIn("data_owner=ai-market-machine-data", printed)
        self.assertIn("ingestion_role=read_only_consumer", printed)
        self.assertIn("production_switch_enabled=false", printed)

    def test_known_gap_present(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch("sys.argv", ["diagnose_verified_calendar_consumer_implementation_plan.py"]):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("known_comparison_gap=2025-01-01 closure difference", printed)

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_verified_calendar_consumer_implementation_plan.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("requests", text)
        self.assertNotIn("POLYGON_API_KEY", text)
