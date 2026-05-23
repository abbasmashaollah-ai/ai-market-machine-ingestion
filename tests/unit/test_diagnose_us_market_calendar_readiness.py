from __future__ import annotations

import unittest
from unittest.mock import patch


class DiagnoseUsMarketCalendarReadinessTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_us_market_calendar_readiness as mod

        return mod

    def test_readiness_diagnostic_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["diagnose_us_market_calendar_readiness.py", "--start-date", "2025-01-01", "--end-date", "2025-01-15"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("calendar_mode=minimal_explicit_closures", printed)
        self.assertIn("calendar_readiness_status=manual_only_not_production_complete", printed)

    def test_known_2025_01_09_closure_appears(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["diagnose_us_market_calendar_readiness.py", "--start-date", "2025-01-01", "--end-date", "2025-01-15"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("2025-01-09", printed)

    def test_no_db_required(self) -> None:
        mod = self._module()
        with patch("builtins.print"), patch(
            "sys.argv",
            ["diagnose_us_market_calendar_readiness.py", "--start-date", "2025-01-01", "--end-date", "2025-01-15"],
        ):
            mod.main()

    def test_no_vendor_calls(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["diagnose_us_market_calendar_readiness.py", "--start-date", "2025-01-01", "--end-date", "2025-01-15"],
        ), patch("scripts.diagnose_us_market_calendar_readiness.expected_trading_days", wraps=mod.expected_trading_days) as expected_trading_days:
            mod.main()

        expected_trading_days.assert_called()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertNotIn("DATABASE_URL", printed)
        self.assertNotIn("POLYGON_API_KEY", printed)

    def test_source_has_no_schema_migration_scheduler_api_ai_behavior(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_us_market_calendar_readiness.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("migration", text.lower())
        self.assertNotIn("strategy", text.lower())
        self.assertNotIn("prediction", text.lower())
