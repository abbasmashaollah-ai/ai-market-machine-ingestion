from __future__ import annotations

import unittest
from unittest.mock import patch


class DiagnoseMarketCalendarFallbackBehaviorTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_market_calendar_fallback_behavior as mod

        return mod

    def _printed(self, mock_print) -> str:
        return "\n".join(" ".join(str(arg) for arg in call.args) for call in mock_print.mock_calls)

    def test_fallback_diagnostic_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_market_calendar_fallback_behavior.py",
                "--exchange",
                "XNYS",
            ],
        ):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("exchange=XNYS", printed)
        self.assertIn("production_calendar_available=false", printed)
        self.assertIn("current_fallback=minimal_static_helper", printed)
        self.assertIn("fallback_status=manual_only", printed)

    def test_allowed_and_forbidden_sets_present(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch("sys.argv", ["diagnose_market_calendar_fallback_behavior.py"]):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("fallback_allowed_for=manual_tests,planning_diagnostics", printed)
        self.assertIn("fallback_forbidden_for=production_scheduler,large_backfills,flatfile_persistence,official_gap_fill", printed)
        self.assertIn("required_before_production=data_calendar_schema,verified_calendar_loaded,deterministic_tests,consumer_integration", printed)

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_market_calendar_fallback_behavior.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("requests", text)
        self.assertNotIn("POLYGON_API_KEY", text)
