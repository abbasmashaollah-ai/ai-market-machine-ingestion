from __future__ import annotations

import os
import sys
import unittest
from datetime import date
from importlib import util
from pathlib import Path
from unittest.mock import Mock, patch

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "dry_run_fred_macro_incremental.py"
SPEC = util.spec_from_file_location("dry_run_fred_macro_incremental", MODULE_PATH)
dry_run_module = util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = dry_run_module
SPEC.loader.exec_module(dry_run_module)


class DryRunFredMacroIncrementalScriptTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def test_cli_argument_parsing_and_main_helper(self) -> None:
        with patch.object(dry_run_module, "load_local_env_if_available", return_value=False), patch.object(
            dry_run_module, "select_incremental_series_ids", return_value=("GDP",)
        ) as select_mock, patch.object(dry_run_module, "build_manual_fred_macro_incremental_dry_run") as dry_run_mock:
            dry_run_mock.return_value.series_summaries = ()
            with patch.dict(os.environ, {"FRED_API_KEY": "test-api-key"}, clear=True), patch(
                "builtins.print"
            ) as print_mock, patch(
                "sys.argv",
                [
                    "dry_run_fred_macro_incremental.py",
                    "--series-id",
                    "GDP",
                    "--start-date",
                    "2025-01-01",
                    "--end-date",
                    "2025-12-31",
                ],
            ):
                exit_code = dry_run_module.main()

        self.assertEqual(exit_code, 0)
        select_mock.assert_called_once()
        dry_run_mock.assert_called_once()
        self.assertFalse(print_mock.mock_calls)

    def test_missing_fred_api_key_fails_safely(self) -> None:
        with patch.object(dry_run_module, "load_local_env_if_available", return_value=False), patch(
            "builtins.print"
        ) as print_mock, patch.dict(os.environ, {}, clear=True), patch(
            "sys.argv",
            [
                "dry_run_fred_macro_incremental.py",
                "--series-id",
                "GDP",
                "--start-date",
                "2025-01-01",
                "--end-date",
                "2025-12-31",
            ],
        ):
            with self.assertRaises(RuntimeError):
                dry_run_module.main()

        self.assertFalse(print_mock.mock_calls)

    def test_safe_output_shape(self) -> None:
        from app.ingestion.manual.fred_macro_dry_run import (
            ManualFREDMacroIncrementalDryRun,
            ManualFREDMacroIncrementalDryRunRow,
        )

        summary = ManualFREDMacroIncrementalDryRun(
            series_summaries=(
                ManualFREDMacroIncrementalDryRunRow(
                    series_id="GDP",
                    rows_fetched=2,
                    rows_valid=1,
                    rows_invalid=1,
                    validation_failures=1,
                    planned_start_date=date(2025, 1, 1),
                    planned_end_date=date(2025, 12, 31),
                ),
            )
        )
        with patch("builtins.print") as print_mock:
            dry_run_module._print_summary(summary)

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("series_id=GDP", printed)
        self.assertIn("rows_fetched=2", printed)
        self.assertIn("rows_valid=1", printed)
        self.assertIn("rows_invalid=1", printed)
        self.assertIn("validation_failures=1", printed)
        self.assertIn("planned_start_date=2025-01-01", printed)
        self.assertIn("planned_end_date=2025-12-31", printed)

    def test_no_database_url_required(self) -> None:
        with patch.object(dry_run_module, "load_local_env_if_available", return_value=False), patch.object(
            dry_run_module, "select_incremental_series_ids", return_value=("GDP",)
        ), patch.object(dry_run_module, "build_manual_fred_macro_incremental_dry_run") as dry_run_mock, patch(
            "builtins.print"
        ), patch.dict(os.environ, {"FRED_API_KEY": "test-api-key"}, clear=True), patch(
            "sys.argv",
            [
                "dry_run_fred_macro_incremental.py",
                "--series-id",
                "GDP",
                "--start-date",
                "2025-01-01",
                "--end-date",
                "2025-12-31",
            ],
        ):
            dry_run_mock.return_value.series_summaries = ()
            dry_run_module.main()

        dry_run_mock.assert_called_once()

    def test_no_db_writes_or_scheduler_behavior(self) -> None:
        with patch.object(dry_run_module, "load_local_env_if_available", return_value=False), patch.object(
            dry_run_module, "select_incremental_series_ids", return_value=("GDP",)
        ), patch.object(dry_run_module, "build_manual_fred_macro_incremental_dry_run") as dry_run_mock, patch(
            "builtins.print"
        ), patch.dict(os.environ, {"FRED_API_KEY": "test-api-key"}, clear=True), patch(
            "sys.argv",
            [
                "dry_run_fred_macro_incremental.py",
                "--series-id",
                "GDP",
                "--start-date",
                "2025-01-01",
                "--end-date",
                "2025-12-31",
            ],
        ):
            dry_run_mock.return_value.series_summaries = ()
            dry_run_module.main()

        dry_run_mock.assert_called_once()

    def test_dry_run_summary_from_mocked_payload(self) -> None:
        from app.ingestion.manual.fred_macro_dry_run import build_manual_fred_macro_incremental_dry_run

        fake_client = Mock()
        fake_client.fetch_series_observations_raw.return_value = {
            "observations": [
                {"date": "2025-01-01", "value": "1.0"},
                {"date": "2025-01-02", "value": "1.1"},
            ]
        }
        with patch(
            "app.ingestion.manual.fred_macro_dry_run._build_fred_client",
            return_value=fake_client,
        ):
            summary = build_manual_fred_macro_incremental_dry_run(
                series_ids=("GDP",),
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                api_key="test-api-key",
            )

        self.assertEqual(summary.series_summaries[0].series_id, "GDP")
        self.assertEqual(summary.series_summaries[0].rows_fetched, 2)
        self.assertEqual(summary.series_summaries[0].rows_valid, 2)
        self.assertEqual(summary.series_summaries[0].rows_invalid, 0)
        self.assertEqual(summary.series_summaries[0].validation_failures, 0)

    def test_validation_failure_reporting(self) -> None:
        from app.ingestion.manual.fred_macro_dry_run import build_manual_fred_macro_incremental_dry_run

        fake_client = Mock()
        fake_client.fetch_series_observations_raw.return_value = {
            "observations": [
                {"date": "2025-01-01", "value": "."},
            ]
        }
        with patch(
            "app.ingestion.manual.fred_macro_dry_run._build_fred_client",
            return_value=fake_client,
        ):
            summary = build_manual_fred_macro_incremental_dry_run(
                series_ids=("GDP",),
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                api_key="test-api-key",
            )

        self.assertEqual(summary.series_summaries[0].rows_fetched, 1)
        self.assertEqual(summary.series_summaries[0].rows_valid, 0)
        self.assertEqual(summary.series_summaries[0].rows_invalid, 1)
        self.assertEqual(summary.series_summaries[0].validation_failures, 1)

    def test_no_secrets_printed(self) -> None:
        with patch.object(dry_run_module, "load_local_env_if_available", return_value=False), patch.object(
            dry_run_module, "select_incremental_series_ids", return_value=("GDP",)
        ), patch.object(dry_run_module, "build_manual_fred_macro_incremental_dry_run") as dry_run_mock, patch(
            "builtins.print"
        ) as print_mock, patch.dict(os.environ, {"FRED_API_KEY": "secret-value"}, clear=True), patch(
            "sys.argv",
            [
                "dry_run_fred_macro_incremental.py",
                "--series-id",
                "GDP",
                "--start-date",
                "2025-01-01",
                "--end-date",
                "2025-12-31",
            ],
        ):
            dry_run_mock.return_value.series_summaries = ()
            dry_run_module.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertNotIn("secret-value", printed)
