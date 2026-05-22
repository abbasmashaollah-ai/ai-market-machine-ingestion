from __future__ import annotations

from datetime import date
import unittest
from unittest.mock import patch


class PreviewFredMacroIncrementalScriptTests(unittest.TestCase):
    def test_cli_argument_parsing_and_main_helper(self) -> None:
        from scripts import preview_fred_macro_incremental as mod

        with patch.object(mod, "build_manual_fred_macro_incremental_preview") as preview_mock:
            preview_mock.return_value.plan.plan_id = "manual-preview"
            preview_mock.return_value.plan.series_ids = ("GDP",)
            preview_mock.return_value.plan.start_date = date(2025, 1, 1)
            preview_mock.return_value.plan.end_date = date(2025, 12, 31)
            preview_mock.return_value.plan.checkpoint_keys = ("fred:macro_observations:GDP:1d:2025-01-01:2025-12-31",)
            preview_mock.return_value.checkpoints = ()
            preview_mock.return_value.results = ()
            with patch("builtins.print") as print_mock:
                with patch("sys.argv", ["preview_fred_macro_incremental.py", "--series-id", "GDP", "--start-date", "2025-01-01", "--end-date", "2025-12-31"]):
                    exit_code = mod.main()

        self.assertEqual(exit_code, 0)
        preview_mock.assert_called_once()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("plan_id=manual-preview", printed)

    def test_safe_output_shape(self) -> None:
        from scripts import preview_fred_macro_incremental as mod

        with patch.object(mod, "build_manual_fred_macro_incremental_preview") as preview_mock:
            preview_mock.return_value.plan.plan_id = "manual-preview"
            preview_mock.return_value.plan.series_ids = ("GDP",)
            preview_mock.return_value.plan.start_date = date(2025, 1, 1)
            preview_mock.return_value.plan.end_date = date(2025, 12, 31)
            preview_mock.return_value.plan.checkpoint_keys = ("fred:macro_observations:GDP:1d:2025-01-01:2025-12-31",)
            preview_mock.return_value.checkpoints = ()
            preview_mock.return_value.results = ()
            with patch("builtins.print") as print_mock:
                with patch("sys.argv", ["preview_fred_macro_incremental.py", "--series-id", "GDP", "--start-date", "2025-01-01", "--end-date", "2025-12-31"]):
                    mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("series_ids=('GDP',)", printed)
        self.assertIn("start_date=2025-01-01", printed)
        self.assertIn("end_date=2025-12-31", printed)

    def test_no_vendor_calls(self) -> None:
        from scripts import preview_fred_macro_incremental as mod

        with patch.object(mod, "build_manual_fred_macro_incremental_preview") as preview_mock:
            preview_mock.return_value.plan.plan_id = "manual-preview"
            preview_mock.return_value.plan.series_ids = ("GDP",)
            preview_mock.return_value.plan.start_date = date(2025, 1, 1)
            preview_mock.return_value.plan.end_date = date(2025, 12, 31)
            preview_mock.return_value.plan.checkpoint_keys = ()
            preview_mock.return_value.checkpoints = ()
            preview_mock.return_value.results = ()
            with patch("sys.argv", ["preview_fred_macro_incremental.py", "--series-id", "GDP", "--start-date", "2025-01-01", "--end-date", "2025-12-31"]):
                mod.main()

        preview_mock.assert_called_once()

    def test_no_db_writes(self) -> None:
        from scripts import preview_fred_macro_incremental as mod

        with patch.object(mod, "build_manual_fred_macro_incremental_preview") as preview_mock:
            preview_mock.return_value.plan.plan_id = "manual-preview"
            preview_mock.return_value.plan.series_ids = ("GDP",)
            preview_mock.return_value.plan.start_date = date(2025, 1, 1)
            preview_mock.return_value.plan.end_date = date(2025, 12, 31)
            preview_mock.return_value.plan.checkpoint_keys = ()
            preview_mock.return_value.checkpoints = ()
            preview_mock.return_value.results = ()
            with patch("sys.argv", ["preview_fred_macro_incremental.py", "--series-id", "GDP", "--start-date", "2025-01-01", "--end-date", "2025-12-31"]):
                mod.main()

        preview_mock.assert_called_once()

    def test_no_scheduler_behavior(self) -> None:
        from scripts import preview_fred_macro_incremental as mod

        with patch.object(mod, "build_manual_fred_macro_incremental_preview") as preview_mock:
            preview_mock.return_value.plan.plan_id = "manual-preview"
            preview_mock.return_value.plan.series_ids = ("GDP",)
            preview_mock.return_value.plan.start_date = date(2025, 1, 1)
            preview_mock.return_value.plan.end_date = date(2025, 12, 31)
            preview_mock.return_value.plan.checkpoint_keys = ()
            preview_mock.return_value.checkpoints = ()
            preview_mock.return_value.results = ()
            with patch("sys.argv", ["preview_fred_macro_incremental.py", "--series-id", "GDP", "--start-date", "2025-01-01", "--end-date", "2025-12-31"]):
                mod.main()

        preview_mock.assert_called_once()

    def test_no_required_database_url_or_fred_api_key(self) -> None:
        from scripts import preview_fred_macro_incremental as mod

        with patch.object(mod, "build_manual_fred_macro_incremental_preview") as preview_mock:
            preview_mock.return_value.plan.plan_id = "manual-preview"
            preview_mock.return_value.plan.series_ids = ("GDP",)
            preview_mock.return_value.plan.start_date = date(2025, 1, 1)
            preview_mock.return_value.plan.end_date = date(2025, 12, 31)
            preview_mock.return_value.plan.checkpoint_keys = ()
            preview_mock.return_value.checkpoints = ()
            preview_mock.return_value.results = ()
            with patch("sys.argv", ["preview_fred_macro_incremental.py", "--series-id", "GDP", "--start-date", "2025-01-01", "--end-date", "2025-12-31"]):
                mod.main()

        preview_mock.assert_called_once()
